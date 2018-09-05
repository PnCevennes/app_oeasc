
from pypnnomenclature.repository import (
    get_nomenclature_list
)

import random

from app.utils.env import DB
from app.utils.utilssqlalchemy import as_dict

from config import config
from sqlalchemy import text
from sqlalchemy.sql import func

from pypnusershub.db.models import (

    AppUser
)

from app.ref_geo.models import TAreas, LAreas
from app.ref_geo.repository import get_id_type

from .models import (
    TDeclaration,
    TForet,
    TProprietaire
)

from datetime import timedelta
from datetime import datetime


def get_nomenclature_from_id(id_nomenclature, nomenclature, key="label_fr"):
    '''
        retourne un element de nomenclature a partir de son id
        si key == "", retourne l'element entier, sinon juste la clé choisie
    '''
    for _, nomenclature_type in nomenclature.items():

        for elem in nomenclature_type["values"]:

            if str(elem["id_nomenclature"]) == str(id_nomenclature):

                if key != "":

                    return elem[key]

                else:

                    return elem

    return ""


def dfp_as_dict(declaration, foret, proprietaire):

    if not declaration:

        declaration = TDeclaration()

    if not foret:

        foret = TForet()

    if not proprietaire:

        proprietaire = TProprietaire()

    declaration_dict = declaration.as_dict(True)
    declaration_dict["foret"] = foret.as_dict(True)
    declaration_dict['foret']['proprietaire'] = proprietaire.as_dict(True)

    return declaration_dict


def get_foret(id_foret):

    foret = proprietaire = None

    foret = DB.session.query(TForet).filter(id_foret == TForet.id_foret).first()

    if foret:

        id_proprietaire = foret.id_proprietaire

        if id_proprietaire:

            proprietaire = DB.session.query(TProprietaire).filter(id_proprietaire == TProprietaire.id_proprietaire).first()

    return foret, proprietaire


def get_dfp(id_declaration):

    declaration = foret = proprietaire = None

    declaration = DB.session.query(TDeclaration).filter(id_declaration == TDeclaration.id_declaration).first()

    if declaration:

        id_foret = declaration.id_foret

        if id_foret:

            foret, proprietaire = get_foret(id_foret)

    return (declaration, foret, proprietaire)


def create_or_modify(model, key, val, dict_in):

    elem = None

    if key:

        elem = DB.session.query(model).filter(getattr(model, key) == val).first()

    if elem is None:
        print("create", model, key, val)
        elem = model()
        DB.session.add(elem)

    else:

        print("mod", model, key, val)


    elem.from_dict(dict_in, True)

    DB.session.commit()

    return elem


def get_liste_organismes_oeasc():
    '''
        Retourne la liste des organisme concernés par l'OEASC
    '''

    sql_text = text("SELECT b.id_organisme, b.nom_organisme \
  FROM utilisateurs.cor_organism_tag as c, utilisateurs.bib_organismes as b, utilisateurs.t_tags as t \
  WHERE c.id_tag = t.id_tag AND b.id_organisme = c.id_organism AND t.tag_code = 'ORG_OEASC' \
  ORDER BY b.nom_organisme;")

    result = DB.engine.execute(sql_text)

    v = [{'id_organism': row[0], 'nom_organisme': row[1]} for row in result]

    return v


def get_users():
    '''
    Retourne la liste des utilisateurs OEASC
    '''

    data = DB.session.query(AppUser).filter(AppUser.id_application == config.ID_APP)

    v = [as_dict(d) for d in data]

    return v


def nomenclature_oeasc():

    list_data = [
        'OEASC_PEUPLEMENT_ESSENCE',
        'OEASC_PEUPLEMENT_MATURITE',
        'OEASC_PEUPLEMENT_PROTECTION_TYPE',
        'OEASC_PEUPLEMENT_PATURAGE_TYPE',
        'OEASC_PEUPLEMENT_PATURAGE_STATUT',
        'OEASC_PEUPLEMENT_ESPECE',
        'OEASC_PEUPLEMENT_ORIGINE',
        'OEASC_PEUPLEMENT_TYPE',
        'OEASC_PEUPLEMENT_ACCES',
        'OEASC_PEUPLEMENT_PATURAGE_FREQUENCE',
        'OEASC_DEGAT_TYPE',
        'OEASC_DEGAT_GRAVITE',
        'OEASC_DEGAT_ETENDUE',
        'OEASC_DEGAT_ANTERIORITE',
        'OEASC_PEUPLEMENT_ESSENCE',
        'OEASC_DEGAT_GRAVITE',
        'OEASC_DEGAT_ETENDUE',
        'OEASC_DEGAT_ANTERIORITE',
        'OEASC_FORET_TYPE',
        'OEASC_PROPRIETAIRE_DECLARANT',
        'OEASC_PROPRIETAIRE_TYPE',
    ]

    data = {}

    for code_type in list_data:

        data[code_type] = get_nomenclature_list(code_type=code_type)
        data[code_type]["values"].reverse()

    return data


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

    v_ind = v_rand_nomenclature(nomenclature, mnemonique)
    return get_nomenclature_sample(nomenclature, mnemonique, v_ind, key)


def degats_dict_sample(nomenclature=None):

    if not nomenclature:

        nomenclature = nomenclature_oeasc()

    degats = []

    degat_1 = {"id_nomenclature_degat_type": get_nomenclature_sample(nomenclature, "OEASC_DEGAT_TYPE", 1, "id_nomenclature")}
    degat_2 = {"id_nomenclature_degat_type": get_nomenclature_sample(nomenclature, "OEASC_DEGAT_TYPE", 2, "id_nomenclature")}
    degat_3 = {"id_nomenclature_degat_type": get_nomenclature_sample(nomenclature, "OEASC_DEGAT_TYPE", 4, "id_nomenclature")}

    degat_1_1 = {"id_nomenclature_degat_essence": get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_ESSENCE", 1, "id_nomenclature"),
                 "id_nomenclature_degat_etendue": get_nomenclature_sample(nomenclature, "OEASC_DEGAT_ETENDUE", 0, "id_nomenclature"),
                 "id_nomenclature_degat_gravite": get_nomenclature_sample(nomenclature, "OEASC_DEGAT_GRAVITE", 1, "id_nomenclature"),
                 "id_nomenclature_degat_anteriorite": get_nomenclature_sample(nomenclature, "OEASC_DEGAT_ANTERIORITE", 2, "id_nomenclature")}

    degat_1_2 = {"id_nomenclature_degat_essence": get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_ESSENCE", 2, "id_nomenclature"),
                 "id_nomenclature_degat_etendue": get_nomenclature_sample(nomenclature, "OEASC_DEGAT_ETENDUE", 1, "id_nomenclature"),
                 "id_nomenclature_degat_gravite": get_nomenclature_sample(nomenclature, "OEASC_DEGAT_GRAVITE", 2, "id_nomenclature"),
                 "id_nomenclature_degat_anteriorite": get_nomenclature_sample(nomenclature, "OEASC_DEGAT_ANTERIORITE", 0, "id_nomenclature")}

    degat_2_1 = {"id_nomenclature_degat_essence": get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_ESSENCE", 0, "id_nomenclature"),
                 "id_nomenclature_degat_etendue": get_nomenclature_sample(nomenclature, "OEASC_DEGAT_ETENDUE", 2, "id_nomenclature"),
                 "id_nomenclature_degat_gravite": get_nomenclature_sample(nomenclature, "OEASC_DEGAT_GRAVITE", 0, "id_nomenclature"),
                 "id_nomenclature_degat_anteriorite": get_nomenclature_sample(nomenclature, "OEASC_DEGAT_ANTERIORITE", 1, "id_nomenclature")}

    degat_1['degat_essences'] = [degat_1_1, degat_1_2]

    degat_2['degat_essences'] = [degat_2_1]

    degats.append(degat_1)
    degats.append(degat_2)
    degats.append(degat_3)

    return degats


def proprietaire_dict_sample(nomenclature=None):

    if not nomenclature:

        nomenclature = nomenclature_oeasc()
    pass

    proprietaire = {

        "id_nomenclature_proprietaire_type": get_nomenclature_sample(nomenclature, "OEASC_PROPRIETAIRE_TYPE", 3, "id_nomenclature"),
        "s_nom_proprietaire": "Georges",
        "s_telephone": "06...",
        "s_email": "roger@rogers.frt",
        "s_adresse": "lou_malherbous",
        "s_code_postal": "48470",
        "s_commune_proprietaire": "Espigoule"

    }

    return proprietaire


def foret_dict_sample(nomenclature=None):

    if not nomenclature:

        nomenclature = nomenclature_oeasc()

    id_area = DB.session.query(TAreas.id_area).filter(TAreas.area_name == "48-ramponenche").first()[0]

    foret = {

        "proprietaire": proprietaire_dict_random_sample(),
        "b_statut_public": False,
        "b_document": False,
        "s_nom_foret": "Les sequoias",
        "d_superficie": 2.5,
        "areas_foret": [{"id_area": id_area}]

    }

    return foret


def declaration_dict_sample(nomenclature=None):

    if not nomenclature:

        nomenclature = nomenclature_oeasc()

    id_area0 = DB.session.query(TAreas.id_area).filter(TAreas.area_name == "0-CHIBIEL").first()[0]
    id_area1 = DB.session.query(TAreas.id_area).filter(TAreas.area_name == "1-CHIBIEL").first()[0]

    declaration = {

        "id_declarant": 1,

        "id_nomenclature_proprietaire_declarant": get_nomenclature_sample(nomenclature, "OEASC_PROPRIETAIRE_DECLARANT", 2, "id_nomenclature"),

        "foret": foret_dict_sample(),

        "degats": degats_dict_sample(),

        'areas_localisation': [{'id_area': id_area0}, {'id_area': id_area1}],

        'b_peuplement_paturage_presence': True,
        'b_peuplement_protection_existence': False,

        'id_nomenclature_peuplement_essence_principale': get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_ESSENCE", 0, "id_nomenclature"),
        'id_nomenclature_peuplement_origine': get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_ORIGINE", 0, "id_nomenclature"),
        'id_nomenclature_peuplement_type': get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_TYPE", 0, "id_nomenclature"),
        'id_nomenclature_peuplement_paturage_frequence': get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_PATURAGE_FREQUENCE", 0, "id_nomenclature"),
        'id_nomenclature_peuplement_acces': get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_ACCES", 1, "id_nomenclature"),

        'nomenclatures_peuplement_essence_secondaire': [{'id_nomenclature': id} for id in get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_ESSENCE", [5, 1, 2], "id_nomenclature")],
        'nomenclatures_peuplement_essence_complementaire': [{'id_nomenclature': id} for id in get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_ESSENCE", [3, 4], "id_nomenclature")],
        'nomenclatures_peuplement_maturite': [{'id_nomenclature': id} for id in get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_MATURITE", [1, 2], "id_nomenclature")],
        'nomenclatures_peuplement_paturage_type': [{'id_nomenclature': id} for id in get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_PATURAGE_TYPE", [1], "id_nomenclature")],
        'nomenclatures_peuplement_paturage_statut': [{'id_nomenclature': id} for id in get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_PATURAGE_STATUT", [1], "id_nomenclature")],
        'nomenclatures_peuplement_espece': [{'id_nomenclature': id} for id in get_nomenclature_sample(nomenclature, "OEASC_PEUPLEMENT_ESPECE", [3, 4], "id_nomenclature")],

        's_commentaire': "Un commentaire...."

    }

    return declaration


def proprietaire_dict_random_sample(nomenclature=None):

    if not nomenclature:

        nomenclature = nomenclature_oeasc()
    pass

    proprietaire = {

        "id_nomenclature_proprietaire_type": get_nomenclature_random_sample(nomenclature, "OEASC_PROPRIETAIRE_TYPE", "id_nomenclature"),
        "s_nom_proprietaire": "Georges",
        "s_telephone": "06...",
        "s_email": "roger@rogers.frt",
        "s_adresse": "lou_malherbous",
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
        "s_nom_foret": "Les sequoias",
        "d_superficie": 2.5,
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


def declaration_dict_random_sample(nomenclature=None):

    if not nomenclature:

        nomenclature = nomenclature_oeasc()

    foret = foret_dict_random_sample()
    b_statut_public = foret['b_statut_public']
    b_document = foret['b_document']

    id_area_foret = foret['areas_foret'][0]['id_area']

    code_type_parcelle = get_code_type_statut_document(b_statut_public, b_document, "parcelle")

    sql_text = text("SELECT id_role FROM utilisateurs.t_roles WHERE remarques = 'utilisateur test OEASC'")
    data = DB.engine.execute(sql_text)
    v = [d[0] for d in data]
    id_declarant = random.choice(v)

    sql_text = text("SELECT ref_geo.intersect_rel_area({}, '{}', 0.05)".format(id_area_foret, code_type_parcelle))
    data = DB.engine.execute(sql_text)
    v = [d[0] for d in data]
    if v == []:
        return None
    id_area = v[random.randint(0, len(v) - 1)]
    areas_localisation = [{'id_area': id_area}]

    v_essences = v_rand_nomenclature(nomenclature, 'OEASC_PEUPLEMENT_ESSENCE', 7)

    random_seconds = random.randint(1, 2 * 3600 * 24 * 365)

    date = (datetime.strptime('1/1/2015', '%m/%d/%Y') + timedelta(seconds=random_seconds))

    s_date = str(date)

    declaration = {

        "id_declarant": id_declarant,

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

        's_commentaire': "Un commentaire....",

        "meta_create_date": s_date,
        "meta_update_date": s_date

    }

    return declaration
