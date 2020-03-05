'''
    api fonctionalite utilisée dans l'OEASC
'''
from flask import Blueprint, current_app

from app.modules.oeasc.nomenclature import nomenclature_oeasc
from app.utils.utilssqlalchemy import json_resp

from .repository import get_db

config = current_app.config
DB = config['DB']

bp = Blueprint('oeasc_api', __name__)


@bp.route('get_nomenclature_oeasc', methods=['GET'])
@json_resp
def get_nomenclature_oeasc():
    '''
        Retourne un dictionnaire contenant toutes les nomenclatures concernant l'oeasc


    '''

    return nomenclature_oeasc()


@bp.route('get_db/<type_data>/<key>/<val>', methods=['GET'])
@json_resp
def api_get_db(type_data, key, val):
    '''
        pour recuperer des infos (par exemple email d'un utilisateurs)
        TODO remove
    '''
    out = get_db(type_data, key, val)
    return out
