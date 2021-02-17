from flask import Blueprint, request, render_template


bp = Blueprint('misc', __name__)


@bp.route('/cookies', methods=['GET'])
def cookies():
    allowed_cookie = {'pirate': 'shiver_me_timbers'}
    
    if allowed_cookie.items() <= dict(request.cookies).items():
        returned_cookies = request.cookies
    else:
        returned_cookies = {'naughty': 'cookie'}

    return render_template('misc/cookies.html', cookies=returned_cookies)