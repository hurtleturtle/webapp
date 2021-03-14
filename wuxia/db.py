import sqlite3
import click
from flask import current_app, g, flash
from flask.cli import with_appcontext
from os.path import dirname, basename
import os
from werkzeug.utils import secure_filename
from shutil import rmtree


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
        self.challenge_parent_folder = 'challenges'

    def make_admin(self, uid, admin_level=0):
        levels = {0: 'no', 1: 'read', 2: 'read-write'}
        query = 'UPDATE users SET admin = ? WHERE id = ?'
        params = (levels[admin_level], uid)
        self.execute(query, params)
        self.commit()

    def get_users(self, columns=('*',)):
        users = self.execute(select(columns, 'users')).fetchall()
        return users

    def get_user(self, uid=None, name=None, columns=('*',)):
        query = select(columns, 'users') + ' WHERE '
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

    def add_challenge(self, title, short_description, long_description, verification_file_name, verifiers,
                      expected_results, samples=None):
        query = 'INSERT INTO challenges (title, short_description, verifier_filename) VALUES (?, ?, ?)'
        params = (title, short_description, verification_file_name)
        cursor = self.execute(query, params)
        challenge_id = cursor.lastrowid
        
        self.add_challenge_description(challenge_id, long_description.splitlines())
        self.add_challenge_files(challenge_id, verifiers, expected_results, samples)
        self.commit()
        return challenge_id

    def add_challenge_description(self, challenge_id, description=(None,)):
        query = 'INSERT INTO challenge_descriptions (challenge_id, sequence_num, description) VALUES (?, ?, ?)'
        params = [(challenge_id, idx, paragraph) for idx, paragraph in enumerate(description)]
        self.executemany(query, params)

    def add_challenge_files(self, challenge_id, verifiers, expected_results, samples=None):
        query = 'INSERT INTO challenge_files (challenge_id, type, file_name) VALUES (?, ?, ?)'
        params = save_files(challenge_id, verifiers, 'verifier', self.challenge_parent_folder)
        params.extend(save_files(challenge_id, expected_results, 'result', self.challenge_parent_folder))
        if samples:
            params.extend(save_files(challenge_id, samples, 'sample', self.challenge_parent_folder))

        self.executemany(query, params)

    def add_challenge_file(self, new_file, challenge_id, file_type, file_name, user_id=None):
        # Check whether user code file already exists
        if user_id and self.get_challenge_files(challenge_id, user_id, ['user']):
            return save_files(challenge_id, [new_file], file_type, self.challenge_parent_folder, file_name)[0]
        else:
            query = 'INSERT INTO challenge_files (challenge_id, type, file_name' + ', user_id)' if user_id else ')'
            query += ' VALUES (?, ?, ?' + ', ?)' if user_id else ')'
            params = save_files(challenge_id, [new_file], file_type, self.challenge_parent_folder, file_name)[0]
            if user_id:
                params.append(user_id)
            self.execute(query, params)
            self.commit()

    def get_challenges(self, challenge_id=None, columns=('*',), order_by=None, descending=False):
        query = select(columns, 'challenges')
        params = []
        if challenge_id:
            query += ' WHERE id = ?'
            params.append(challenge_id)

        query += order_query(params, order_by, descending)
        return self.execute(query, params).fetchall()

    def get_challenge_description(self, challenge_id, columns=('*',), order_by=None, descending=False):
        query = select(columns, 'challenge_descriptions') + ' WHERE challenge_id = ?'
        params = [challenge_id]
        query += order_query(params, order_by, descending)
        return self.execute(query, params).fetchall()

    def get_challenge_files(self, challenge_id, user_id=None, file_types=None, columns=('*',)):
        query = select(columns, 'challenge_files') + ' WHERE challenge_id = ?'
        params = [challenge_id]

        if file_types:
            query += ' AND (' + ('type = ? OR' * len(file_types))[:-3] + ')'
            params.extend(file_types)
        if user_id:
            query += ' AND user_id = ?'
            params.append(user_id)

        return self.execute(query, params).fetchall()

    def get_challenge_file_paths(self, challenge_id, file_types=None, user_id=None):
        file_types = file_types if file_types else ['sample']
        files = self.get_challenge_files(challenge_id, user_id=user_id, file_types=file_types,
                                         columns=('type', 'file_name'))
        full_paths = []
        
        for f in files:
            path = get_file_path(challenge_id, f['type'], f['file_name'], self.challenge_parent_folder)
            full_paths.append(path)

        return full_paths

    def get_challenge_file_urls(self, challenge_id, file_types=None, url_prefix='/challenges/files'):
        files = self.get_challenge_file_paths(challenge_id, file_types)
        parent_folder = current_app.instance_path
        urls = [f.replace(parent_folder, url_prefix) for f in files]
        return urls

    def delete_challenge(self, challenge_id):
        query = 'DELETE FROM challenges WHERE id = ?'
        params = [challenge_id]
        self.execute(query, params)
        self.delete_challenge_files(challenge_id)
        self.delete_challenge_description(challenge_id)
        self.commit()
        flash(f'Deleted challenge {challenge_id} from database.')
        # Remove challenge files from file system
        try:
            challenge_id = int(challenge_id)
            challenge_folder = os.path.join(current_app.instance_path, self.challenge_parent_folder, str(challenge_id))
            rmtree(challenge_folder)
            flash(f'Deleted files for challenge {challenge_id}.')
        except ValueError:
            flash(f'Could not delete files for challenge {challenge_id}.')
        except FileNotFoundError:
            pass

    def delete_challenge_description(self, challenge_id, seq=None, commit=False):
        query = 'DELETE FROM challenge_descriptions WHERE challenge_id = ?'
        params = [challenge_id]
        if seq:
            query += ' AND sequence_num = ?'
            params.append(seq)

        self.execute(query, params)
        if commit:
            self.commit()

    def delete_challenge_files(self, challenge_id, file_types=None, user_id=None, commit=False):
        query = 'DELETE FROM challenge_files WHERE challenge_id = ?'
        params = [challenge_id]
        if file_types:
            query += ' AND (' + ('type = ? OR' * len(file_types))[:-3] + ')'
            params.extend(file_types)
        if user_id:
            query += ' AND user_id = ?'
            params.append(user_id)

        self.execute(query, params)
        if commit:
            self.commit()


def order_query(params, order, descending):
    if order:
        q = ' ORDER BY ? DESC' if descending else ' ORDER BY ?'
        params.append(order)
    else:
        q = ''
    
    return q


def select(columns, table):
    return 'SELECT ' + ', '.join(columns) + ' FROM ' + table


def save_files(challenge_id, files, file_purpose, parent_folder, file_name=None):
    params = []
    for f in files:
        if f.filename:
            file_name = file_name if file_name else f.filename
            path = get_file_path(challenge_id, file_purpose, file_name, parent_folder)
            f.save(path)
            params.append([challenge_id, file_purpose, basename(path)])
            file_name = None

    return params


def get_file_path(challenge_id, purpose, file_name, parent_folder):
    path = os.path.join(current_app.instance_path, parent_folder, str(challenge_id), purpose)
    path = make_folder(os.path.join(path, secure_filename(file_name)))
    return path


# TODO: build filename dynamically
def get_file_name(sub_path):
    instance_path = current_app.instance_path
    filename = secure_filename(basename(sub_path))
    sub_path = os.path.join(dirname(sub_path), filename)
    save_path = make_folder(os.path.join(instance_path, sub_path))
    return save_path


def make_folder(path):
    try:
        os.makedirs(dirname(path))
    except OSError:
        pass
    return path


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
