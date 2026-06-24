import numpy as np

KAZAN_CENTER_COORDS = (55.790833, 49.114500)

metro_stations_coords = {
        'Авиастроительная': (55.855851, 49.084495),
        'Северный вокзал': (55.841193, 49.080916),
        'Яшьлек': (55.827919, 49.082826),
        'Козья слобода': (55.816718, 49.098544),
        'Кремлёвская': (55.795924, 49.106293),
        'Площадь Тукая': (55.787224, 49.122008),
        'Суконная слобода': (55.776386, 49.143466),
        'Аметьево': (55.764986, 49.167720),
        'Горки': (55.760036, 49.192426),
        'Проспект Победы': (55.750007, 49.208735),
        'Дубравная': (55.7436, 49.2189)
    }

def distance(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])

    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon / 2) ** 2
    c = 2 * np.arcsin(np.sqrt(a))

    return 6371 * c

def distance_to_center(lat, lon):
    return distance(lat, lon, KAZAN_CENTER_COORDS[0], KAZAN_CENTER_COORDS[1])

def calculate_min_distance_to_metro(lat, lon):
    minimal_distance = ('', float('inf'))
    for station, coords in metro_stations_coords.items():
        distance_to_metro = distance(lat, lon, coords[0], coords[1])

        if distance_to_metro < minimal_distance[1]:
            minimal_distance = (station, distance_to_metro)

    return minimal_distance