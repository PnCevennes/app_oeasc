'''
    api user
'''
from flask import (
    Blueprint, request, redirect, current_app
)
from app.utils.utilssqlalchemy import json_resp
from .repository import (
    get_user_form_email,
    get_users
)
from ..user.utils import check_auth_redirect_login
from utils_flask_sqla.response import csv_resp


config = current_app.config

bp = Blueprint('user_api', __name__)


@bp.route('/logout', methods=['GET', 'POST'])
def logout():
    '''
        logout redefinition
    '''
    params = request.args
    if 'redirect' in params:
        resp = redirect(params['redirect'], code=302)
    else:
        resp = redirect("/", code=302)
    resp.delete_cookie('token')
    return resp


@bp.route('/get_user_from_email/<email>', methods=['GET'])
@json_resp
def api_get_user_from_mail(email):
    '''
        get user form email
    '''
    return get_user_form_email(email)


@bp.route('/export', methods=['GET'])
@check_auth_redirect_login(1)
@csv_resp
def api_export_user():
    '''
        export
    '''

    file_name = 'export_user_oeasc'
    separator = ';'

    data = get_users()

    print(data)

    columns = list(data[0].keys())

    return (file_name, data, columns, separator)
