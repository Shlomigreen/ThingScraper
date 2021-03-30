import json
import os
import config as conf
import db_queries as dbq
import pymysql

import general_config as gconf
import logging

from ThingScraper import Thing, User, Make, to_field_format

# Define file logger
logger = logging.getLogger(gconf.Logs.LOGGER_NAME)

# Test constants
RELATIVE_JSON_PATH = "save.json"
PARENT_PATH = os.path.dirname(os.getcwd())
FULL_JSON_PATH = os.path.join(PARENT_PATH, RELATIVE_JSON_PATH)


def _insert_user(cursor, user):
    """
    Insert a single user to dataframe at cursor.
    Return user id from database after insert.
    """
    # Create a tuple with user fields
    user_data = (user[User.PROPERTIES.USERNAME],
                 user[User.PROPERTIES.FOLLOWERS],
                 user[User.PROPERTIES.FOLLOWING],
                 user[User.PROPERTIES.DESIGNS],
                 user[User.PROPERTIES.COLLECTIONS],
                 user[User.PROPERTIES.MAKES],
                 user[User.PROPERTIES.LIKES],
                 user[User.PROPERTIES.SKILL_LEVEL])

    cursor.execute(dbq.INSERT_USER, user_data)
    user_id = cursor.lastrowid
    logger.debug("User {} inserted to the database under user_id {}".format(user[User.PROPERTIES.USERNAME],
                                                                            user_id))

    return user_id


def _insert_user_title(cursor, user_id, title):
    """
    Insert a title if doesnt exist and pairs it with given user id.
    """
    # run query to find title id for given title
    cursor.execute(dbq.SELECT_TITLE_ID, [title])
    title_id_query = cursor.fetchone()

    # if title exists: obtain title_id
    if title_id_query:
        title_id = title_id_query.popitem()[1]
    # if title does not exists: add it to titles table, and obtain it's id
    else:
        cursor.execute(dbq.INSERT_TITLE, [title])
        title_id = cursor.lastrowid
        logger.debug("Title '{}' inserted at title_id '{}'".format(title, title_id))

    # Add title id and user id to new table
    cursor.execute(dbq.INSERT_TITLE_USER, [title_id, user_id])
    logger.debug("Linked title_id '{}' and user_id '{}'".format(title, title_id))
    

def _fetch_value(cursor, index=1):
    """
    Returns the fetchone value of previously run query at cursor.
    """
    return cursor.fetchone().popitem()[index]


def _insert_users(users, cur):
    """Inserts a list of user dictionaries into database at courser cur."""
    for user in users.values():
        try:
            # user exists in the database: obtain user_id
            if cur.execute(dbq.SELECT_USER_ID, [user[User.PROPERTIES.USERNAME]]):
                user_id = _fetch_value(cur)
    
            # user doest not exists: add it and obtain user_id
            else:
                user_id = _insert_user(cur, user)
        
        except KeyError as e:
            logger.error(e)
            continue

        # add new title if doesnt exist, get its id, add it with user id to common table
        try:
            user_titles = user[User.PROPERTIES.TITLES]
            if user_titles:
                for title in user_titles:
                    _insert_user_title(cur, user_id, title)
        except KeyError as e:
            logger.error(e)
            continue


def _insert_tag(cur, tag):
    """
    Inserts a signle tag (if doesnt exist) into the database at cursor cur.
    :return: inserted tag id as appear in the database
    """
    # if tag exists: obtain tag_id
    if cur.execute(dbq.SELECT_TAG_ID, [tag]):
        tag_id = _fetch_value(cur)
    # if title does not exists: add it to titles table, and obtain it's id
    else:
        cur.execute(dbq.INSERT_TAG, [tag])
        tag_id = cur.lastrowid

    return tag_id


def _insert_tag_thing(cur, tag_id, thing_id):
    """
    Pair tag and thing based on given ids and insert them into tag_thing table.
    :return: tag_thing_id
    """
    # Add tag id and thing id to new table
    cur.execute(dbq.INSERT_TAG_THING, [tag_id, thing_id])

    return cur.lastrowid


def _insert_print_settings(cur, thing_print_settings):
    """
    Inserts new print settings a cursor cur location.
    :return: setting_id
    """
    # add print settings, get print setting id
    if thing_print_settings is None:
        return None
    else:
        # create a list for print settings
        print_settings = []

        # for each possible print setting, append to list, if setting needs encoding, apply it before adding
        for setting in gconf.ThingSettings.POSSIBLE_PRINT_SETTINGS:

            if setting not in thing_print_settings:
                print_settings.append(None)
                continue

            setting_value = thing_print_settings[to_field_format(setting)]

            if setting in gconf.ThingSettings.ENCODE_PRINT_SETTINGS:
                setting_value = gconf.ThingSettings.PRINT_SETTINGS_ENCODER[setting_value.lower()]

            print_settings.append(setting_value)

        # insert as new print settings
        cur.execute(dbq.INSERT_PRINT_SETTINGS, print_settings)
        return cur.lastrowid


def _insert_thing(cur, thing, user_id, settings_id, remix_id=None, remix_thingiverse_id=None):
    """Inserts single thing or remix"""
    # construct thing data tuple to be used in query
    thing_data = (thing[Thing.PROPERTIES.THING_ID],
                  user_id,
                  thing[Thing.PROPERTIES.MODEL_NAME],
                  thing[Thing.PROPERTIES.UPLOADED],
                  thing[Thing.PROPERTIES.FILES],
                  thing[Thing.PROPERTIES.COMMENTS],
                  thing[Thing.PROPERTIES.MAKES],
                  thing[Thing.PROPERTIES.REMIXES],
                  thing[Thing.PROPERTIES.LIKES],
                  settings_id,
                  thing[Thing.PROPERTIES.LICENSE],
                  remix_id,
                  remix_thingiverse_id,
                  thing[Thing.PROPERTIES.CATEGORY])

    # add thing to database, return row id
    cur.execute(dbq.INSERT_THING, thing_data)
    return cur.lastrowid


def _insert_things(things, cur):
    """Inserts a list of thing dictionaries into database at courser cur."""
    for thing in things:
        # thing exists
        if cur.execute(dbq.SELECT_THING_ID, [thing[Thing.PROPERTIES.THING_ID]]):
            thing_id = _fetch_value(cur)

        #  thing doesn't exist
        else:

            # get setting_id from print setting table; insert new print setting and get its id
            settings_id = _insert_print_settings(cur, thing[Thing.PROPERTIES.PRINT_SETTINGS])

            # find user id in database and gets its id, enter none if user doesn't exist
            user_id = _fetch_value(cur) if cur.execute(dbq.SELECT_USER_ID, [thing[Thing.PROPERTIES.USERNAME]]) else None

            # check if thing is remix, get original thing id from database
            remix_id = _fetch_value(cur) if cur.execute(dbq.SELECT_THING_ID,
                                                        [thing[Thing.PROPERTIES.REMIX]]) else None

            # insert new thing
            thing_id = _insert_thing(cur,
                                     thing,
                                     user_id,
                                     settings_id,
                                     remix_id,
                                     remix_thingiverse_id=thing[Thing.PROPERTIES.REMIX])

            # for each tag, add new if doesnt exist, add tag id and thing id into common table
            if thing[Thing.PROPERTIES.TAGS]:
                for tag in thing[Thing.PROPERTIES.TAGS]:
                    # Obtain tag id in exist in database, insert as new tag if not.
                    tag_id = _insert_tag(cur, tag)

                    # Link tag id and thing id
                    _insert_tag_thing(cur, tag_id, thing_id)


def _insert_makes(makes, cur):
    """Inserts a list of make dictionaries into database at courser cur."""
    for make in makes.values():
        # Check if make exists in the database based on thingiverse make id

        if cur.execute(dbq.SELECT_MAKE_ID, [make[Make.PROPERTIES.MAKE_ID]]):
            make_id = _fetch_value(cur)

        # create new make if doesn't exist
        else:

            # insert print settings and get id
            settings_id = _insert_print_settings(cur, make[Make.PROPERTIES.PRINT_SETTINGS])

            # find user id in database and gets its id, enter none if user doesn't exist
            user_id = _fetch_value(cur) if cur.execute(dbq.SELECT_USER_ID,
                                                       [make[Make.PROPERTIES.USERNAME]]) else None

            # find original thing id in database, enter none if doesn't exist
            thing_id = _fetch_value(cur) if cur.execute(dbq.SELECT_THING_ID,
                                                        [make[Make.PROPERTIES.THING_ID]]) else None

            # construct make data tuple to be used in query
            make_data = (make[Make.PROPERTIES.MAKE_ID],
                         thing_id,
                         user_id,
                         make[Make.PROPERTIES.UPLOADED],
                         make[Make.PROPERTIES.COMMENTS],
                         make[Make.PROPERTIES.LIKES],
                         make[Make.PROPERTIES.VIEWS],
                         make[Make.PROPERTIES.CATEGORY],
                         settings_id)

            # add make to database
            cur.execute(dbq.INSERT_MAKE, make_data)


def parse_sql(filename=gconf.DB_builder.SQL_CONSTRUCTION):
    """Parse .sql file to match mysql query style."""
    data = open(filename, 'r').readlines()
    statements = []
    delimiter = ';'
    stmt = ''

    for line_no, line in enumerate(data):
        if not line.strip():
            continue

        if line.startswith('--'):
            continue

        if 'delimiter' in line:
            delimiter = line.split()[1]
            continue

        if delimiter not in line:
            stmt += line.replace(delimiter, ';')
            continue

        if stmt:
            stmt += line
            statements.append(stmt.strip())
            stmt = ''
        else:
            statements.append(line.strip())
    return statements


def _build_db_form_script(cur, db_name):
    """Build database at cur based on script path in genral configurations"""
    building_script = gconf.DB_builder.SQL_CONSTRUCTION
    logger.info("`{}` database was not found. Running database building script: {}".format(db_name.title(),
                                                                                           building_script))
    for statement in parse_sql(filename=building_script):
        cur.execute(statement)
    cur.execute('USE {};'.format(db_name))


def _insert_data(cur, data):
    """Insert data users, things, remixes and makes into the database at cur"""
    try:
        _insert_users(data['users'], cur)
        logger.info('Users inserted to database')
    except KeyError as e:
        logger.error(f"Failed to insert users to database: {e}")
    try:
        things = [thing for thing in data['things'].values() if thing['remix'] is None]
        _insert_things(things, cur)
        logger.info('Things inserted to database')
    except KeyError as e:
        logger.error(f"Failed to insert things to database: {e}")
    try:
        remixes = [thing for thing in data['things'].values() if thing['remix'] is not None]
        _insert_things(remixes, cur)
        logger.info('Remixes inserted to database')
    except KeyError as e:
        logger.error(f"Failed to insert remixes to database: {e}")
    try:
        _insert_makes(data['makes'], cur)
        logger.info('Makes inserted to database')
    except KeyError as e:
        logger.error(f"Failed to insert makes to database: {e}")


def build_database(json_path, db_name=gconf.DB_builder.DB_NAME, drop_existing=True):
    """
    Builds a database of given things, makes and users from a json file.
     :param json_path: the absolute path to json file
     :param db_name: the path to save the database. Default:  gconf.DB_builder.DB_NAME
     :param drop_existing: if true, drop database first if existing. Default: True.
    """
    logger.info("Building database {}".format(db_name))

    if os.path.exists(json_path):
        data = json.load(open(json_path, 'r'))
    else:
        logger.error("Could not find JSON file at given path: {}".format(json_path))
        logger.error("Building database aborted.")
        return
    logger.debug("JSON file loaded")

    # Set up mysql server connection
    try:
        connection = pymysql.connect(host=conf.MYSQL_HOST,
                                     user=conf.MYSQL_USER,
                                     password=conf.MYSQL_PASSWORD,
                                     cursorclass=pymysql.cursors.DictCursor,
                                     auth_plugin_map='mysql_native_password')
    except pymysql.err.OperationalError as e:
        logger.error("Connection to mysql server failed : {}".format(e))
        return

    logger.debug("Connected to mysql successfully")
    cur = connection.cursor()

    try:
        cur.execute('USE {};'.format(db_name))
        logger.debug("Database `{}` exists".format(db_name))

        if drop_existing:
            cur.execute('DROP DATABASE {};'.format(db_name))
            logger.debug("Database dropped".format(db_name))
        else:
            logger.warning("Database already exists, nothing happened. "
                           "Use drop_existing=True argument to first remove it.")
            return

    finally:
        _build_db_form_script(cur, db_name)

    connection.select_db(db_name)

    _insert_data(cur, data)

    cur.close()
    connection.commit()
    connection.close()


def main():
    json_path = FULL_JSON_PATH
    build_database(json_path, drop_existing=True)


if __name__ == '__main__':
    main()
