import json
import os
import Database.config as conf
import Database.db_queries as dbq
import pymysql

import general_config as gconf
import logging

from ThingScraper import Thing, User, Make, to_field_format

# Define file logger
logger = logging.getLogger(gconf.Logs.LOGGER_NAME)

# Test constants
# FULL_JSON_PATH = "/Users/shlomi/Google Drive/ITC/Projects/Data Mining Project/ITC_Data_Mining_Thingiverse/JSON/scraped_data_03042021-1433.json"


def _insert_user(cursor, user):
    """
    Insert a single user to database at cursor.
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


def _update_user(cursor, user_id, user):
    """
    Update a single user in database at cursor.
    """
    # Create a tuple with user fields
    user_data = (user[User.PROPERTIES.FOLLOWERS],
                 user[User.PROPERTIES.FOLLOWING],
                 user[User.PROPERTIES.DESIGNS],
                 user[User.PROPERTIES.COLLECTIONS],
                 user[User.PROPERTIES.MAKES],
                 user[User.PROPERTIES.LIKES],
                 user[User.PROPERTIES.SKILL_LEVEL],
                 user_id)

    cursor.execute(dbq.UPDATE_USER, user_data)
    logger.debug("user_id {} updated".format(user_id))


def _get_title_id(cursor, title):
    """Returns title id for given title"""
    # run query to find title id for given title
    title_id_query = cursor.execute(dbq.SELECT_TITLE_ID, [title])

    if title_id_query:
        return _fetch_value(cursor)
    else:
        return None


def _insert_title(cursor, title):
    """Inserts a new title and returns its id"""
    cursor.execute(dbq.INSERT_TITLE, [title])
    title_id = cursor.lastrowid
    logger.debug("Title '{}' inserted at title_id '{}'".format(title, title_id))

    return title_id


def _insert_user_title(cursor, user_id, title_id):
    """
    Insert a user_id title_id pair into user_title table
    """
    # Add title id and user id to new table
    cursor.execute(dbq.INSERT_TITLE_USER, [title_id, user_id])
    logger.debug("Linked title_id '{}' and user_id '{}'".format(title_id, user_id))


def _fetch_value(cursor, index=1):
    """
    Returns the fetchone value of previously run query at cursor.
    """
    return cursor.fetchone().popitem()[index]


def _insert_users(users, cur):
    """Inserts a list of user dictionaries into database at courser cur."""
    for user in users.values():
        try:
            # user exists in the database: obtain user_id and update
            if cur.execute(dbq.SELECT_USER_ID, [user[User.PROPERTIES.USERNAME]]):
                user_id = _fetch_value(cur)
                _update_user(cur, user_id, user)

            # user doest not exists: add it and obtain user_id
            else:
                user_id = _insert_user(cur, user)

        except KeyError as e:
            logger.error(e)
            continue

        # add new title if doesnt exist, get its id, add it with user id to common table
        try:
            user_titles = user[User.PROPERTIES.TITLES]

            # if user has no titles, define an empty set
            if user_titles:
                user_titles = set(user_titles)
            else:
                user_titles = set()

            # get db updated titles for user id
            if cur.execute(dbq.USER_TITLES, user_id):
                db_titles = {db_title['title'] for db_title in cur.fetchall()}
            else:
                db_titles = set()

            new_titles = user_titles.difference(db_titles)
            remove_titles = db_titles.difference(user_titles)

            # add new titles
            for title in new_titles:
                # get id for title if exists
                title_id = _get_title_id(cur, title)
                # if it doesnt, add it and get its id
                if title_id is None:
                    title_id = _insert_title(cur, title)
                # pair user and title
                _insert_user_title(cur, user_id, title_id)

            # remove no longer existing titles for user
            for title in remove_titles:
                title_id = _get_title_id(cur, title)
                cur.execute(dbq.REMOVE_USER_TITLE, [title_id, user_id])

        except KeyError as e:
            logger.error(e)
            continue


def _get_tag_id(cursor, tag):
    if cursor.execute(dbq.SELECT_TAG_ID, [tag]):
        return _fetch_value(cursor)
    else:
        return None


def _insert_tag(cur, tag):
    cur.execute(dbq.INSERT_TAG, [tag])
    tag_id = cur.lastrowid
    logger.debug("Tag '{}' inserted at tag_id '{}'".format(tag, tag_id))

    return tag_id


def _insert_tag_thing(cur, tag_id, thing_id):
    """
    Pair tag and thing based on given ids and insert them into tag_thing table.
    :return: tag_thing_id
    """
    cur.execute(dbq.INSERT_TAG_THING, [tag_id, thing_id])
    logger.debug("Linked tag_id '{}' and thing_id '{}'".format(tag_id, thing_id))


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
            setting = to_field_format(setting)

            if setting not in thing_print_settings:
                print_settings.append(None)
                continue

            setting_value = thing_print_settings[setting]

            if setting_value is not None and setting in gconf.ThingSettings.ENCODE_PRINT_SETTINGS:
                setting_value = gconf.ThingSettings.PRINT_SETTINGS_ENCODER[setting_value.lower()]

            print_settings.append(setting_value)

        # insert as new print settings
        try:
            cur.execute(dbq.INSERT_PRINT_SETTINGS, print_settings)
            return cur.lastrowid
        except:
            return None


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
    logger.debug("Inserting thing {}".format(thing[Thing.PROPERTIES.THING_ID]))
    cur.execute(dbq.INSERT_THING, thing_data)
    return cur.lastrowid


def _update_thing(cur, thing, thing_id):
    thing_data = (thing[Thing.PROPERTIES.MODEL_NAME],
                  thing[Thing.PROPERTIES.FILES],
                  thing[Thing.PROPERTIES.COMMENTS],
                  thing[Thing.PROPERTIES.MAKES],
                  thing[Thing.PROPERTIES.REMIXES],
                  thing[Thing.PROPERTIES.LIKES],
                  thing[Thing.PROPERTIES.LICENSE],
                  thing[Thing.PROPERTIES.CATEGORY],
                  thing_id)
    logger.debug("Updating thing id {} (thingiverse id : {} ) ".format(thing_id, thing[Thing.PROPERTIES.THING_ID]))
    cur.execute(dbq.UPDATE_THING, thing_data)


def _insert_things(things, cur):
    """Inserts a list of thing dictionaries into database at courser cur."""
    for thing in things:
        # thing exists
        if cur.execute(dbq.SELECT_THING_ID, [thing[Thing.PROPERTIES.THING_ID]]):
            thing_id = _fetch_value(cur)
            _update_thing(cur, thing, thing_id)
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
        thing_tags = thing[Thing.PROPERTIES.TAGS]

        if thing_tags:
            thing_tags = set(thing_tags)
        else:
            thing_tags = set()

        if cur.execute(dbq.THING_TAGS, thing_id):
            db_tags = {db_title['tag'] for db_title in cur.fetchall()}
        else:
            db_tags = set()

        new_tags = thing_tags.difference(db_tags)
        remove_tags = db_tags.difference(thing_tags)

        for tag in new_tags:
            tag_id = _get_tag_id(cur, tag)
            if tag_id is None:
                tag_id = _insert_tag(cur, tag)
            _insert_tag_thing(cur, tag_id, thing_id)

        for tag in remove_tags:
            tag_id = _get_tag_id(cur, tag)
            cur.execute(dbq.REMOVE_THING_TAG, [tag_id, thing_id])


def _update_make(cur, make, make_id):
    make_data = (make[Make.PROPERTIES.COMMENTS],
                 make[Make.PROPERTIES.LIKES],
                 make[Make.PROPERTIES.VIEWS],
                 make[Make.PROPERTIES.CATEGORY],
                 make_id)

    cur.execute(dbq.UPDATE_MAKE, make_data)


def _insert_makes(makes, cur):
    """Inserts a list of make dictionaries into database at courser cur."""
    for make in makes.values():
        # Check if make exists in the database based on thingiverse make id

        if cur.execute(dbq.SELECT_MAKE_ID, [make[Make.PROPERTIES.MAKE_ID]]):
            make_id = _fetch_value(cur)
            _update_make(cur, make, make_id)
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
    """Build database at cur based on script path in general configurations"""
    building_script = os.path.abspath(os.path.join(gconf.DB_builder.DB_DIR, gconf.DB_builder.SQL_CONSTRUCTION))
    logger.info("`{}` database was not found. Running database building script: {}".format(db_name.title(),
                                                                                           building_script))
    for statement in parse_sql(filename=building_script):
        cur.execute(statement)


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


def build_database(json_data, db_name=gconf.DB_builder.DB_NAME, drop_existing=True):
    """
    Builds a database of given things, makes and users from a JSON file.
     :param json_data: either JSON data or an  absolute path to a JSON file
     :param db_name: the path to save the database. Default:  gconf.DB_builder.DB_NAME
     :param drop_existing: if true, drop database first if existing. Default: True.
    """
    logger.info("Building database {}".format(db_name))

    if isinstance(json_data, str):
        if os.path.exists(json_data):
            data = json.load(open(json_data, 'r'))
        else:
            logger.error("Could not find JSON file at given path: {}".format(json_data))
            logger.error("Building database aborted.")
            return
        logger.debug("JSON file loaded")
    else:
        data = json_data

    print(data)

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

    except pymysql.err.OperationalError:
        _build_db_form_script(cur, db_name)

    finally:
        cur.execute('USE {};'.format(db_name))

    connection.select_db(db_name)

    _insert_data(cur, data)

    cur.close()
    connection.commit()
    connection.close()


# def main():
#     json_path = FULL_JSON_PATH
#     build_database(json_path, drop_existing=False)
#
#
# if __name__ == '__main__':
#     main()
