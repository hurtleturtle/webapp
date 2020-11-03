from flask import Blueprint, flash, g, render_template, request, url_for
from flask import redirect, current_app
from werkzeug.utils import secure_filename
from wuxia.db import get_db
from wuxia.auth import approval_required
import os
from forms import gen_form_item


bp = Blueprint('story', __name__, url_prefix='/stories')
ALLOWED_EXTENSIONS = {'html', 'htm'}


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
                                       placeholder='Container CSS'),
            'heading': gen_form_item('heading',
                                     placeholder='Chapter heading CSS')
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
        if upload_file():
            pass
        else:
            return redirect(url_for(request.url))

    return render_template('story/add.html', form_groups=groups)


def allowed_file(filename):
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
        flash('No selected file')
        return False
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file.save(os.path.join(UPLOAD_FOLDER, filename))
        return True
