from ThingScraper import Browser, Thing
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

import config as conf
import os
import time

full_driver_path = os.path.abspath(conf.driver_path)
BROWSER_TYPE = "chrome"
URL = "https://www.thingiverse.com/"
URL_FRONT = "https://www.thingiverse.com/"
ELEMENT_NAME = "ThingCard__thingCard--1IcHY"
ELEMENT_LINK = "ThingCardBody__cardBodyWrapper--ba5pu"
ELEMENT_PROJECT = "ThingCard__thingCard--1IcHY"
ELEMENT_NEXT_PAGE = "Pagination__button--2X-2z Pagination__more--24exV"
TIMEOUT_TOLERANCE = 5

PAGES_TO_SCAN = 500
TEST = r"https://www.thingiverse.com/search?page=3&per_page=20&sort=popular&posted_after=now-30d&type=things&q="
TEST1 = r"search?page="
TEST2 = r"&per_page=20&sort=popular&posted_after=now-30d&type=things&q="



URL_THING_4734271 = "https://www.thingiverse.com/thing:4734271"


def get_elements(browser, *args):
    """
    Scans a webpage for the provided element names, and returns a list of the results
    :param browser: A web browser loaded with the web page we're scraping
    :param args: The elements we're looking for in the page
    :return: A list of lists, where each element corresponds to an input argument
    """
    res = []
    for element in args:
        found_elements = None
        try:
            WebDriverWait(browser.driver, TIMEOUT_TOLERANCE).until(
                EC.presence_of_element_located((By.CLASS_NAME, element))
            )
            time.sleep(4)
            found_elements = browser.driver.find_elements_by_class_name(element)
        except TimeoutException:
            # TODO: Handle exceptions
            pass
        finally:
            res.append(found_elements)
        time.sleep(4)
    return res


def scraper_search(browser, pages_to_scan=PAGES_TO_SCAN):
    """
    Scans the top pages of the last month, and returns a dictionary of the projects
    :param browser: The browser we're using
    :param pages_to_scan: The amount of pages we want to scan on the site
    :return: A dictionary, where the key is the "thing id", and the value is a dictionary containing the likes value.
    """
    data = []
    for i in range(pages_to_scan):
        url = URL + TEST1 + str(i+1) + TEST2
        browser.get(url)
        projects = get_elements(browser, ELEMENT_PROJECT)
        print(f"Found {len(projects[0])} projects on page {i+1}")
        for item in projects[0]:
            item_id = item.find_element_by_class_name("ThingCardBody__cardBodyWrapper--ba5pu").get_attribute("href")
            item_id = item_id.rsplit(':', 1)[1]
            likes = item.find_elements_by_class_name("CardActionItem__textWrapper--2wTM-")[1]
            thing = Thing(id=item_id)
            thing['likes'] = int(likes.text)
            data.append((int(item_id), thing))
    return dict(data)


def main():
    browser = Browser(BROWSER_TYPE, full_driver_path)
    data = scraper_search(browser, 5)
    for key in data:
        # print(f"For item {key}:\n{data[key].properties}\n")
        print(data[key])
    browser.close()
    # browser = Browser(conf.browser, conf.driver_path)
    # try:
    #     thing = Thing(URL_THING_4734271)
    #     thing.fetch_all(browser)
    #     print("Model Name:", thing.elements['model_name'].text)
    #     print("Created", thing.elements['created_by'].text)
    # finally:
    #     browser.close()


if __name__ == '__main__':
    main()
