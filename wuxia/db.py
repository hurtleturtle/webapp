import sqlite3
import click
from flask import current_app, g
from flask.cli import with_appcontext


def connect(path):
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


class Database:
    def __init__(self, path=None):
        path = path if path else current_app.config['DATABASE']
        self.db = connect(path)
        self.execute = self.db.execute
        self.commit = self.db.commit
        self.close = self.db.close
        self.executemany = self.db.executemany
        self.executescript = self.db.executescript

    def make_admin(self, uid, admin_level=0):
        levels = {0: 'no', 1: 'read', 2: 'read-write'}
        query = 'UPDATE users SET admin = ? WHERE id = ?'
        params = (levels[admin_level], uid)
        self.execute(query, params)
        self.commit()

    def get_users(self, columns=('*',)):
        users = self.execute('SELECT ' + ','.join(columns) + ' FROM users').fetchall()
        return users

    def get_user(self, uid=None, name=None, columns=('*',)):
        query = 'SELECT ' + ','.join(columns) + ' FROM users WHERE '
        params = tuple()

        if uid:
            query += 'id = ?'
            params = (uid,)
        elif name:
            query += 'username = ?'
            params = (name,)
        else:
            return params

        return self.execute(query, params).fetchone()

    def set_story_access(self, uid, access=True):
        query = 'UPDATE users SET access_approved = ? WHERE id = ?'
        params = (int(access), uid)
        self.execute(query, params)
        self.commit()


def get_db():
    if 'db' not in g:
        g.db = Database()

    return g.db


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


@click.command('init-db')
@with_appcontext
def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

    click.echo('Initialised the database.')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db)
