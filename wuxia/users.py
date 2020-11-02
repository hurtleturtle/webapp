from flask import Blueprint, flash, g, render_template, request, url_for
from flask import redirect
from werkzeug.exceptions import abort
from wuxia.db import get_db
from wuxia.auth import admin_required


bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('/')
@admin_required
def list():
    db = get_db()
    users = db.execute(
        'SELECT * FROM user'
    ).fetchall()
    return render_template('users/list.html', users=users)


@bp.route('/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit(id):
    user = get_user(id)
    admin_levels = g.admin_levels

    if request.method == 'POST':
        error = None
        username = request.form['username']
        admin = request.form['admin']
        db = get_db()
        username_new = (username != user['username'])
        username_exists = db.execute('SELECT id FROM user WHERE username = ?',
                                     (username,)).fetchone() is not None

        if username_new:
            if username_exists:
                error = 'Username exists.'
            else:
                db.execute(
                    'UPDATE user SET username = ? WHERE id = ?',
                    (username, id)
                )
        if admin in admin_levels:
            db.execute(
                'UPDATE user SET admin = ? WHERE id = ?', (admin, id)
            )
        else:
            error = error + '\n' if error else ''
            error += 'Admin Status must be one of:'
            error += ' {}'.format(', '.join(admin_levels))

        if error:
            flash(error)
        else:
            db.commit()
            return redirect(url_for('users.list'))

    return render_template('users/edit.html', user=user)


@bp.route('/<int:id>/delete', methods=['GET', 'POST'])
@admin_required
def delete(id):
    db = get_db()
    db.execute('DELETE FROM user WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('users.list'))


@bp.route('/<int:id>/allow', methods=['GET', 'POST'])
@admin_required
def allow(id):
    db = get_db()
    db.execute('UPDATE user SET access_approved = true WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('users.list'))


@bp.route('/<int:id>/disallow', methods=['GET', 'POST'])
@admin_required
def disallow(id):
    db = get_db()
    db.execute('UPDATE user SET access_approved = false WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('users.list'))


def get_user(id):
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?', (id,)).fetchone()
    return user
