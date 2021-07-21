#!/usr/bin/env python3
import os
from argparse import ArgumentParser
import shlex
import pandas as pd
from getpass import getpass
from wuxia.routes.story import Story
from wuxia.db import Database


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
    parser.add_argument('-s', '--story', action='store_true', help='Generate lorem ipsum story')
    parser.add_argument('-c', '--chapters', type=int, default=5, help='Number of chapters to generate')
    parser.add_argument('-t', '--title', help='Story title')
    parser.add_argument('-e', '--execute-script', help='Execute SQL script')
    parser.add_argument('-x', '--experiment', action='store_true')
    parser.add_argument('-q', '--query', help='Execute custom query')
    parser.add_argument('--commit', action='store_true', help='Commit query changes to database')
    parser.add_argument('--db-user', default='webapp', help='Database user')
    parser.add_argument('--db-pass', help='Password to login to database')
    parser.add_argument('--db-host', help='IP address of database')
    parser.add_argument('--reset-password', action='store_true', help='Reset password for user')

    return parser.parse_args()


def get_database_details(host, user, password, config_path='instance/config.py'):
    if not all((host, user, password)):
        config = {}
        try:
            with open(config_path) as f:
                for line in f:
                    key, equals, value = shlex.split(line)
                    config[key] = value
            host = config.get('DATABASE_HOST') if not host else host
            user = config.get('DATABASE_USER') if not user else user
            password = config.get('DATABASE_PASS') if not password else password
        except OSError:
            print(f'Error reading database details from {config_path}. Please supply DB details.')
            exit()
    
    details = {
        'db_host': host,
        'db_user': user,
        'db_pass': password
    }
    return details


if __name__ == '__main__':
    args = get_args()
    db = Database(**get_database_details(args.db_host, args.db_user, args.db_pass))

    try:
        user = db.get_user(uid=args.user_id, name=args.username)
    except Exception:
        user = None

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
        users = db.get_users()
        try:
            print(pd.DataFrame(users, columns=users[0].keys()))
        except IndexError:
            print('No users')

    if args.story:
        s = Story(title=args.title, chapters=args.chapters, db=db)
        s.add_to_db()
        
    if args.execute_script:
        with open(args.execute_script) as f:
            db.executescript(f.read())
        print('Database updated.')
        
    if args.experiment:
        db.add_challenge('A new challenge', 'A very short test challenge', 'Nah\nbro', None,  None, None)

    if args.reset_password:
        if user:
            password = getpass(f'Enter new password for {user["username"]}: ')
            if password == getpass('Re-enter password to confirm change: '):
                db.change_password(user['id'], password)
        else:
            print('Please specify the user whose password you want to reset.')
        
    if args.query:
        cur = db.execute(args.query)
        results = cur.fetchall()
        try:
            df = pd.DataFrame(results, columns=results[0].keys())
            print(df)
        except IndexError:
            print('No results returned')
        if args.commit:
            db.commit()
