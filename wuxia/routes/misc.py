from flask import Blueprint, request, render_template, render_template_string
from wuxia.routes.auth import admin_required, write_admin_required
from wuxia.forms import gen_form_item
from wuxia.db import get_db
from mysql.connector import Error as SQLError
from pandas import DataFrame

bp = Blueprint('misc', __name__, template_folder='templates/misc')


@bp.route('/cookies', methods=['GET'])
def cookies():
    allowed_cookie = {'pirate': 'shiver_me_timbers'}
    
    if allowed_cookie.items() <= dict(request.cookies).items():
        returned_cookies = request.cookies
    else:
        returned_cookies = {'naughty': 'cookie'}

    return render_template('cookies.html', cookies=returned_cookies)


@bp.route('/template-injection', methods=['GET', 'POST'])
@admin_required
def inject():
    if request.method == 'POST':
        template_injection = request.form['injection']
        result = render_template_string(template_injection)
        return render_template('injection.html', result=result)

    return render_template('injection.html')


@bp.route('/bots', methods=['GET'])
def bots():
    return render_template('bots.html')


@bp.route('/query', methods=['GET', 'POST'])
@write_admin_required
def query():
    groups = {
        'query': {
            'group_title': 'SQL Query',
            'query_string': gen_form_item('query', name='query', placeholder='Type SQL query here (no commits)', field_type='textarea')
        },
        'submit': {
            'btn-submit': gen_form_item('btn-submit', item_type='submit', value='Submit')
        }
    }

    if request.method == 'POST':
        query = request.form.get('query')
        db = get_db()
        result = ''

        try:
            db.execute(query)
            result = QueryResult(db.cursor.fetchall()).to_html()
        except SQLError as e:
            result = f'SQL error encountered:<br />{e}'
        
        return render_template('misc/query.html', form_groups=groups, result=result)

    return render_template('misc/query.html', form_groups=groups)


class QueryResult(DataFrame):
    def __bool__(self):
        return self.empty