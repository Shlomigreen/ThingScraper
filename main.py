import json

from selenium.webdriver.common.by import By

import cli
import general_config as gconf
import personal_config
from ThingScraper import Browser, Thing, User, Make
import os
import logging


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


def scraper_search(browser, pages_to_scan=personal_config.PAGES_TO_SCAN):
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
        while len(projects) < gconf.THINGS_PER_PAGE:
            projects = browser.wait_and_find(By.CLASS_NAME, gconf.ExploreList.THING_CARD, find_all=True)
        logger.debug(f"Found {len(projects)} projects on page {i+1}")
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
    num_runs = settings['num_runs'] if settings['search_type'] != 'all' else settings['preliminary_count']
    if settings['search_type'] != 'thing' and settings['preliminary_count'] > 0:
        num_runs = settings['preliminary_count']
    browser = settings['browser_obj']
    data_to_scrape = scraper_search(browser, num_runs)
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
            # if volume == 'v':
            #     data_to_scrape[key].print_info()
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
        if k != 'users' or settings['save_to_db_mode'] == 'u':
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
    failed = []
    j = settings['num_runs']
    i = 0
    for k in names_to_scrape:
        i += 1
        if j == 0 and settings['search_type'] != 'all':
            # scan up to num_runs items. If negative, scan all
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
            # if volume == 'v':
            #     user.print_info()
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
            makes = items[k].get_makes(max_makes=settings['num_runs'])
        except Exception as E:
            logger.exception(f'{i} - (Makes) Failed to get makes from Thing id {k}')
            # print(f"Error of type {type(E)}:\n{E}")
            makes = [None]
        else:
            logger.debug(f'{i} - (Makes) Success: {k}:\n{makes}')
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
    volume = settings['volume']
    failed = []
    j = settings['num_runs']
    i = 0
    for k in makes_to_scrape:
        i += 1
        if j == 0 and settings['search_type'] != 'all':
            # scan up to num_runs items. If negative, scan all
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
            # if volume == 'v':
            #     make.print_info()
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
            remixes = items[k].get_remixes(max_remixes=settings['num_runs'])
        except Exception as E:
            logger.exception(f'{i} - (Remixes) Failed to get remixes from Thing id {k}')
            remixes = [None]
        else:
            logger.debug(f'{i} - (Remixes) Success: {k}:\n{remixes}')
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
    volume = settings['volume']
    failed = []
    j = settings['num_runs']
    i = 0
    for k in remixes_to_scrape:
        i += 1
        if j == 0 and settings['search_type'] != 'all':
            # scan up to num_runs items. If negative, scan all
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
            # if volume == 'v':
            #     remix.print_info()
    return db, failed


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
    if search_type == 'thing' or (search_type != 'all' and inp['preliminary_count'] > 0):
        data, fail = scrape_main_page(settings=inp, data=data)
    elif search_type == 'user':
        data, fail = scrape_users_in_db(inp, data)
    elif search_type == 'make':
        data, fail = scrape_make_in_db(inp, data)
    elif search_type == 'remix':
        data, fail = scrape_remixes_in_db(inp, data)
    elif search_type == 'all':
        data, fail = scrape_main_page(settings=inp, data=data)
        data, fail = scrape_remixes_in_db(inp, data)
        data, fail = scrape_make_in_db(inp, data)
        data, fail = scrape_users_in_db(inp, data)
    else:
        logger.warning(f"{search_type} scraping not implemented yet")

    if inp['do_save_json']:
        save_json(inp['save_name'] + '.json', data)

    return data


def log_file_gen():
    """
    handles file location for logs storage
    :return: path to main log file
    """
    # check if dir path exists
    if not os.path.exists(gconf.Logs.LOG_DIR):
        os.mkdir(gconf.Logs.LOG_DIR)
    # generate saving path for log file
    saving_path = os.path.join(gconf.Logs.LOG_DIR, gconf.Logs.NAME_LOG + '.log')

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
    if inp['volume'] == 'v':
        stream_handler.setLevel(logging.DEBUG)
        formatter_stream = logging.Formatter(gconf.Logs.FORMAT_STREAM_V)
    elif inp['volume'] == 'q':
        stream_handler.setLevel(logging.INFO)
        formatter_stream = logging.Formatter(gconf.Logs.FORMAT_STREAM_Q)
    else:
        stream_handler.setLevel(logging.INFO)
        formatter_stream = logging.Formatter(gconf.Logs.FORMAT_STREAM)
    stream_handler.setFormatter(formatter_stream)
    log.addHandler(file_handler)
    log.addHandler(stream_handler)
    log.info("logger has been setup successfully")


def main():
    # get initial input
    args = cli.inter_parser()
    setup_log(logger, args)
    data = data_format.copy()
    logger.debug('Created base data template')
    with Browser(args['browser'], args['driver_path']) as browser:
        logger.info('Opened browser obj')
        args['browser_obj'] = browser
        data = follow_cli(args, data)
        while args['Interactive']:
            input('*'*25)
            args = cli.inter_parser()
            logger.debug(f"args = {args}")
            logger.warning("Interactive mode not implemented yet, quiting")
            # TODO: implement support for interactive mode
            break
            data = follow_cli(args)
        for k in data:
            logger.debug(f"{k}:\n{data[k]}")
        input('Done, press any key to quit')
    logger.info('Done with browser obj')


if __name__ == '__main__':
    main()
