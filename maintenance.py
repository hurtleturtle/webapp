#!/usr/bin/env python3
import sqlite3
import pandas as pd
import sys
from argparse import ArgumentParser


class Database():
    def __init__(self, path='instance/wuxia.sqlite'):
        self.db = self.connect(path)
        self.execute = self.db.execute
        self.commit = self.db.commit

    def connect(self, path):
        db = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
        db.row_factory = sqlite3.Row
        return db

    def make_admin(self, uid, admin_level=0):
        levels = {0: 'no', 1: 'read', 2: 'read-write'}
        query = 'UPDATE user SET admin = ? WHERE id = ?'
        params = (levels[admin_level], uid)
        self.execute(query, params)
        self.commit()

    def get_users(self):
        users = self.execute('SELECT * FROM user').fetchall()
        if users:
            return pd.DataFrame(users, columns=users[0].keys())
        else:
            return pd.DataFrame()

    def get_user(self, uid=None, name=None):
        query = 'SELECT * FROM user WHERE '
        params = tuple()

        if uid:
            query += 'id = ?'
            params = (uid,)
        elif name:
            query += 'username = ?'
            params = (name,)

        return self.execute(query, params).fetchone()

    def set_story_access(self, uid, access=True):
        query = 'UPDATE user SET access_approved = ? WHERE id = ?'
        params = (int(access), uid)
        self.execute(query, params)
        self.commit()


def get_args():
    parser = ArgumentParser()
    parser.add_argument('-a', '--admin', type=int, default=None,
                        help='Give user specified with -u admin privileges: 0' +
                        ' - none, 1 - read-only, 2 - read-write')
    parser.add_argument('-l', '--list', action='store_true', help='List users')
    parser.add_argument('-u', '--username', help='Username of user to act on')
    parser.add_argument('-i', '--user-id', type=int, help='ID of user')
    parser.add_argument('--approve', action='store_true',
                        help='Approve story access')
    parser.add_argument('--remove', action='store_true',
                        help='Remove story access')

    return parser.parse_args()


if __name__ == '__main__':
    db = Database()
    args = get_args()
    user = db.get_user(uid=args.user_id, name=args.username)

    if args.admin is not None:
        if user:
            db.make_admin(user['id'], admin_level=args.admin)
        else:
            print('Invalid username and/or user ID')

    if args.approve:
        db.set_story_access(user['id'], True)
    if args.remove:
        db.set_story_access(user['id'], False)

    if args.list:
        print(db.get_users())
