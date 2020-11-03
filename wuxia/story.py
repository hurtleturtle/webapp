from flask import Blueprint, flash, g, render_template, request, url_for
from flask import redirect, current_app
from werkzeug.utils import secure_filename
from wuxia.db import get_db
from wuxia.auth import approval_required
from wuxia.forms import gen_form_item
import os


bp = Blueprint('story', __name__, url_prefix='/stories')


@bp.route('/')
@approval_required
def list():
    db = get_db()
    stories = db.execute(
        'SELECT * from story'
    ).fetchall()

    return render_template('story/list.html', stories=stories)


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
        if not upload_file():
            return render_template('story/add.html',
                                   form_groups=preserve_form_data(groups))
        if not add_story_to_db(db):
            return render_template('story/add.html',
                                   form_groups=preserve_form_data(groups))

    return render_template('story/add.html', form_groups=groups)


def allowed_file(filename):
    ALLOWED_EXTENSIONS = {'html', 'htm'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def upload_file():
    UPLOAD_FOLDER = os.path.join(current_app.instance_path, 'stories')
    try:
        os.makedirs(UPLOAD_FOLDER)
    except OSError:
        pass

    # check if the post request has the file part
    if 'file' not in request.files:
        flash('No file part')
        return False
    file = request.files['file']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
        flash('No file selected')
        return False
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return True


def add_story_to_db(db):
    title = request.form.get('title')
    author = request.form.get('author', 'Unknown')
    story_exists = db.execute(
        'SELECT id FROM story WHERE title = ? AND author = ?', (title, author)
    ).fetchone()

    if story_exists:
        flash('A story with that title by that author already exists')
        return False
    else:
        db.execute(
            'INSERT INTO story (title, author) VALUES (?, ?)', (title, author)
        )
        db.commit()
        return True


def preserve_form_data(groups):
    groups['details']['story_title']['value'] = request.form['title']
    groups['details']['author']['value'] = request.form['author']
    groups['attributes']['container']['value'] = request.form['container']
    groups['attributes']['heading']['value'] = request.form['heading']
    return groups
