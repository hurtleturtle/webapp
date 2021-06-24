from flask import Blueprint, render_template, request, escape, flash, redirect, url_for, current_app
from flask import send_from_directory, g
from wuxia.routes.auth import write_admin_required, redirect_to_referrer
from wuxia.forms import gen_form_item
from wuxia.db import get_db
from wuxia.validation import Validator


bp = Blueprint('challenges', __name__, url_prefix='/challenges', template_folder='templates/challenges')


@bp.route('', methods=['GET'])
def show_all():
    db = get_db()
    challenges = db.get_challenges()
    return render_template('list.html', challenges=challenges)


@bp.route('/<int:challenge_id>', methods=['GET', 'POST'])
def show_challenge(challenge_id):
    db = get_db()
    challenge = db.get_challenges(challenge_id, columns=['title'])[0]
    description = db.get_challenge_description(challenge_id, ['description'], order_by='sequence_num')
    sample_files = db.get_challenge_file_urls(challenge_id, file_types=['sample'])
    groups = {
        'answer_files': {
            'group_title': 'Submit Files',
            'files': gen_form_item('answer_file', item_type='file', required=True),
            'submit': gen_form_item('btn-submit', item_type='submit', value='Submit')
        }
    }

    if request.method == 'POST':
        user_id, view = accept_answer(challenge_id)
        if not user_id:
            return view

        user_code = request.files['answer_file']
        db.add_challenge_file(user_code, challenge_id, 'user', str(user_id), user_id=user_id)
        # validator = Validator(challenge_id, user_id)
        # result, error = validator.validate()

        return render_template('description.html', challenge=challenge, description_paragraphs=description,
                               files=sample_files, form_groups=groups, form_enc='multipart/form-data',
                               user_result=result, user_error=error)

    # GET response
    return render_template('description.html', challenge=challenge, description_paragraphs=description,
                           files=sample_files, form_groups=groups, form_enc='multipart/form-data')


# TODO: handle approval requests
def accept_answer(challenge_id):
    error = ''
    view = None
    accept = True

    if not g.user:
        error = 'You must be logged in to submit answers'
        view = redirect_to_referrer()
    # elif not g.user['submission_approved']:
    #     error = 'Please request approval to submit answers. Hover over your username and hit the button.'
    #     view = redirect(url_for('challenges.show_challenge', challenge_id=challenge_id))
    else:
        accept = g.user['id']

    if error:
        flash(error)
        accept = False

    return accept, view


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
        verification_file_name = escape(form.get('verification_file_name'))
        samples = request.files.getlist('sample_files')
        verifiers = request.files.getlist('verification_files')
        results = request.files.getlist('results_files')
        db = get_db()
        challenge_id = db.add_challenge(title, short_description, long_description, verification_file_name, verifiers,
                                        results, samples)
        flash(f'Challenge: "{title}" added to database')
        return redirect(url_for('challenges.show_all'))

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
            'verification_file_name': gen_form_item('verification_file_name', placeholder='Verification File Name',
                                                    required=True),
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


@bp.route('/modify', methods=['GET'])
def modify():
    challenges, files, _ = get_challenge_data()

    return render_template('modify.html', challenges=challenges, sample_files=files['sample'],
                           result_files=files['result'], verification_files=files['verifier'])


@bp.route('/delete', methods=['GET'])
@write_admin_required
def delete():
    challenge_id = request.args.get('challenge_id')
    db = get_db()
    db.delete_challenge(challenge_id)
    return redirect(url_for('challenges.modify'))


@bp.route('/edit/<int:challenge_id>', methods=['GET'])
def edit(challenge_id):
    challenges, files, description = get_challenge_data(challenge_id=challenge_id, description=True)
    challenge = challenges[0]
    groups = {
        'details': {
            'group_title': 'Modify Challenge',
            'challenge_title': gen_form_item('title', placeholder='Title', value=challenge['title'], required=True),
            'challenge_short_description': gen_form_item('short_description', placeholder='Short Description',
                                                         value=challenge['short_description'], required=True),
            'challenge_description': gen_form_item('long_description', placeholder='Description', required=True,
                                                   field_class='challenge-long-description', field_type='textarea',
                                                   textarea_text=description[challenge_id]),
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
                                    value='Change')
        },
    }

    # TODO: Add POST handler

    return render_template('add.html', form_groups=groups, form_enc="multipart/form-data")


def get_challenge_data(challenge_id=None, file_types=('sample', 'result', 'verifier'), description=False):
    db = get_db()
    challenges = db.get_challenges() if not challenge_id else db.get_challenges(challenge_id)
    challenge_ids = [challenge['id'] for challenge in challenges]
    files = {}
    descriptions = {}

    def get_filenames(rows):
        return [row['file_name'] for row in rows]

    for file_type in file_types:
        files[file_type] = {}
        for cid in challenge_ids:
            files[file_type][cid] = get_filenames(db.get_challenge_files(cid, file_types=[file_type],
                                                                         columns=['file_name']))

    if description:
        for cid in challenge_ids:
            paragraphs = db.get_challenge_description(cid, columns=('description',), order_by='sequence_num')
            paras = [p['description'] for p in paragraphs]
            descriptions[cid] = '\n'.join(paras)

    return challenges, files, descriptions
