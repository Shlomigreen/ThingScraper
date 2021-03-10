import general_config as gconf
import personal_config as pconf
from ThingScraper import Browser, Thing, User, Make
from selenium.webdriver.common.by import By
import cli
import json


data_format = {
        "Things": dict(),
        "Users": dict(),
        "Makes": dict()
    }


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
            thing = Thing(thing_id=item_id)
            thing['likes'] = int(likes.text)
            data.append((item_id, thing))
    return dict(data)


def scrape_main_page(settings, data=None):
    """
    Scrape main page for
    :param settings: A dict containing settings
    :param data: data from previous runs
    :return: Data we scraped, and a list of ids we failed to scrape
    """
    if data is None:
        data = data_format.copy()
    volume = settings['volume']
    num_runs = settings['num_runs']
    if settings['search_type'] != 'thing' and settings['preliminary_count'] > 0:
        num_runs = settings['preliminary_count']
    with Browser(settings['browser'], settings['driver_path']) as browser:
        data_to_scrape = scraper_search(browser, num_runs)
        failed = []
        for key in data_to_scrape:
            try:
                data_to_scrape[key].fetch_all(browser)
                data_to_scrape[key].parse_all()
                data['Things'][key] = data_to_scrape[key]
            except Exception as E:
                failed.append((key, E))
                if volume != 'q':
                    print(f"Failed to retrieve for item id = {key}\n")
            else:
                if volume != 'q':
                    print(f"Success: {key}")
                if volume == 'v':
                    data_to_scrape[key].print_info()
    return data, failed


def get_users(data, settings):
    """
    gets all usernames in data
    :param data: loaded data
    :param settings: A dict containing settings
    :return: a set of all the usernames in the input
    """
    res = set()
    items = dict()
    for k in data:
        if k != 'Users' or settings['save_to_db_mode'] == 'u':
            items.update(data[k])
    for k in items:
        a = items[k]['username']
        if a is not None:
            res.add(a)
    return res


def scrape_users_in_db(settings, db):
    """
    Scrape user data
    :param settings: A dict containing settings
    :param db: data we can extract usernames from
    :return: Data we scraped, and a list of ids we failed to scrape
    """
    names_to_scrape = get_users(db, settings)
    volume = settings['volume']
    with Browser(settings['browser'], settings['driver_path']) as browser:
        failed = []
        i = settings['num_runs']
        for k in names_to_scrape:
            if i == 0:
                # scan up to num_runs items. If negative, scan all
                break
            else:
                i += -1
            try:
                user = User(username=k, browser=browser)
                user.fetch_all()
                user.parse_all()
                db['Users'][k] = user
            except Exception as E:
                failed.append((k, E))
                if volume != 'q':
                    print(f"Failed to retrieve for item id = {k}\n")
            else:
                if volume != 'q':
                    print(f"Success: {k}")
                if volume == 'v':
                    user.print_info()
    return db, failed


def scrape_make_in_db(db, volume='q'):
    # TODO: Implement make scrape
    print("Make scrape not implemented yet")
    data = db
    return data, None


def follow_cli(inp, data=None):
    """
    Follow instructions from CLI
    :param inp: Instructions from CLI
    :param data: Data about the website
    :return: Data object updated
    """
    if data is None:
        data = data_format.copy()
    a = inp['load_type']
    if a == 'j':
        data = load_json(inp['save_name'] + '.json')
    elif a == 'd':
        pass

    search_type = inp['search_type']
    if search_type == 'thing' or inp['preliminary_count'] > 0:
        data, fail = scrape_main_page(settings=inp, data=data)

    if search_type == 'user':
        data, fail = scrape_users_in_db(inp, data)
    elif search_type == 'make':
        data, fail = scrape_make_in_db(inp, data)
    else:
        print(f"{inp['search_type']} scraping not implemented yet")

    if inp['do_save_json']:
        save_json(inp['save_name'] + '.json', data)

    return data


def main():
    # get initial input
    args = cli.inter_parser()
    data = data_format.copy()
    data = follow_cli(args, data)
    while args['Interactive']:
        input()
        args = cli.inter_parser()
        print(args)
        print("Interactive mode not implemented yet, quiting")
        break
        data = follow_cli(args)
    for k in data:
        print(f"{k}:\n{data[k]}")


if __name__ == '__main__':
    main()
