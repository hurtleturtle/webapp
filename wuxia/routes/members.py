from flask import Blueprint, request, render_template, flash
from pandas import options
from wuxia.routes.auth import admin_required, login_required
from wuxia.forms import gen_form_item, gen_options
from wuxia.db import get_db, QueryResult


bp = Blueprint('members', __name__, url_prefix='/members', template_folder='templates/members')


@bp.route('/check-in', methods=['GET'])
@login_required
def check_in_to_class():
    db = get_db()
    current_user = db.get_user()
    class_id = 1
    # TODO: Fetch available classes
    # TODO: Check in to class/offer options

    flash('Checked in!')

    return render_template('checkin.html')


@bp.route('/add-class', methods=['GET', 'POST'])
@admin_required
def add_class():
    groups = {
        'class': {
            'group_title': 'Add Class',
            'class_name': gen_form_item('class_name', label='Class Name'),
            'class_type': gen_form_item('class_type', label='Class Type', field_type='select',
                                        options=gen_options(('Gi', 'No Gi')), value='No Gi',
                                        selected_option='No Gi'),
            'class_coach': gen_form_item('class_coach', label='Coach', field_type='select',
                                         options=gen_options(('Kevin Webb', 'Thomas Grandjean'), values=(2, 3))),
            'class_day': gen_form_item('class_day', label='Day', field_type='select',
                                       options=gen_options(('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday',
                                                            'Saturday', 'Sunday'))),
            'class_time': gen_form_item('class_time', label='Time (24h)', item_type='time'),
            'class_duration': gen_form_item('class_duration', label='Duration', item_type='time', value="01:00")
        },
        'submit': {
            'btn_submit': gen_form_item('btn-submit', item_type='submit', value='Submit')
        }
    }

    if request.method == 'POST':
        db = get_db()
        form = request.form
        class_name = form.get('class_name')
        class_type = form.get('class_type')
        class_coach_id = form.get('class_coach')
        class_day = form.get('class_day')
        class_time = form.get('class_time')
        class_duration = form.get('class_duration')

        db.add_class(class_name, class_day, class_time, class_duration, class_coach_id, class_type)

        flash('Class added!')


    return render_template('add_class.html', form_groups=groups)


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