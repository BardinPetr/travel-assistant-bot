from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from math import sin, cos, sqrt, atan2, radians
from tools.enums import HOTEL_TYPES
import datetime
from api import geocoder
from PIL import Image
import time
import os


def parse_time(x):
    return datetime.datetime.strptime(x, '%Y-%m-%d')


def decode_hotel_type(x):
    return HOTEL_TYPES[x]


def build_menu(buttons,
               n_cols,
               header_buttons=None,
               footer_buttons=None):
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons)
    if footer_buttons:
        menu.append(footer_buttons)
    return menu


def gen_hotels_selector(htls, fburl):
    button_list = [
        InlineKeyboardButton("Вариант №1", url=htls[0]['link']),
        InlineKeyboardButton("Вариант №2", url=htls[1]['link']),
        InlineKeyboardButton("Вариант №3", url=htls[2]['link']),
        InlineKeyboardButton("Покажи еще / Не нравятся", url=fburl)
    ]
    return InlineKeyboardMarkup(build_menu(button_list, n_cols=1))


def _gen_btns(y, n_cols=1):
    button_list = list(map(lambda x: InlineKeyboardButton(x[0], callback_data=x[1]), y))
    return InlineKeyboardMarkup(build_menu(button_list, n_cols=n_cols))


def gen_btns(id, ud):
    if id == 1:
        l = list(ud['recent_src']) + ['Москва', 'Пенза', 'Саранск']
        cnt = min(len(l), 3)
        return _gen_btns(map(lambda x: [x, x], l[:cnt]), cnt)
    elif id == 2:
        l = list(ud['recent_dst']) + ['Москва', 'Пенза', 'Саранск']
        cnt = min(len(l), 3)
        return _gen_btns(map(lambda x: [x, x], l[:cnt]), cnt)
    elif id == 3:
        return _gen_btns([datetime.datetime.now().strftime("%d %B"),
                          (datetime.datetime.now() + datetime.timedelta(days=3)).strftime("%d %B")], 2)


def gen_goto_booking_site(url):
    button_list = [
        InlineKeyboardButton("Перейти к бронированию", url=url)
    ]
    return InlineKeyboardMarkup(build_menu(button_list, n_cols=1))


def dist(x, y):
    R = 6373.0
    lat1 = radians(x[1])
    lon1 = radians(x[0])
    lat2 = radians(y[1])
    lon2 = radians(y[0])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def xdist(a, b):
    a = geocoder.extract_point_prog(geocoder.geocoder(a))
    b = geocoder.extract_point_prog(geocoder.geocoder(b))
    return dist(a, b)


def fullpage_screenshot(driver, file):
    total_width = driver.execute_script("return document.body.offsetWidth")
    total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
    viewport_width = driver.execute_script("return document.body.clientWidth")
    viewport_height = driver.execute_script("return window.innerHeight")
    print("Total: ({0}, {1}), Viewport: ({2},{3})".format(total_width, total_height, viewport_width, viewport_height))
    rectangles = []

    i = 0
    while i < total_height:
        ii = 0
        top_height = i + viewport_height

        if top_height > total_height:
            top_height = total_height

        while ii < total_width:
            top_width = ii + viewport_width

            if top_width > total_width:
                top_width = total_width

            print("Appending rectangle ({0},{1},{2},{3})".format(ii, i, top_width, top_height))
            rectangles.append((ii, i, top_width, top_height))

            ii = ii + viewport_width

        i = i + viewport_height

    stitched_image = Image.new('RGB', (total_width, total_height))
    previous = None
    part = 0

    for rectangle in rectangles:
        if not previous is None:
            driver.execute_script("window.scrollTo({0}, {1})".format(rectangle[0], rectangle[1]))
            driver.execute_script(
                "document.getElementsByClassName('of_main_form_wrapper')[0].setAttribute('style', 'position: absolute; top: 0px;');")
            print("Scrolled To ({0},{1})".format(rectangle[0], rectangle[1]))
            time.sleep(0.2)

        file_name = "part_{0}.png".format(part)
        print("Capturing {0} ...".format(file_name))

        driver.get_screenshot_as_file(file_name)
        screenshot = Image.open(file_name)

        if rectangle[1] + viewport_height > total_height:
            offset = (rectangle[0], total_height - viewport_height)
        else:
            offset = (rectangle[0], rectangle[1])

        print("Adding to stitched image with offset ({0}, {1})".format(offset[0], offset[1]))
        stitched_image.paste(screenshot, offset)

        del screenshot
        os.remove(file_name)
        part = part + 1
        previous = rectangle

    stitched_image.save(file)
    print("Finishing chrome full page screenshot workaround...")
    return True
