import os
import json
import time
import calculate_distances
import csv

with open('kvartiras.csv', 'w', encoding='utf-8', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(
        ('Кол-во комнат',
         'Площадь, м^2',
         'Этаж квартиры',
         'Кол-во этажей в доме',
         'Относительный этаж',
         'Расстояние до центра, км',
         'Ближайшая станция метро',
         'Расстояние до ближайшей станции метро, км',
         'Балкон/Лоджия (1, 2)',
         'Чистовая отделка',
         'Проверено в Росреестре',
         'От зайстройщика',
         'Цена'
         )
    )

folder_path = ['data_json/', 'flats/flat1/', 'flats/flat2/', 'flats/flat3/', 'flats/flat4/', 'flats/studia/']

for path in folder_path:
    print(f'Работа с директорией {path}')
    time.sleep(3)
    for i, filik in enumerate(os.listdir(path)):
        title_full = ''
        try:
            print(f'Работа с файликом {i+1}')

            with open(f'{path}{filik}', encoding='utf-8') as file:
                source = json.load(file)

            items = source['catalog']['items']
            true_items = [item for item in items if len(item.keys()) > 35]

            for item in true_items:
                title = item['title'].split()
                title_full = title

                ##### Количество комант/Студия
                # Очистка случайных данных
                if title[0] in ['Доля:', 'Аукцион:']:
                    title = title[1:]

                if title[0][0].isdigit(): # здесь может быть количество этажей или "Студия"
                    rooms = title[0][0]
                    title = title[2:]
                else:
                    rooms = 'студия'
                    title = title[1:]

                ##### Площадь квартиры (м^2)
                area = float(title[0].replace(',', '.'))
                title = title[2:]

                ##### Этаж/Всего этажей в доме
                flat_floor, max_floor = [int(x) for x in title[0].split('/')]
                relative_floor = flat_floor / max_floor
                relative_floor = round(relative_floor, 6)

                #### Цена
                price = item['priceDetailed']['value']

                ##### Расстояние до центра и до ближайшего метро/название
                geo = item['coords']
                latitude = float(geo['lat'])
                longitude = float(geo['lng'])

                to_center = calculate_distances.distance_to_center(latitude, longitude)
                closest_station, min_distance_to_metro = calculate_distances.calculate_min_distance_to_metro(latitude, longitude)

                ##### Дополнительные фичи
                iva = item['iva']

                balkony_or_lojiya = 0
                chistovaya_otdelka = 0
                rosreestr = 0
                from_zastroishik = 0
                try:
                    badges = iva['BadgeBarStep'][0]['payload']['badges']
                    badges_names = [item['title'] for item in badges]

                    for name in badges_names:
                        if name == 'Балкон':
                            balkony_or_lojiya = 1

                        elif name == 'Лоджия':
                            balkony_or_lojiya = 2

                        elif name == 'Чистовая отделка':
                            chistovaya_otdelka = 1

                        elif name == 'Проверено в Росреестре':
                            rosreestr = 1

                        elif name == 'От застройщика':
                            from_zastroishik = 1

                except:
                    pass

                # print(rooms, area, flat_floor, max_floor, to_center, closest_station, min_distance_to_metro, price)
                #
                with open('kvartiras.csv', 'a', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow((rooms, area, flat_floor, max_floor, relative_floor,
                                     to_center, closest_station, min_distance_to_metro,
                                     balkony_or_lojiya, chistovaya_otdelka, rosreestr, from_zastroishik,
                                     price))
        except Exception as e:
            print(title_full)
            print(path, filik)
            print(e)
            input('Остановлено, запиши проблему')


# проблема в flat1/data_2.json  could not convert string to float: '1-к.'

# /flats/flat2/ data_17.json
# could not convert string to float: '2-к.'

# flats/flat5plus/ data_1.json
# could not convert string to float: 'более-к.'














