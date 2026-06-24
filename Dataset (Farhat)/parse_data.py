import time
import random
import json
from playwright.sync_api import sync_playwright

def main():
    with sync_playwright() as p:
        # Запускаем браузер со специальными аргументами маскировки
        browser = p.chromium.launch(
            headless=False,
            args=[
                '--disable-blink-features=AutomationControlled',  # Отключает детекты автоматизации Chromium
                '--start-maximized'
            ]
        )

        # Настраиваем контекст, подменяя User-Agent на реальный человеческий
        context = browser.new_context(
            no_viewport=True,  # Позволяет окну быть на весь экран легитимно
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
            locale='ru-RU',
            timezone_id='Europe/Moscow'
        )

        page = context.new_page()

        # Скрываем флаг navigator.webdriver (главный триггер для антифрода) на уровне движка страницы
        page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # 1. Инициализируем сессию
        print("Инициализация сессии на Avito...")
        referer_url = 'https://www.avito.ru/kazan/kvartiry/prodam/studii-ASgBAgICAkSSA8YQygj~WA?cd=1&context=H4sIAAAAAAAA_wEmANn_YToxOntzOjE6InkiO3M6MTY6Inl3Q3E4czJpTmdLZnFQRFMiO30kW0UTJgAAAA&localPriority=0'
        page.goto(referer_url, wait_until='domcontentloaded')

        time.sleep(random.uniform(4.0, 6.0))

        # 2. Основной цикл пагинации (ваш код)
        for i in range(1, 40):
            print(f'Итерация {i}')
            url = f'https://www.avito.ru/web/1/js/items?categoryId=24&locationId=650400&cd=1&p=2&params%5B201%5D=1059&params%5B549%5D%5B0%5D=5695&verticalCategoryId=1&rootCategoryId=4&localPriority=0&updateListOnly=true&features%5BimageAspectRatio%5D=1%3A1&features%5BnoPlaceholders%5D=true&features%5BjustSpa%5D=true&features%5Bresponsive%5D=true&features%5BuseReload%5D=true&features%5BstickyCatalogFilters%5D=false&features%5BadsInMapTest%5D%5Bstep7_3%5D=false&features%5BadsInMapTest%5D%5Bstep5%5D=false&features%5BadsInMapTest%5D%5Bstep7%5D=false&features%5BmapButtonSlimTest%5D=false&features%5BlistVip%5D=false&features%5BnewDoublesUxTest%5D=false&features%5BnewDoublesUxRealtyTest%5D=false&features%5BnewDoublesMapRealtyTest%5D=false&features%5BsimpleCounters%5D=true&features%5BisRatingExperiment%5D=true&features%5BisContactsButtonRedesigned%5D=false&features%5BdesktopPublishFromSerpTest%5D=false&features%5BdesktopPinPositionVrTop%5D=false&features%5BdesktopHideContextPositionOnReject%5D=false&features%5BdesktopShowBigContextPositions%5D=true&features%5BdesktopSpaInFilters%5D=false&features%5BisReMapPreviewAb%5D=true&features%5BisReItemNewViewAb%5D=true&features%5BisReNewSortAb%5D=true&features%5BisReItemXlAb%5D=true&features%5BisSplitAdvertBlock%5D=false&features%5BsuggestParams%5D%5BcategoryID%5D=24&features%5BsuggestParams%5D%5BlocationID%5D=650400&features%5BsuggestParams%5D%5BpresentationType%5D=serp&features%5BsuggestParams%5D%5Bparams%5D%5B201%5D=1059&features%5BsuggestParams%5D%5Bparams%5D%5B549%5D%5B0%5D=5695&features%5BisShowWithPhotoFilter%5D=true&features%5BreverseVisualRubricator%5D=false&features%5BisReInterestingHouseAb%5D=false&features%5BjobsConsentDisclaimer%5D=false&features%5BaltViewedBadgeDesktopAb%5D=false&features%5BisHideRecommendationsInfinite%5D=false&features%5BdesktopGridRedesign%5D%5BisReducedGridWidth%5D=true&features%5BivaItemRedesign%5D=true&features%5BshouldSendRreLayoutEvents%5D=true&features%5BisRedesignZhkSerp%5D=true&features%5BisHotelsSnippetRedesign%5D=false&subscription%5Bvisible%5D=true&subscription%5BisShowSavedTooltip%5D=false&subscription%5BisErrorSaved%5D=false&subscription%5BisAuthenticated%5D=false&proprofile=1&useReload=true&spaFlow=true&context=H4sIAAAAAAAA_wEmANn_YToxOntzOjE6InkiO3M6MTY6IndRajJoU3h4YmQxZ1I0ZnUiO33Res1SJgAAAA'

            try:
                js_script = f'''
                async () => {{
                    const response = await fetch("{url}");
                    const status = response.status;
                    let data = null;
                    if (response.ok) {{
                        data = await response.json();
                    }}
                    return {{ status: status, data: data }};
                }}
                '''

                result = page.evaluate(js_script)
                status_code = result['status']
                content = result['data']

                print(f'Итерация {i} -> Статус-код ответа сервера: {status_code}')

                if status_code != 200:
                    print("Сервер вернул ошибку или капчу. Проверьте окно браузера!")
                    time.sleep(15)
                    continue

                file_path = f'flats/studia/data_{i}.json'
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(content, file, indent=4, ensure_ascii=False)

                print(f'Успешно сохранено: {file_path}')

            except Exception as e:
                print(f'Ошибка на итерации {i}: {e}')
                time.sleep(20)
                continue

            time.sleep(random.uniform(6.0, 11.0))

        browser.close()


if __name__ == '__main__':
    main()
