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

# titles table queries
SELECT_TITLE_ID = "SELECT title_id FROM titles WHERE title = (%s);"
INSERT_TITLE = "INSERT INTO titles (title) VALUES (%s);"

# user_title table queries
INSERT_TITLE_USER = "INSERT INTO user_title (title_id,user_id) VALUES (%s,%s);"

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

# tags table queries
SELECT_TAG_ID = "SELECT tag_id FROM tags WHERE tag = (%s)"
INSERT_TAG = "INSERT INTO tags (tag) VALUES (%s);"

# thing tag table queries
INSERT_TAG_THING = "INSERT INTO thing_tag (tag_id, thing_id) VALUES (%s, %s)"

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