from flask import Blueprint, flash, g, render_template, request, url_for
from flask import redirect, escape
from werkzeug.exceptions import abort
from werkzeug.security import check_password_hash, generate_password_hash
from wuxia.db import get_db
from wuxia.auth import admin_required
from wuxia.forms import gen_form_item, gen_options


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
    admin_levels = g.privilege_levels

    if request.method == 'POST':
        error = None
        username = escape(request.form['username'])
        admin = request.form['admin']
        access = escape(request.form['access'])
        db = get_db()
        username_new = (username != user['username'])
        username_exists = db.execute('SELECT id FROM user WHERE username = ?',
                                     (username,)).fetchone() is not None

        if username_new:
            if username_exists:
                error = 'Username exists'
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
            error += f'{admin}\nAdmin Status must be one of:'
            error += ' {}'.format(', '.join(admin_levels))

        db.execute(
            'UPDATE user SET access_approved = ? WHERE id = ?', (access, id)
        )

        if error:
            flash(error)
        else:
            db.commit()
            return redirect(url_for('users.list'))

    groups = generate_form_groups(user)
    return render_template('users/edit.html', form_groups=groups)

@bp.route('/<int:id>/change-password', methods=['GET', 'POST'])
def change_password(id):
    user = get_user(id)
    db = get_db()

    if not g.user or g.user['id'] != id:
        error = 'Could not change password for the specified user.'
        flash(error)
        return redirect(url_for('index'))

    if request.method == 'POST':
        error = None
        old_pass = escape(request.form['old_pass'])
        new_pass = escape(request.form['new_pass'])
        confirm_pass = escape(request.form['confirm_pass'])

        if new_pass != confirm_pass:
            error = 'Passwords do not match.'

        if not check_password_hash(user['password'], old_pass):
            error = 'Existing password incorrect.'

        if error:
            flash(error)
            return redirect(url_for('users.change_password', id=id))

        query = 'UPDATE user SET password = ? WHERE id = ?'
        params = (generate_password_hash(new_pass), id)
        db.execute(query, params)
        db.commit()

        flash('Password updated.')
        return redirect(url_for('index'))


    groups = gen_pass_groups(user)
    return render_template('users/edit.html', form_groups=groups)

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


def generate_form_groups(user):
    password_href = url_for('users.change_password', id=user['id'])
    delete_href = url_for('users.delete', id=user['id'])

    groups = {
        'user': {
            'group_title': 'Edit: {}'.format(user['username']),
            'username': gen_form_item('username', value=user['username'],
                                      required=True, label='Username'),
            'access': gen_form_item('access', label='Story Access',
                                    field_type='select',
                                    options=gen_options(['Yes', 'No'], [1, 0]),
                                    value=user['access_approved'],
                                    selected_option=user['access_approved']),
            'admin': gen_form_item('admin', required=True, label='Admin',
                                   field_type='select',
                                   options=gen_options(['None', 'Read Only',
                                                        'Read & Write'],
                                                       g.privilege_levels),
                                   value=user['admin'],
                                   selected_option=user['admin'])
        },
        'change_pass': {
            'button': gen_form_item('change_pass', field_type='link',
                                     href=password_href,
                                     value='Change Password')
        },
        'submit': {
            'button': gen_form_item('btn-submit', item_type='submit',
                                    value='Update', field_type='input')
        },
        'delete': {
            'button': gen_form_item('delete', field_class='danger',
                                    field_type='link', href=delete_href,
                                    value='Delete')
        }
    }
    return groups


def gen_pass_groups(user):
    groups = {
        'user': {
            'group_title': 'Change Password for {}'.format(user['username']),
            'old_pass': gen_form_item('old_pass', label='Old Password',
                                      item_type='password', required=True),
            'new_pass': gen_form_item('new_pass', label='New Password',
                                      item_type='password', required=True),
            'confirm_pass': gen_form_item('confirm_pass', label='Confirm ' +
                                          'Password', item_type='password',
                                          required=True)
        },
        'submit': {
            'button': gen_form_item('btn-submit', item_type='submit',
                                    value='Change', field_type='input')
        }
    }
    return groups
