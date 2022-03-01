from re import template
from tracemalloc import start
from flask import Blueprint, request, render_template, flash
from pandas import options
from wuxia.routes.auth import admin_required, login_required
from wuxia.forms import gen_form_item, gen_options
from wuxia.db import get_db, QueryResult, get_end_of_day
from datetime import datetime, timedelta


bp = Blueprint('reports', __name__, url_prefix='/reports', template_folder='templates/reports')


@bp.route('/attendance/custom', methods=['GET', 'POST'])
@admin_required
def attendance_custom():
    groups = {
        'report': {
            'group_title': 'Generate Attendance Report'
        },
        'dates': {
            'start_picker': gen_form_item('start_date', label='Start Date', item_type='date', required=True),
            'end_picker': gen_form_item('end_date', label='End Date', item_type='date', required=True)
        },
        'submit': {
            'btn-submit': gen_form_item('btn-submit', item_type='submit', value='Submit')
        }
    }

    if request.method == 'POST':
        start_date = (request.form.get('start_date'))
        end_date = request.form.get('end_date')
        results = get_attendance(start_date, end_date)
        if results:
            return render_template('attendance.html', result=results.to_html(index=False), start_date=start_date,
                                   end_date=end_date)
            
    return render_template('attendance.html', form_groups=groups)


def get_attendance(start_date, end_date):
    if start_date == end_date:
        start_date = datetime.fromisoformat(start_date)
        end_date = (datetime.fromisoformat(end_date) + timedelta(days=1)).replace(hour=0, minute=0, second=0)

    db = get_db()
    results = QueryResult(db.get_attendance(start_date, end_date))
    
    if results:
        results.sort_values(by='date', inplace=True)
    else:
        flash('No classes were attended in that date range')
    
    return results
