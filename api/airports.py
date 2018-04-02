from tools.settings import get_iata_token
import requests


def get_iata(name):
    search_api_server = 'http://iatacodes.org/api/v6/autocomplete/'

    search_params = {
        'api_key': get_iata_token(),
        'query': name
    }
    response = requests.get(search_api_server, params=search_params, verify=False)

    if not response:
        return None
    else:
        json_response = response.json()
        if 'response' in json_response.keys():
            res = json_response['response']['airports_by_cities']
            return list(map(lambda x: x['code'], res)) if len(res) > 0 else None
        else:
            return None
