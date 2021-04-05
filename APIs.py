import requests
import json
import logging
import general_config as gconf
import personal_config as pconf


logger = logging.getLogger(gconf.Logs.LOGGER_NAME)


def enrich_with_apis(data_dict, items=1, app_id_google=None):
    """
    Enrich a dict of scraped data with data from APIs
    :param data_dict: A dict containing project save data
    :param items: max number of items to get from the each API that returns lists
    :param app_id_google: google developer key for the API
    :return: None
    """
    logger.info('Starting enrichment with PAIs')
    enrich_things_with_google_ktree(data_dict["things"], items=items, app_id=app_id_google)
    logger.info('Done enriching with APIs')


def enrich_things_with_google_ktree(things_dict, items=1, app_id=None):
    """
    Enrich a dict of things with data from google knowledge tree
    :param things_dict: a dict of things, the keys are ids, and the values are dicts representing the thing.
    :param items: max number of items to get from the knowledge tree
    :param app_id: google developer key for the API
    :return: None
    """
    logger.info("Using google's knowledge tree API")
    for thing_id in things_dict:
        thing = things_dict[thing_id]
        thing_name = thing[gconf.ThingSettings.Elements.MODEL_NAME]
        ex_data = query_google_ktree(thing_name, items, app_id=app_id)
        if ex_data is not None:
            if len(ex_data) > 0:
                ex_data = parse_data_from_ktree_list(ex_data)
                thing[gconf.google_ktree.final_id] = ex_data
    logger.info("Done using google's knowledge tree API")


def query_google_ktree(thing, nitems=1, lan='en', app_id=None):
    """
    Look for item in google knowledge tree, and pass results in a list with minimal
    processing
    :param thing: search query
    :param nitems: max amount of results to deliver
    :param lan: language of results
    :param app_id: google developer key for the API. Can also be provided in personal config file (pass as None)
    :return: A list of results from google knowledge tree
    """
    if app_id is None:
        app_id = pconf.google_ktree_API_key
    q = gconf.google_ktree.api_address + f'query={thing}' \
                                         f'&key={app_id}' \
                                         f'&limit={nitems}' \
                                         f'&indent=True' \
                                         f'&types=Thing' \
                                         f'&languages={lan}'
    response = requests.get(q)
    if response.status_code == 200:
        data = json.loads(response.text)
        data = data.get(gconf.google_ktree.main_list_identifier, None)
    else:
        logger.error(f'bad google knowledge tree response: {response.status_code}')
        data = None
    return data


def parse_data_from_ktree_list(ktree_data):
    """
    Get a list of results from google knowledge tree, and process it, keep only useful info in a convenient format
    :param ktree_data: a list of results from google knowledge tree
    :return: ktree_data parsed
    """
    parsed_data = []
    for res in ktree_data:
        res = parse_item_from_ktree_list(res)
        parsed_data.append(res)
    return parsed_data


def choose_tags_in_ktree(old_ktree_item):
    """
    chooses only tags in the database template,
    allocates space for non found attributes
    :param old_ktree_item: item with tags from the api
    :return: item with only selected tags
    """
    new_ktree_item = dict()
    tag_names = [tag for tag in dir(gconf.google_ktree.Tags) if tag[0] != "_"]
    tags = vars(gconf.google_ktree.Tags)
    for tag_name in tag_names:
        tag = tags[tag_name]
        new_ktree_item[tag] = old_ktree_item.get(tag, None)
    return new_ktree_item


def parse_item_from_ktree_list(ktree_item):
    """
    get one search result from google knowledge tree and parse it
    :param ktree_item: one search result in the form of a dict
    :return: parsed dict
    """
    if ktree_item[gconf.google_ktree.OldTags.type] == gconf.google_ktree.res_identifier:
        # We are in the result layer, we need to go a layer deeper
        score = ktree_item[gconf.google_ktree.Tags.res_score]
        ktree_item = parse_item_from_ktree_list(ktree_item[gconf.google_ktree.res])
        ktree_item[gconf.google_ktree.Tags.res_score] = score
    else:
        # rename old tags
        if gconf.google_ktree.OldTags.id in ktree_item:
            ktree_item[gconf.google_ktree.Tags.id] = ktree_item.pop(gconf.google_ktree.OldTags.id)
        if gconf.google_ktree.OldTags.type in ktree_item:
            ktree_item[gconf.google_ktree.Tags.type] = ktree_item.pop(gconf.google_ktree.OldTags.type)
        # unpack detailed description
        if gconf.google_ktree.OldTags.dit_desc in ktree_item:
            ktree_item.update(ktree_item[gconf.google_ktree.OldTags.dit_desc])
            del ktree_item[gconf.google_ktree.OldTags.dit_desc]
        ktree_item = choose_tags_in_ktree(ktree_item)
    return ktree_item
