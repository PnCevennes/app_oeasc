
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

from .models import (
    TDeclaration,
    TForet,
    TProprietaire
)


def get_liste_communes(declaration):

    areas = declaration["foret"]["areas_foret"]

    communes = []

    for area in areas:

        id_area = area["id_area"]

        sql_text = text("SELECT b.area_name \
         FROM ref_geo.l_areas as b, \
         (SELECT l.id_area as id_area, c.id_foret, l.area_name,  ref_geo.intersect_rel_area(c.id_area,'OEASC_COMMUNE',0.05) as id_com, geom\
             FROM oeasc.cor_areas_forets as c, ref_geo.l_areas as l\
             WHERE l.id_area = " + str(id_area) + " AND l.id_area = c.id_area) a\
         WHERE b.id_area = a.id_com\
         ORDER BY a.area_name, b.area_name;")

        data = DB.engine.execute(sql_text)

        for d in data:
            if d[0] not in communes:
                communes.append(d[0])

    return communes


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

    # data = DB.session.query(AppUser)
    data = DB.session.query(AppUser).filter(AppUser.id_application == config.ID_APP)

    v = [as_dict(d) for d in data]

    print(v)

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
        declaration_dict["foret"]["communes"] = get_liste_communes(declaration_dict)

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
