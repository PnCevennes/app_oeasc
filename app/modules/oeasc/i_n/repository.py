'''
    repository in
'''

import math
import numpy
from utils_flask_sqla.generic import GenericQuery
from flask import current_app

config = current_app.config
DB = config['DB']


student = [0, 0, 12.71, 4.30, 3.18, 2.78, 2.57]


def sort_data(res):
    
    keys = ['espece', 'ug', 'annee', 'serie', 'numero_circuit']
    for key in keys:
        res.sort(key=lambda x: x.get(key))

def regroup_data(res):

    out = { 'especes' : {}}
    regroup = ['espece', 'ug', 'annee', 'serie', 'id_circuit']
    for r in res:

        cur = out
        for key_group in regroup:

            group_name = key_group + 's'
            if group_name not in cur:
                cur[group_name] = {}

            group = cur[group_name]
            key = r[key_group]
            item = group.get(key)
            if not item:
                if key_group == "id_circuit":
                    group[key] = r
                else:
                    item = group[key] = {}

            cur = item

    return out

def in_data():

    res = GenericQuery(
        DB,
        'v1',
        'oeasc_in',
        limit=1e6
    ).as_dict()['items']

    sort_data(res)
    out = regroup_data(res)
    process_especes(out)

    return out

def process_especes(res):

    especes = res['especes']

    for key_espece in especes:
        espece = especes.get(key_espece)
        process_ugs(espece)


def process_ugs(espece):

    ugs = espece['ugs']

    for key_ug in ugs:
        ug = ugs.get(key_ug)
        process_annees(ug)


def process_annees(ug):

    annees = ug['annees']

    # regression lineaire avec numpy
    # https://fr.wikibooks.org/wiki/Python_pour_le_calcul_scientifique/Régression_et_optimisation
    X = []
    Y = []

    for key_annee in annees:
        annee = annees.get(key_annee)
        process_series(annee)
        if not annee.get('moy'):
            continue
        
        X.append([key_annee, 1])
        Y.append([annee['moy']])

    if not len(X):
        return
        
    resultat = numpy.linalg.lstsq(X,Y)
    err = (resultat[1][0] if len(resultat[1]) else 0) / len(Y)
    a, b = resultat[0]
    ug['reg_lin'] = {}
    ug['reg_lin']['a'] =  a[0] 
    ug['reg_lin']['b'] =  b[0] 
    ug['reg_lin']['err'] =  err 
    print(ug['reg_lin'])


def process_series(annee):

    series = annee['series']

    # calcul de la moyenne par annee

    somme_series = 0
    nb_series = 0

    for key_serie in series:
        serie = series.get(key_serie)

        process_circuits(serie)

        if serie['moy'] is None:
            continue

        somme_series += serie['moy']
        nb_series += 1

    if not nb_series:
        return

    annee['moy'] = somme_series / nb_series

    # écart à la moyenne

    if nb_series == 1:
        return

    annee['s_e_moy_2'] = 0


    for key_serie in series:
        serie = series.get(key_serie)

        if serie['moy'] is None:
            continue

        serie['e_moy'] = annee['moy'] - serie['moy']
        serie['e_moy_2'] = serie['e_moy']**2
        annee['s_e_moy_2'] += serie['e_moy_2']

    annee['s_e_moy_2_n_nm1'] = annee['s_e_moy_2'] / (nb_series * (nb_series -1))
    annee['E'] = math.sqrt(annee['s_e_moy_2_n_nm1'])

    t = student[nb_series]
    d = annee['E']* t
    annee['d'] = d
    annee['inf'] = max(0, annee['moy'] - d)
    annee['sup'] = annee['moy'] + d


def process_circuits(serie):

    circuits = serie['id_circuits']

    # calcul de la moyenne par serie
    somme_circuit = 0
    nb_circuits = 0

    for key_circuit in circuits:
        circuit = circuits[key_circuit]
        if not circuit['valid']:
            continue
        somme_circuit += circuit['nb'] / circuit['km']
        nb_circuits += 1

    if nb_circuits:
        serie['moy'] = somme_circuit / nb_circuits
    else:
        serie['moy'] = None
