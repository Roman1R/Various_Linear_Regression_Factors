import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler


def compute_metrics(y_true, y_pred):
    """
    Вычисляет MSE, RMSE и R2 с использованием векторных операций NumPy.
    """
    # MSE
    mse = np.mean((y_true - y_pred) ** 2)
    rmse = np.sqrt(mse)

    # R2
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_total = np.sum((y_true - np.mean(y_true)) ** 2)
    r2 = 1 - (ss_res / ss_total)

    return mse, rmse, r2


def fit_linear_regression(X, y, learning_rate=0.05, epochs=1000):
    """
    Обучение линейной регрессии градиентным спуском в матричном виде.
    """
    X = np.array(X)
    y = np.array(y).reshape(-1, 1)  # Превращаем в вектор-столбец

    # Столбец единиц
    ones = np.ones((X.shape[0], 1))
    X_bias = np.hstack((ones, X))

    # Инициализируем веса нулями
    n_samples, n_features = X_bias.shape
    weights = np.zeros((n_features, 1))

    # Цикл градиентного спуска
    for epoch in range(epochs):
        # Предсказание модели: Y_pred = X * w
        y_pred = np.dot(X_bias, weights)

        # Ошибка: (Y_pred - Y)
        error = y_pred - y

        # Векторный градиент
        gradient = (2 / n_samples) * np.dot(X_bias.T, error)

        # Обновление весов
        weights -= learning_rate * gradient

    b = weights[0][0]
    w = weights[1:].flatten()
    return w, b


def predict(X, w, b):
    """Функция предсказания"""
    return np.dot(np.array(X), w) + b


# Загружаем тренировочный сэмпл
df_train = pd.read_csv('dataset_sample_1000.csv')
X_train = df_train.drop(columns=['Цена_log'])
y_train = df_train['Цена_log']

# Загружаем тестовый датасет
df_test = pd.read_csv('dataset_prepared.csv')
X_test = df_test.drop(columns=['Цена_log'])
y_test = df_test['Цена_log']

scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

w, b = fit_linear_regression(X_train_scaled, y_train, learning_rate=0.05, epochs=1000)

print("Обучение завершено")
print(f"Свободный член (b): {b:.4f}")
print(f"Количество весов: {len(w)}")

# Предсказание
y_pred_test = predict(X_test_scaled, w, b)

mse, rmse, r2 = compute_metrics(y_test.values, y_pred_test.flatten())

print("\nРезультаты на тестовой выборке")
print(f"MSE:  {mse:.5f}")
print(f"RMSE: {rmse:.5f}")
print(f"R2:   {r2:.5f}")
