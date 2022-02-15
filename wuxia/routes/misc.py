from flask import Blueprint, request, render_template, render_template_string, flash, current_app
from wuxia.routes.auth import admin_required, write_admin_required, test_access_required
from wuxia.forms import gen_form_item
from wuxia.db import get_db, QueryResult
from urllib.parse import unquote_plus
from mysql.connector import Error as SQLError
from pandas import DataFrame
from bs4 import BeautifulSoup
from lipsum import generate_paragraphs
import os


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
        result = {
                'sequence': True,
                'data': injection_template
        }
        groups['injection']['injection_string']['textarea_text'] = injection_string
        return render_template('misc/query.html', form_groups=groups, result=result)
            
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
            result = QueryResult(db.cursor.fetchall()).to_html(index=False)
            groups['query']['query_string']['textarea_text'] = query
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


@bp.route('/compression', methods=['GET'])
@test_access_required
def compress():
    large_text_file_name = 'large.txt'
    large_text_file_path = os.path.join(os.path.abspath(current_app.root_path), 'static', large_text_file_name)

    with open(large_text_file_path) as f:
        file_contents = f.read()

    return render_template('misc/compress.html', file_contents=file_contents)


@bp.route('/padding-oracle', methods=['GET', 'POST'])
def oracle():
    page_title = 'Padding Oracle Attack'
    groups = {
        'examples': {
            'group_title': 'Encrypted Text',
            1: gen_form_item('example1', label='Example 1', label_class='do-not-wrap', field_type='text', value='<p>0xba185629dec5816200bd7f35c532c9ec</p>'),
            2: gen_form_item('example2', label='Example 2', label_class='do-not-wrap',field_type='text', value=''),
            3: gen_form_item('example3', label='Example 3', label_class='do-not-wrap',field_type='text', value='')
        },
        'attack': {
            'group_title': 'Padding Oracle Attack',
            'attack_text': gen_form_item('attack', placeholder='Input padding oracle initialisation vector and ciphertext', field_type='textarea')
        },
        'submit': {
            'btn-submit': gen_form_item('btn-submit', item_type='submit', value='Submit')
        }
    }

    if request.method == 'POST':
        attack = request.form.get('attack')
        db = get_db()
        result = ''
       
        return render_template('misc/query.html', form_groups=groups, result=result, title=page_title)

    return render_template('misc/query.html', form_groups=groups, title=page_title)


class PaddingOracleAttack:
    def __init__(self, attack_string=''):
        self.attack_string = attack_string