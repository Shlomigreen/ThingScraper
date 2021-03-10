import general_config as gconf
import personal_config as pconf
from ThingScraper import Browser, Thing
from selenium.webdriver.common.by import By
import cli
import json


def parse_explore_url(sort_='popular', time_restriction=None, page=1):
    """
    Generates a url that leads to an explore page based on given parameters
    :param sort_: sort type. can be: popular, newest or makes
    :param time_restriction: restriction when sorted by popular: now-7d, now-30d, now-365d, None (All time)
    :param page: page number
    :return: url in str format
    """
    base_url = gconf.MAIN_URL + r'search?type=things&q=&sort='
    # sort_: popular, newest or makes
    base_url += sort_
    if time_restriction:
        # time_restriction: now-7d, now-30d, now-365d, None (All time)
        base_url += r"&posted_after=" + time_restriction
    base_url += r"&page=" + str(page)

    return base_url


def save_json(file_path, things_dict):
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


def load_json(file_path):
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


def scraper_search(browser, pages_to_scan=gconf.PAGES_TO_SCAN):
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
        while len(projects) < gconf.THINGS_PER_PAGE :
            projects = browser.wait_and_find(By.CLASS_NAME, gconf.ExploreList.THING_CARD, find_all=True)
        print(f"Found {len(projects)} projects on page {i+1}")
        for item in projects:
            item_id = item.find_element_by_class_name(gconf.ExploreList.CARD_BODY).get_attribute("href")
            item_id = item_id.rsplit(':', 1)[1]
            likes = item.find_elements_by_class_name(gconf.ExploreList.THING_LIKES)[1]
            thing = Thing(id=item_id)
            thing['likes'] = int(likes.text)
            data.append((item_id, thing))
    return dict(data)


def scrape_main_page(volume='q'):
    f"""
    Scrape main page for 
    :param volume: Volume of output text: [q = quit, v = verbose, n = normal]
    :return: Data we scraped, and a list of ids we failed to scrape
    """
    with Browser(pconf.browser, pconf.driver_path) as browser:
        data = scraper_search(browser, 1)
        failed = []
        for key in data:
            try:
                data[key].fetch_all(browser)
                data[key].parse_all()
            except Exception as E:
                failed.append((key, E))
                if volume != 'q':
                    print(f"Failed to retrieve for item id = {key}\n")
            else:
                if volume != 'q':
                    print(f"Success: {key}")
                if volume == 'v':
                    print(data[key].print_info())
    return data, failed


def scrape_users_in_db(db, volume='q'):
    # TODO: Implement user scrape
    print("User scrape not implemented yet")
    data = db
    return data, None


def scrape_make_in_db(db, volume='q'):
    # TODO: Implement make scrape
    print("Make scrape not implemented yet")
    data = db
    return data, None


def follow_cli(inp, data=[]):
    """
    Follow instructions from CLI
    :param inp: Instructions from CLI
    :param data: Data about the website
    :return: Data object updated
    """
    a = inp['load_type']
    if a == 'j':
        data = load_json(inp['save_name'] + '.json')
    elif a == 'd':
        pass

    volume = inp['volume']
    if inp['search_type'] == 'thing':
        data, fail = scrape_main_page(volume)
    elif inp['search_type'] == 'user':
        data, fail = scrape_users_in_db(data, volume)
    elif inp['search_type'] == 'make':
        data, fail = scrape_make_in_db(data, volume)
    else:
        print(f"{inp['search_type']} scraping not implemented yet")

    if inp['do_save_json']:
        save_json(inp['save_name'] + '.json', data)

    return data


def main():
    # get initial input
    args = cli.inter_parser()
    data = follow_cli(args)
    while args['Interactive']:
        input()
        args = cli.inter_parser()
        print(args)
        print("Interactive mode not implemented yet, quiting")
        break
        data = follow_cli(args)
    print(data)


if __name__ == '__main__':
    main()
