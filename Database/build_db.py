import sqlite3
import os
import contextlib


def main() :
    DB_FILENAME = 'thingiverse.db'

    sql_file = open("thingiverse.sql")
    sql_as_string = sql_file.read()

    with contextlib.closing(sqlite3.connect(DB_FILENAME)) as con :  # auto-closes
        with con :  # auto-commits
            cur = con.cursor()
            if not os.path.exists(DB_FILENAME) :
                cur.executescript(sql_as_string)

            cur.execute("USE thingiverse;")


if __name__ == '__main__' :
    main()
