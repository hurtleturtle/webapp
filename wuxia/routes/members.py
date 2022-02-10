from flask import Blueprint, request, render_template
from wuxia.routes.auth import admin_required, write_admin_required, test_access_required
from wuxia.forms import gen_form_item
from wuxia.db import get_db


bp = Blueprint('members', __name__, url_prefix='members', template_folder='routes/members')
