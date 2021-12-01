from flask import Blueprint, jsonify, request
from wuxia.db import get_db
from wuxia.routes.misc import QueryResult
from mysql.connector import Error as SQLError


bp = Blueprint('api_testing', __name__, url_prefix='/api')


@bp.route('/query', methods=['POST'])
def query():
    request_query = request.get_json()
    db = get_db()
    result = {}

    try:
        db.execute(request_query['query'])
        result = QueryResult(db.cursor.fetchall()).to_json(), 200
    except SQLError as e:
        result = {
            'error': 'SQL error encountered',
            'detail': e
            }, 500
    except Exception as e:
        result = {
            'error': 'Application error',
            'detail': e
        }

    return result