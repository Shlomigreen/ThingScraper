from ThingScraper import Browser, Thing
import config as conf
from selenium.webdriver.common.by import By
import json
import webpage_elements as elm


NEW_FILE = True


def parse_explore_url(sort_='popular', time_restriction=None, page=1):
    """
    Generates a url that leads to an explore page based on given parameters
    :param sort_: sort type. can be: popular, newest or makes
    :param time_restriction: restriction when sorted by popular: now-7d, now-30d, now-365d, None (All time)
    :param page: page number
    :return: url in str format
    """
    base_url = conf.MAIN_URL + r'search?type=things&q=&sort='
    # sort_: popular, newest or makes
    base_url += sort_
    if time_restriction:
        # time_restriction: now-7d, now-30d, now-365d, None (All time)
        base_url += r"&posted_after=" + time_restriction
    base_url += r"&page=" + str(page)

    return base_url


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


def scraper_search(browser, pages_to_scan=conf.PAGES_TO_SCAN):
    """
    Scans the top pages of the last month, and returns a dictionary of the projects
    :param browser: The browser we're using
    :param pages_to_scan: The amount of pages we want to scan on the site
    :return: A dictionary, where the key is the "thing id", and the value is a dictionary containing the likes value.
    """
    data = []
    for i in range(pages_to_scan):
        url = parse_explore_url('popular', 'now-30d', i+1)
        browser.get(url)
        projects = []
        while len(projects) < conf.THINGS_PER_PAGE:
            projects = browser.wait_and_find(By.CLASS_NAME, elm.ExploreList.THING_CARD, find_all=True)
        print(f"Found {len(projects)} projects on page {i+1}")
        for item in projects:
            item_id = item.find_element_by_class_name(elm.ExploreList.CARD_BODY).get_attribute("href")
            item_id = item_id.rsplit(':', 1)[1]
            likes = item.find_elements_by_class_name(elm.ExploreList.THING_LIKES)[1]
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
                    # data[key].print_info()
                    print(f"Success: {key}")
            save_file("save.json", data)
    else:
        data = open_file("save.json")
        for key in data:
            data[key].print_info()


if __name__ == '__main__':
    main()
