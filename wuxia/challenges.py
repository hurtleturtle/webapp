from flask import Blueprint, render_template


bp = Blueprint('challenges', __name__, url_prefix='/challenges', template_folder='templates/challenges')


@bp.route('/', methods=['GET'])
def show_all():
    chals = [
        {
            'challenge_id': 1,
            'title': 'Test Challenge',
            'short_description': 'A naughty test challenge'
        }
    ]
    return render_template('list.html', challenges=chals)


@bp.route('/<int:challenge_id>', methods=['GET'])
def show_challenge(challenge_id):
    pass
