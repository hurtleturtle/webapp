from flask import Blueprint, render_template


bp = Blueprint('challenges', __name__, url_prefix='/challenges', template_folder='templates/challenges')


@bp.route('/', methods=['GET'])
def show():
    pass
