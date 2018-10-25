
from pypnnomenclature.repository import (
    get_nomenclature_list
)

from pypnnomenclature.models import (
    TNomenclatures
)

from app.utils.env import DB
from app.utils.utilssqlalchemy import as_dict

from config import config
from sqlalchemy import text


from pypnusershub.db.models import (
    User, AppUser
)

from app.ref_geo.models import TAreas

from app.ref_geo.repository import (
    get_type_code,
)

import datetime

from flask import g

import re

from .models import (
    TDeclaration,
    TForet,
    TProprietaire
)


def get_organisme_name_from_id_organisme(id_organisme):

    sql_text = text("SELECT b.nom_organisme \
        FROM utilisateurs.bib_organismes as b \
        WHERE b.id_organisme = {};".format(id_organisme))

    result = DB.engine.execute(sql_text).first()[0]

    return result


def get_organisme_name_from_id_declarant(id_declarant):

    sql_text = text("SELECT b.nom_organisme \
        FROM utilisateurs.bib_organismes as b, utilisateurs.t_roles as r \
        WHERE b.id_organisme = r.id_organisme AND r.id_role = {};".format(id_declarant))

    result = DB.engine.execute(sql_text).first()[0]

    return result


def get_description_droit(id_droit):

    switcher = {
        1: "Déclarant",
        2: "Déclarant",
        3: "Responsable",
        4: "Animateur",
        5: "Animateur",
        6: "Admin"
    }

    return switcher.get(id_droit, 'id_droit {} invalide'.format(id_droit))


def get_fonction_droit(function):
    '''
        retourne le niveau de droit en fonction de la fonction renseignée
    '''

    dict_function = {

        "Déclarant": 1,
        "Responsable": 3,
        "Animateur": 4,
        "Admin": 6,

    }

    return dict_function.get(function, None)


def get_nomenclature_from_id(id_nomenclature, key=""):
    '''
        retourne un element de nomenclature a partir de son id
        si key == "", retourne l'element entier, sinon juste la clé choisie
    '''
    if not id_nomenclature:

        return None

    for _, nomenclature_type in nomenclature_oeasc().items():

        for elem in nomenclature_type["values"]:

            if str(elem["id_nomenclature"]) == str(id_nomenclature):

                if key != "":

                    return elem[key]

                else:

                    return elem

    return None


def get_nomenclature(key_in, value_in, type_code, key_out=""):

    nomemclature_type = nomenclature_oeasc().get(type_code, None)

    if not nomemclature_type:

        return None

    for elem in nomemclature_type["values"]:

        if str(elem[key_in]) == str(value_in):

            if key_out != "":

                return elem[key_out]

            else:

                return elem

    return None


def get_area_from_id(id_area):

    if not getattr(g, '_areas', None):

        g._areas = {}

    if not getattr(g._areas, str(id_area), None):

        data = DB.session.query(TAreas).filter(id_area == TAreas.id_area).first()

        if not data:

            return None

        out = data.as_dict(columns=['id_area', 'id_type', 'area_name', 'area_code'])

        out['type_code'] = get_type_code(out['id_type'])

        g._areas[str(id_area)] = out

    return g._areas[str(id_area)]


def get_dict_nomenclature_areas(dict_in):
    '''
        récupère les nomenclatures et les aires dans un dictionnaire pour les element d'un dictionnaire
        qui commencent par 'id_nomenclature' ou 'nomenclatures'
        la fonction est appliquées récursivement aux dictionnaire et aux listes
    '''

    if not isinstance(dict_in, dict):

        return dict_in

    for key in dict_in:

        if key.startswith("id_nomenclature_"):
            dict_in[key] = get_nomenclature_from_id(dict_in.get(key, None))
            continue

        if key.startswith("areas"):
            dict_in[key] = [get_area_from_id(elem['id_area']) for elem in dict_in[key]]

        if key.startswith("nomenclatures_"):

            dict_in[key] = [get_nomenclature_from_id(elem['id_nomenclature']) for elem in dict_in[key]]
            continue

        if isinstance(dict_in[key], dict):

            dict_in[key] = get_dict_nomenclature_areas(dict_in[key])
            continue

        if isinstance(dict_in[key], list):

            dict_in[key] = [get_dict_nomenclature_areas(elem) for elem in dict_in[key]]
            continue

    return dict_in


def get_foret_type(foret_dict):
    print(foret_dict['proprietaire'])
    if not foret_dict['proprietaire']['id_nomenclature_proprietaire_type']:

        return "Indéterminé"

    if not isinstance(foret_dict['proprietaire']['id_nomenclature_proprietaire_type'], dict):

        foret_dict['proprietaire']['id_nomenclature_proprietaire_type'] = get_nomenclature_from_id(foret_dict['proprietaire']['id_nomenclature_proprietaire_type'])

    print(foret_dict['proprietaire']['id_nomenclature_proprietaire_type'])

    proprietaire_type = foret_dict['proprietaire']['id_nomenclature_proprietaire_type']['label_fr']

    d_prop_foret_type = {

        'État': 'Domaniale',
        'Centre hospitalier': 'Autre forêt publique',
        'EP PNC': 'Autre forêt publique',
        'Commune': 'Communale',
        'Groupement forestier': 'Groupement forestier',
        'Section / hameau': 'Sectionale',
        'Privé': 'Privée'

    }

    foret_type = d_prop_foret_type.get(proprietaire_type, "")

    foret_dict['foret_type'] = foret_type

    return foret_type


def dfpu_as_dict(declaration, foret, proprietaire, declarant):

    if not declaration:

        declaration = TDeclaration()

    if not foret:

        foret = TForet()

    if not proprietaire:

        proprietaire = TProprietaire()

    if not declarant:

        declarant = User()

    declaration_dict = declaration.as_dict(True)
    declaration_dict["foret"] = foret.as_dict(True)
    declaration_dict["declarant"] = as_dict(declarant)
    declaration_dict['foret']['proprietaire'] = proprietaire.as_dict(True)

    get_dict_nomenclature_areas(declaration_dict)

    get_foret_type(declaration_dict["foret"])

    return declaration_dict


def dfpu_as_dict_from_id_declaration(id_declaration):


    declaration, foret, proprietaire, declarant = get_dfpu(id_declaration)
    declaration_dict = dfpu_as_dict(declaration, foret, proprietaire, declarant)

    return declaration_dict


def get_foret(id_foret):

    foret = proprietaire = None

    foret = DB.session.query(TForet).filter(id_foret == TForet.id_foret).first()

    if foret:

        id_proprietaire = foret.id_proprietaire

        if id_proprietaire:

            proprietaire = DB.session.query(TProprietaire).filter(id_proprietaire == TProprietaire.id_proprietaire).first()

    return foret, proprietaire


def get_declarant(id_declarant):

    declarant = DB.session.query(User).filter(id_declarant == User.id_role).first()

    return declarant


def get_dfpu(id_declaration):

    declaration = foret = proprietaire = declarant = None

    declaration = DB.session.query(TDeclaration).filter(id_declaration == TDeclaration.id_declaration).first()

    if declaration:

        id_declarant = declaration.id_declarant

        if id_declarant:

            declarant = get_declarant(id_declarant)
        id_foret = declaration.id_foret

        if id_foret:

            foret, proprietaire = get_foret(id_foret)

    return (declaration, foret, proprietaire, declarant)


def create_or_modify(model, key, val, dict_in):

    elem = None

    if key:

        elem = DB.session.query(model).filter(getattr(model, key) == val).first()

    if elem is None:
        elem = model()
        DB.session.add(elem)

    elem.from_dict(dict_in, True)

    DB.session.commit()

    return elem


def f_create_or_update_declaration(declaration_dict):

    declaration = proprietaire = foret = None

    id_declaration = declaration_dict.get("id_declaration", None)

    # on n'écrit la foret ou le proprietaire dans la base dans la base que dans le cas d'une foret non documentée
    if not declaration_dict["foret"]["b_document"]:

        id_foret = declaration_dict["foret"].get("id_foret", None)
        id_proprietaire = declaration_dict["foret"]["proprietaire"].get("id_proprietaire", None)

        proprietaire = create_or_modify(TProprietaire, 'id_proprietaire', id_proprietaire, declaration_dict["foret"]["proprietaire"])

        declaration_dict['foret']['id_proprietaire'] = proprietaire.id_proprietaire

        foret = create_or_modify(TForet, 'id_foret', id_foret, declaration_dict["foret"])

        declaration_dict['id_foret'] = foret.id_foret

    else:

        proprietaire = TProprietaire().from_dict(declaration_dict["foret"]["proprietaire"], True)
        foret = TForet().from_dict(declaration_dict["foret"], True)
        # proprietaire = DB.session.query(TProprietaire).filter(TProprietaire.id_proprietaire == declaration_dict["foret"]["proprietaire"]["id_proprietaire"])
        # foret = DB.session.query(TForet).filter(TForet.id_foret == declaration_dict["foret"]["proprietaire"]["id_foret"])

    # pour le cas ou on veut generer une create date en random :
    # - elle sera crée un fois avec la date courante
    # - puis modifiée pour lui donner la date choisie aléatoirement
    if declaration_dict.get("meta_create_date", None):

        declaration = create_or_modify(TDeclaration, 'id_declaration', id_declaration, declaration_dict)
        id_declaration = declaration.id_declaration

    declaration = create_or_modify(TDeclaration, 'id_declaration', id_declaration, declaration_dict)

    d = dfpu_as_dict(declaration, foret, proprietaire, None)

    return d


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

    data = DB.session.query(User)
    v = [as_dict(d) for d in data]

    data_app = DB.session.query(AppUser).filter(AppUser.id_application == config.ID_APP)
    v_app = [as_dict(d) for d in data_app]

    v_out = []

    for user in v:

        if user['id_organisme']:

            user['organisme'] = get_organisme_name_from_id_organisme(user['id_organisme'])

        for user_app in v_app:

            if user['id_role'] == user_app['id_role']:

                user['id_droit_max'] = user_app['id_droit_max']
                user['id_application'] = user_app['id_application']

                v_out.append(user)

    return v_out


def get_user(id_declarant):
    '''
        Retourne l'utilisateur ayant pour id_role id_declarant
    '''

    data = DB.session.query(User).filter(User.id_role == id_declarant).first()
    data_app = DB.session.query(AppUser).filter(id_declarant == AppUser.id_role).first()

    if not data or not data_app:

        return None


    user = as_dict(data)
    user_app = as_dict(data_app)

    user['id_droit_max'] = user_app['id_droit_max']
    user['id_application'] = user_app['id_application']
    user['organisme'] = get_organisme_name_from_id_organisme(user['id_organisme'])

    return user


def nomenclature_oeasc():
    '''
        fonction pour récuprér toutes les nomenclatures qui concernent l'oeasc
        à l'aide de la commande get_nomenclature_list du module pypnnomenclature
    '''

    # on regarde si la nomenclature existe dans la variable globale g
    if not getattr(g, '_nomenclature', None):

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
            'OEASC_DECLARANT_FONCTION',

        ]

        data = {}

        for type_code in list_data:

            data[type_code] = get_nomenclature_list(code_type=type_code)

            if not data[type_code]:

                continue

            # on ne garde que les colonnes qui nous intéresse

            cols = ['id_nomenclature', 'mnemonique', 'label_fr']

            values = []

            for d in data[type_code]["values"]:

                d_new = {}

                for key in cols:

                    d_new[key] = d.get(key, None)

                values.append(d_new)

            data[type_code]["values"] = values

        g._nomenclature = data

    return g._nomenclature


def get_declarations(b_synthese, id_declarant=None):
    '''
        retourne une liste de declaration sous forme de tableau de dictionnaire

        b_synthese :s
            True : grand public -> toutes les données
            False : vue des déclarations -> on filtre les données
    '''

    # toutes les declaration dans le cas d'une synthese

    if b_synthese:

        id_declarations = DB.session.query(TDeclaration.id_declaration).all()

    else:

        if not id_declarant:

            return None

        data = DB.session.query(User).filter(id_declarant == User.id_role).first()
        data_app = DB.session.query(AppUser).filter(id_declarant == AppUser.id_role).first()

        if not data:

            return None

        user = as_dict(data)
        user_app = as_dict(data_app)

        user['id_droit_max'] = user_app['id_droit_max']
        user['id_application'] = user_app['id_application']

        # administrateur et animateur
        if user["id_droit_max"] >= get_fonction_droit("Animateur") or b_synthese:

            data = DB.session.query(TDeclaration.id_declaration).all()

        # les declarant de la meme structure (sauf les particuliers)
        elif user["id_droit_max"] >= get_fonction_droit("Déclarant") and get_organisme_name_from_id_organisme(user['id_organisme']) != 'Particulier':

            sql_text = text("SELECT oeasc.get_declarations_structure_declarant({})".format(user["id_role"]))

            data = DB.engine.execute(sql_text)

        #
        elif user["id_droit_max"] >= get_fonction_droit("Déclarant"):

            data = DB.session.query(TDeclaration.id_declaration).filter(id_declarant).all()

        #
        else:

            return None

        id_declarations = [d[0] for d in data]

    declarations = []

    for id_declaration in id_declarations:

        declaration_dict = dfpu_as_dict_from_id_declaration(id_declaration)
        declarations.append(declaration_dict)


    return declarations


def get_db(type, key, val):

    switch_model = {

        "user": User,
        "t_areas": TAreas,
        "nomenclature": TNomenclatures,
    }

    table = switch_model.get(type, None)

    if table:

        data = DB.session.query(table).filter(getattr(table, key) == val).first()

        if data:

            return as_dict(data)

    return "None"
