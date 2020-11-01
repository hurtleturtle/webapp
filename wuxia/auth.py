import functools
from flask import Blueprint, flash, g, render_template, request, session
from flask import url_for, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from wuxia.db import get_db


bp = Blueprint('auth', __name__, url_prefix='/auth')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'
        elif db.execute('SELECT id FROM user WHERE username = ?',
                        (username,)).fetchone() is not None:
            error = f'User {username} is already registered.'

        if error is None:
            db.execute('INSERT INTO user (username, password) VALUES (?, ?)',
                       (username, generate_password_hash(password)))
            db.commit()
            return login()

        flash(error)

    return render_template('auth/register.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute('SELECT * FROM user WHERE username = ?',
                          (username,)).fetchone()

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            db.execute(
                'UPDATE user SET last_access = CURRENT_TIMESTAMP WHERE id = ?',
                (user['id'],)
            )
            db.commit()
            return redirect(url_for('index'))

        flash(error)
    return render_template('auth/login.html')


@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute('SELECT * FROM user WHERE id = ?',
                                  (user_id,)).fetchone()


@bp.before_app_request
def load_admin_levels():
    g.privilege_levels = ['no', 'read', 'read-write']
    g.admin_levels = ['read', 'read-write']


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))

        return view(**kwargs)

    return wrapped_view


def approval_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        error = None

        if g.user is None:
            return redirect(url_for('auth.login'))
        if not g.user['access_approved']:
            error = 'You do not have access to this page. Please contact '
            error += 'support.'

        flash(error)
        return view(**kwargs)

    return wrapped_view


def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        if g.user['admin'] not in g.admin_levels:
            return redirect(url_for('blog.index'))

        return view(**kwargs)

    return wrapped_view
