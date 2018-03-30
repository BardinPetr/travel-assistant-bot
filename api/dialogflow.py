import json
import sys
import os

try:
    import apiai
except ImportError:
    sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir))
    import apiai


class ApiAI:
    def __init__(self, token):
        self.ai = apiai.ApiAI(token)

    def run(self, query, session):
        try:
            request = self.ai.text_request()
            request.lang = 'ru'
            request.session_id = session
            request.query = query
            return json.loads(request.getresponse().read().decode("utf-8"), encoding="utf-8")['result']
        except Exception as e:
            print(e)
            return None


def get_fulfillment(e):
    return e['fulfillment']['speech']


def is_incomplete(e):
    return e['actionIncomplete']


def get_action(e):
    return e['action']


def get_params(e):
    return e['parameters']
