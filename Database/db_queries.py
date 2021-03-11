# users table queries
SELECT_USER_ID = "SELECT user_id FROM users WHERE username = (?);"
INSERT_USER = """INSERT INTO users ('username',
                                  'followers',
                                  'following',
                                  'designs',
                                  'collections',
                                  'makes',
                                  'likes',
                                  'skill_level')
                VALUES (?, ?, ?, ?, ?, ?, ?, ?);"""

# titles table queries
SELECT_TITLE_ID = "SELECT title_id FROM titles WHERE title = (?);"
INSERT_TITLE = "INSERT INTO titles (title) VALUES (?);"

# user_title table queries
INSERT_TITLE_USER = "INSERT INTO user_title (title_id,user_id) VALUES (?,?);"

# print settings table queries
INSERT_PRINT_SETTINGS = """INSERT INTO print_settings ('printer_brand',
                                                       'printer_model',
                                                       'rafts',
                                                       'supports',
                                                       'resolution',
                                                       'infill',
                                                       'filament_brand',
                                                       'filament_color',
                                                       'filament_material') 
                                  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""

# things table queries
SELECT_THING_ID = "SELECT thing_id FROM things WHERE thigiverse_id = (?);"
INSERT_THING = """INSERT INTO things ('thigiverse_id',
                                      'user_id',
                                      'model_name',
                                      'uploaded',
                                      'files',
                                      'comments',
                                      'makes',
                                      'remixes',
                                      'likes',
                                      'setting_id',
                                      'license',
                                      'remix_id',
                                      'thigiverse_remix',
                                      'category') 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,?);"""

# tags table queries
SELECT_TAG_ID = "SELECT tag_id FROM tags WHERE tag = (?)"
INSERT_TAG = "INSERT INTO tags (tag) VALUES (?);"

# thing tag table queries
INSERT_TAG_THING = "INSERT INTO thing_tag ('tag_id', 'thing_id') VALUES (?, ?)"

# makes table queries
SELECT_MAKE_ID = "SELECT make_id FROM makes WHERE thigiverse_id= (?)"
INSERT_MAKE = """INSERT INTO makes ('thigiverse_id',
                                      'thing_id',
                                      'user_id',
                                      'uploaded',
                                      'comments',
                                      'likes',
                                      'views',
                                      'category',
                                      'setting_id') 
                          VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);"""