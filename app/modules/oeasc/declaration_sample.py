from app.ref_geo.models import TAreas
from app.ref_geo.repository import get_id_type

from .repository import (nomenclature_oeasc, get_nomenclature_from_id)
from app.utils.utilssqlalchemy import as_dict

from app.utils.env import DB
from pypnusershub.db.models import (
    User
)

import random

from sqlalchemy import text

from datetime import timedelta
from datetime import datetime


def rand_nomenclature(nomenclature, mnemonique):

    return random.randint(0, len(nomenclature[mnemonique]['values']) - 1)


def v_rand_nomenclature(nomenclature, mnemonique, k=-1):

    n = len(nomenclature[mnemonique]['values'])

    if k == -1:

        k = random.randint(0, n - 1)

    return random.sample(range(n), k)


def get_nomenclature_sample(nomenclature, mnemonique, ind, key=""):

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

    ind = rand_nomenclature(nomenclature, mnemonique)

    return get_nomenclature_sample(nomenclature, mnemonique, ind, key)


def get_v_nomenclature_random_sample(nomenclature, mnemonique, key=""):

    v_ind = []

    # pour être sur d'avoir au moins un element
    while not v_ind:

        v_ind = v_rand_nomenclature(nomenclature, mnemonique)

    return get_nomenclature_sample(nomenclature, mnemonique, v_ind, key)


def proprietaire_dict_random_sample(nomenclature=None):

    if not nomenclature:

        nomenclature = nomenclature_oeasc()
    pass

    proprietaire = {

        "id_nomenclature_proprietaire_type": get_nomenclature_random_sample(nomenclature, "OEASC_PROPRIETAIRE_TYPE", "id_nomenclature"),
        "nom_proprietaire": "Georges",
        "telephone": "06...",
        "email": "roger@rogers.frt",
        "adresse": "lou_malherbous",
        "s_code_postal": "48470",
        "s_commune_proprietaire": "Espigoule"

    }

    return proprietaire


def get_code_type_statut_document(b_statut_public, b_document, type):

    code_type = ""

    if type == "foret":

        if b_statut_public and b_document:

            code_type = 'OEASC_ONF_FRT'

        elif (not b_statut_public) and b_document:

            code_type = 'OEASC_DGD'

        else:

            code_type = 'OEASC_COMMUNE'

    if type == "parcelle":

        if b_statut_public and b_document:

            code_type = 'OEASC_ONF_PRF'

        else:

            code_type = 'OEASC_CADASTRE'

    return code_type


def foret_dict_random_sample(nomenclature=None):

    if not nomenclature:

        nomenclature = nomenclature_oeasc()

        b_statut_public = random.randint(0, 1) == 1
        b_document = random.randint(0, 1) == 1

    id_type_foret = get_id_type(get_code_type_statut_document(b_statut_public, b_document, "foret"))

    areas = DB.session.query(TAreas.id_area).filter(TAreas.id_type == id_type_foret).filter(TAreas.enable).all()

    id_area = areas[random.randint(0, len(areas) - 1)][0]

    foret = {

        "b_statut_public": b_statut_public,
        "b_document": b_document,
        "proprietaire": proprietaire_dict_random_sample(),
        "nom_foret": "Les sequoias",
        "superficie": 2.5,
        "areas_foret": [{"id_area": id_area}]

    }

    return foret


def degats_dict_random_sample(v_essences, nomenclature=None):

    if not nomenclature:

        nomenclature = nomenclature_oeasc()

    v_degat_type = get_v_nomenclature_random_sample(nomenclature, 'OEASC_DEGAT_TYPE', 'id_nomenclature')

    degats = [{"id_nomenclature_degat_type": id_nomenclature} for id_nomenclature in v_degat_type]

    for d in degats:

        mnemonique = get_nomenclature_from_id(d['id_nomenclature_degat_type'], nomenclature, "mnemonique")

        if mnemonique in ['DT_ABSC', 'DT_POC']:

            continue

        degat = {
            "id_nomenclature_degat_essence": get_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_ESSENCE", "id_nomenclature"),
            "id_nomenclature_degat_etendue": get_nomenclature_random_sample(nomenclature, "OEASC_DEGAT_ETENDUE", "id_nomenclature"),
            "id_nomenclature_degat_gravite": get_nomenclature_random_sample(nomenclature, "OEASC_DEGAT_GRAVITE", "id_nomenclature"),
            "id_nomenclature_degat_anteriorite": get_nomenclature_random_sample(nomenclature, "OEASC_DEGAT_ANTERIORITE", "id_nomenclature")}

        d['degat_essences'] = [degat]

    return degats


def get_random_id_declarant():

    sql_text = text("SELECT id_role FROM utilisateurs.t_roles WHERE remarques = 'utilisateur test OEASC'")
    data = DB.engine.execute(sql_text)
    v = [d[0] for d in data]
    if v == []:
        return None
    id_declarant = random.choice(v)

    return id_declarant


def get_random_areas_localisation(id_area_foret, code_type_parcelle):

    sql_text = text("SELECT ref_geo.intersect_rel_area({}, '{}', 0.05)".format(id_area_foret, code_type_parcelle))
    data = DB.engine.execute(sql_text)
    v = [d[0] for d in data]

    if v == []:

        return None

    id_area = v[random.randint(0, len(v) - 1)]
    areas_localisation = [{'id_area': id_area}]

    return areas_localisation


def declaration_dict_random_sample(nomenclature=None):

    if not nomenclature:

        nomenclature = nomenclature_oeasc()

    foret = foret_dict_random_sample()
    b_statut_public = foret['b_statut_public']
    b_document = foret['b_document']

    id_area_foret = foret['areas_foret'][0]['id_area']

    code_type_parcelle = get_code_type_statut_document(b_statut_public, b_document, "parcelle")

    id_declarant = get_random_id_declarant()

    if not id_declarant:

        return None

    declarant = DB.session.query(User).filter(id_declarant == User.id_role).first()

    if not declarant:

        return None

    areas_localisation = get_random_areas_localisation(id_area_foret, code_type_parcelle)
    # areas_localisation = [{"id_area": 204413}]

    v_essences = v_rand_nomenclature(nomenclature, 'OEASC_PEUPLEMENT_ESSENCE', 7)

    random_seconds = random.randint(1, 2 * 3600 * 24 * 365)

    date = (datetime.strptime('1/1/2015', '%m/%d/%Y') + timedelta(seconds=random_seconds))

    s_date = str(date)

    declaration = {

        "id_declarant": id_declarant,

        "declarant": as_dict(declarant),

        "id_nomenclature_proprietaire_declarant": get_nomenclature_random_sample(nomenclature, "OEASC_PROPRIETAIRE_DECLARANT", "id_nomenclature"),

        "foret": foret,

        "degats": degats_dict_random_sample(v_essences),

        'areas_localisation': areas_localisation,

        'b_peuplement_paturage_presence': True,
        'b_peuplement_protection_existence': False,

        'id_nomenclature_peuplement_origine': get_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_ORIGINE", "id_nomenclature"),
        'id_nomenclature_peuplement_type': get_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_TYPE", "id_nomenclature"),
        'id_nomenclature_peuplement_paturage_frequence': get_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_PATURAGE_FREQUENCE", "id_nomenclature"),
        'id_nomenclature_peuplement_acces': get_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_ACCES", "id_nomenclature"),

        'id_nomenclature_peuplement_essence_principale': get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_ESSENCE", v_essences[0], "id_nomenclature"),
        'nomenclatures_peuplement_essence_secondaire': [{'id_nomenclature': id} for id in get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_ESSENCE", v_essences[1:3], "id_nomenclature")],
        'nomenclatures_peuplement_essence_complementaire': [{'id_nomenclature': id} for id in get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_ESSENCE", v_essences[4:6], "id_nomenclature")],
        'nomenclatures_peuplement_maturite': [{'id_nomenclature': id} for id in get_v_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_MATURITE", "id_nomenclature")],
        'nomenclatures_peuplement_paturage_type': [{'id_nomenclature': id} for id in get_v_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_PATURAGE_TYPE", "id_nomenclature")],
        'nomenclatures_peuplement_paturage_statut': [{'id_nomenclature': id} for id in get_v_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_PATURAGE_STATUT", "id_nomenclature")],
        'nomenclatures_peuplement_espece': [{'id_nomenclature': id} for id in get_v_nomenclature_random_sample(nomenclature, "OEASC_PEUPLEMENT_ESPECE", "id_nomenclature")],

        'commentaire': "Un commentaire....",

        "meta_create_date": s_date,
        "meta_update_date": s_date

    }

    return declaration
