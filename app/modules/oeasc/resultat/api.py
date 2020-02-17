'''
    api pour les resultats
'''

from flask import Blueprint, current_app
from utils_flask_sqla.response import json_resp
from utils_flask_sqla.generic import GenericQuery
from ..user.utils import check_auth_redirect_login

config = current_app.config
DB = config['DB']
bp = Blueprint('resultat_api', __name__)


@bp.route('get_view/<string:schema>/<string:view>', methods=['GET'])
@check_auth_redirect_login(1)
@json_resp
def get_view(schema, view):
    '''
        retourne la vue schema.view
        TODO args pour filtres etc...
    '''

    data = GenericQuery(DB, view, schema).as_dict()

    return data['items']
