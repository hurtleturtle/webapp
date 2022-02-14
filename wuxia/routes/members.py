from flask import Blueprint, request, render_template, flash
from wuxia.routes.auth import admin_required, login_required
from wuxia.forms import gen_form_item
from wuxia.db import get_db


bp = Blueprint('members', __name__, url_prefix='/members', template_folder='templates/members')


@bp.route('/check-in', methods=['GET'])
@login_required
def check_in_to_class():
    db = get_db()
    current_user = db.get_user()
    class_id = 1
    query = 'INSERT INTO attendance (member_id, class_id) VALUES (%s, %s);'
    params = (current_user['id'], class_id)
    db.execute(query, params)
    db.commit()

    flash('Checked in!')

    return render_template('checkin.html')


@bp.route('/add-class', methods=['GET', 'POST'])
@admin_required
def add_class():
    return render_template('add_class.html')