# Консольное приложение на вход получает аргументы:
# - Токен приложения
# - ID географического объекта
#
# Возвращает в STDOUT JSON документ с погодными данными «Текущая погода» с сайта https://www.gismeteo.ru/api/
# Структура результирующего документа представлена кодом на языке Python.

from datetime import datetime, timezone, timedelta


t_times = [
    {"tg": 3, "tm": 0, "tod": "night", "todn": 0},
    {"tg": 9, "tm": 6, "tod": "morning", "todn": 1},
    {"tg": 15, "tm": 12, "tod": "day", "todn": 2},
    {"tg": 21, "tm": 18, "tod": "evening", "todn": 3},
]

tod = {
    0: 'night',
    1: 'morning',
    2: 'day',
    3: 'evening'
}

level_values = {
    1: 'small',
    2: 'medium',
    3: 'strong'
}

precipitations = {
    1: 'rain',
    2: 'snow'
}

directionValues = {
    1: 'n',
    2: 'ne',
    3: 'e',
    4: 'se',
    5: 's',
    6: 'sw',
    7: 'w',
    8: 'nw'
}


def parse_response(value, time_delta=6):
    _date = datetime.strptime(value['date']['UTC'], "%Y-%m-%d %H:%M:%S")
    _date_local = datetime.strptime(value['date']['local'], "%Y-%m-%d %H:%M:%S")
    _date_local.replace(tzinfo=timezone(timedelta(minutes=value['date']['time_zone_offset'])))

    _delta = timedelta(hours=time_delta)

    precipitation = {}

    precipitation_type = value['precipitation']['type']
    if precipitation_type in precipitations:
        precipitation_key = precipitations[precipitation_type]
        precipitation_intensity = value['precipitation']['intensity']
        if precipitation_intensity in level_values:
            precipitation_value = level_values[precipitation_intensity]
            precipitation[precipitation_key] = precipitation_value

    if value['cloudiness']['type'] in level_values:
        precipitation['cloudiness'] = level_values[value['cloudiness']['type']]

    wind = value['wind']['direction']['scale_8']

    tod_map = {
        0: "night",
        6: "morning",
        12: "day",
        18: "evening",
        24: "night"
    }
    local_date = datetime.strptime(value['date']['local'], "%Y-%m-%d %H:%M:%S")
    for h1, h2 in [(0, 6), (6, 12), (12, 18), (18, 24)]:
        if h1 <= local_date.hour <= h2:
            s1 = abs(h1 - local_date.hour)
            s2 = abs(h2 - local_date.hour)
            if s1 <= s2:
                tod = tod_map[h1]
            else:
                tod = tod_map[h2]
    result = {
        "provider": "gismeteo",
        "date": {
            "tod": tod,
            "local": _date_local,
            "utc": _date,
            "time_zone_offset": value['date']['time_zone_offset']
        },
        "valid": {
            "from": _date,
            "to": _date + _delta
        },
        "temperature": {
            "feeling": value['temperature']['comfort']['C'],
            "air": value['temperature']['air']['C']
        },
        "precipitations": precipitation,
        "humidity": value['humidity']['percent'],
        "pressure": {
            "atmospheric": value['pressure']['mm_hg_atm'],
        },
        "wind": {
            "direction": [directionValues.get(wind, ''), value['wind']['direction']['degree']],
            "speed": value['wind']['speed']['m_s']
        },
        "icon": value["icon"],
    }

    return result
