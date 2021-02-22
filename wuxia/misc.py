from flask import Blueprint, request, render_template, render_template_string
from wuxia.auth import admin_required


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

    return render_template('misc/injection.html')
