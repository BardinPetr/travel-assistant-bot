import requests


def extract_bbox(toponym):
    try:
        env = toponym['boundedBy']['Envelope']
        return '~'.join([env['lowerCorner'].replace(" ", ","), env['upperCorner'].replace(" ", ",")])
    except Exception:
        return None


def extract_bbox_prog(toponym):
    try:
        env = toponym['boundedBy']['Envelope']
        return list(map(float, env['lowerCorner'].split())), list(map(float, env['upperCorner'].split()))
    except Exception:
        return None


def extract_spn(toponym):
    try:
        b = extract_bbox_prog(toponym)
        return ','.join(list(map(str, (abs(b[1][0] - b[0][0]), abs(b[1][1] - b[0][1])))))
    except Exception:
        return None


def extract_spn_prog(toponym):
    try:
        b = extract_bbox_prog(toponym)
        return abs(b[1][0] - b[0][0]), abs(b[1][1] - b[0][1])
    except Exception:
        return None


def extract_name(toponym):
    try:
        return toponym['name']
    except Exception:
        return None


def extract_point(toponym):
    try:
        return toponym['Point']['pos'].replace(' ', ',')
    except Exception:
        return None


def extract_point_prog(toponym):
    try:
        return list(map(float, toponym['Point']['pos'].split()))
    except Exception:
        return None


def geocoder(e, p={}):
    geocoder_uri = 'http://geocode-maps.yandex.ru/1.x/'
    try:
        params = {
            'format': 'json',
            'geocode': e
        }
        params.update(p)
        response = requests.get(geocoder_uri, params=params)

        if response:
            toponym = response.json()['response']['GeoObjectCollection']['featureMember']
            if len(toponym) == 0:
                return None
            else:
                toponym = toponym[0]['GeoObject']
                return toponym
        else:
            raise Exception()
    except Exception:
        return None


def extract_org_name(x):
    try:
        return x['properties']['name']
    except Exception:
        return None


def extract_org_addr(x):
    try:
        return x['properties']['CompanyMetaData']['address']
    except Exception:
        return None


def extract_org_coord(x):
    try:
        return x['geometry']['coordinates']
    except Exception:
        return None


def extract_org_whours_text(x):
    try:
        return x['properties']['CompanyMetaData']['Hours']['text']
    except Exception:
        return None


def extract_org_whours(x):
    try:
        if 'Availabilities' not in x['properties']['CompanyMetaData']['Hours'].keys():
            return 0
        if len(x['properties']['CompanyMetaData']['Hours']['Availabilities']) == 0:
            return 0
        for e in x['properties']['CompanyMetaData']['Hours']['Availabilities']:
            if 'TwentyFourHours' in e.keys():
                return 1 if e['TwentyFourHours'] else 2
            elif 'Intervals' in e.keys():
                return 2
        return 0
    except Exception:
        return 0


def search(x, params={}):
    search_api_server = "https://search-maps.yandex.ru/v1/"
    api_key = "3c4a592e-c4c0-4949-85d1-97291c87825c"

    search_params = {
        "apikey": api_key,
        "text": x,
        "lang": "ru_RU"
    }
    search_params.update(params)
    response = requests.get(search_api_server, params=search_params)

    if not response:
        return None
    else:
        json_response = response.json()
        res = json_response["features"]
        return res
