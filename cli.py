import personal_config as pconf
import argparse
from datetime import datetime

DEF_SAVE_NAME = pconf.DEF_SAVE_NAME + datetime.now().strftime("_%d%m%Y-%H%M")


def cli_set_arguments():
    """
    Adds arguments to parser obj
    :return: The parser with the new arguments
    """
    parser = argparse.ArgumentParser(description="Scrap data from thingiverse")
    parser = set_parser_args(parser)
    parser = set_parser_groups(parser)
    return parser


def set_parser_args(parser):
    """
    Add arguments to parser
    :param parser: parser we are modifying
    :return: modified parser
    """
    parser.add_argument('type', type=str, metavar='{Thing, Make, User, Remix, APIs, All}',
                        help='Type of data to scrap', default='Thing')
    # parser.add_argument('-I', '--Interactive', help='Opens program in interactive mode', action='store_true')
    parser.add_argument('-n', '--num_items', help='How many items to scrape', type=int, default=500)
    parser.add_argument('-N', '--Name', help='change name of save file (for local save)',
                        type=str, default=DEF_SAVE_NAME)
    parser.add_argument('-B', '--Browser', help='Browser name',
                        type=str, default=pconf.browser)
    parser.add_argument('-D', '--Driver', help='Driver path (for salenium)',
                        type=str, default=pconf.driver_path)
    parser.add_argument('-J', '--save-json', help='save a copy of results as a json file', action='store_true')
    parser.add_argument('-S', '--pre-search', type=int, default=0,
                        help='When scraping for a non-thing type object can first scrape for things, and then scrape '
                             'for data based on result. Please provide number of pages to scrape')
    parser.add_argument('-v', '--volume', type=int, default=0,
                        help='Set how much info is printed out: '
                             '10 = quite, '
                             '20 = normal, '
                             '30 = debug, '
                             '40 = verbose')
    parser.add_argument('--google-app-name', help='google developer code used to access google APIs',
                        type=str, default=pconf.google_ktree_API_key)

    parser.add_argument('--headless', help='runs the scraper in headless mode (no visible browser)',
                        action='store_true')
    return parser


def set_parser_groups(parser):
    """
    Add mutually exclusive groups to parser
    :param parser: parser we are modifying
    :return: modified parser
    """
    gr_data = parser.add_mutually_exclusive_group()
    # where to load data from at the start of the run
    gr_data.add_argument('-j', '--load-json', help='loads a json save file', action='store_true')
    gr_data.add_argument('-d', '--load-db', help='(el) Loads json save', action='store_true')

    # gr_db = parser.add_mutually_exclusive_group()
    # # how to save results to db
    # gr_db.add_argument('-u', '--update', help='replace duplicates', action='store_true')
    # gr_db.add_argument('-a', '--append', help='ignore duplicates', action='store_true')
    # gr_db.add_argument('-p', '--print', help="don't save results to database, just print to screen",
    #                    action='store_true')
    # gr_db.add_argument('--replace', help='delete all data once done scraping, and start anew', action='store_true')
    return parser
