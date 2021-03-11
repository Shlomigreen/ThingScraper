import sqlite3
import os
import contextlib
import json
import db_queries as dbq

RELATIVE_JSON_PATH = "temp/data.json"
PARENT_PATH = os.path.dirname(os.getcwd())
FULL_JSON_PATH = os.path.join(PARENT_PATH, RELATIVE_JSON_PATH)

DB_FILENAME = 'thingiverse.db'


def main() :
    data = json.load(open(FULL_JSON_PATH, 'r'))

    sql_file = open("thingiverse.sql")
    sql_as_string = sql_file.read()

    initiate_db = not os.path.exists(DB_FILENAME)

    with contextlib.closing(sqlite3.connect(DB_FILENAME)) as con :  # auto-closes
        with con :  # auto-commits
            cur = con.cursor()

            if initiate_db :
                cur.executescript(sql_as_string)

            # 1. add users and titles to database
            for user in data['users'].values() :
                # 1.1. add new user if doesnt exist and get its id
                # TODO: handle sqlite3.IntegrityError

                # Create a tuple with user fields
                user_data = (user['username'],
                             user['followers'],
                             user['following'],
                             user['designs'],
                             user['collections'],
                             user['makes'],
                             user['likes'],
                             user['skill_level'])

                user_id_query = cur.execute(dbq.SELECT_USER_ID, [user['username']]).fetchone()

                # user exists in the database: obtain user_id
                if user_id_query :
                    user_id = user_id_query[0]

                # user doest not exists: add it and obtain user_id
                else :
                    cur.execute(dbq.INSERT_USER, user_data)
                    user_id = cur.lastrowid

                # 1.2 add new title if doesnt exist, get its id, add it with user id to common table
                if user['titles'] :
                    for title in user['titles'] :
                        # run query to find title id for given title
                        title_id_query = cur.execute(dbq.SELECT_TITLE_ID, [title]).fetchone()

                        # if title exists: obtain title_id
                        if title_id_query :
                            title_id = title_id_query[0]
                        # if title does not exists: add it to titles table, and obtain it's id
                        else :
                            cur.execute(dbq.INSERT_TITLE, [title])
                            title_id = cur.lastrowid

                        # Add title id and user id to new table
                        cur.execute(dbq.INSERT_TITLE_USER, [title_id, user_id])

            # 2. add things, tags, print settings
            things = [thing for thing in data['things'].values() if thing['remix'] is None]
            for thing in things :
                # 2.1 Check if thing exists in the database based on thigiverse id
                thing_id_query = cur.execute(dbq.SELECT_THING_ID, [thing['thing_id']]).fetchone()
                # thing exists
                if thing_id_query :
                    thing_id = thing_id_query[0]

                #  thing doesn't exist
                else :

                    # 2.1.2  add print settings, get print setting id
                    # if all print settings are none, set settings id to None.
                    if all(setting is None for setting in thing['print_settings'].values()) :
                        settings_id = None
                    else :
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
                    if thing['tags'] :
                        for tag in thing['tags'] :
                            # run query to find tag id for given tag
                            tag_id_query = cur.execute(dbq.SELECT_TAG_ID, [tag]).fetchone()

                            # if tag exists: obtain tag_id
                            if tag_id_query :
                                tag_id = tag_id_query[0]
                            # if title does not exists: add it to titles table, and obtain it's id
                            else :
                                cur.execute(dbq.INSERT_TAG, [tag])
                                tag_id = cur.lastrowid

                            # Add tag id and thing id to new table
                            cur.execute(dbq.INSERT_TAG_THING, [tag_id, thing_id])

            # 3. add remixes
            remixes = [thing for thing in data['things'].values() if thing['remix'] is not None]
            for thing in remixes :
                # 3.1 Check if thing exists in the database based on thigiverse id
                thing_id_query = cur.execute(dbq.SELECT_THING_ID, [thing['thing_id']]).fetchone()
                # thing exists
                if thing_id_query :
                    thing_id = thing_id_query[0]

                #  thing doesn't exist
                else :

                    # 3.1.2  add print settings, get print setting id
                    # if all print settings are none, set settings id to None.
                    if all(setting is None for setting in thing['print_settings'].values()) :
                        settings_id = None
                    else :
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
                    if thing['tags'] :
                        for tag in thing['tags'] :
                            # run query to find tag id for given tag
                            tag_id_query = cur.execute(dbq.SELECT_TAG_ID, [tag]).fetchone()

                            # if tag exists: obtain tag_id
                            if tag_id_query :
                                tag_id = tag_id_query[0]
                            # if title does not exists: add it to titles table, and obtain it's id
                            else :
                                cur.execute(dbq.INSERT_TAG, [tag])
                                tag_id = cur.lastrowid

                            # Add tag id and thing id to new table
                            cur.execute(dbq.INSERT_TAG_THING, [tag_id, thing_id])

            # 4. add makes
            for make in data['makes'].values() :
                # 4.1 Check if make exists in the database based on thigiverse make id
                make_id_query = cur.execute(dbq.SELECT_MAKE_ID, [make['make_id']]).fetchone()
                if make_id_query :
                    make_id = make_id_query[0]
                # create new make if doesn't exist
                else :
                    # check if all settings are non, if so, print setting id is none as well
                    if all(setting is None for setting in thing['print_settings'].values()) :
                        settings_id = None
                    else :
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



if __name__ == '__main__' :
    main()
    print("OMG")
