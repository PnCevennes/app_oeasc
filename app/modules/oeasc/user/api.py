from flask import (
    Blueprint, render_template, request, session, url_for, redirect, current_app
)
from .utils import check_auth_redirect_login
from app.modules.oeasc.nomenclature import nomenclature_oeasc
from .repository import (
    get_liste_organismes_oeasc,
    get_users,
    get_user,
    get_user_form_email
)
from pypnusershub.db.models import User

from app.utils.utilssqlalchemy import json_resp


config = current_app.config

bp = Blueprint('user_api', __name__)

@bp.route('/get_user_from_email/<email>', methods=['GET'])
@json_resp
def api_get_user_from_mail(email):

    return get_user_form_email(email)
