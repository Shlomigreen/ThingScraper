import personal_config as pconf
import Database.config as dbconf
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
    parser = set_parser_long_args(parser)
    parser = set_parser_groups(parser)
    parser = set_mysql_args(parser)
    return parser


def set_parser_args(parser):
    """
    Add arguments to parser
    :param parser: parser we are modifying
    :return: modified parser
    """
    parser.add_argument('type', action='extend', nargs='*', type=str,
                        choices=['Thing', 'Make', 'User', 'Remix', 'API', 'All'],
                        help='Type of data to scrap. \n'
                             ' can provide multiple types and it will be scraped in the provided order. \n'
                             'All is equivalent to writing: \n'
                             'Thing Remix Make API User.')
    parser.add_argument('-n', '--num-items', type=int, action='extend', nargs='*', default=[],
                        help='How many items to scrape per action. \n'
                             'If not enough arguments are provided the last argument will be used as substitute. \n'
                             'If too many arguments are provided the extras will be ignored. \n'
                             'The arguments corresponding to User will be ignored unless the '
                             '--not-all-users tag is raised. \n'
                             'Arguments that are a shorthand for multiple commands (like All) require multiple '
                             'corresponding num-items arguments')
    parser.add_argument('-N', '--Name', help='change name of save file (for local save)',
                        type=str, default=DEF_SAVE_NAME)
    parser.add_argument('-B', '--Browser', help='Browser name',
                        type=str, default=pconf.browser)
    parser.add_argument('-D', '--Driver', help='Driver path (for selenium)',
                        type=str, default=pconf.driver_path)
    parser.add_argument('-J', '--save-json', help='save a copy of results as a json file', action='store_true')
    parser.add_argument('-v', '--volume', type=int, default=0,
                        help='Set how much info is printed out: '
                             '10 = quite, '
                             '20 = normal, '
                             '30 = debug, '
                             '40 = verbose')
    return parser


def set_parser_long_args(parser):
    """
    Add arguments to parser
    :param parser: parser we are modifying
    :return: modified parser
    """
    parser.add_argument('--google-app-name', help='google developer code used to access google APIs',
                        type=str, default=pconf.google_ktree_API_key)

    parser.add_argument('--headless', help='runs the scraper in headless mode (no visible browser)',
                        action='store_true')

    parser.add_argument('-d', '--database', help="If indicated, a database will be created over the MySQL server "
                                                 "specified in Database/config.py",
                        action='store_true')
    parser.add_argument('--not-all-users', action='store_true',
                        help='search only for the exact number of users specified in the --num-items tag')
    # parser.add_argument('-S', '--save-to-db', action='store_true',
    #                     help='save results in mySQL database (not implemented yet)')
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
    # gr_data.add_argument('-d', '--load-db', help='(el) Loads json save', action='store_true')

    # gr_db = parser.add_mutually_exclusive_group()
    # # how to save results to db
    # gr_db.add_argument('-u', '--update', help='replace duplicates', action='store_true')
    # gr_db.add_argument('-a', '--append', help='ignore duplicates', action='store_true')
    # gr_db.add_argument('-p', '--print', help="don't save results to database, just print to screen",
    #                    action='store_true')
    # gr_db.add_argument('--replace', help='delete all data once done scraping, and start anew', action='store_true')
    return parser


def set_mysql_args(parser):
    """
    Add mySQL arguments to parser
    :param parser: parser we are modifying
    :return: modified parser
    """
    parser.add_argument('--mysql-host', type=str, default=dbconf.MYSQL_HOST,
                        help='set the host name of the mySQL server')
    parser.add_argument('--mysql-user', type=str, default=dbconf.MYSQL_USER,
                        help='set the username of the mySQL server')
    parser.add_argument('--mysql-password', type=str, default=dbconf.MYSQL_PASSWORD,
                        help='set the password of the mySQL server')
    return parser
