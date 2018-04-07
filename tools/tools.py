from tools.enums import HOTEL_TYPES
from datetime import datetime


def parse_time(x):
    return datetime.strptime(x, '%Y-%m-%d')


def decode_hotel_type(x):
    return HOTEL_TYPES[x]
