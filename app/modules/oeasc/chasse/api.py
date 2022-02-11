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

    columns = GenericTable('v_pre_bilan_pretty', 'oeasc_chasse', DB.engine).tableDef.columns

    id_espece = request.args.get('id_espece')
    ids_zone_indicative = getlist(request.args, 'ids_zone_indicative')
    ids_zone_cynegetique = getlist(request.args, 'ids_zone_cynegetique')
    ids_secteur = getlist(request.args, 'ids_secteur')

    localisation = (
        'zone_indicative' if ids_zone_indicative
        else 'zone_cynegetique' if ids_zone_cynegetique
        else 'secteur' if ids_secteur
        else ""
    )

    localisation_id_key = 'id_{}'.format(localisation)
    localisation_name_key = 'nom_{}'.format(localisation or 'espece')

    localisation_keys = (
        ids_zone_indicative
        or ids_zone_cynegetique
        or ids_secteur
        or []
    )


    suffix = (
        '_zi' if ids_zone_indicative
        else '_zc' if ids_zone_cynegetique
        else '_secteur' if ids_secteur
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

    localisation_name_keys = (
        [localisation_name_key] if localisation_name_key
        else []
    )

    scope = (
        list(map(lambda k: (columns[k]), res_keys + name_keys + localisation_name_keys))
    )

    res = (
        DB.session.query(*scope)
        .filter(columns['id_espece']==id_espece)
    )

    if localisation:
        res = res.filter(columns[localisation_id_key].in_(localisation_keys))

    res = res.order_by(columns['nom_saison'])
    res = res.group_by(
        * (map(lambda k: columns[k], res_keys + name_keys + localisation_name_keys))
    )

    res = res.subquery()

    scope2 = (
        list(map(lambda k: func.sum(res.columns[k]), res_keys))
        + list(map(lambda k: res.columns[k], name_keys))
    )

    if localisation_name_key:
        scope2.append(func.string_agg(res.columns[localisation_name_key], ', '))

    res2 = (
        DB.session.query(*scope2)
        .group_by(
            * (map(lambda k: res.columns[k], name_keys))
        )
        .order_by( res.columns['nom_saison'])
    )

    res2 = res2.all()
    res  = res2

    if not res:
        return None

    out = {}
    query_keys = res_keys + name_keys
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
    elif ids_secteur:
        out['nom_secteur'] = res[0][-1]

    return out

@bp.route('results/ice', methods=['GET'])
@json_resp
def api_result_ice():
    '''
        API ICE
    '''

    id_espece = request.args.get('id_espece')
    ids_secteur = getlist(request.args, 'ids_secteur')
    ids_zone_cynegetique = getlist(request.args, 'ids_zone_cynegetique')
    ids_zone_indicative = getlist(request.args, 'ids_zone_indicative')

    ids_secteur = list(map(lambda x: int(x), ids_secteur))
    ids_zone_cynegetique = list(map(lambda x: int(x), ids_zone_cynegetique))
    ids_zone_indicative = list(map(lambda x: int(x), ids_zone_indicative))

    # priorisation ZI > ZC > Secteur
    if len(ids_zone_indicative) > 0:
        ids_secteur = ids_zone_cynegetique = []

    if len(ids_zone_cynegetique) > 0:
        ids_secteur = []


    req = func.oeasc_chasse.fct_calcul_ice_mc(id_espece, ids_zone_indicative, ids_zone_cynegetique, ids_secteur)
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
