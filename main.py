from ThingScraper import Browser, Thing
import config as conf
from selenium.webdriver.common.by import By
import json

BROWSER_TYPE = "chrome"
URL = "https://www.thingiverse.com/"
URL_FRONT = "https://www.thingiverse.com/"
ELEMENT_NAME = "ThingCard__thingCard--1IcHY"
ELEMENT_LINK = "ThingCardBody__cardBodyWrapper--ba5pu"
ELEMENT_PROJECT = "ThingCard__thingCard--1IcHY"
ELEMENT_NEXT_PAGE = "Pagination__button--2X-2z Pagination__more--24exV"
ELEMENT_LIKES = "CardActionItem__textWrapper--2wTM-"
TIMEOUT_TOLERANCE = 5
THINGS_PER_PAGE = 20
PAGES_TO_SCAN = 500
URL_SEARCH_EXAMPLE = r"https://www.thingiverse.com/search?page=3&per_page=20&sort=popular&posted_after=now-30d&type=things&q="
SEARCH_PARAM_FRONT = r"search?page="
SEARCH_PARAM_END = r"&per_page=20&sort=popular&posted_after=now-30d&type=things&q="
NEW_FILE = True


def save_file(file_path, things_dict):
    """
    Saves the file
    :param file_path: where to save the file (includes name)
    :param things_dict: A dictionary where the key is the id, and the value is a Thing object
    :return: (bool) True if saved successfully
    """
    state = False
    try:
        with open(file_path, 'w') as file:
            data = [(id, things_dict[id].properties) for id in things_dict]
            json.dump(data, file)
    except Exception as E:
        print(f"Could not save the file:\n{type(E)}: {E}")
    else:
        state = True
    finally:
        return state


def open_file(file_path):
    """
    Opens saved file
    :param file_path: where to save the file (includes name)
    :return: A dict where the key is a thing id, and the value is a Thing object
    """
    res = None
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError as E:
        print(f"File {file_path} not found:\n{E}")
    except Exception as E:
        print(f"Could not open the file:\n{E}")
    else:
        res = {key: Thing(id=key, properties=val) for key, val in data}
    finally:
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
        url = URL + SEARCH_PARAM_FRONT + str(i + 1) + SEARCH_PARAM_END
        browser.get(url)
        projects = []
        while len(projects) < THINGS_PER_PAGE:
            projects = browser.wait_and_find(By.CLASS_NAME, ELEMENT_PROJECT, find_all=True)
        print(f"Found {len(projects)} projects on page {i+1}")
        thing_browser = Browser(conf.browser, conf.driver_path)
        for item in projects:
            item_id = item.find_element_by_class_name(ELEMENT_LINK).get_attribute("href")
            item_id = item_id.rsplit(':', 1)[1]
            likes = item.find_elements_by_class_name(ELEMENT_LIKES)[1]
            thing = Thing(id=item_id)
            thing['likes'] = int(likes.text)
            data.append((item_id, thing))
    return dict(data)


def main():
    if NEW_FILE:
        with Browser(conf.browser, conf.driver_path) as browser:
            data = scraper_search(browser, 1)
            failed = []
            for key in data:
                try:
                    data[key].fetch_all(browser)
                    data[key].parse_all()
                except Exception as E:
                    failed.append((key, E))
                    print(f"Failed to retrieve for item id = {key}\n")
                else:
                    print(data[key].print_info())
            save_file("save.json", data)
    else:
        data = open_file("save.json")
        for key in data:
            print(data[key].print_info())


if __name__ == '__main__':
    main()
