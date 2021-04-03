import json

from selenium.webdriver.common.by import By

import cli
import APIs
import general_config as gconf
import personal_config
from ThingScraper import Browser, Thing, User, Make
import os
import logging
from Database.build_db import build_database

# Define new logger
logger = logging.getLogger(gconf.Logs.LOGGER_NAME)

# Data output structure
data_format = {
    "things": dict(),
    "users": dict(),
    "makes": dict()
}


def parse_explore_url(sort_='popular', time_restriction=None, page=1):
    """
    Generates a url that leads to an explore page based on given parameters
    :param sort_: sort type. can be: popular, newest or makes
    :param time_restriction: restriction when sorted by popular: now-7d, now-30d, now-365d, None (All time)
    :param page: page number
    :return: url in str format
    """
    restrictions = {'7': 'now-7d',
                    '30': 'now-30d',
                    '365': 'now-365d',
                    'inf': None}

    base_url = gconf.MAIN_URL + r'search?type=things&q=&sort='
    # sort_: popular, newest or makes
    base_url += sort_
    if time_restriction:
        if time_restriction in restrictions.keys():
            time_restriction = restrictions[time_restriction]
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
            logger.debug("beginning save: opened save file")
            data = {data_type: {k: things_dict[data_type][k].properties for k in things_dict[data_type]}
                    for data_type in things_dict}
            json.dump(data, file)
    except Exception as E:
        logger.exception(f"Could not save the file:\n{type(E)}: {E}")
    else:
        state = True
        logger.debug("saved successfully")
    finally:
        return state


def load_json(file_path):
    """
    Opens saved file
    :param file_path: where to save the file (includes name)
    :return: A dict where the key is a thing id, and the value is a Thing object
    """
    res = data_format.copy()
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
    except FileNotFoundError as E:
        logger.exception(f"File {file_path} not found:\n{E}")
    except Exception as E:
        logger.exception(f"Could not open the file:\n{E}")
    else:
        res["things"] = {k: Thing(thing_id=k, properties=data["things"][k]) for k in data["things"]}
        res["users"] = {k: User(username=k, properties=data["users"][k]) for k in data["users"]}
        res["makes"] = {k: Make(make_id=k, properties=data["makes"][k]) for k in data["makes"]}
    finally:
        return res


def scraper_search(browser, pages_to_scan=personal_config.PAGES_TO_SCAN, **kwargs):
    """
    Scans the top pages of the last month, and returns a dictionary of the projects
    :param browser: The browser we're using
    :param pages_to_scan: The amount of pages we want to scan on the site
    :param kwargs: passed to parse_explore_url (sort_, time_restriction)
    :return: A dictionary, where the key is the "thing id", and the value is a dictionary containing the likes value.
    """
    data = []
    for i in range(pages_to_scan):
        url = parse_explore_url(page=i + 1, **kwargs)
        browser.get(url)
        projects = []
        while len(projects) < gconf.THINGS_PER_PAGE:
            projects = browser.wait_and_find(By.CLASS_NAME, gconf.ExploreList.THING_CARD, find_all=True)
        logger.debug(f"Found {len(projects)} projects on page {i + 1}")
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
    num_runs = settings['num_items'] if settings['type'] != 'all' else settings['pre_search']
    if settings['type'] != 'thing' and settings['pre_search'] > 0:
        num_runs = settings['pre_search']
    browser = settings['browser_obj']
    data_to_scrape = scraper_search(browser, num_runs, sort_='popular', time_restriction='30')
    failed = []
    i = 0
    for key in data_to_scrape:
        i += 1
        try:
            data_to_scrape[key].fetch_all(browser)
            data_to_scrape[key].parse_all()
            data['things'][key] = data_to_scrape[key]
        except Exception as E:
            failed.append((key, E))
            logger.debug(f"{i} - (Thing) Failed to retrieve for item id = {key}\n")
        else:
            logger.debug(f"{i} - (Thing) Success: {key}")
            if settings['volume'] >= 40:
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
        # if k != 'users' or settings['update']:
        if k != 'users':
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
    failed = []
    j = settings['num_items']
    i = 0
    for k in names_to_scrape:
        i += 1
        if j == 0 and settings['type'] != 'all':
            # scan up to num_items items. If negative, scan all
            break
        else:
            j += -1
        try:
            user = User(username=k, browser=settings['browser_obj'])
            user.fetch_all()
            user.parse_all()
            db['users'][k] = user
        except Exception as E:
            failed.append((k, E))
            logger.debug(f"{i} - (User) Failed to retrieve for item id = {k}\n")
        else:
            logger.debug(f"{i} - (User) Success: {k}")
            if settings['volume'] >= 40:
                user.print_info()
    return db, failed


def get_makes(data, settings):
    """
    gets all makes in data
    :param data: loaded data
    :param settings: A dict containing settings
    :return: a set of all the usernames in the input
    """
    res = set()
    items = data['things']
    i = 0
    for k in items:
        i += 1
        try:
            makes = items[k].get_makes(max_makes=settings['num_items'])
        except Exception as E:
            logger.exception(f'{i} - (Makes) Failed to get makes from Thing id {k}')
            # print(f"Error of type {type(E)}:\n{E}")
            makes = [None]
        else:
            logger.debug(f'{i} - (Thing > Makes) Success {k}: {makes}')
        for make in makes:
            if make is not None:
                if type(make) == tuple:
                    res.add(make[0])
                else:
                    res.add(make)
    return res


def scrape_make_in_db(settings, db):
    """
    Scrape makes from thing objects
    :param settings: A dict containing settings
    :param db: data we can extract makes from
    :return: Data we scraped, and a list of ids we failed to scrape
    """
    makes_to_scrape = get_makes(db, settings)
    failed = []
    j = settings['num_items']
    i = 0
    for k in makes_to_scrape:
        i += 1
        if j == 0 and settings['type'] != 'all':
            # scan up to num_items items. If negative, scan all
            break
        else:
            j += -1
        try:
            make = Make(make_id=k, browser=settings['browser_obj'])
            make.fetch_all()
            make.parse_all()
            db['makes'][k] = make
        except Exception as E:
            failed.append((k, E))
            logger.debug(f"{i} - (Make) Failed to retrieve for item id = {k}\n")
        else:
            logger.debug(f"{i} - (Make) Success: {k}")
            if settings['volume'] >= 40:
                make.print_info()
    return db, failed


def get_remixes(data, settings):
    """
    gets all remixes in data
    :param data: loaded data
    :param settings: A dict containing settings
    :return: a set of all the usernames in the input
    """
    res = dict()
    items = data['things']
    i = 0
    for k in items:
        i += 1
        try:
            remixes = items[k].get_remixes(max_remixes=settings['num_items'])
        except Exception as E:
            logger.exception(f'{i} - (Remixes) Failed to get remixes from Thing id {k}')
            remixes = [None]
        else:
            logger.debug(f'{i} - (Thing > Remixes) Success {k}: {remixes}')
        for remix in remixes:
            if remix is not None:
                res[remix[0]] = remix
    return res


def scrape_remixes_in_db(settings, db):
    """
    Scrape remixes from thing objects
    :param settings: A dict containing settings
    :param db: data we can extract makes from
    :return: Data we scraped, and a list of ids we failed to scrape
    """
    remixes_to_scrape = get_remixes(db, settings)
    failed = []
    j = settings['num_items']
    i = 0
    for k in remixes_to_scrape:
        i += 1
        if j == 0 and settings['type'] != 'all':
            # scan up to num_items items. If negative, scan all
            break
        else:
            j += -1
        try:
            remix = Thing(thing_id=k, browser=settings['browser_obj'])
            remix.fetch_all(settings['browser_obj'])
            remix.parse_all()
            remix['likes'] = remixes_to_scrape[k][1]
            db['things'][k] = remix
        except Exception as E:
            failed.append((k, E))
            logger.debug(f"{i} - (Remix) Failed to retrieve for item id = {k}\n")
        else:
            logger.debug(f"{i} - (Remix) Success: {k}")
            if settings['volume'] >= 40:
                remix.print_info()
    return db, failed


def enrich_with_apis(inp, data):
    """
    Use external APIs to add data to the database (modifies data inplace)
    :param inp: arguments passed by the user
    :param data: loaded data
    :return: None
    """
    APIs.enrich_with_apis(data, inp['num_items'], inp['google_app_name'])


def follow_cli(inp, data=None):
    """
    Follow instructions from CLI
    :param inp: Instructions from CLI
    :param data: Data about the website
    :return: Data object updated
    """
    # Generate empty data dictionary if not provided
    if data is None:
        data = data_format.copy()

    # Load a JSON file from given path, if was not given - scrape data into a new JSON
    if inp['load_json']:
        file_path = inp['load_json']

        if os.path.exists(file_path):
            data = load_json(file_path)
        else:
            logger.error("Given JSON path was not found: `{}`".format(file_path))
    else:
        data = scrape_data(data, inp)

        # Only save JSON if a new scrapping was done
        if inp['save_json']:
            file_path = os.path.abspath(inp['Name'] + '.json')
            save_json(file_path, data)

    if inp['database']:
        json_path = inp['Name'] + ".json"
        logger.info("Building database from `{}`".format(json_path))
        build_database(json_path, drop_existing=False)

    return data


def scrape_data(data, inp):
    search_type = inp['type'].lower()

    logger.debug(f"chose to scan for {search_type}")
    if search_type == 'thing' or (search_type != 'all' and inp['pre_search'] > 0):
        data, fail = scrape_main_page(settings=inp, data=data)
    elif search_type == 'user':
        data, fail = scrape_users_in_db(inp, data)
    elif search_type == 'make':
        data, fail = scrape_make_in_db(inp, data)
    elif search_type == 'remix':
        data, fail = scrape_remixes_in_db(inp, data)
    elif search_type == 'apis':
        enrich_with_apis(inp, data)
    elif search_type == 'all':
        data, fail = scrape_main_page(settings=inp, data=data)
        data, fail = scrape_remixes_in_db(inp, data)
        data, fail = scrape_make_in_db(inp, data)
        data, fail = scrape_users_in_db(inp, data)
        enrich_with_apis(inp, data)
    else:
        logger.error(f"Unknown type : `{search_type}`")

    return data


def log_file_gen():
    """
    handles file location for logs storage
    :return: path to main log file
    """
    from datetime import datetime

    file_name = gconf.Logs.NAME_LOG + datetime.now().strftime("_%d%m%Y-%H%M")

    # check if dir path exists
    if not os.path.exists(gconf.Logs.LOG_DIR):
        os.mkdir(gconf.Logs.LOG_DIR)
    # generate saving path for log file
    saving_path = os.path.join(gconf.Logs.LOG_DIR, file_name + '.log')
    return os.path.abspath(saving_path)


def setup_log(log, inp):
    """
    setup the log based on the config file settings
    :param log: logger obj we're setting up
    :param inp: user arguments
    :return: None
    """
    log.setLevel(eval(f"logging.{gconf.Logs.LEVEL_GENERAL}"))

    formatter_log = logging.Formatter(gconf.Logs.FORMAT_LOG)
    log_path = log_file_gen()

    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter_log)
    file_handler.setLevel(eval(f"logging.{gconf.Logs.LEVEL_LOG}"))

    stream_handler = logging.StreamHandler()
    cli_log_level = logging.INFO
    if inp.volume < 20:
        # quite mode
        formatter_stream = logging.Formatter(gconf.Logs.FORMAT_STREAM_Q)
    elif inp.volume < 30:
        # normal mode
        formatter_stream = logging.Formatter(gconf.Logs.FORMAT_STREAM)
    elif inp.volume < 40:
        # debug mode
        cli_log_level = logging.DEBUG
        stream_handler.setLevel(logging.DEBUG)
        formatter_stream = logging.Formatter(gconf.Logs.FORMAT_STREAM_V)
    else:
        # verbose mode
        cli_log_level = logging.DEBUG
        stream_handler.setLevel(logging.DEBUG)
        formatter_stream = logging.Formatter(gconf.Logs.FORMAT_STREAM_V)

    stream_handler.setLevel(cli_log_level)
    if inp.volume > 0:
        file_handler.setLevel(cli_log_level)

    stream_handler.setFormatter(formatter_stream)
    log.addHandler(file_handler)
    log.addHandler(stream_handler)
    log.info("logger has been setup successfully")


def main():
    # args = cli.inter_parser()
    parser = cli.cli_set_arguments()
    args = parser.parse_args()
    setup_log(logger, args)
    data = data_format.copy()
    logger.debug('Created base data template')
    # Scraping
    with Browser(args.Browser, args.Driver, headless=args.headless) as browser:
        logger.info('Opened browser obj')
        args_dict = vars(args)
        args_dict['type'] = args_dict['type'].lower()
        args_dict['browser_obj'] = browser
        data = follow_cli(args_dict, data)
        for k in data:
            logger.debug(f"{k}:\n{data[k]}")
    logger.info('Browser object closed')

    logger.info('Quiting data miner')


if __name__ == '__main__':
    main()
