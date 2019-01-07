from app.modules.oeasc.nomenclature import get_nomenclature_from_id, get_dict_nomenclature_areas, pre_get_dict_nomenclature_areas
from flask import session, current_app
from .models import TDeclaration, TForet, TProprietaire
from app.modules.oeasc.user.repository import get_user, get_id_organismes
from app.utils.utilssqlalchemy import GenericQuery

config = current_app.config
DB = config['DB']


def get_foret_type(foret_dict):

    if not foret_dict:

        return

    if not foret_dict['proprietaire']['id_nomenclature_proprietaire_type']:

        return "Indéterminé"

    if not isinstance(foret_dict['proprietaire']['id_nomenclature_proprietaire_type'], dict):

        foret_dict['proprietaire']['id_nomenclature_proprietaire_type'] = get_nomenclature_from_id(foret_dict['proprietaire']['id_nomenclature_proprietaire_type'])

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


def dfpu_as_dict(declaration, foret, proprietaire, declarant, b_resolve=True):

    if not declaration:

        declaration = TDeclaration()

    if not foret:

        foret = TForet()

    if not proprietaire:

        proprietaire = TProprietaire()

    if not declarant:

        declarant = get_user()

    declaration_dict = declaration.as_dict(True)
    declaration_dict["foret"] = foret.as_dict(True)
    declaration_dict["declarant"] = declarant
    declaration_dict['foret']['proprietaire'] = proprietaire.as_dict(True)

    if b_resolve:
        get_dict_nomenclature_areas(declaration_dict)
        get_foret_type(declaration_dict.get("foret"))

    return declaration_dict


def resolve_declaration(declaration_dict):

    get_dict_nomenclature_areas(declaration_dict)
    get_foret_type(declaration_dict.get("foret"))
    resume_gravite(declaration_dict)

    return declaration_dict


def dfpu_as_dict_from_id_declaration(id_declaration, b_resolve=True):

    declaration, foret, proprietaire, declarant = get_dfpu(id_declaration)
    declaration_dict = dfpu_as_dict(declaration, foret, proprietaire, declarant, b_resolve)
    return declaration_dict


def get_foret(id_foret):

    foret = proprietaire = None

    foret = DB.session.query(TForet).filter(id_foret == TForet.id_foret).first()

    if foret:

        id_proprietaire = foret.id_proprietaire

        if id_proprietaire:

            proprietaire = DB.session.query(TProprietaire).filter(id_proprietaire == TProprietaire.id_proprietaire).first()

    return foret, proprietaire


def get_dfpu(id_declaration):

    declaration = foret = proprietaire = declarant = None

    declaration = DB.session.query(TDeclaration).filter(id_declaration == TDeclaration.id_declaration).first()

    if declaration:

        id_declarant = declaration.id_declarant

        if id_declarant:

            declarant = get_user(id_declarant)
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


def get_declaration(id_declaration):
    '''
        verifie les droit de l'utilisateur et renvoie la declaration
    '''
    user = session.get('current_user')

    if not user:
        return None

    declaration = dfpu_as_dict_from_id_declaration(id_declaration)

    if user['id_role'] == declaration['id_declarant']:
        return declaration

    if user['id_droit_max'] >= 5:
        return declaration

    if user["id_droit_max"] >= 2 \
        and user['id_organisme'] not in get_id_organismes(["Pas d'organisme"]) \
            and user['id_organisme'] == declaration['declarant']['id_organisme']:
        return declaration

    return None


def get_declarations(b_synthese, id_declarant=None):
    '''
        retourne une liste de declaration sous forme de tableau de dictionnaire

        b_synthese :s
            True : grand public -> toutes les données
            False : vue des déclarations -> on filtre les données
    '''

    # toutes les declaration dans le cas d'une synthese
    data = None

    if id_declarant > 0:

        user = get_user(id_declarant)
        print(user)
        liste_id_organismes_solo = get_id_organismes(['Autre (préciser)', "Pas d'organisme"])

        # administrateur et animateur >=5
        if user["id_droit_max"] >= 5:
            data = GenericQuery(DB.session, 'v_declarations', 'oeasc', None, None, 1e6).return_query()

        # les declarant de la meme structure (sauf les particuliers) >=)2
        elif user["id_droit_max"] >= 2 and user['id_organisme'] not in liste_id_organismes_solo:
            data = GenericQuery(DB.session, 'v_declarations', 'oeasc', None, {"organisme": user['organisme']}, 1e6).return_query()

        elif user["id_droit_max"] >= 1:
            data = GenericQuery(DB.session, 'v_declarations', 'oeasc', None, {"id_declarant": id_declarant}, 1e6).return_query()

    elif b_synthese:
        data = GenericQuery(DB.session, 'v_declarations', 'oeasc', None, None, 1e6).return_query()

    if not data:
        return []

    if not data.get('items'):
        return []

    declarations = data.get('items')
    pre_get_dict_nomenclature_areas(declarations)
    declarations = [resolve_declaration(d) for d in declarations]

    return declarations


def resume_gravite(declaration_dict):

    gravite = None
    if not declaration_dict.get('degats'):
        return
    for degat in declaration_dict.get('degats'):
        for degat_essence in degat['degat_essences']:
            if not degat_essence['id_nomenclature_degat_gravite']:
                continue
            if not degat_essence['id_nomenclature_degat_gravite']['cd_nomenclature']:
                continue
            gravite_ = degat_essence['id_nomenclature_degat_gravite']
            if not gravite:
                gravite = gravite_
            if gravite_['cd_nomenclature'] == "DG_IMPT" or (gravite['cd_nomenclature'] == "DG_FLB" and gravite_['cd_nomenclature'] == "DG_MOY"):
                gravite = gravite_

    declaration_dict['gravite'] = gravite
