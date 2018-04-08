import requests
import pygame
import sys
import os


def getImg(params):
    url = 'http://static-maps.yandex.ru/1.x/'
    try:
        response = requests.get(url, params)
        if not response:
            error = 'Request failed! HTTP status: {} ({})'.format(response.status_code, response.reason)
            print(error)
            return None
    except:
        return None

    map_file = 'map.png'
    try:
        with open(map_file, 'wb') as file:
            file.write(response.content)
        os.remove(map_file)
        return open(map_file, 'rb')
    except IOError as ex:
        print('Map file saving error', ex)
        return None


def getImgByURL(url):
    print(url)
    try:
        response = requests.get(url)
        if not response:
            error = 'Request failed! HTTP status: {} ({})'.format(response.status_code, response.reason)
            print(error)
            return None
    except:
        return None

    map_file = 'map.png'
    try:
        with open(map_file, 'wb') as file:
            file.write(response.content)
        f = pygame.image.load(map_file)
        os.remove(map_file)
        return f
    except IOError as ex:
        print('Map file saving error', ex)
        return None
