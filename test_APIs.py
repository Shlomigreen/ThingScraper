import APIs
import logging
import general_config as gconf


logger = logging.getLogger(gconf.Logs.LOGGER_NAME)


sample_data_template = {
        "things": dict(),
        "users": dict(),
        "makes": dict()
    }
sample_data = sample_data_template.copy()
sample_data['things'] = {"4760325": {"model_name": "Uno Box Holder"},
                         "4760326": {"model_name": "Pocket hole jig"},
                         "4760327": {"model_name": "brick"},
                         "4760328": {"model_name": "Bricks"},
                         "4760329": {"model_name": "maya"},
                         "4760330": {"model_name": "Finally done with this test :)"}}


def test_enrich_things_with_google_ktree_sample_run():
    data = sample_data["things"].copy()
    print(len(data))


def test_enrich_things_with_google_ktree_len_conservation():
    data = sample_data["things"].copy()
    L = len(data)
    APIs.enrich_things_with_google_ktree(data)
    L_new = len(data)
    assert L == L_new


def test_query_google_ktree_res_type():
    data = APIs.query_google_ktree('maya', 5)
    assert type(data) == list


def test_query_google_ktree_res_len():
    data = APIs.query_google_ktree('maya', 5)
    assert len(data) <= 5


def test_query_google_ktree_has_dicts():
    data = APIs.query_google_ktree('maya', 5)
    for sub in data:
        assert type(sub) == dict


def test_parse_data_from_ktree_list():
    pass
