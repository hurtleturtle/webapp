from flask import Blueprint, flash, g, render_template, request, url_for
from flask import redirect, escape
from werkzeug.security import check_password_hash, generate_password_hash
from wuxia.db import get_db
from wuxia.routes.auth import admin_required, write_admin_required, login_required
from wuxia.forms import gen_form_item, gen_options


bp = Blueprint('users', __name__, url_prefix='/users')


@bp.route('')
@admin_required
def show_all():
    db = get_db()
    users = db.get_users()
    return render_template('users/list.html', users=users)


@bp.route('/<int:uid>/edit', methods=['GET', 'POST'])
@admin_required
def edit(uid):
    db = get_db()
    user = db.get_user(uid)
    admin_levels = g.privilege_levels

    if request.method == 'POST' and g.user['admin'] == 'read-write':
        error = None
        username = escape(request.form['username'])
        admin = request.form['admin']
        access = escape(request.form['access'])
        is_coach = request.form['is_coach']
        username_new = (username != user['username'])
        username_exists = db.get_user(name=username) is not None

        if username_new:
            if username_exists:
                error = 'Username exists'
            else:
                db.update_user(uid, 'username', username)
        if admin in admin_levels:
            db.update_user(uid, 'admin', admin)
        if is_coach is not None:
            db.update_user(uid, 'is_coach', is_coach)
        else:
            error = error + '\n' if error else ''
            error += f'{admin}\nAdmin Status must be one of:'
            error += ' {}'.format(', '.join(admin_levels))

        if error:
            flash(error)
        else:
            db.update_user(uid, 'access_approved', access)
            return redirect(url_for('users.show_all'))
    elif request.method == 'POST' and g.user['admin'] != 'read-write':
        flash('Write access required')

    groups = generate_form_groups(user)
    return render_template('users/edit.html', form_groups=groups)


@bp.route('/<int:uid>/change-password', methods=['GET', 'POST'])
def change_password(uid):
    db = get_db()
    user = db.get_user(uid)

    if (not g.user or g.user['id'] != uid) and g.user['admin'] != 'read-write':
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

        if not check_password_hash(user['password'], old_pass) and \
        g.user['admin'] != 'read-write':
            error = 'Existing password incorrect.'

        if error:
            flash(error)
            return redirect(url_for('users.change_password', uid=uid))

        db.update_user(uid, 'password', generate_password_hash(new_pass))

        flash('Password updated.')
        return redirect(url_for('index'))

    groups = gen_pass_groups(user)
    return render_template('users/edit.html', form_groups=groups)


@bp.route('/<int:uid>/delete', methods=['GET', 'POST'])
@write_admin_required
def delete(uid):
    db = get_db()
    db.delete_user(uid)
    return redirect(url_for('users.show_all'))


@bp.route('/<int:uid>/allow', methods=['GET', 'POST'])
@write_admin_required
def allow(uid):
    db = get_db()
    db.update_user(uid, 'access_approved', True)
    return redirect(url_for('users.show_all'))


@bp.route('/<int:uid>/disallow', methods=['GET', 'POST'])
@write_admin_required
def disallow(uid):
    db = get_db()
    db.update_user(uid, 'access_approved', False)
    return redirect(url_for('users.show_all'))


@bp.route('/<int:uid>/challenge-permission')
@login_required
def request_challenge_permission(uid):
    referrer = request.args.get('next', url_for('challenges.show_all'))
    flash('Permission to submit answers to challenges requested.')
    return redirect(referrer)

@bp.route('/<int:uid>/clear-session')
@write_admin_required
def clear_session(uid):
    db = get_db()

def get_current_user_id(default_uid=-1):
    try:
        user = g.user['id']
    except RuntimeError:
        user = default_uid
    
    return user


def generate_form_groups(user):
    password_href = url_for('users.change_password', uid=user['id'])
    delete_href = url_for('users.delete', uid=user['id'])

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
                                   options=gen_options(g.privilege_levels,
                                                       g.privilege_levels),
                                   value=user['admin'],
                                   selected_option=user['admin']),
            'coach': gen_form_item('is_coach', label='Coach', field_type='select',
                                   options=gen_options(['No', 'Yes'], [0, 1]),
                                   selected_option=user['is_coach'])
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
                                      item_type='password', required=False),
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
