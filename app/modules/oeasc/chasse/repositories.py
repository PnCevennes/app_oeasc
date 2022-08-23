from asyncore import file_dispatcher
from posixpath import normpath
import json
from psycopg2 import paramstyle
from utils_flask_sqla.generic import GenericTable
from flask import request, current_app
from ..generic.repository import getlist
from ..resultat.repository import result_custom
from sqlalchemy import column, select, func, table, distinct, over, cast
from ..commons.models import TEspeces, TSecteurs
from .models import TSaisons, TZoneCynegetiques, TZoneIndicatives, TAttributionMassifs, VPlanChasseRealisationBilan

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
    poids_ou_dagues = request.args.get('poids_ou_dagues')

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
        'poids_ou_dagues': poids_ou_dagues
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


def build_chasse_bilan_filters(params, query, tableModel):

    # filter query
    if params['id_zone_indicative']:
        query = query.filter(
            tableModel.id_zone_indicative.in_(params['id_zone_indicative'])
        )
    elif params['id_zone_cynegetique']:
        query = query.filter(tableModel.id_zone_cynegetique.in_(params['id_zone_cynegetique']))
    elif params['id_secteur']:
        query = query.join(
            TZoneCynegetiques, TZoneCynegetiques.id_zone_cynegetique == TAttributionMassifs.id_zone_cynegetique
        ).filter(
            TZoneCynegetiques.id_secteur.in_(params['id_secteur'])
        )
    if params['id_espece']:
        query = query.filter(tableModel.id_espece == params['id_espece'])

    return query

def get_chasse_bilan_realisation(params):
    # Fonction de représentation de la réalisation des plans de chasse
    # Pb dans les données, les données historiques sont aggrégés à la zi pour la réalisation et à la zc pour les attributions
    # D'où le fait d'utiliser 2 requêtes différentes en fonction du filtre demandé

    if params['id_zone_indicative']:
        query = DB.session.query(
            TSaisons.nom_saison,
            VPlanChasseRealisationBilan.id_espece,
            func.sum(VPlanChasseRealisationBilan.nb_affecte_min).label("nb_attribution_min"),
            func.sum(VPlanChasseRealisationBilan.nb_affecte_max).label("nb_attribution_max"),
            func.sum(VPlanChasseRealisationBilan.nb_realisation).label("nb_realisation"),
            func.sum(VPlanChasseRealisationBilan.nb_realisation_avant_11).label("nb_realisation_avant_11")
        )
        query = query.join(VPlanChasseRealisationBilan,
                    TSaisons.id_saison == VPlanChasseRealisationBilan.id_saison)
        query = build_chasse_bilan_filters(params, query, VPlanChasseRealisationBilan)
        # group by
        query = query.group_by(VPlanChasseRealisationBilan.id_espece, TSaisons.nom_saison)

    else:
        realisation = DB.session.query(
            VPlanChasseRealisationBilan.id_espece,
            VPlanChasseRealisationBilan.id_saison,
            func.sum(VPlanChasseRealisationBilan.nb_realisation).label("nb_realisation"),
            func.sum(VPlanChasseRealisationBilan.nb_realisation_avant_11).label("nb_realisation_avant_11")
        )
        realisation =  build_chasse_bilan_filters(params, realisation, VPlanChasseRealisationBilan)
        realisation = realisation.group_by(
            VPlanChasseRealisationBilan.id_espece, VPlanChasseRealisationBilan.id_saison
        ).subquery()

        attribution = DB.session.query(
            TAttributionMassifs.id_espece,
            TAttributionMassifs.id_saison,
            func.sum(TAttributionMassifs.nb_affecte_min).label("nb_attribution_min"),
            func.sum(TAttributionMassifs.nb_affecte_max).label("nb_attribution_max"),
        )
        attribution =  build_chasse_bilan_filters(params, attribution, TAttributionMassifs)
        attribution = attribution.group_by(
            TAttributionMassifs.id_espece, TAttributionMassifs.id_saison
        ).subquery()


        query = DB.session.query(
            TSaisons.nom_saison,
            attribution.c.id_espece,
            attribution.c.nb_attribution_min,
            attribution.c.nb_attribution_max,
            realisation.c.nb_realisation,
            realisation.c.nb_realisation_avant_11
        ).join(
            realisation,  TSaisons.id_saison == realisation.c.id_saison
        ).join(
            attribution,  attribution.c.id_saison == realisation.c.id_saison
        )
    query = query.order_by(TSaisons.nom_saison)

    return query

def get_plain_text_data(params):
    # Espèces
    out = {}
    print(params)
    if 'id_espece' in params:
        res = TEspeces.query.get(params['id_espece'])
        out['nom_espece'] = res.nom_espece
    # Saison
    if 'id_saison' in params:
        res = TSaisons.query.get(params['id_saison'])
        if res:
            out['nom_saison'] = res.nom_saison
    # Nom zone
    zones = None
    if params['id_zone_indicative']:
        zones = TZoneIndicatives.query.filter(TZoneIndicatives.id_zone_indicative.in_(params['id_zone_indicative']))
        column_name = 'nom_zone_indicative'
    elif params['id_zone_cynegetique']:
        zones = TZoneCynegetiques.query.filter(TZoneCynegetiques.id_zone_cynegetique.in_(params['id_zone_cynegetique']))
        column_name = 'nom_zone_cynegetique'
    elif params['id_secteur']:
        zones = TSecteurs.query.filter(TSecteurs.id_secteur.in_(params['id_secteur']))
        column_name = 'nom_secteur'

    if zones:
        out[column_name] = ', '.join([getattr( z, column_name) for z in zones])

    return out


def get_chasse_bilan(params):

    query = get_chasse_bilan_realisation(params)
    res = query.all()
    # 0: nom_saison
    # 1: id_espece
    # 2: nb_affecte_min
    # 3: nb_affecte_max
    # 4: nb_realisation
    # 5: nb_realisation_avant_11
    columns_index = {
        "nom_saison" : 0,
        "id_espece" : 1,
        "nb_realisation" : 4,
        "nb_realisation_avant_11" : 5,
        "nb_attribution_min" : 2,
        "nb_attribution_max" : 3
    }
    out = {}
    # Fonction permettant de formater les données pour highcharts
    # traitement des colones contenus dans res_keys
    #   "nb_realisation": [["2001-2002", 809], ["2002-2003", 702], ["2003-2004", 595], [...]],
    #   "nb_realisation_avant_11": [["2010-2011", 0], [...]],
    #   "nb_attribution_min": [["2010-2011", 0], [...]],
    #   "nb_attribution_max": [["2010-2011", 0], [...]]
    for key in ["nb_attribution_min", "nb_attribution_max", "nb_realisation", "nb_realisation_avant_11"]:
        index_nom_saison = columns_index["nom_saison"]
        index_col = columns_index[key]
        print(key, index_col)
        out[key] = [
            [
                r[index_nom_saison],
                (
                    int(r[index_col]) if r[index_col] is not None
                    else 0
                )
            ]
            for r in res
        ]
    # Calcul du taux de réalisation
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

    # Récupération des données d'affichage des paramètres
    # TSaisons, TZoneIndicatives, TZoneCynegetiques
    context_data = get_plain_text_data(params=params)
    return {**out, **context_data}



def get_details(nom_saison, nom_espece, filter= {}):
    out = {}

    res_details = {}

    for field_name in [
        'label_sexe',
        'mois_txt',
        'label_classe_age',
        'label_mode_chasse',
        'bracelet'
    ]:
        res_details[field_name] = result_custom({
            'view': 'oeasc_chasse.v_custom_results',
            'field_name': field_name,
            'filters': {
                "nom_saison": [nom_saison],
                "nom_espece": [nom_espece],
                **filter
            }
        })

    res_details['bracelet_attr'] = result_custom({
        'view': 'oeasc_chasse.v_custom_result_attribution',
        'field_name': field_name,
        'filters': {
            "nom_saison": [nom_saison],
            "nom_espece": [nom_espece],
            **filter
        }
    })


    out['nb_sexe_male'] = next((elem['count'] for elem in res_details['label_sexe'] if elem['text'] == 'Mâle'), 0) or ""
    out['nb_sexe_femelle'] = next((elem['count'] for elem in res_details['label_sexe'] if elem['text'] == 'Femelle'), 0) or ""
    out['nb_sexe_ind'] = next((elem['count'] for elem in res_details['label_sexe'] if elem['text'] == 'Indéterminé'), 0) or ""
    out['nb_mois_sep'] = next((elem['count'] for elem in res_details['mois_txt'] if elem['text'] == 'Sep.'), 0) or ""
    out['nb_mois_oct'] = next((elem['count'] for elem in res_details['mois_txt'] if elem['text'] == 'Oct.'), 0) or ""
    out['nb_mois_nov'] = next((elem['count'] for elem in res_details['mois_txt'] if elem['text'] == 'Nov.'), 0) or ""
    out['nb_mois_dec'] = next((elem['count'] for elem in res_details['mois_txt'] if elem['text'] == 'Déc.'), 0) or ""
    out['nb_mois_jan'] = next((elem['count'] for elem in res_details['mois_txt'] if elem['text'] == 'Jan.'), 0) or ""
    out['nb_mois_fev'] = next((elem['count'] for elem in res_details['mois_txt'] if elem['text'] == 'Fév.'), 0) or ""
    out['nb_age_ad'] = next((elem['count'] for elem in res_details['label_classe_age'] if elem['text'] == 'Adulte'), 0) or ""
    out['nb_age_ind'] = next((elem['count'] for elem in res_details['label_classe_age'] if elem['text'] == 'Indéterminé'), 0) or ""
    out['nb_age_suba'] = next((elem['count'] for elem in res_details['label_classe_age'] if elem['text'] == 'Sub-adulte'), 0) or ""
    out['nb_age_juv'] = next((elem['count'] for elem in res_details['label_classe_age'] if elem['text'] == 'Juvénile'), 0) or ""
    out['nb_mode_chasse_app'] = next((elem['count'] for elem in res_details['label_mode_chasse'] if elem['text'] == 'Approche'), 0) or ""
    out['nb_mode_chasse_aff'] = next((elem['count'] for elem in res_details['label_mode_chasse'] if elem['text'] == 'Affut'), 0) or ""
    out['nb_mode_chasse_ind'] = next((elem['count'] for elem in res_details['label_mode_chasse'] if elem['text'] == 'Indéterminé'), 0) or ""
    out['nb_mode_chasse_bat'] = next((elem['count'] for elem in res_details['label_mode_chasse'] if elem['text'] == 'Battue'), 0) or ""
    out['nb_real_cem'] = next((elem['count'] for elem in res_details['bracelet'] if elem['text'] == 'CEM'), 0) or ""
    out['nb_real_ceff'] = next((elem['count'] for elem in res_details['bracelet'] if elem['text'] == 'CEFF'), 0) or ""
    out['nb_real_ceffd'] = next((elem['count'] for elem in res_details['bracelet'] if elem['text'] == 'CEFFD'), 0) or ""
    out['nb_attr_cem'] = next((elem['count'] for elem in res_details['bracelet_attr'] if elem['text'] == 'CEM'), 0) or ""
    out['nb_attr_ceff'] = next((elem['count'] for elem in res_details['bracelet_attr'] if elem['text'] == 'CEFF'), 0) or ""
    out['nb_attr_ceffd'] = next((elem['count'] for elem in res_details['bracelet_attr'] if elem['text'] == 'CEFFD'), 0) or ""
    out['pourcent_cem'] = round(1.0 * out['nb_real_cem'] / out['nb_attr_cem'] * 100) if out['nb_real_cem'] else ''
    out['pourcent_ceff'] = round(1.0 * out['nb_real_ceff'] / out['nb_attr_ceff'] * 100) if out['nb_real_ceff'] else ''
    out['pourcent_ceffd'] = round(1.0 * out['nb_real_ceffd'] / out['nb_attr_ceffd'] * 100) if out['nb_real_ceffd'] else ''
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
            cast(columns.code_zone_indicative, DB.Integer),
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
                    'mini': r['nb_attribution_min_zc'] or '',
                    'maxi': r['nb_attribution_max_zc'] or '',
                    'realisation': int(r['nb_realisation_zc']) or '',
                    'pourcent': round(r['nb_realisation_zc']/r['nb_attribution_max_zc']*100) or '',
                    'zis': [],
                    **get_details(nom_saison, nom_espece, { 'nom_zone_cynegetique': [r['nom_zone_cynegetique']]})
                }
            zcs.append(zc)
        zc['zis'].append({
            'nom': r['nom_zone_indicative'] or '',
            'code': r['code_zone_indicative'] or '',
            'mini': r['nb_attribution_min_zi'] or '',
            'maxi': r['nb_attribution_max_zi'] or '',
            'realisation': int(r['nb_realisation_zi']) or '',
            'pourcent': round(r['nb_realisation_zi']/r['nb_attribution_max_zi']*100) or '',
            **get_details(nom_saison, nom_espece, { 'nom_zone_indicative': [r['nom_zone_indicative']]})

        })

    data = {
        'nom_saison': nom_saison,
        'nom_espece': nom_espece,
        'mini':  r['nb_attribution_min_espece'] or '',
        'maxi':  r['nb_attribution_max_espece'] or '',
        'realisation': int(r['nb_realisation_espece']) or '',
        'pourcent': round(r['nb_realisation_espece']/r['nb_attribution_max_espece']*100) or '',
        'zcs': zcs,
        **get_details(nom_saison, nom_espece)
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