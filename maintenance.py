#!/usr/bin/env python3
import os
import sqlite3
from argparse import ArgumentParser
import lipsum
from bs4 import BeautifulSoup
from wuxia.db import Database
from wuxia.story import add_story_to_db, add_chapters_to_db
import pandas as pd


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
            new_story = BeautifulSoup(f.read(), features='lxml')

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
            p.string = lipsum.generate_paragraphs(1)
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
        story = add_story_to_db(wuxia_db, title=self.title, author=lipsum.generate_words(1))
        if not story:
            print('Story {} could not be added to database using {}.'.format(self.title, self.filepath))
            return False
        else:
            add_chapters_to_db(wuxia_db, self.filepath, story['id'], 'div.chapter', 'div.chapter > h2.chapter-heading')
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
    parser.add_argument('-e', '--execute-script', help='Execute SQL script')
    parser.add_argument('-x', '--experiment', action='store_true')
    parser.add_argument('-q', '--query', help='Execute custom query')
    parser.add_argument('--commit', help='Commit query changes to database')

    return parser.parse_args()


if __name__ == '__main__':
    db = Database('instance/wuxia.sqlite')
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
        
    if args.execute_script:
        with open(args.execute_script) as f:
            db.executescript(f.read())
        print('Database updated.')
        
    if args.experiment:
        db.add_challenge('A new challenge', 'A very short test challenge', 'Nah\nbro', None, None)
        
    if args.query:
        cur = db.execute(args.query)
        results = cur.fetchall()
        df = pd.DataFrame(results, columns=results[0].keys())
        print(df)
        if args.commit:
            db.commit()
