'''
api chasse
'''

from .models import (
    TPersonnes, TZoneCynegetiques, TZoneIndicatives,
    TLieuTirs, TLieuTirSynonymes, TSaisons, TSaisonDates,
    TAttributionMassifs, TTypeBracelets, TAttributions, TRealisationsChasse,
    VChasseBilan, 
)
from ..generic.definitions import GenericRouteDefinitions
from ..generic.repository import getlist
from flask import Blueprint, current_app, request
from utils_flask_sqla.response import json_resp
from utils_flask_sqla.generic import GenericQuery
from sqlalchemy import select, func
import json

config = current_app.config
DB = config['DB']


bp = Blueprint('chasse_api', __name__)
grd = GenericRouteDefinitions()

droits = { 'C': 4, 'R': 0, 'U': 4, 'D': 4 }

definitions = {
    'personne': {
        'model': TPersonnes,
        'droits': droits
    },
    'zone_cynegetique': {
        'model': TZoneCynegetiques,
        'droits': droits
    },
    'zone_cynegetique': {
        'model': TZoneCynegetiques,
        'droits': droits
    },
    'zone_indicative': {
        'model': TZoneIndicatives,
        'droits': droits
    },
    'lieu_tir': {
        'model': TLieuTirs,
        'droits': droits
    },
    'lieu_tir_synonyme': {
        'model': TLieuTirSynonymes,
        'droits': droits
    },
    'saison': {
        'model': TSaisons,
        'droits': droits
    },
    'saison_date': {
        'model': TSaisonDates,
        'droits': droits
    },
    'attribution_massif': {
        'model': TAttributionMassifs,
        'droits': droits
    },
    'type_bracelet': {
        'model': TTypeBracelets,
        'droits': droits
    },
    'attribution': {
        'model': TAttributions,
        'droits': droits
    },
    'realisation': {
        'model': TRealisationsChasse,
        'droits': droits
    },
}

grd.add_generic_routes('chasse', definitions)


@bp.route('results/bilan/<id_espece>/<id_zone_cynegetique>', methods=['GET'])
@json_resp
def chasse_bilan(id_espece, id_zone_cynegetique):
    '''
        route pour le bilan chasse
    '''

    res = (
        DB.session.query(VChasseBilan)
        .filter(VChasseBilan.id_espece==id_espece)
        .filter(VChasseBilan.id_zone_cynegetique==id_zone_cynegetique)
        .all()
    )

    out = {}
    for key in [
        'nb_affecte_min',
        'nb_affecte_max',
        'nb_realise',
        'nb_realise_avant_11',
    ]:
        out[key] = [ [r.nom_saison, getattr(r, key)] for r in res]

    for key in [
        'nom_espece',
        'nom_zone_cynegetique'
    ]:
        out[key] = getattr(res[0], key)

    return out

@bp.route('results/ice/<id_espece>/<id_zone_cynegetique>', methods=['GET'])
@json_resp
def api_result_ice(id_espece, id_zone_cynegetique):
    '''
        API ICE
    '''

    req = func.oeasc_chasse.fct_calcul_ice_mc(id_espece, id_zone_cynegetique)
    res = DB.engine.execute(req).first()[0]
    return res


@bp.route('results/custom/', methods=['GET'])
@json_resp
def api_result_custom():
    '''
        API CUSTOM
    '''

    # gestion paramètres
    args = {}
    params=['field_name', 'view']
    params_list = ['filters']

    for p in params:
        args[p] = request.args.get(p)

    for p in params_list:
        args[p] = getlist(request.args, 'filters')

    args['filters']={}

    req = func.oeasc_chasse.fct_custom_results_j(json.dumps(args))
    res = DB.engine.execute(req).first()[0]
    return res