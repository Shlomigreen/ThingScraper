CREATE DATABASE thingiverse;
USE thingiverse;

CREATE TABLE users(
    user_id         INTEGER PRIMARY KEY AUTO_INCREMENT,
    username        VARCHAR(50)     NOT NULL    UNIQUE,
    followers       INT             NOT NULL,
    following       INT             NOT NULL,
    designs         INT             NOT NULL,
    collections     INT             NOT NULL,
    makes           INT             NOT NULL,
    likes           INT             NOT NULL,
    skill_level     VARCHAR(15)
);

CREATE TABLE titles(
    title_id    INTEGER PRIMARY KEY AUTO_INCREMENT,
    title       VARCHAR(50)    NOT NULL  UNIQUE
);

CREATE TABLE user_title(
    title_id    INT             NOT NULL,
    user_id     INT             NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (user_id)     ON DELETE CASCADE,
    FOREIGN KEY (title_id) REFERENCES titles (title_id)     ON DELETE CASCADE
);

CREATE TABLE tags(
    tag_id      INTEGER PRIMARY KEY AUTO_INCREMENT,
    tag         VARCHAR(200)     NOT NULL        UNIQUE
);

CREATE TABLE print_settings(
    setting_id          INTEGER PRIMARY KEY AUTO_INCREMENT,
    printer_brand       VARCHAR(50),
    printer_model       VARCHAR(50),
    rafts               INT(1),
    supports            INT(1),
    resolution          VARCHAR(50),
    infill              VARCHAR(50),
    filament_brand      VARCHAR(50),
    filament_color      VARCHAR(50),
    filament_material   VARCHAR(50)
);

CREATE TABLE things(
    thing_id        INTEGER PRIMARY KEY AUTO_INCREMENT,
    thigiverse_id   INT             NOT NULL    UNIQUE,
    user_id         INT             ,
    model_name      VARCHAR(200)    NOT NULL,
    uploaded        TEXT            NOT NULL,
    files           INT             NOT NULL,
    comments        INT             NOT NULL,
    makes           INT             NOT NULL,
    remixes         INT             NOT NULL,
    likes           INT,
    setting_id      INT,
    license         VARCHAR(100)    NOT NULL,
    remix_id           INT,
    thigiverse_remix           INT,
    category        VARCHAR(50),
    FOREIGN KEY (user_id)  REFERENCES users (user_id)    ON DELETE CASCADE,
    FOREIGN KEY (setting_id)  REFERENCES print_settings (setting_id)    ON DELETE CASCADE,
    FOREIGN KEY (remix_id)  REFERENCES things (thing_id)    ON DELETE CASCADE
);

CREATE TABLE thing_tag(
    tag_id          INT             NOT NULL,
    thing_id        INT             NOT NULL,
    FOREIGN KEY (thing_id) REFERENCES things (thing_id)     ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags (tag_id)           ON DELETE CASCADE
);


CREATE TABLE makes(
    make_id         INTEGER PRIMARY KEY AUTO_INCREMENT,
    thigiverse_id   INT         NOT NULL       UNIQUE,
    thing_id        INT         NOT NULL,
    user_id         INT,
    uploaded        TEXT         NOT NULL,
    comments        INT,
    likes           INT,
    views           INT,
    category        VARCHAR(50),
    setting_id      INT,
    FOREIGN KEY (thing_id)  REFERENCES things (thing_id)    ON DELETE CASCADE,
    FOREIGN KEY (user_id)  REFERENCES users (user_id)    ON DELETE CASCADE,
    FOREIGN KEY (setting_id)  REFERENCES print_settings (setting_id)    ON DELETE CASCADE
);