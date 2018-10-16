from app.ref_geo.models import TAreas
from app.ref_geo.repository import get_id_type

from .repository import (nomenclature_oeasc, get_nomenclature_from_id)
from .models import TForet, TProprietaire

from app.utils.utilssqlalchemy import as_dict

from app.utils.env import DB
from pypnusershub.db.models import (
    User
)

from sqlalchemy.sql import func

import random

from sqlalchemy import text

from datetime import timedelta
from datetime import datetime


def rand_nomenclature(nomenclature, mnemonique):
    '''
        renvoie un entier compris entre 0 et le nombre de nomenclature pour un type (ou mnemonique) donné
    '''
    return random.randint(0, len(nomenclature[mnemonique]['values']) - 1)


def v_rand_nomenclature(nomenclature, mnemonique, k=-1):
    '''
        renvoie un echantillion de k entiers entiers compris en 0 et le nombre de nomenclature pour un type (ou mnemonique) donné
        si k=-1 k est choisi de façcon aléatoire
    '''

    n = len(nomenclature[mnemonique]['values'])

    if k == -1:

        k = random.randint(1, n - 1)

    sample = random.sample(range(n), k)

    return sample


def get_nomenclature_sample(nomenclature, mnemonique, ind, key=""):
    '''
        si ind est un indice => retourne un elment de nomenclature
        si ind est un tableau => retourne un tableau d'element de nomenclature

        si key=="" renvoie toute un dictionnaire contenant toutes les clé de nomenclature
        si key est renseigné (ex key='label_fr' ou key='mnemonique') renvoie juste cette valeur
    '''

    if type(ind) == list:
        _ind = ind
    else:
        _ind = [ind]

    v_elem = []

    n = len(nomenclature[mnemonique]['values'])

    for i in _ind:

        elem = nomenclature[mnemonique]['values'][i % n]

        if key != "":
            v_elem.append(elem[key])
        else:
            v_elem.append(elem)

    if type(ind) == list:

        return v_elem

    else:

        return v_elem[0]


def get_nomenclature_random_sample(nomenclature, mnemonique, key=""):
    '''
        renvoie un element de nomenclature au hasard pour un type donné
        tout si key="" ou juste la valeur associée à la clé (ex key='label_fr')
    '''

    ind = rand_nomenclature(nomenclature, mnemonique)

    return get_nomenclature_sample(nomenclature, mnemonique, ind, key)


def get_v_nomenclature_random_sample(nomenclature, mnemonique, key=""):
    '''
        renvoie un tableau d'element de nomenclature au hasard pour un type donné, la taille du tableau est aléatoire
        tout si key="" ou juste la valeur associée à la clé (ex key='label_fr')
    '''

    v_ind = []

    # pour être sur d'avoir au moins un element
    while not v_ind:

        v_ind = v_rand_nomenclature(nomenclature, mnemonique)

    return get_nomenclature_sample(nomenclature, mnemonique, v_ind, key)


def proprietaire_dict_random_sample(b_statut_public, nom_commune, nomenclature=None):
    '''
        Renvoie un proprietaire aleatoire
        TODO
    '''

    if not nomenclature:

        nomenclature = nomenclature_oeasc()

    if b_statut_public:

        proprietaire = {

            "nom_proprietaire": nom_commune,

        }

    else:

        proprietaire = {

            "id_nomenclature_proprietaire_type": get_nomenclature_random_sample(nomenclature, "OEASC_PROPRIETAIRE_TYPE", "id_nomenclature"),
            "nom_proprietaire": "Privé",

        }

    return proprietaire


def get_type_code_statut_document(b_statut_public, b_document, type):
    '''
        Renvoie le type code de géométrie correspondant aux statuts de la foret (documentée/ou non, public/privé)
    '''
    type_code = ""

    if type == "foret":

        if b_statut_public and b_document:

            type_code = 'OEASC_ONF_FRT'

        elif (not b_statut_public) and b_document:

            type_code = 'OEASC_DGD'

        else:

            type_code = 'OEASC_COMMUNE'

    if type == "parcelle":

        if b_statut_public and b_document:

            type_code = 'OEASC_ONF_PRF'

        else:

            type_code = 'OEASC_CADASTRE'

    return type_code


def test():

    return get_random_area_section('48150')

    d = declaration_dict_random_sample()

    v = [
        'b_peuplement_paturage_presence',
        'id_nomenclature_peuplement_paturage_frequence',
        'nomenclatures_peuplement_paturage_type',
        'nomenclatures_peuplement_paturage_statut',
        'b_peuplement_protection_existence',
        'nomenclatures_peuplement_protection_type'
    ]

    d2 = {}
    for e in v:
        d2[e] = d[e]

    return d2

    foret = foret_dict_random_sample()

    areas_localisation = get_random_areas_localisation(foret)

    return [foret, areas_localisation]


def get_random_area_commune():

    area = DB.session.query(TAreas).filter(TAreas.id_type == get_id_type('OEASC_COMMUNE')).order_by(func.random()).first()

    if area:

        return area.as_dict()

    return None


def get_random_area_section(area_code_commune):

    area = DB.session.query(TAreas).filter(TAreas.id_type == get_id_type('OEASC_SECTION')).filter(TAreas.area_code.like(area_code_commune + '-%')).order_by(func.random()).first()

    if area:

        return area.as_dict()

    return None


def get_random_area_onf_prf(area_code_onf_frt):

    area = DB.session.query(TAreas).filter(TAreas.id_type == get_id_type('OEASC_ONF_PRF')).filter(TAreas.area_code.like(area_code_onf_frt + '-%')).order_by(func.random()).first()

    if area:

        return area.as_dict()

    return None


def get_random_area_onf_ug(area_code_onf_prf):

    area = DB.session.query(TAreas).filter(TAreas.id_type == get_id_type('OEASC_ONF_UG')).filter(TAreas.area_code.like(area_code_onf_prf + '-%')).order_by(func.random()).first()

    if area:

        return area.as_dict()

    return None


def get_random_area_dgd_cadastre(area_code_dgd):

    res = DB.engine.execute(text("SELECT area_code_cadastre FROM ref_geo.cor_dgd_cadastre WHERE area_code_dgd = '{}' ORDER BY RANDOM() LIMIT 1;".format(area_code_dgd))).first()[0]

    area_code = res

    area = DB.session.query(TAreas).filter(TAreas.id_type == get_id_type('OEASC_CADASTRE')).filter(TAreas.area_code == area_code).first()

    if area:

        return area.as_dict()

    return None


def get_random_area_section_cadastre(area_code_section):

    area = DB.session.query(TAreas).filter(TAreas.id_type == get_id_type('OEASC_CADASTRE')).filter(TAreas.area_code.like(area_code_section + '-%')).order_by(func.random()).first()

    if area:

        return area.as_dict()

    return None


def foret_dict_random_sample(nomenclature=None):
    '''
        Renvoie une foret aleatoire
    '''
    if not nomenclature:

        nomenclature = nomenclature_oeasc()

    b_statut_public = random.randint(0, 1) == 1
    b_document = random.randint(0, 1) == 1

    # cas docmumenté : on récupère en base
    if b_document:

        foret = DB.session.query(TForet).filter(TForet.b_statut_public == b_statut_public).order_by(func.random()).first()

        if not foret:

            return None

        proprietaire = DB.session.query(TForet).filter(TProprietaire.id_proprietaire == foret.id_proprietaire).first()

        if not proprietaire:

            return None

        foret_dict = foret.as_dict(True)

        foret_dict['proprietaire'] = proprietaire.as_dict()

        return foret_dict

    # cas nom documenté on invente
    else:

        area_commune = get_random_area_commune()

        if not area_commune:

            return None

        area_section = get_random_area_section(area_commune['area_code'])

        if not area_section:

            return None

        areas_foret = [{'id_area': area_section['id_area']}, {'id_area': area_commune['id_area']}]

        foret = {

            "b_statut_public": b_statut_public,
            "b_document": False,
            "proprietaire": proprietaire_dict_random_sample(b_statut_public, area_commune['area_name'], nomenclature),
            "nom_foret": "foret au hasard ",
            "superficie": random.randint(0, 1000),
            "areas_foret": areas_foret

        }

        return foret


def degats_dict_random_sample(v_essences, nomenclature=None):
    '''
        Renvoie des degats aléatoires
    '''
    if not nomenclature:

        nomenclature = nomenclature_oeasc()

    v_degat_type = get_v_nomenclature_random_sample(nomenclature, 'OEASC_DEGAT_TYPE', 'id_nomenclature')

    degats = [{"id_nomenclature_degat_type": id_nomenclature} for id_nomenclature in v_degat_type]

    for d in degats:

        mnemonique = get_nomenclature_from_id(d['id_nomenclature_degat_type'], nomenclature, "mnemonique")

        if mnemonique in ['P/C']:

            continue

        if mnemonique in ['ABS']:

            degat = {
                "id_nomenclature_degat_essence": get_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_ESSENCE", "id_nomenclature"),
            }

        else:

            degat = {
                "id_nomenclature_degat_essence": get_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_ESSENCE", "id_nomenclature"),
                "id_nomenclature_degat_etendue": get_nomenclature_random_sample(nomenclature, "OEASC_DEGAT_ETENDUE", "id_nomenclature"),
                "id_nomenclature_degat_gravite": get_nomenclature_random_sample(nomenclature, "OEASC_DEGAT_GRAVITE", "id_nomenclature"),
                "id_nomenclature_degat_anteriorite": get_nomenclature_random_sample(nomenclature, "OEASC_DEGAT_ANTERIORITE", "id_nomenclature")
            }

        d['degat_essences'] = [degat]

    return degats


def get_random_id_declarant():
    '''
        renvoie un id_declarant aléatoire
    '''
    sql_text = text("SELECT id_role FROM utilisateurs.t_roles WHERE remarques = 'utilisateur test OEASC'")
    data = DB.engine.execute(sql_text)
    v = [d[0] for d in data]
    if v == []:
        return None
    id_declarant = random.choice(v)

    return id_declarant


def get_random_areas_localisation(foret):
    '''
        renvoie des localisations aléatoires
        TODO
    '''

    id_area = foret['areas_foret'][0]['id_area']

    area_foret = DB.session.query(TAreas).filter(id_area == TAreas.id_area).first()

    areas_localisation = []

    if area_foret.id_type == get_id_type('OEASC_ONF_FRT'):

        area_ONF_PRF = get_random_area_onf_prf(area_foret.area_code)
        areas_localisation.append({'id_area': area_ONF_PRF['id_area']})

        area_ONF_UG = get_random_area_onf_ug(area_ONF_PRF['area_code'])
        areas_localisation.append({'id_area': area_ONF_UG['id_area']})

    if area_foret.id_type == get_id_type('OEASC_SECTION'):

        area = get_random_area_section_cadastre(area_foret.area_code)
        areas_localisation.append({'id_area': area['id_area']})

    if area_foret.id_type == get_id_type('OEASC_DGD'):

        area = get_random_area_dgd_cadastre(area_foret.area_code)
        areas_localisation.append({'id_area': area['id_area']})

    return areas_localisation


def get_random_declarant():

    id_declarant = get_random_id_declarant()

    if not id_declarant:

        return None

    declarant = DB.session.query(User).filter(id_declarant == User.id_role).first()

    return as_dict(declarant)


def get_random_date():

    time_ref = datetime.strptime('1/1/2015', '%m/%d/%Y')

    diff = datetime.now() - time_ref

    random_seconds = random.randint(0,int(diff.total_seconds()))

    date = (time_ref + timedelta(seconds=random_seconds))

    s_date = str(date)

    return s_date


def declaration_dict_random_sample(nomenclature=None):
    '''
        Renvoie une déclaration aléatoire
    '''
    if not nomenclature:

        nomenclature = nomenclature_oeasc()

    foret = foret_dict_random_sample()

    if not foret:

        return None

    areas_localisation = get_random_areas_localisation(foret)

    declarant = get_random_declarant()

    if not declarant:

        return None

    v_essences = v_rand_nomenclature(nomenclature, 'OEASC_PEUPLEMENT_ESSENCE')

    # random_seconds = random.randint(1, 2 * 3600 * 24 * 365)
    time_ref = datetime.strptime('1/1/2015', '%m/%d/%Y')

    nomenclatures_peuplement_paturage_statut = []
    nomenclatures_peuplement_paturage_type = []
    id_nomenclature_peuplement_paturage_frequence = None

    b_peuplement_paturage_presence = random.randint(0, 1) == 1

    if b_peuplement_paturage_presence:

        nomenclatures_peuplement_paturage_type = [{'id_nomenclature': id} for id in get_v_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_PATURAGE_TYPE", "id_nomenclature")]
        nomenclatures_peuplement_paturage_statut = [{'id_nomenclature': id} for id in get_v_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_PATURAGE_STATUT", "id_nomenclature")]
        id_nomenclature_peuplement_paturage_frequence = get_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_PATURAGE_FREQUENCE", "id_nomenclature")

    nomenclatures_peuplement_protection_type = []

    b_peuplement_protection_existence = random.randint(0, 1) == 1

    if b_peuplement_protection_existence:

        nomenclatures_peuplement_protection_type = [{'id_nomenclature': id} for id in get_v_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_PROTECTION_TYPE", "id_nomenclature")]

    nomenclatures_peuplement_espece = [{'id_nomenclature': id} for id in get_v_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_ESPECE", "id_nomenclature")]

    for elem in nomenclatures_peuplement_espece:

        mnemonique = get_nomenclature_from_id(elem['id_nomenclature'], nomenclature, "mnemonique")

        if mnemonique == 'NSP':

            nomenclatures_peuplement_espece = [elem]
            break

    s_date = get_random_date()

    declaration = {

        "id_declarant": declarant['id_role'],

        "declarant": declarant,

        "id_nomenclature_proprietaire_declarant": get_nomenclature_random_sample(nomenclature, "OEASC_PROPRIETAIRE_DECLARANT", "id_nomenclature"),

        "foret": foret,

        "degats": degats_dict_random_sample(v_essences),

        'areas_localisation': areas_localisation,

        'b_peuplement_paturage_presence': b_peuplement_paturage_presence,
        'b_peuplement_protection_existence': b_peuplement_protection_existence,

        'id_nomenclature_peuplement_origine': get_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_ORIGINE", "id_nomenclature"),
        'id_nomenclature_peuplement_type': get_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_TYPE", "id_nomenclature"),
        'id_nomenclature_peuplement_acces': get_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_ACCES", "id_nomenclature"),

        'id_nomenclature_peuplement_essence_principale': get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_ESSENCE", v_essences[0], "id_nomenclature"),

        'nomenclatures_peuplement_essence_secondaire': [{'id_nomenclature': id} for id in get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_ESSENCE", v_essences[1:4], "id_nomenclature")],
        'nomenclatures_peuplement_essence_complementaire': [{'id_nomenclature': id} for id in get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_ESSENCE", v_essences[4:7], "id_nomenclature")],

        'nomenclatures_peuplement_maturite': [{'id_nomenclature': id} for id in get_v_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_MATURITE", "id_nomenclature")],

        'id_nomenclature_peuplement_paturage_frequence': id_nomenclature_peuplement_paturage_frequence,
        'nomenclatures_peuplement_paturage_type': nomenclatures_peuplement_paturage_type,
        'nomenclatures_peuplement_paturage_statut': nomenclatures_peuplement_paturage_statut,

        'nomenclatures_peuplement_protection_type': nomenclatures_peuplement_protection_type,

        'nomenclatures_peuplement_espece': nomenclatures_peuplement_espece,

        'commentaire': "Un commentaire....",

        "meta_create_date": s_date,
        "meta_update_date": s_date

    }

    return declaration
