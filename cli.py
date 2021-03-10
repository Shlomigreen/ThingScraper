import personal_config as pconf
import argparse


def cli_set_arguments():
    """
    Adds arguments to parser obj
    :return: The parser with the new arguments
    """
    parser = argparse.ArgumentParser(description="Scrap data from thingiverse")
    parser.add_argument('type', type=str, metavar='{Thing, Mix, User, Make}',
                        help='Type of data to scrap', default='Thing')
    parser.add_argument('-I', '--Interactive', help='Opens program in interactive mode', action='store_true')
    parser.add_argument('-n', '--num_items', help='How many items to scrape', type=int, default=500)
    parser.add_argument('-N', '--Name', help='change name of save file (for local save)',
                        type=str, default=pconf.def_save_name)
    parser.add_argument('-B', '--Browser', help='Browser name',
                        type=str, default=pconf.browser)
    parser.add_argument('-D', '--Driver', help='Driver path (for salenium)',
                        type=str, default=pconf.driver_path)
    parser.add_argument('-J', '--save-json', help='save a copy of results as a json file', action='store_true')
    # TODO: implement different search parameters
    parser.add_argument('-O', '--Order-parameter', metavar='{Test1, Test2}',
                        help='The order of things on the search page', default='Test1')
    parser.add_argument('-S', '--pre-search', type=int, default=0,
                        help='When scraping for a non-thing type object can first scrape for things, and then scrape '
                             'for data based on result. Please provide number of pages to scrape')

    gr_volume = parser.add_mutually_exclusive_group()
    # volume of CLI output
    gr_volume.add_argument('-q', '--quiet', help='Print quiet', action='store_true')
    gr_volume.add_argument('-v', '--verbose', help='Print verbose', action='store_true')

    gr_data = parser.add_mutually_exclusive_group()
    # where to load data from at the start of the run
    gr_data.add_argument('-j', '--load-json', help='Saves as json', action='store_true')
    gr_data.add_argument('-d', '--load-db', help='(el) Loads json save', action='store_true')

    gr_db = parser.add_mutually_exclusive_group()
    # how to save results to db
    gr_db.add_argument('-u', '--update', help='replace duplicates', action='store_true')
    gr_db.add_argument('-a', '--append', help='ignore duplicates', action='store_true')
    gr_db.add_argument('-p', '--print', help="don't save results to database, just print to screen",
                       action='store_true')
    gr_db.add_argument('--replace', help='delete all data once done scraping, and start anew', action='store_true')
    return parser


def inter_parser(args=None, parser=None):
    """
    An interpreter for the parser obj, can inject our own arguments.
    :param args: Arguments passed for testing/ through other program (If None use CLI input)
    :param parser: A predefined parser
    :return: None
    """
    if parser is None:
        parser = cli_set_arguments()
    if args is None:
        # No arguments, use command line for input (CLI mode)
        args = parser.parse_args()
    inp = dict()

    inp['num_runs'] = vars(args).get("num_items", 500)
    inp['save_name'] = vars(args).get("Name", pconf.def_save_name)
    inp['browser'] = vars(args).get("Browser", pconf.browser)
    inp['driver_path'] = vars(args).get("Driver", pconf.driver_path)

    inp['search_type'] = vars(args).get("type", 'thing').lower()
    inp['volume'] = 'q' if vars(args).get("quiet", False) else \
        'v' if vars(args).get("verbose", False) else \
        'n'
    inp['save_to_db_mode'] = 'u' if vars(args).get("update", False) else \
        'a' if vars(args).get("append", False) else \
        'p' if vars(args).get("print", False) else \
        'n'
    inp['load_type'] = 'd' if vars(args).get("load-db", False) else \
        'j' if vars(args).get("load-json", False) else \
        'n'
    inp['do_save_json'] = vars(args).get("save-json", False)
    inp['Interactive'] = vars(args).get("Interactive", False)
    inp['preliminary_count'] = vars(args).get("pre-search", 0) if inp['search_type'] != 'thing' else 0
    return inp
