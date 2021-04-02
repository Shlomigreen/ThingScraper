# users table queries
SELECT_USER_ID = f"SELECT user_id FROM users WHERE username = (%s);"
INSERT_USER = """INSERT INTO users (username,
                                  followers,
                                  following,
                                  designs,
                                  collections,
                                  makes,
                                  likes,
                                  skill_level)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"""
UPDATE_USER = """UPDATE users 
                 SET followers = %s, 
                     following = %s, 
                     designs = %s, 
                     collections = %s, 
                     makes = %s, 
                     likes = %s, 
                     skill_level = %s
                 WHERE user_id = %s"""
USER_TITLES = """SELECT t.title
                 FROM user_title AS ut
                 JOIN titles AS t ON t.title_id = ut.title_id
                 WHERE user_id = %s;"""

# titles table queries
SELECT_TITLE_ID = "SELECT title_id FROM titles WHERE title = (%s);"
INSERT_TITLE = "INSERT INTO titles (title) VALUES (%s);"

# user_title table queries
INSERT_TITLE_USER = "INSERT INTO user_title (title_id,user_id) VALUES (%s,%s);"
REMOVE_USER_TITLE = "DELETE FROM user_title WHERE title_id = %s AND user_id = %s;"

# print settings table queries
INSERT_PRINT_SETTINGS = """INSERT INTO print_settings (printer_brand,
                                                       printer_model,
                                                       rafts,
                                                       supports,
                                                       resolution,
                                                       infill,
                                                       filament_brand,
                                                       filament_color,
                                                       filament_material) 
                                  VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""

# things table queries
SELECT_THING_ID = "SELECT thing_id FROM things WHERE thigiverse_id = %s;"
INSERT_THING = """INSERT INTO things (thigiverse_id,
                                      user_id,
                                      model_name,
                                      uploaded,
                                      files,
                                      comments,
                                      makes,
                                      remixes,
                                      likes,
                                      setting_id,
                                      license,
                                      remix_id,
                                      thigiverse_remix,
                                      category) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s);"""

UPDATE_THING = """UPDATE things 
                 SET model_name = %s, 
                     files = %s, 
                     comments = %s, 
                     makes = %s, 
                     remixes = %s, 
                     likes = %s, 
                     license = %s,
                     category = %s
                 WHERE thing_id = %s"""


THING_TAGS = """SELECT t.tag
                FROM thing_tag AS tt
                JOIN tags AS t ON t.tag_id = tt.tag_id
                WHERE thing_id = %s;"""

# tags table queries
SELECT_TAG_ID = "SELECT tag_id FROM tags WHERE tag = (%s)"
INSERT_TAG = "INSERT INTO tags (tag) VALUES (%s);"

# thing tag table queries
INSERT_TAG_THING = "INSERT INTO thing_tag (tag_id, thing_id) VALUES (%s, %s)"
REMOVE_THING_TAG = "DELETE FROM thing_tag WHERE tag_id = %s AND thing_id = %s;"

# makes table queries
SELECT_MAKE_ID = "SELECT make_id FROM makes WHERE thigiverse_id= (%s)"
INSERT_MAKE = """INSERT INTO makes (thigiverse_id,
                                      thing_id,
                                      user_id,
                                      uploaded,
                                      comments,
                                      likes,
                                      views,
                                      category,
                                      setting_id) 
                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""
UPDATE_MAKE = """UPDATE makes 
                 SET comments = %s, 
                     likes = %s, 
                     views = %s, 
                     category = %s
                 WHERE make_id = %s"""