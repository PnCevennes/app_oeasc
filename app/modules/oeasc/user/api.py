'''
    api user
'''
from flask import (
    Blueprint, request, redirect, current_app
)
from app.utils.utilssqlalchemy import json_resp
from .repository import (
    get_user_form_email
)


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
