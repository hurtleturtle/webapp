#!/usr/bin/env python3
import sqlite3
import pandas as pd
import sys


def get_db(path='instance/wuxia.sqlite'):
    db = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    db.row_factory = sqlite3.Row
    return db


def make_admin(db, id):
    query = 'UPDATE user SET admin = ? WHERE id = ?'
    params = ('read-write', id)
    db.execute(query, params)
    db.commit()


def get_users(db):
    users = db.execute('SELECT * FROM user').fetchall()
    if users:
        return pd.DataFrame(users, columns=users[0].keys())
    else:
        return pd.DataFrame()


if __name__ == '__main__':
    db = get_db()
    if len(sys.argv) == 2:
        make_admin(db, int(sys.argv[1]))
    else:
        make_admin(db, 1)

    print(get_users(db))
