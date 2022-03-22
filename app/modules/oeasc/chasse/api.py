'''
api chasse
'''

from .models import (
    TPersonnes, TZoneCynegetiques, TZoneIndicatives,
    TLieuTirs, TLieuTirSynonymes, TSaisons, TSaisonDates,
    TAttributionMassifs, TTypeBracelets, TAttributions, TRealisationsChasse,
)
from ..generic.definitions import GenericRouteDefinitions
from ..generic.repository import getlist
from flask import Blueprint, current_app, request
from utils_flask_sqla.response import json_resp, csv_resp
from utils_flask_sqla.generic import GenericQuery, GenericTable
from .repositories import (
    get_chasse_bilan,
    chasse_process_args,
    chasse_get_infos
)
from sqlalchemy import column, select, func, table, distinct, over
import json
import datetime

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



@bp.route('results/bilan', methods=['GET'])
@json_resp
def chasse_bilan():
    '''
        route pour le bilan chasse
    '''

    params = chasse_process_args()

    return get_chasse_bilan(params)

@bp.route('results/ice', methods=['GET'])
@json_resp
def api_result_ice():
    '''
        API ICE
    '''

    params = chasse_process_args()

    req = func.oeasc_chasse.fct_calcul_ice_mc(
        params['id_espece'],
        params['id_zone_indicative'],
        params['id_zone_cynegetique'],
        params['id_secteur']
    )
    res = DB.engine.execute(req).first()[0]
    return res

# @bp.route('results/realisation', methods=['GET'])
# @json_resp
# def api_result_realisation():
#     params = chasse_process_args()
#     columns = GenericTable('v_pre_bilan_pretty', 'oeasc_chasse', DB.engine).tableDef.columns


@bp.route('results/infos', methods=['GET'])
@json_resp
def api_chasse_result_info():
    '''
    '''
    return chasse_get_infos()

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


@bp.route('export/csv/', methods=['GET'])
@csv_resp
def api_result_export():
    '''
        API CUSTOM
    '''

    # gestion paramètres
    data_type = request.args.get('data_type')
    filters = getlist(request.args, 'filters')

    views = {
        'realisation': 'oeasc_chasse.v_export_realisation_csv'
    }

    view = views.get(data_type)
    schema_name = view.split('.')[0]
    table_name = view.split('.')[1]

    # view + filters
    results = (
        GenericQuery(DB, schemaName=schema_name, tableName=table_name, filters=filters, limit=1e6)
        .return_query()
    )
    data = results['items']
    file_name = 'export_{}_{}'.format(data_type, datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%s"))
    return (file_name, data, data[0].keys(), ";")
