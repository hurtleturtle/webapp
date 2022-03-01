from re import template
from flask import Blueprint, request, render_template, flash
from pandas import options
from wuxia.routes.auth import admin_required, login_required
from wuxia.forms import gen_form_item, gen_options
from wuxia.db import get_db, QueryResult, get_end_of_day
from datetime import datetime, time


bp = Blueprint('reports', __name__, url_prefix='/reports', template_folder='templates/reports')


@bp.route('/attendance')
@admin_required
def attendance():
    db = get_db()
    today = datetime.today()
    results = QueryResult(db.get_attendance('2022-02-01', get_end_of_day(today)))
    if results:
        results.sort_values(by='date', inplace=True)

    groups = {
        'report': {
            'group_title': 'Generate Report'
        },
        'submit': {
            'btn-submit': gen_form_item('btn-submit', item_type='submit', value='Submit')
        }
    }
            
    return render_template('attendance.html', result=results.to_html(index=False))