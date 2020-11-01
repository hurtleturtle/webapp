from flask import Blueprint, flash, g, render_template, request, url_for
from flask import redirect
from werkzeug.exceptions import abort
from wuxia.db import get_db
from wuxia.auth import admin_required, approval_required


bp = Blueprint('story', __name__)


@bp.route('/stories')
@approval_required
def list():
    db = get_db()
    stories = db.execute(
        'SELECT * from story'
    ).fetchall()

    return render_template('story/list.html', stories=stories)
