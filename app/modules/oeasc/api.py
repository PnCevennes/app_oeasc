# -*- coding: utf-8 -*
from flask import Blueprint, current_app
from app.modules.oeasc.nomenclature import nomenclature_oeasc
from .repository import get_db
from app.utils.utilssqlalchemy import json_resp

config = current_app.config
DB = config['DB']

bp = Blueprint('oeasc_api', __name__)


@bp.route('get_nomenclature_oeasc', methods=['GET'])
@json_resp
def get_nomenclature_oeasc():
    '''
        Retourne un dictionnaire contenant toutes les nomenclatures concernant l'oeasc

        Exemple:

        nomenclature = nomenclature_oeasc()
        for elem in nomenclature["OEASC_PEUPLEMENT_ESSENCE"]["values"]:
            print(elem.label_fr)
    '''

    return nomenclature_oeasc()


@bp.route('get_db/<type>/<key>/<val>', methods=['GET'])
@json_resp
def api_get_db(type, key, val):
    '''

    '''
    out = get_db(type, key, val)
    return out
