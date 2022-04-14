from asyncore import file_dispatcher
from posixpath import normpath
import json
from utils_flask_sqla.generic import GenericTable
from flask import request, current_app
from ..generic.repository import getlist
from sqlalchemy import column, select, func, table, distinct, over
from ..commons.models import TEspeces, TSecteurs
from .models import TSaisons, TZoneCynegetiques, TZoneIndicatives

config = current_app.config
DB = config['DB']

def chasse_process_args():
    '''
        Traitement des arguments de requete
        communs à plusieurs routes
        bilan, ice, restitution etc..
    '''
    id_espece = request.args.get('id_espece')
    id_saison = request.args.get('id_saison')

    id_secteur = getlist(request.args, 'id_secteur')
    id_zone_cynegetique = getlist(request.args, 'id_zone_cynegetique')
    id_zone_indicative = getlist(request.args, 'id_zone_indicative')

    id_secteur = list(map(lambda x: int(x), id_secteur))
    id_zone_cynegetique = list(map(lambda x: int(x), id_zone_cynegetique))
    id_zone_indicative = list(map(lambda x: int(x), id_zone_indicative))

    # priorisation ZI > ZC > Secteur
    if len(id_zone_indicative) > 0:
        id_secteur = id_zone_cynegetique = []

    if len(id_zone_cynegetique) > 0:
        id_secteur = []

    return {
        'id_saison': id_saison,
        'id_espece': id_espece,
        'id_secteur': id_secteur,
        'id_zone_cynegetique': id_zone_cynegetique,
        'id_zone_indicative': id_zone_indicative,
    }

def get_attribution_result(params):

    columns = GenericTable('v_custom_result_attribution', 'oeasc_chasse', DB.engine).tableDef.columns

    query = (
        DB.session.query(
            func.count(columns.id_attribution),
            func.count(columns.id_attribution).filter(columns.id_realisation != None)
        )
    )

    for filter_key, filter_value in params.items():
        if not hasattr(columns, filter_key) or filter_value in [None, []]:
            continue
        print(filter_key, filter_value)
        if isinstance(filter_value, list):
            query = query.filter(getattr(columns, filter_key).in_(filter_value))
        else:
            query = query.filter(getattr(columns, filter_key) == (filter_value))

    res = query.one()

    return {
        "nb_realisation": res[1],
        "nb_attribution": res[0],
        "taux_realisation": 0 if not res[1]  else round(res[1]/res[0] * 100)
    }


def chasse_get_infos():
    args = chasse_process_args()
    nom_espece = DB.session.query(TEspeces.nom_espece).filter(TEspeces.id_espece == args['id_espece']).one()[0]

    zone_echelle = ''

    query_zones_echelle = (
        DB.session.query(TZoneIndicatives.nom_zone_indicative)
        .filter(TZoneIndicatives.id_zone_indicative.in_(args['id_zone_indicative']))
        if args['id_zone_indicative']
        else DB.session.query(TZoneCynegetiques.nom_zone_cynegetique)
        .filter(TZoneCynegetiques.id_zone_cynegetique.in_(args['id_zone_cynegetique']))
        if args['id_zone_cynegetique']
        else DB.session.query(TSecteurs.nom_secteur)
        .filter(TSecteurs.id_secteur.in_(args['id_secteur']))
        if args['id_secteur']
        else None
    )

    nom_zones_echelle = (
        ', '.join(
            map(
                lambda x: x[0],
                query_zones_echelle.all()
            )
        )
        if query_zones_echelle
        else ''
    )

    echelle = (
        f'Zone(s) indicative(s) : {nom_zones_echelle}' if args['id_zone_indicative']
        else f'Zone(s) Cynegetique(s) : {nom_zones_echelle}' if args['id_zone_indicative']
        else f'Secteur(s): {nom_zones_echelle}' if args['id_secteur']
        else 'Cœur'
    )

    # taux_realisation = get_chasse_bilan(args)['taux_realisation'][-1][1]

    nom_saison = DB.session.query(TSaisons.nom_saison).filter(TSaisons.id_saison == args['id_saison']).one()[0]
    last_5_id_saisons = list(map(
        lambda x: x[0],
        DB.session.query(TSaisons.id_saison)
        .filter(TSaisons.nom_saison <= nom_saison)
        .order_by(TSaisons.nom_saison.desc())
        .limit(5)
        .all()
    ))

    return {
        'nom_saison': nom_saison,
        'nom_espece': nom_espece,
        'echelle': echelle,
        'last_5_id_saison': last_5_id_saisons,
        'nom_saison': nom_saison,
        **get_attribution_result(args)
    }


def get_chasse_bilan(params):

    columns = GenericTable('v_pre_bilan_pretty', 'oeasc_chasse', DB.engine).tableDef.columns
    localisation = (
        'zone_indicative' if params['id_zone_indicative']
        else 'zone_cynegetique' if params['id_zone_cynegetique']
        else 'secteur' if params['id_secteur']
        else ""
    )

    localisation_id_key = 'id_{}'.format(localisation)
    localisation_name_key = 'nom_{}'.format(localisation or 'espece')

    localisation_keys = (
        params['id_zone_indicative']
        or params['id_zone_cynegetique']
        or params['id_secteur']
        or []
    )


    suffix = (
        '_zi' if params['id_zone_indicative']
        else '_zc' if params['id_zone_cynegetique']
        else '_secteur' if params['id_secteur']
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
        .filter(columns['id_espece']==params['id_espece'])
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
                    int(r[index]) if r[index] is not None
                    else 0
                )
            ]
            for r in res
        ]

    out['taux_realisation'] = [
        [
            out['nb_realisation'][i][0],
            (
                out['nb_realisation'][i][1] / out['nb_attribution_max'][i][1]
                if out['nb_attribution_max'][i][1] else 0
            )
        ]
        for i in range(len(out['nb_realisation']))
    ]

    for key in name_keys:
        try:
            out[key] = res[0][query_keys.index(key)] if query_keys.index(key)  else None
        except ValueError:
            pass

    if params['id_zone_indicative']:
        out['nom_zone_indicative'] = res[0][-1]
    elif params['id_zone_cynegetique']:
        out['nom_zone_cynegetique'] = res[0][-1]
    elif params['id_secteur']:
        out['nom_secteur'] = res[0][-1]

    return out


def get_data_export_ods(nom_saison, nom_espece):

    columns = GenericTable('v_pre_bilan_pretty', 'oeasc_chasse', DB.engine).tableDef.columns

    query = (
        DB.session.query(
            *[c for c in columns]
        )
        .filter(columns.nom_saison==nom_saison)
        .filter(columns.nom_espece==nom_espece)
        .order_by(
            columns.nom_zone_cynegetique,
            columns.nom_zone_indicative,
        )
    )

    res = [
        {
            (str(col.key)): getattr(r, str(col.key))
            for col in columns
        }
        for r in query.all()
    ]

    zcs = []

    for r in res:

        zc = next((item for item in zcs if item["nom"] == r['nom_zone_cynegetique']), None)
        if not zc:
            zc = {
                    'nom': r['nom_zone_cynegetique'],
                    'mini': r['nb_attribution_max_zc'],
                    'maxi': r['nb_attribution_min_zc'],
                    'realisation': int(r['nb_realisation_zc']),
                    'pourcent': round(r['nb_realisation_zc']/r['nb_attribution_max_zc']*100),
                    'zis': []
                }
            zcs.append(zc)
        zc['zis'].append({
            'nom': r['nom_zone_indicative'],
            'mini': r['nb_attribution_max_zi'],
            'maxi': r['nb_attribution_min_zi'],
            'realisation': int(r['nb_realisation_zi']),
            'pourcent': round(r['nb_realisation_zi']/r['nb_attribution_max_zi']*100),
        })





    data = {
        'nom_saison': nom_saison,
        'nom_espece': nom_espece,
        'zcs': zcs
    }

    return data

def get_data_all_especes_export_ods(nom_saison):
    data = {
        'nom_saison': nom_saison,
        'especes': []
    }
    for nom_espece in ['Cerf', 'Chevreuil', 'Mouflon']:
        data['especes'].append(get_data_export_ods(nom_saison, nom_espece))

    return data