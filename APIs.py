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

    """things = data_dict["things"]
    for item in things:
        thing = things[item]
        thing_api_data = thing.get('ktree_data', None)
        if thing_api_data is not None:
            print(f"printing for {thing[gconf.ThingSettings.Elements.MODEL_NAME]}:")
            for sub_dict in thing_api_data:
                print('\t' + '*' * 25)
                for key in sub_dict:
                    print(f"\t{key}: {sub_dict[key]}")"""
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
                thing['ktree_data'] = ex_data
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


def parse_item_from_ktree_list(ktree_item):
    """
    get one search result from google knowledge tree and parse it
    :param ktree_item: one search result in the form of a dict
    :return: parsed dict
    """
    if ktree_item['@type'] == 'EntitySearchResult':
        score = ktree_item['resultScore']
        ktree_item = parse_item_from_ktree_list(ktree_item['result'])
        ktree_item['resultScore'] = score
    else:
        if "@id" in ktree_item:
            ktree_item["id"] = ktree_item.pop("@id")
        if "@type" in ktree_item:
            ktree_item["type"] = ktree_item.pop("@type")
        if "detailedDescription" in ktree_item:
            ktree_item.update(ktree_item["detailedDescription"])
            del ktree_item["detailedDescription"]
    return ktree_item
