import math
import telebot
from telebot import types
import tgtoken

bot = telebot.TeleBot(tgtoken.TOKEN)

# Временные хранилища сессий
USER_DATA = {}   # {chat_id: {имя_колонки: значение}}
USER_STEPS = {}  # {chat_id: текущий_объект_шага}

# ЭТАЛОННЫЙ список признаков, строго в том порядке, в котором их ждет модель
FEATURE_COLUMNS = [
    "Чистовая отделка", "Проверено в Росреестре", "От зайстройщика",
    "Log_Площадь", "Log_Кол_во_этажей", "Близость_к_центру_exp",
    "is_first_floor", "is_last_floor",
    "Ближайшая станция метро_Аметьево", "Ближайшая станция метро_Горки",
    "Ближайшая станция метро_Дубравная", "Ближайшая станция метро_Козья слобода",
    "Ближайшая станция метро_Кремлёвская", "Ближайшая станция метро_Площадь Тукая",
    "Ближайшая станция метро_Проспект Победы", "Ближайшая станция метро_Северный вокзал",
    "Ближайшая станция метро_Суконная слобода", "Ближайшая станция метро_Яшьлек",
    "Балкон/Лоджия_Балкон", "Балкон/Лоджия_Лоджия"
]

# --- БАЗОВЫЙ КЛАСС ЦЕПОЧКИ ---
class BaseStep:
    def __init__(self, prompt_text, next_step=None):
        self.prompt_text = prompt_text        # Вопрос для пользователя
        self.next_step = next_step            # Следующий шаг

    def send_question(self, chat_id):
        """Отправляет вопрос. По умолчанию добавляет кнопку 'Пропустить'"""
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton("🤷‍♂️ Пропустить / Не знаю"))
        bot.send_message(chat_id, self.prompt_text, reply_markup=markup)

    def process_input(self, message, data_dict):
        """Валидирует ввод и записывает данные в data_dict.
        Возвращает (True, None) или (False, "Текст ошибки")"""
        raise NotImplementedError

# --- 1. ШАГ ДЛЯ ЛОГАРИФМИРУЕМЫХ ЧИСЕЛ ---
class LogNumericStep(BaseStep):
    def __init__(self, feature_name, prompt_text, default_value, next_step=None):
        super().__init__(prompt_text, next_step)
        self.feature_name = feature_name
        self.default_value = default_value  # Среднее значение в реальных единицах (например, 55 для площади)

    def process_input(self, message, data_dict):
        text = message.text.strip()
        if text == "🤷‍♂️ Пропустить / Не знаю":
            data_dict[self.feature_name] = math.log(self.default_value)
            return True, None

        try:
            value = float(text.replace(',', '.'))
            if value <= 0:
                return False, "Значение должно быть больше 0. Попробуй еще раз:"

            # Логарифмируем на лету перед записью в словарь признаков
            data_dict[self.feature_name] = math.log1p(value)
            return True, None
        except ValueError:
            return False, "Пожалуйста, введи корректное число (например, 45.5):"

# --- 2. ШАГ ДЛЯ ОБЫЧНЫХ ЧИСЕЛ ---
class RegularNumericStep(BaseStep):
    def __init__(self, feature_name, prompt_text, default_value, next_step=None):
        super().__init__(prompt_text, next_step)
        self.feature_name = feature_name
        self.default_value = default_value

    def process_input(self, message, data_dict):
        text = message.text.strip()
        if text == "🤷‍♂️ Пропустить / Не знаю":
            data_dict[self.feature_name] = self.default_value
            return True, None
        try:
            value = float(text.replace(',', '.'))
            data_dict[self.feature_name] = value
            return True, None
        except ValueError:
            return False, "Не удалось распознать число. Введи еще раз:"

# --- 3. ШАГ ДЛЯ БИНАРНЫХ ПРИЗНАКОВ (Да/Нет -> 1/0) ---
class BinaryStep(BaseStep):
    def __init__(self, feature_name, prompt_text, default_value=0, next_step=None):
        super().__init__(prompt_text, next_step)
        self.feature_name = feature_name
        self.default_value = default_value # По умолчанию 0 (наиболее частый класс)

    def send_question(self, chat_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        markup.add(types.KeyboardButton("Да"), types.KeyboardButton("Нет"))
        markup.add(types.KeyboardButton("🤷‍♂️ Пропустить / Не знаю"))
        bot.send_message(chat_id, self.prompt_text, reply_markup=markup)

    def process_input(self, message, data_dict):
        text = message.text.strip().lower()
        if text == "🤷‍♂️ пропустить / не знаю":
            data_dict[self.feature_name] = self.default_value
            return True, None
        if text == "да":
            data_dict[self.feature_name] = 1
            return True, None
        if text == "нет":
            data_dict[self.feature_name] = 0
            return True, None
        return False, "Пожалуйста, нажми кнопку 'Да' или 'Нет':"

# --- 4. ШАГ ДЛЯ ONE-HOT КАТЕГОРИЙ (Метро, Балконы) ---
class OneHotCategoricalStep(BaseStep):
    def __init__(self, prefix, categories, prompt_text, default_category=None, next_step=None):
        super().__init__(prompt_text, next_step)
        self.prefix = prefix                  # Например, "Ближайшая станция метро_"
        self.categories = categories          # Список чистых названий ["Аметьево", "Горки"...]
        self.default_category = default_category # Мода (самая частая категория для пропуска)

    def send_question(self, chat_id):
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        # Добавляем кнопки категорий по 2 в ряд для красоты
        buttons = [types.KeyboardButton(cat) for cat in self.categories]
        markup.add(*buttons)
        markup.add(types.KeyboardButton("🤷‍♂️ Пропустить / Не знаю"))
        bot.send_message(chat_id, self.prompt_text, reply_markup=markup)

    def process_input(self, message, data_dict):
        text = message.text.strip()

        if text == "🤷‍♂️ Пропустить / Не знаю":
            chosen = self.default_category
        elif text in self.categories:
            chosen = text
        else:
            return False, "Такого варианта нет. Выберите, пожалуйста, вариант на кнопках:"

        # Кодируем One-Hot: сбрасываем все станции/балконы группы в 0, выбранную ставим в 1
        for cat in self.categories:
            column_name = f"{self.prefix}{cat}"
            if column_name in FEATURE_COLUMNS:
                data_dict[column_name] = 1 if cat == chosen else 0

        return True, None


# =====================================================================
# СБОРКА ЦЕПОЧКИ ОБЯЗАННОСТЕЙ (С конца к началу)
# =====================================================================

# 10. От застройщика
step_developer = BinaryStep("От зайстройщика", "Квартира продается от застройщика?", default_value=0)

# 9. Проверено в Росреестре
step_rosreestr = BinaryStep("Проверено в Росреестре", "Объект проверен в Росреестре?", default_value=1, next_step=step_developer)

# 8. Чистовая отделка
step_renovation = BinaryStep("Чистовая отделка", "В квартире выполнена чистовая отделка?", default_value=0, next_step=step_rosreestr)

# 7. Балкон / Лоджия (Категориальный One-Hot)
# Если пользователь выберет "Нет", обе колонки (Балкон/Лоджия) останутся нулями, что логично
step_balcony = OneHotCategoricalStep(
    prefix="Балкон/Лоджия_",
    categories=["Балкон", "Лоджия", "Нет"],
    prompt_text="Что из этого есть в квартире?",
    default_category="Нет",
    next_step=step_renovation
)

# 6. Ближайшее метро (Категориальный One-Hot)
metro_list = ["Аметьево", "Горки", "Дубравная", "Козья слобода", "Кремлёвская", "Площадь Тукая", "Проспект Победы", "Северный вокзал", "Суконная слобода", "Яшьлек"]
step_metro = OneHotCategoricalStep(
    prefix="Ближайшая станция метро_",
    categories=metro_list,
    prompt_text="Выберите ближайшую станцию метро:",
    default_category="Площадь Тукая",
    next_step=step_balcony
)

# 5. Близость к центру
step_center = RegularNumericStep("Близость_к_центру_exp", "Введите показатель близости к центру (из вашего датасета):", default_value=1.0, next_step=step_metro)

# 4. Последний этаж?
step_last_floor = BinaryStep("is_last_floor", "Это последний этаж?", default_value=0, next_step=step_center)

# 3. Первый этаж?
step_first_floor = BinaryStep("is_first_floor", "Это первый этаж?", default_value=0, next_step=step_last_floor)

# 2. Количество этажей в доме (будет логарифмировано)
step_floors = LogNumericStep("Log_Кол_во_этажей", "Введите общее количество этажей в доме:", default_value=9.0, next_step=step_first_floor)

# 1. Площадь квартиры (СТАРТ ЦЕПОЧКИ, будет логарифмировано)
start_chain_step = LogNumericStep("Log_Площадь", "Введите площадь квартиры в кв.м.:", default_value=50.0, next_step=step_floors)


# =====================================================================
# ФУНКЦИЯ ИНФЕРЕНСА МОДЕЛИ
# =====================================================================
def predict_apartment_price(data_dict):
    """
    Функция принимает сырой словарь с признаками пользователя,
    сортирует их строго под модель и делает предсказание.
    """
    # 1. Собираем вектор признаков строго в нужном порядке колонок
    input_vector = [data_dict[col] for col in FEATURE_COLUMNS]

    # Печать для отладки в консоль сервера
    print("Входной вектор для модели:", input_vector)

    # 2. ТВОЙ КОД ИНФЕРЕНСА (Заглушка)
    # Здесь ты загрузишь свою модель через pickle/joblib:
    # log_prediction = model.predict([input_vector])[0]

    # Имитация работы линейной регрессии для теста:
    log_prediction = 11.0 + (data_dict["Log_Площадь"] * 0.8) + (data_dict["Чистовая отделка"] * 0.1)

    # 3. Экспонируем предсказание, так как модель предсказывала логарифм цены
    actual_price = math.expm1(log_prediction)

    return round(actual_price)


# =====================================================================
# ОБРАБОТЧИКИ ТЕЛЕГРАМ
# =====================================================================
@bot.message_handler(commands=['start', 'predict'])
def start_prediction(message):
    chat_id = message.chat.id

    # Важно: Инициализируем словарь НУЛЯМИ для всех признаков из датасета
    USER_DATA[chat_id] = {col: 0 for col in FEATURE_COLUMNS}

    # Сажаем пользователя на первый шаг цепочки
    USER_STEPS[chat_id] = start_chain_step

    bot.send_message(chat_id, "📈 Привет! Я помогу рассчитать рыночную стоимость квартиры на основе ML-модели. Ответь на несколько вопросов.")
    start_chain_step.send_question(chat_id)

@bot.message_handler(func=lambda message: message.chat.id in USER_STEPS)
def handle_chain(message):
    chat_id = message.chat.id
    current_step = USER_STEPS[chat_id]

    # Запускаем обработку и валидацию текущего звена цепи
    success, error_msg = current_step.process_input(message, USER_DATA[chat_id])

    if not success:
        # Если пользователь ввел ерунду, бот ругается и просит ввести заново на этом же шаге
        bot.send_message(chat_id, error_msg)
        return

    # Если шаг пройден успешно, проверяем, есть ли следующее звено
    if current_step.next_step:
        USER_STEPS[chat_id] = current_step.next_step
        USER_STEPS[chat_id].send_question(chat_id)
    else:
        # Цепочка завершена! Время делать магию предсказания
        bot.send_message(chat_id, "⏳ Все данные собраны. Произвожу расчет стоимости...", reply_markup=types.ReplyKeyboardRemove())

        try:
            predicted_price = predict_apartment_price(USER_DATA[chat_id])

            # Красиво форматируем цену (разделяем разряды пробелами, например, 6 500 000)
            formatted_price = f"{predicted_price:,}".replace(",", " ")

            bot.send_message(chat_id, f"🎯 **Прогноз стоимости квартиры:**\n💰 примерно **{formatted_price} руб.**", parse_mode="Markdown")
        except Exception as e:
            bot.send_message(chat_id, "❌ Произошла ошибка при вычислении стоимости моделью.")
            print(f"Ошибка инференса: {e}")

        # Очищаем состояние пользователя, завершая сессию
        USER_STEPS.pop(chat_id, None)
        USER_DATA.pop(chat_id, None)

if __name__ == '__main__':
    print("Робот-оценщик успешно запущен...")
    bot.infinity_polling()