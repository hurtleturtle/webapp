from flask import Blueprint, request, render_template, render_template_string
from wuxia.routes.auth import admin_required, write_admin_required, test_access_required
from wuxia.forms import gen_form_item
from wuxia.db import get_db
from urllib.parse import unquote_plus
from mysql.connector import Error as SQLError
from pandas import DataFrame
from bs4 import BeautifulSoup

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
@test_access_required
def inject():
    groups = {
        'injection': {
            'group_title': 'Jinja2 Template Injection',
            'injection_string': gen_form_item('injection', name='injection', placeholder='Type Jinja2 SSTI here.\n\n'
                                              "E.g. {{ ''.__class__.__mro__[1].__subclasses__()[216]('id', stdout=-1)"
                                              '.communicate()[0].decode() }}', field_type='textarea')
        },
        'submit': {
            'btn-submit': gen_form_item('btn-submit', item_type='submit', value='Submit')
        }
    }

    if request.method == 'POST':
        injection_string = request.form.get('injection')
        injection_template = render_template_string(injection_string).split('\n')
        result = {
            'sequence': True,
            'data': injection_template
        }
        
        return render_template('misc/query.html', form_groups=groups, result=injection_template)

    return render_template('misc/query.html', form_groups=groups)


@bp.route('/bots', methods=['GET'])
def bots():
    return render_template('bots.html')


@bp.route('/query', methods=['GET', 'POST'])
@test_access_required
def query():
    groups = {
        'query': {
            'group_title': 'SQL Query',
            'query_string': gen_form_item('query', name='query', placeholder='Type SQL query here\n\nE.g. SELECT * FROM stories', field_type='textarea')
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