from flask import Blueprint, render_template


bp = Blueprint('challenges', __name__, url_prefix='/challenges', template_folder='templates/challenges')
test_challenge = {
    'challenge_id': 1,
    'title': 'Test Challenge',
    'short_description': 'A naughty test challenge'
}


@bp.route('/', methods=['GET'])
def show_all():
    chals = [test_challenge, {'title': 'A New Problem', 'short_description': 'Who da boss?', 'challenge_id': 2},
             test_challenge, test_challenge, test_challenge, test_challenge, test_challenge, test_challenge]
    return render_template('list.html', challenges=chals)


@bp.route('/<int:challenge_id>', methods=['GET'])
def show_challenge(challenge_id):
    challenge = test_challenge
    return render_template('description.html', challenge=challenge)
