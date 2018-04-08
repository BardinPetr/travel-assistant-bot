from selenium import webdriver
from datetime import datetime
from time import sleep
from tools.tools import parse_time
from bs4 import BeautifulSoup
import contextlib
import selenium.webdriver.support.ui as ui


def processhotel(x):
    res = {"finished": False}
    try:
        e = x.find_elements_by_class_name("hotel-thumbnail")
        if len(e) > 0:
            img = e[0].get_attribute("data-image")
            if img.startswith("//"):
                img = "https:" + img
            res['img'] = img
        else:
            res['img'] = "https://freeiconshop.com/wp-content/uploads/edd/document-error-flat.png"
        res['link'] = x.find_element_by_class_name("flex-link").get_attribute("href")
        res['name'] = x.find_element_by_class_name("hotelName").text.strip('')
        res['stars'] = int(x.find_element_by_class_name("stars-grey").get_attribute("title")[:1])
        res['rank'] = x.find_element_by_class_name("reviewOverall").find_elements_by_tag_name("span")[1].text
        res['cost'] = int(x.find_element_by_class_name("actualPrice").text.strip("")[1:]) * 56
        # res['dist'] = float(x.find_element_by_class_name("distance").text.split('mi')[0].strip("\n").strip()) / 0.62137
        res['finished'] = True
    except Exception as e:
        pass
    return res


def get_hotel(d, d0, d1, c0, ht):
    d0 = d0.strftime("%m/%d/%Y")
    d1 = d1.strftime("%m/%d/%Y")

    url = "https://www.expedia.com/Hotels"
    res = None

    try:
        with contextlib.closing(webdriver.Chrome()) as driver:
            driver.get(url)
            wait = ui.WebDriverWait(driver, 60 * 5)

            e = driver.find_element_by_name("destination")
            e.clear()
            e.send_keys(d)
            e = driver.find_element_by_id("hotel-checkin-hlp")
            e.clear()
            e.send_keys(d0)
            e = driver.find_element_by_id("hotel-checkout-hlp")
            e.clear()
            e.send_keys(d1)

            driver.find_element_by_class_name("gcw-traveler-amount-select").click()
            me = driver.find_elements_by_class_name("uitk-step-input-minus")
            mp = driver.find_elements_by_class_name("uitk-step-input-plus")
            ml = driver.find_elements_by_class_name("uitk-step-input-value")
            d = c0 - int(ml[0].text.strip(''))
            for i in range(abs(d)):
                (me if d < 0 else mp)[0].click()

            driver.find_element_by_class_name("gcw-submit").click()
            print(1)
            wait.until_not(lambda xd: len(xd.find_elements_by_class_name('hotel-thumbnail')) == 0)
            print(1.5, len(driver.find_elements_by_class_name('hotel-thumbnail')))
            print(1.6, driver.find_element_by_class_name('hotel-thumbnail'),
                  driver.find_element_by_class_name('hotel-thumbnail').is_displayed())
            wait.until(lambda xd: xd.find_element_by_class_name('hotel-thumbnail').is_displayed())
            print(2)
            wait.until_not(lambda xd: len(xd.find_elements_by_id('lodging0')) == 0)
            print(2.5, len(driver.find_elements_by_id('lodging0')))
            wait.until(lambda xd: xd.find_element_by_id('lodging0').is_displayed())
            print(driver.find_element_by_id('lodging0').is_displayed())
            print(3)
            if ht in [0, 1, 2]:
                driver.find_element_by_id("lodging%d" % ht).click()
            print(4000)
            print(0)
            wait.until_not(lambda xd: len(xd.find_elements_by_class_name('loader')) == 0)
            # wait.until(lambda xd: xd.find_element_by_class_name('loader').is_displayed())
            print(1)
            wait.until_not(lambda xd: len(xd.find_elements_by_class_name('hotel-thumbnail')) == 0)
            print(1.5, len(driver.find_elements_by_class_name('hotel-thumbnail')))
            print(1.6, driver.find_element_by_class_name('hotel-thumbnail'),
                  driver.find_element_by_class_name('hotel-thumbnail').is_displayed())
            wait.until(lambda xd: xd.find_element_by_class_name('hotel-thumbnail').is_displayed())
            print(2)
            wait.until_not(lambda xd: len(xd.find_elements_by_id('lodging0')) == 0)
            print(2.5, len(driver.find_elements_by_id('lodging0')))
            wait.until(lambda xd: xd.find_element_by_id('lodging0').is_displayed())
            print(driver.find_element_by_id('lodging0').is_displayed())
            print(3)
            sleep(4)
            htls = driver.find_elements_by_tag_name("article")
            if len(htls) > 0:
                res = htls
                res = list(filter(lambda x: x['finished'], map(processhotel, res[:min(len(res) - 1, 50)])))
                # res = sorted(filter(lambda x: x['finished'], map(processhotel, res)), key=lambda x: x['dist'])
                res.append(driver.current_url)
    except Exception as e:
        print(e)
        res = None
    return res
