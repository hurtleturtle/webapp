from flask import Blueprint, flash, render_template, request, url_for
from flask import redirect, current_app, escape, g
from werkzeug.utils import secure_filename
from wuxia.db import get_db, Database
from wuxia.routes.auth import approval_required, write_admin_required
from wuxia.forms import gen_form_item
from wuxia.routes.chapters import get_soup, get_chapters, get_heading
import os
import lipsum
from random import randint
from bs4 import BeautifulSoup


bp = Blueprint('story', __name__, url_prefix='/stories')


class Story:
    def __init__(self, title=None, chapters=10, template_path=None, db=None):
        self.title = title if title else lipsum.generate_words(randint(2, 5)).capitalize().replace('?', '')
        self.chapters = chapters
        self.template_path = template_path if template_path else os.path.join(os.path.dirname(__file__), 'templates/story/story.html')
        self.db = db if db else Database()
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

        for _ in range(paragraphs):
            p = soup.new_tag('p')
            p.string = lipsum.generate_paragraphs(1)
            div.append(p)

        soup.body.append(div)

    def _save_story(self, filepath=None):
        filepath = filepath if filepath else os.path.join('instance/stories', self.title.replace(' ', '_'))

        try:
            os.makedirs(os.path.dirname(filepath))
        except OSError:
            pass

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
        wuxia_db = self.db
        story = add_story_to_db(wuxia_db, title=self.title, author=lipsum.generate_words(2).replace('?', ''))
        if not story:
            print('Story {} could not be added to database using {}.'.format(self.title, self.filepath))
            return False
        else:
            add_chapters_to_db(wuxia_db, self.filepath, story['id'], 'div.chapter', 'div.chapter > h2.chapter-heading')
            return True


@bp.route('')
@approval_required
def story_list():
    db = get_db()
    stories = db.get_stories()
    print(stories)
    return render_template('story/list.html', stories=stories)


@bp.route('/<int:story_id>')
@approval_required
def display(story_id):
    db = get_db()
    chapter_rows = db.get_chapters(story_id, columns=['chapter_content'])
    story = db.get_story(story_id, ['title'])['title']

    if not chapter_rows:
        flash('No chapters found for that story')
        return redirect(url_for('story.story_list'))

    return render_template('story/display.html', chapters=chapter_rows,
                           title=story)


@bp.route('/add', methods=['GET', 'POST'])
@approval_required
def add():
    db = get_db()
    groups = {
        'details': {
            'group_title': 'Details',
            'story_title': gen_form_item('title', placeholder='Title',
                                         required=True),
            'author': gen_form_item('author', placeholder='Author')
        },
        'attributes': {
            'group_title': 'Attributes',
            'container': gen_form_item('container',
                                       placeholder='Container CSS',
                                       autocomplete='on'),
            'heading': gen_form_item('heading',
                                     placeholder='Chapter heading CSS',
                                     autocomplete='on')
        },
        'upload': {
            'group_title': 'Location',
            'file': gen_form_item('file', placeholder='Story file',
                                  item_type='file')
        },
        'submit': {
            'button': gen_form_item('btn-submit', item_type='submit',
                                    value='Add')
        },
    }

    if request.method == 'POST':
        print(request)
        print(request.__dict__)
        filepath = upload_file()
        if not filepath:
            return render_template('story/add.html',
                                   form_groups=preserve_form_data(groups))

        story = add_story_to_db(db)
        if not story:
            return render_template('story/add.html',
                                   form_groups=preserve_form_data(groups))

        add_chapters_to_db(db, filepath, story['id'],
                           escape(request.form['container']),
                           escape(request.form['heading']))

    return render_template('story/add.html', form_groups=groups, form_enc='multipart/form-data')


@bp.route('/<int:story_id>/delete', methods=['GET', 'DELETE'])
@write_admin_required
def delete(story_id):
    db = get_db()
    db.delete_story(story_id)
    return redirect(url_for('story.story_list'))


def allowed_file(filename):
    allowed_extensions = {'html', 'htm'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions


def upload_file():
    upload_folder = os.path.join(current_app.instance_path, 'stories')
    try:
        os.makedirs(upload_folder)
    except OSError:
        pass

    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        print(request.files)
        return False
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No file selected')
        return False
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(upload_folder, filename)
        file.save(filepath)
        return filepath


def add_story_to_db(db, title=None, author=None):
    title = title if title else escape(request.form.get('title'))
    author = author if author else escape(request.form.get('author', 'Unknown'))
    story_exists = db.check_story(title, author)
    try:
        user = g.user['id']
    except RuntimeError:
        user = 1

    if story_exists:
        flash('A story with that title by that author already exists')
        return False
    else:
        db.add_story(title, author, user)
        return db.check_story(title, author)


def add_chapters_to_db(db, filepath, story_id, chapter_container,
                       heading_selector):
    soup = get_soup(filepath)
    chapters = get_chapters(soup, chapter_container)
    try:
        user = g.user['id']
    except RuntimeError:
        user = 1

    for idx, chapter in enumerate(chapters):
        heading = get_heading(chapter, heading_selector)
        if chapter.name == 'div':
            chapter = '\n'.join([str(child) for child in chapter.children])

        db.add_chapter(int(story_id), heading, str(chapter), idx + 1, user, False)
        
    db.commit()
    os.remove(filepath)


def preserve_form_data(groups):
    groups['details']['story_title']['value'] = escape(request.form['title'])
    groups['details']['author']['value'] = escape(request.form['author'])
    container = escape(request.form['container'])
    groups['attributes']['container']['value'] = container
    groups['attributes']['heading']['value'] = escape(request.form['heading'])
    return groups
