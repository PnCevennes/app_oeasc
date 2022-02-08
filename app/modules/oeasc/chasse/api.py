'''
api chasse
'''

from typing import KeysView
from unittest import result
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
from sqlalchemy import column, select, func, table, distinct
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

    columns = GenericTable('v_pre_bilan_pretty', 'oeasc_chasse', DB.engine).tableDef.columns

    id_espece = request.args.get('id_espece')
    ids_zone_indicative = getlist(request.args, 'ids_zone_indicative')
    ids_zone_cynegetique = getlist(request.args, 'ids_zone_cynegetique')

    suffix = (
        '_zi' if ids_zone_indicative
        else '_zc' if ids_zone_cynegetique
        else '_espece'
    )

    res_keys = [
        'nb_realisation{}'.format(suffix),
        'nb_realisation_avant_11{}'.format(suffix),
        'nb_attribution_min{}'.format(suffix),
        'nb_attribution_max{}'.format(suffix),
    ]

    name_keys = [
        'nom_espece',
        'nom_saison',
    ]

    # scope =
    # if ids_zone_indicative:
        # name_keys.append('nom_zone_indicative')
    # elif ids_zone_cynegetique:
        # name_keys.append('nom_zone_cynegetique')

    query_keys = res_keys + name_keys

    scope = (
        list(map(lambda k: func.sum(columns[k]), res_keys))
        + list(map(lambda k: columns[k], name_keys))
    )

    if ids_zone_indicative:
        scope.append(func.string_agg(distinct(columns['nom_zone_indicative']), ', '))
    elif ids_zone_cynegetique:
        scope.append(func.string_agg(distinct(columns['nom_zone_cynegetique']), ', '))


    res = (
        DB.session.query(*scope)
    )
    res = res.filter(columns['id_espece']==id_espece)

    if ids_zone_indicative:
        res = res.filter(columns['id_zone_indicative'].in_(ids_zone_indicative))
    elif ids_zone_cynegetique:
        res = res.filter(columns['id_zone_cynegetique'].in_(ids_zone_cynegetique))

    res = res.order_by(columns['nom_saison'])
    res = res.group_by(
        * (map(lambda k: columns[k], name_keys))
    )

    res = res.all()

    if not res:
        return None

    out = {}
    for index, key in enumerate(res_keys):
        out[key.replace(suffix, '')] = [
            [
                r[query_keys.index('nom_saison')],
                (
                    int(r[query_keys.index(key)]) if r[query_keys.index(key)] is not None
                    else 0
                )
            ]
            for r in res
        ]

    for key in name_keys:
        try:
            out[key] = res[0][query_keys.index(key)] if query_keys.index(key)  else None
        except ValueError:
            pass

    if ids_zone_indicative:
        out['nom_zone_indicative'] = res[0][-1]
    elif ids_zone_cynegetique:
        out['nom_zone_cynegetique'] = res[0][-1]

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
