from flask import Blueprint, render_template, request, escape, flash, redirect, url_for, current_app
from flask import send_from_directory
from wuxia.auth import write_admin_required
from wuxia.forms import gen_form_item
from wuxia.db import get_db


bp = Blueprint('challenges', __name__, url_prefix='/challenges', template_folder='templates/challenges')


@bp.route('', methods=['GET'])
def show_all():
    db = get_db()
    challenges = db.get_challenges()
    return render_template('list.html', challenges=challenges)


@bp.route('/<int:challenge_id>', methods=['GET'])
def show_challenge(challenge_id):
    db = get_db()
    challenge = db.get_challenges(challenge_id, columns=['title'])[0]
    description = db.get_challenge_description(challenge_id, ['description'], order='sequence_num')
    sample_files = db.get_challenge_files(challenge_id, file_types=['sample'], columns=['file_name'])
    return render_template('description.html', challenge=challenge, description_paragraphs=description,
                           files=sample_files)


@bp.route('/files/<path:path>')
def serve_files(path):
    return send_from_directory(current_app.instance_path, path, as_attachment=True)


@bp.route('/add', methods=['GET', 'POST'])
@write_admin_required
def add():
    if request.method == 'POST':
        form = request.form
        title = escape(form.get('title'))
        short_description = escape(form.get('short_description'))
        long_description = escape(form.get('long_description'))
        samples = request.files.getlist('sample_files')
        verifiers = request.files.getlist('verification_files')
        results = request.files.getlist('results_files')
        db = get_db()
        db.add_challenge(title, short_description, long_description, verifiers, results, samples)
        flash(f'Challenge: "{title}" added to database')
        return redirect(url_for('challenges.add'))

    groups = {
        'details': {
            'group_title': 'Add New Challenge',
            'challenge_title': gen_form_item('title', placeholder='Title', required=True),
            'challenge_short_description': gen_form_item('short_description', placeholder='Short Description',
                                                         required=True),
            'challenge_description': gen_form_item('long_description', placeholder='Description', required=True,
                                                   field_class='challenge-long-description', field_type='textarea'),
        },
        'samples': {
            'group_title': 'Sample Files',
            'sample': gen_form_item('sample_files', item_type='file', multiple=True),
        },
        'verification': {
            'group_title': 'Verification Files',
            'verification': gen_form_item('verification_files', item_type='file', multiple=True)
        },
        'results': {
            'group_title': 'Results Files',
            'results': gen_form_item('results_files', item_type='file', multiple=True)
        },
        'submit': {
            'button': gen_form_item('btn-submit', item_type='submit',
                                    value='Add')
        },
    }
    
    return render_template('add.html', form_groups=groups, form_enc="multipart/form-data")
