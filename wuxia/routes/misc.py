from flask import Blueprint, request, render_template, render_template_string, flash
from wuxia.routes.auth import admin_required, write_admin_required, test_access_required
from wuxia.forms import gen_form_item
from wuxia.db import get_db
from urllib.parse import unquote_plus
from mysql.connector import Error as SQLError
from pandas import DataFrame
from bs4 import BeautifulSoup

bp = Blueprint('misc', __name__, url_prefix='/testing', template_folder='templates/misc')


@bp.route('/cookies', methods=['GET'])
def cookies():
    test_cookies = {'test-cookie'}
    request_cookie_keys = dict(request.cookies).keys()
    
    if test_cookies <= request_cookie_keys:
        returned_cookies = request.cookies
    else:
        flash(f'The following cookies have expired:\n<p>{test_cookies - request_cookie_keys}</p>\nLogin again to reset.')
        returned_cookies = request.cookies

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
        return render_template('misc/query.html', form_groups=groups, result=injection_template)

    return render_template('misc/query.html', form_groups=groups, title='Template Injection')


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


@bp.route('/file-upload', methods=['GET', 'POST'])
@test_access_required
def upload_file():
    groups = {
        'file': {
            'group_title': 'File Upload',
            'file': gen_form_item('file', item_type='file')
        },
        'submit': {
            'btn-submit': gen_form_item('btn-submit', item_type='submit', value='Submit')
        }
    }

    if request.method == 'POST':
        uploaded_file = request.files.get('file')
        print(uploaded_file)
        if uploaded_file:
            flash(f'<b>{uploaded_file.filename}</b> successfully received by server')
        else:
            flash(f'File not received by server')

    return render_template('misc/query.html', form_groups=groups, form_enc='multipart/form-data', title='File Upload')


class QueryResult(DataFrame):
    def __bool__(self):
        return self.empty