#!/usr/bin/env python3
import sqlite3
import pandas as pd
import lipsum
from bs4 import BeautifulSoup
from argparse import ArgumentParser
import os
from wuxia.story import add_story_to_db, add_chapters_to_db


def connect(path):
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    return conn


class Database:
    def __init__(self, path='instance/wuxia.sqlite'):
        self.db = connect(path)
        self.execute = self.db.execute
        self.commit = self.db.commit

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


class Story:
    def __init__(self, title, chapters=10, template_path=None):
        self.title = title
        self.chapters = chapters
        self.template_path = template_path if template_path else 'wuxia/templates/story/story.html'
        self.html = self.create_story()
        self.generate_chapters(self.chapters)
        self.filepath = self._save_story()

    def create_story(self):
        with open(self.template_path) as f:
            new_story = BeautifulSoup(f.read())

        new_story.title.string = self.title
        return new_story

    def _add_chapter(self, index, paragraphs=4):
        soup = self.html
        div = soup.new_tag('div')
        heading = soup.new_tag('h2')

        div['class'] = 'chapter'
        heading['class'] = 'chapter-heading'
        heading.string = 'Chapter ' + str(index)
        div.append(heading)

        for paragraph in range(paragraphs):
            p = soup.new_tag('p')
            p.text = lipsum.generate_paragraphs(1)
            div.append(p)

        soup.body.append(div)

    def _save_story(self, filepath=None):
        filepath = filepath if filepath else os.path.join('instance/stories', self.title.replace(' ', '_'))
        with open(filepath, 'w') as f:
            f.write(self.html.prettify())
        return filepath

    def generate_chapters(self, chapters):
        for chapter in range(1, chapters + 1):
            self._add_chapter(chapter)

    def add_to_db(self):
        """
        Add story and chapters to database
        :rtype: bool
        """
        wuxia_db = Database()
        story = add_story_to_db(wuxia_db)
        if not story:
            print('Story {} could not be added to database using {}.'.format(self.title, self.filepath))
            return False
        else:
            add_chapters_to_db(wuxia_db, self.filepath, story['id'], 'div.chapter', 'div.chapter > h2.chapter-heading')
            os.remove(self.filepath)
            return True



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
    parser.add_argument('-t', '--title', default=lipsum.generate_words(1), help='Story title')

    return parser.parse_args()


if __name__ == '__main__':
    db = Database()
    args = get_args()

    try:
        user = db.get_user(uid=args.user_id, name=args.username)
    except sqlite3.OperationalError:
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
        print(db.get_users())

    if args.story:
        s = Story(title=args.title, chapters=args.chapters)
        s.add_to_db()
