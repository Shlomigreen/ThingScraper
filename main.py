from ThingScraper import Browser, Thing
import config as conf
from selenium.webdriver.common.by import By

BROWSER_TYPE = "chrome"
URL = "https://www.thingiverse.com/"
URL_FRONT = "https://www.thingiverse.com/"
ELEMENT_NAME = "ThingCard__thingCard--1IcHY"
ELEMENT_LINK = "ThingCardBody__cardBodyWrapper--ba5pu"
ELEMENT_PROJECT = "ThingCard__thingCard--1IcHY"
ELEMENT_NEXT_PAGE = "Pagination__button--2X-2z Pagination__more--24exV"
TIMEOUT_TOLERANCE = 5
THINGS_PER_PAGE = 20

PAGES_TO_SCAN = 500
TEST = r"https://www.thingiverse.com/search?page=3&per_page=20&sort=popular&posted_after=now-30d&type=things&q="
TEST1 = r"search?page="
TEST2 = r"&per_page=20&sort=popular&posted_after=now-30d&type=things&q="


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
        projects = []
        while len(projects) < THINGS_PER_PAGE:
            projects = browser.wait_and_find(By.CLASS_NAME, ELEMENT_PROJECT, find_all=True)
        print(f"Found {len(projects)} projects on page {i+1}")
        thing_browser = Browser(conf.browser, conf.driver_path)
        for item in projects:
            # TODO: We might need to add support for selenium stale element exception/ wait
            item_id = item.find_element_by_class_name("ThingCardBody__cardBodyWrapper--ba5pu").get_attribute("href")
            item_id = item_id.rsplit(':', 1)[1]
            likes = item.find_elements_by_class_name("CardActionItem__textWrapper--2wTM-")[1]
            thing = Thing(id=item_id)
            thing['likes'] = int(likes.text)
            thing.fetch_all(thing_browser)
            thing.parse_all()
            thing.print_info()
            data.append((int(item_id), thing))
        thing_browser.close()
    return dict(data)


def main():
    with Browser(BROWSER_TYPE, conf.driver_path) as browser:
        data = scraper_search(browser, 30)
        failed = []
        for key in data:
            try:
                # data[key].parse_all(browser)
                pass
            except Exception as E:
                failed.append((key, E))
                print(f"Failed to retrieve for item id = {key}\n")
            else:
                print(data[key])


if __name__ == '__main__':
    main()
