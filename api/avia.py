from __future__ import print_function

import selenium.webdriver.support.ui as ui
from selenium import webdriver
from io import BytesIO
from time import time, sleep
from PIL import Image
from os import remove
import contextlib
import subprocess
from tools.tools import parse_time
import os


def get_ticket(f, t, d0, d1, c0, c1):
    d0 = d0.strftime("%d%m")
    d1 = d1.strftime("%d%m")

    url = "https://www.aviasales.ru/search/{}{}{}{}{}{}".format(f, d0, t, d1, c0, c1)
    res = None

    try:
        with contextlib.closing(webdriver.Chrome("/home/petr/Downloads/chromedriver")) as driver:
            driver.get(url)
            wait = ui.WebDriverWait(driver, 400)

            while len(driver.find_elements_by_class_name("is-with-countdown")) > 0:
                pass

            if len(driver.find_elements_by_class_name("error-message__icon")) > 0:
                print("No")
            else:
                elem = driver.find_elements_by_class_name("ticket__wrapper")
                if len(elem) > 0:
                    elem = elem[0]
                    # {'height': 269, 'width': 523, 'x': 546, 'y': 373}
                    content_elem = driver.find_element_by_class_name("ticket__content")
                    path = str(time()) + ".png"
                    driver.save_screenshot(path)
                    '''
                    im = Image.open(path)
                    im = im.crop((content_elem.rect['x'],
                                  content_elem.rect['y'],
                                  content_elem.rect['x'] + content_elem.rect['width'],
                                  content_elem.rect['y'] + content_elem.rect['height']))
                    im.show()
                    sleep(3)523x269+546+373

                    im.save(path.replace('png', 'jpeg'))
                    '''
                    rect = content_elem.rect
                    subprocess.call(["convert", path, '-crop',
                                     '{}x{}+{}+{}'.format(
                                         rect['width'],
                                         rect['height'],
                                         rect['x'],
                                         rect['y']),
                                     "output.jpg"])
                    sleep(2)
                    price = int(
                        ''.join(
                            list(filter(lambda x: x.isdigit(),
                                        elem.find_element_by_class_name("buy-button__button").text))))
                    redirect_url = elem.find_element_by_class_name("buy-button__link").get_attribute("href")
                    res = {"img": open('output.jpg', 'rb'), "price": price, "link": redirect_url}
                    remove(path)
                    # remove("output.jpg")
                else:
                    raise Exception("Not found any tickets")
    except Exception as e:
        print(e)
    return res

# print(get_ticket("PEZ", "MOW", parse_time("2018-04-23"), parse_time("2018-04-27"), 1, 2))
