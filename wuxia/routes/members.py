from flask import Blueprint, request, render_template, flash
from wuxia.routes.auth import admin_required, login_required
from wuxia.forms import gen_form_item
from wuxia.db import get_db, QueryResult


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


@bp.route('/reports', methods=['GET', 'POST'])
@admin_required
def reports():
    groups = {
        'report': {
            'group_title': 'Generate Report'
        },
        'submit': {
            'btn-submit': gen_form_item('btn-submit', item_type='submit', value='Submit')
        }
    }

    if request.method == 'POST':
        db = get_db()
        result = QueryResult(db.get_attendance('2022-02-14', '2022-02-20')).to_html(index=False)
        return render_template('report.html', form_groups=groups, result=result)
            
    return render_template('report.html', form_groups=groups)