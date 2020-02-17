'''
    api pour les resultats
'''

from flask import Blueprint, current_app, request
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


@bp.route('get_views', methods=['GET'])
@check_auth_redirect_login(1)
@json_resp
def get_views():
    '''
        retourne les vue specifiées en param json : ['schema.view1', 'schema.view2', ect...]
        TODO args pour filtres etc...
    '''

    views = request.args.getlist('view')
    print(views)



    data = {}

    for p in views:

        print(p)
        v = p.split('.')
        schema = v[0]
        view = v[1]
        data_view = GenericQuery(DB, view, schema).as_dict()['items']
        if not data.get(schema):
            data[schema] = {}
        data[schema][view] = data_view

    return data
