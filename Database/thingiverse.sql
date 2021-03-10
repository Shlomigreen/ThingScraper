--DROP DATABASE IF EXISTS thingiverse;
--CREATE DATABASE IF NOT EXISTS thingiverse;
----
--USE thingiverse;
----
--SELECT 'CREATING DATABASE STRUCTURE' as 'INFO';
--
--DROP TABLE IF EXISTS things,
--                     users,
--                     makes,
--                     print_settings,
--                     tags,
--                     user_titles,
--                     titles,
--                     thing_tags;

CREATE TABLE users(
    user_id         INT             NOT NULL,
    username        VARCHAR(50)     NOT NULL,
    followers       INT             NOT NULL,
    following       INT             NOT NULL,
    designs         INT             NOT NULL,
    collections     INT             NOT NULL,
    makes           INT             NOT NULL,
    likes           INT             NOT NULL,
    skill_level     VARCHAR(10),
    PRIMARY KEY (user_id)
);

CREATE TABLE titles(
    title_id    INT             NOT NULL,
    title       VARCHAR(50),
    PRIMARY KEY (title_id)
);

CREATE TABLE user_title(
    title_id    INT             NOT NULL,
    user_id     INT             NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id)     ON DELETE CASCADE,
    FOREIGN KEY (title_id) REFERENCES titles (title_id)     ON DELETE CASCADE
);

CREATE TABLE tags(
    tag_id      INT             NOT NULL,
    tag         VARCHAR(20)     NOT NULL,
    PRIMARY KEY (tag_id)
);

CREATE TABLE print_settings(
    setting_id          INT             NOT NULL,
    printer_brand       VARCHAR(50),
    printer_model       VARCHAR(50),
    rafts               INT(1),
    supports            INT(1),
    resolution          VARCHAR(50),
    infill              VARCHAR(50),
    filament_brand      VARCHAR(50),
    filament_color      VARCHAR(50),
    filament_material   VARCHAR(50),
    PRIMARY KEY (setting_id)
);

CREATE TABLE things(
    thing_id        INT             NOT NULL,
    thigiverse_id   INT             NOT NULL,
    user_id         INT             NOT NULL,
    model_name      VARCHAR(200)    NOT NULL,
    uploaded        TEXT            NOT NULL,
    files           INT             NOT NULL,
    comments        INT             NOT NULL,
    makes           INT             NOT NULL,
    likes           INT,
    setting_id      INT,
    license         VARCHAR(100)    NOT NULL,
    remix           INT,
    category        VARCHAR(50),
    PRIMARY KEY (thing_id),
    FOREIGN KEY (user_id)  REFERENCES users (user_id)    ON DELETE CASCADE,
    FOREIGN KEY (setting_id)  REFERENCES print_settings (setting_id)    ON DELETE CASCADE,
    FOREIGN KEY (remix)  REFERENCES things (thing_id)    ON DELETE CASCADE
);

CREATE TABLE thing_tag(
    tag_id          INT             NOT NULL,
    thing_id        INT             NOT NULL,
    FOREIGN KEY (thing_id) REFERENCES things (thing_id)     ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (tag_id)           ON DELETE CASCADE
);


CREATE TABLE makes(
    make_id         INT         NOT NULL,
    thing_id        INT         NOT NULL,
    user_id         INT         NOT NULL,
    uploaded        INT         NOT NULL,
    comments        INT,
    likes           INT,
    views           INT,
    category        VARCHAR(50),
    setting_id      INT,
    PRIMARY KEY (make_id),
    FOREIGN KEY (thing_id)  REFERENCES things (thing_id)    ON DELETE CASCADE,
    FOREIGN KEY (user_id)  REFERENCES users (user_id)    ON DELETE CASCADE,
    FOREIGN KEY (setting_id)  REFERENCES print_settings (setting_id)    ON DELETE CASCADE
);