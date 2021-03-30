import json
import os
import config as conf
import db_queries as dbq
import pymysql

import general_config as gconf
import logging

from ThingScraper import Thing, User, Make

# Define file logger
logger = logging.getLogger(gconf.Logger.NAME)

# Test constants
RELATIVE_JSON_PATH = "temp/data.json"
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

    return user_id


def _insert_user_title(cursor, user_id, title):
    # run query to find title id for given title
    title_id_query = cursor.execute(dbq.SELECT_TITLE_ID, [title]).fetchone()

    # if title exists: obtain title_id
    if title_id_query:
        title_id = title_id_query[0]
    # if title does not exists: add it to titles table, and obtain it's id
    else:
        cursor.execute(dbq.INSERT_TITLE, [title])
        title_id = cursor.lastrowid

    # Add title id and user id to new table
    cursor.execute(dbq.INSERT_TITLE_USER, [title_id, user_id])


def _insert_users(users, cur):
    """Inserts a list of user dictionaries into database at courser cur."""
    for user in users.values():
        # check if user id exists in database
        cur.execute(dbq.SELECT_USER_ID, [user[User.PROPERTIES.USERNAME]])
        user_id_query = cur.fetchone()

        # user exists in the database: obtain user_id
        if user_id_query:
            user_id = user_id_query[0]

        # user doest not exists: add it and obtain user_id
        else:
            user_id = _insert_user(cur, user)

        # add new title if doesnt exist, get its id, add it with user id to common table
        user_titles = user[User.PROPERTIES.TITLES]
        if user_titles:
            for title in user_titles:
                _insert_user_title(cur, user_id, title)


def _insert_things(things, cur):
    """Inserts a list of thing dictionaries into database at courser cur."""
    for thing in things:
        # Check if thing exists in the database based on thingiverse id
        thing_id_query = cur.execute(dbq.SELECT_THING_ID, [thing['thing_id']]).fetchone()
        # thing exists
        if thing_id_query:
            thing_id = thing_id_query[0]

        #  thing doesn't exist
        else:

            # 2.1.2  add print settings, get print setting id
            # if all print settings are none, set settings id to None.
            if all(setting is None for setting in thing['print_settings'].values()):
                settings_id = None
            else:
                # create a tuple for print settings
                print_settings = (thing['print_settings']['printer_brand'],
                                  thing['print_settings']['printer_model'],
                                  0 if thing['print_settings']['rafts'] == 'No' else 1 if
                                  thing['print_settings']['rafts'] == 'Yes' else -1,
                                  0 if thing['print_settings']['supports'] == 'No' else 1 if
                                  thing['print_settings']['supports'] == 'Yes' else -1,
                                  thing['print_settings']['resolution'],
                                  thing['print_settings']['infill'],
                                  thing['print_settings']['filament_brand'],
                                  thing['print_settings']['filament_color'],
                                  thing['print_settings']['filament_material'])

                # insert as new print settings
                cur.execute(dbq.INSERT_PRINT_SETTINGS, print_settings)
                settings_id = cur.lastrowid

            # 2.1.3 add thing, replace print settings with print settings id, get thing id
            # find user id in database
            user_id_query = cur.execute(dbq.SELECT_USER_ID, [thing['username']])
            user_id = user_id_query.fetchone()[0]

            # construct thing data tuple to be used in query
            thing_data = (thing['thing_id'],
                          user_id,
                          thing['model_name'],
                          thing['uploaded'],
                          thing['thing_files'],
                          thing['comments'],
                          thing['makes'],
                          thing['remixes'],
                          thing['likes'],
                          settings_id,
                          thing['license'],
                          None,
                          None,
                          thing['category'])

            # add thing to database, save the database id
            cur.execute(dbq.INSERT_THING, thing_data)
            thing_id = cur.lastrowid

            # 2.1.4 for each tag, add new if doesnt exist, add tag id and thing id into common table
            if thing['tags']:
                for tag in thing['tags']:
                    # run query to find tag id for given tag
                    tag_id_query = cur.execute(dbq.SELECT_TAG_ID, [tag]).fetchone()

                    # if tag exists: obtain tag_id
                    if tag_id_query:
                        tag_id = tag_id_query[0]
                    # if title does not exists: add it to titles table, and obtain it's id
                    else:
                        cur.execute(dbq.INSERT_TAG, [tag])
                        tag_id = cur.lastrowid

                    # Add tag id and thing id to new table
                    cur.execute(dbq.INSERT_TAG_THING, [tag_id, thing_id])


def _insert_remixes(remixes, cur):
    """Inserts a list of remix dictionaries into database at courser cur."""
    for thing in remixes:
        # 3.1 Check if thing exists in the database based on thingiverse id
        thing_id_query = cur.execute(dbq.SELECT_THING_ID, [thing['thing_id']]).fetchone()
        # thing exists
        if thing_id_query:
            thing_id = thing_id_query[0]

        #  thing doesn't exist
        else:

            # 3.1.2  add print settings, get print setting id
            # if all print settings are none, set settings id to None.
            if all(setting is None for setting in thing['print_settings'].values()):
                settings_id = None
            else:
                # create a tuple for print settings
                print_settings = (thing['print_settings']['printer_brand'],
                                  thing['print_settings']['printer_model'],
                                  0 if thing['print_settings']['rafts'] == 'No' else 1 if
                                  thing['print_settings']['rafts'] == 'Yes' else -1,
                                  0 if thing['print_settings']['supports'] == 'No' else 1 if
                                  thing['print_settings']['supports'] == 'Yes' else -1,
                                  thing['print_settings']['resolution'],
                                  thing['print_settings']['infill'],
                                  thing['print_settings']['filament_brand'],
                                  thing['print_settings']['filament_color'],
                                  thing['print_settings']['filament_material'])

                # insert as new print settings
                cur.execute(dbq.INSERT_PRINT_SETTINGS, print_settings)
                settings_id = cur.lastrowid

            # 3.1.3 add thing, replace print settings with print settings id, get thing id
            # find user id in database
            user_id_query = cur.execute(dbq.SELECT_USER_ID, [thing['username']])
            user_id = user_id_query.fetchone()[0]

            # find remix id (the source thing)
            remix_id_query = cur.execute(dbq.SELECT_THING_ID, [thing['remix']]).fetchone()

            # Check if original thing is in the database, if not set to None
            remix_id = remix_id_query[0] if remix_id_query else None

            # construct thing data tuple to be used in query
            thing_data = (thing['thing_id'],
                          user_id,
                          thing['model_name'],
                          thing['uploaded'],
                          thing['thing_files'],
                          thing['comments'],
                          thing['makes'],
                          thing['remixes'],
                          thing['likes'],
                          settings_id,
                          thing['license'],
                          remix_id,
                          thing['remix'],
                          thing['category'])

            # add thing to database, save the database id
            cur.execute(dbq.INSERT_THING, thing_data)
            thing_id = cur.lastrowid

            # 3.1.4 for each tag, add new if doesnt exist, add tag id and thing id into common table
            if thing['tags']:
                for tag in thing['tags']:
                    # run query to find tag id for given tag
                    tag_id_query = cur.execute(dbq.SELECT_TAG_ID, [tag]).fetchone()

                    # if tag exists: obtain tag_id
                    if tag_id_query:
                        tag_id = tag_id_query[0]
                    # if title does not exists: add it to titles table, and obtain it's id
                    else:
                        cur.execute(dbq.INSERT_TAG, [tag])
                        tag_id = cur.lastrowid

                    # Add tag id and thing id to new table
                    cur.execute(dbq.INSERT_TAG_THING, [tag_id, thing_id])


def _insert_makes(makes, cur):
    """Inserts a list of make dictionaries into database at courser cur."""
    for make in makes.values():
        # 4.1 Check if make exists in the database based on thingiverse make id
        make_id_query = cur.execute(dbq.SELECT_MAKE_ID, [make['make_id']]).fetchone()
        if make_id_query:
            make_id = make_id_query[0]
        # create new make if doesn't exist
        else:
            # check if all settings are non, if so, print setting id is none as well
            if all(setting is None for setting in make['print_settings'].values()):
                settings_id = None
            else:
                # 4.1.1 add print settings, get its id
                # create a tuple for print settings
                print_settings = (make['print_settings']['printer_brand'],
                                  make['print_settings']['printer_model'],
                                  0 if make['print_settings']['rafts'] == 'No' else 1 if make['print_settings'][
                                                                                             'rafts'] == 'Yes' else -1,
                                  0 if make['print_settings']['supports'] == 'No' else 1 if
                                  make['print_settings'][
                                      'supports'] == 'Yes' else -1,
                                  make['print_settings']['resolution'],
                                  make['print_settings']['infill'],
                                  make['print_settings']['filament_brand'],
                                  None,
                                  None)

                # insert as new print settings
                cur.execute(dbq.INSERT_PRINT_SETTINGS, print_settings)
                settings_id = cur.lastrowid

            # 4.2. add make, replace print settings with print settings id
            # find user id in database
            user_id_query = cur.execute(dbq.SELECT_USER_ID, [make['username']]).fetchone()
            user_id = user_id_query[0] if user_id_query else None

            # find original thing id
            thing_id_query = cur.execute(dbq.SELECT_THING_ID, [make['thingiverse_id']]).fetchone()
            thing_id = thing_id_query[0] if thing_id_query else None

            # construct make data tuple to be used in query
            make_data = (make['make_id'],
                         thing_id,
                         user_id,
                         make['uploaded'],
                         make['comments'],
                         make['like'],
                         make['views'],
                         make['category'],
                         settings_id)

            # add make to database
            cur.execute(dbq.INSERT_MAKE, make_data)


def parse_sql(filename=gconf.DB_builder.SQL_CONSTRUCTION):
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


def build_database(json_path, db_name=gconf.DB_builder.DB_NAME):
    """
    Builds a database of given things, makes and users from a json file.
     :param json_path: the absolute path to json file
     :param db_name: the path to save the database. Default:  gconf.DB_builder.DB_NAME
    """
    logger.info("Building database {}".format(db_name))

    logger.debug("Loading json file {}".format(json_path))
    if os.path.exists(json_path):
        data = json.load(open(json_path, 'r'))
    else:
        logger.error(gconf.Errors.DB_ERROR1)
        raise FileNotFoundError(gconf.Errors.DB_ERROR1)

    # Set up mysql server connection
    logger.debug("Trying to connect to mysql server")
    try:
        connection = pymysql.connect(host=conf.MYSQL_HOST,
                                     user=conf.MYSQL_USER,
                                     password=conf.MYSQL_PASSWORD,
                                     cursorclass=pymysql.cursors.DictCursor,
                                     auth_plugin_map='mysql_native_password')
    except pymysql.err.OperationalError as e:
        logger.error(gconf.Errors.DB_ERROR2)
        logger.error(e)
        raise e

    logger.debug("Connected successfully")

    cur = connection.cursor()

    try:
        cur.execute('USE {};'.format(db_name))
    except pymysql.err.OperationalError:
        for statement in parse_sql():
            cur.execute(statement)
    finally:
        cur.execute('USE {};'.format(db_name))

    connection.select_db(db_name)

    _insert_users(data['users'], cur)

    things = [thing for thing in data['things'].values() if thing['remix'] is None]
    _insert_things(things, cur)

    remixes = [thing for thing in data['things'].values() if thing['remix'] is not None]
    _insert_remixes(remixes, cur)

    _insert_makes(data['makes'], cur)

    cur.close()
    connection.commit()
    connection.close()


def main():
    json_path = '/Users/shlomi/Google Drive/ITC/Projects/Data Mining Project/ITC_Data_Mining_Thingiverse/data.json'
    build_database(json_path)


if __name__ == '__main__':
    main()
