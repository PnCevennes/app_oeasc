from app.modules.oeasc.nomenclature import get_nomenclature_from_id, get_dict_nomenclature_areas, pre_get_dict_nomenclature_areas
from flask import session, current_app
from .models import TDeclaration, TForet, TProprietaire, TDegat
from app.modules.oeasc.user.repository import get_user, get_id_organismes
from app.utils.utilssqlalchemy import GenericQuery
from sqlalchemy import text
from .utils import get_areas_from_type_code

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

    # centroid?
    r = '''
SELECT (SELECT ARRAY[st_y(a.center), st_x(a.center)] AS "array"
           FROM ( SELECT st_centroid(st_union(l.geom_4326)) AS center
                   FROM oeasc.cor_areas_declarations c
                     JOIN ref_geo.l_areas l ON c.id_area = l.id_area AND l.id_type <> ref_geo.get_id_type('OEASC_SECTEUR'::character varying)
                  WHERE c.id_declaration = d.id_declaration) a) AS centroid
   FROM oeasc.t_declarations d
   WHERE d.id_declaration={};'''.format(declaration['id_declaration'])

    data = DB.engine.execute(text(r))

    declaration['centroid'] = data.first()[0]

    if user['id_role'] == declaration['id_declarant']:
        return declaration

    if user['id_droit_max'] >= 5:
        return declaration

    if user["id_droit_max"] >= 2 \
        and user['id_organisme'] not in get_id_organismes(["Pas d'organisme"]) \
            and user['id_organisme'] == declaration['declarant']['id_organisme']:
        return declaration

    return None


def get_declarations(user=None, type_export=None, type_out=None):
    '''
        retourne une liste de declaration sous forme de tableau de dictionnaire
        type_export : shape csv (dict par defaut)
        type_out : 1 ligne par declaration ou une ligne par degat
        user : dictionnaire contenant les informations sur l'utilisateur, nottament ses droits
    '''

    liste_id_organismes_solo = get_id_organismes(['Autre (préciser)', "Pas d'organisme"])


    # choix de la vue selon les paramètres
    view_name = ""
    if type_export == "csv":
        view_name = "v_export_declaration_degats_csv" if type_out == "degat" else "v_export_declarations_csv"
    elif type_export == "shape":
        view_name = "v_export_declaration_degats_shape" if type_out == "degat" else "v_export_declarations_shape"
    else:
        view_name = "v_declaration_degats" if type_out == "degat" else "v_declarations"

    # choix des filtrers selon les droits de l'utilisateur
    filters = None
    if user:

        # administrateur et animateur >=5
        if user["id_droit_max"] >= 5:
            pass

        # les declarant de la meme structure (sauf les particuliers) >=)2
        elif user["id_droit_max"] >= 2 and user['id_organisme'] not in liste_id_organismes_solo:
            filters = {"organisme": user['organisme']}

        # les personnes de droit 1 (leurs alertes seulement)
        elif user["id_droit_max"] >= 1:
            filters = {"id_declarant": user['id_declarant']}

    # requête
    data = GenericQuery(DB.session, view_name, 'oeasc', None, filters, 1e6).return_query()

    if not (data and data.get('items')):
        return []

    declarations = data.get('items')

    # TODO !!! gérer dégâts (depuis vue???)
    # data_degats = DB.session.query(TDegat).order_by('id_nomenclature_degat_type').all()

    # for deg in data_degats:
    #     declarations_filtered = list(filter(lambda x: x.get('id_declaration') == deg.id_declaration, declarations))
    #     if len(declarations_filtered) != 1:
    #         continue
    #     declaration = declarations_filtered[0]
    #     if not declaration.get('degats'):
    #         declaration['degats'] = []
    #     declaration['degats'].append(deg.as_dict(True))

    # pre_get_dict_nomenclature_areas(declarations)
    # declarations = [resolve_declaration(d) for d in declarations]

    return declarations


def resume_gravite(declaration_dict):
    '''
        Donne la pire gravité d'une déclaration
    '''
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


def nomenclatures_to_str(nomenclatures, field_name="mnemonique"):

    if not nomenclatures:
        return ""

    return " ,".join(e[field_name] for e in nomenclatures)


def id_nomenclature_to_str(id_nomenclature, field_name="mnemonique"):

    if not id_nomenclature:
        return ""

    return id_nomenclature[field_name]


# def get_declarations_csv(type_csv):
#     '''
#         type_csv:
#             "degat" -> renvoie une ligne par degat déclaré
#     '''

#     declarations = get_declarations(True)

#     columns = [
#         'id',
#         'Nom_déclarant',
#         'Organisme',
#         'Date',
#         'Nom_forêt',
#         'Statut_foret',
#         'Documentée',
#         'Secteur',
#         'Communes',
#         'Parcelles',

#         'Ess. 1',
#         'Ess. 2',
#         'Ess. 3',

#         'Type de peuplement',
#         'Origine du peuplement',
#         'Maturite du peuplement',

#         'Type de paturage',
#         'Statut du paturage',
#         'Frequence du paturage',
#         'Saisonalité du paturage',

#         'Type de protection',
#         'Autre protection',

#         'Especes',
#         'Accès'

#     ]

#     if type_csv == "degat":

#         columns += [
#             "Type de dégât",
#             "Essence",
#             "Gravité",
#             "Étendue",
#             "Antériorité",
#         ]

#     data = []

#     for declaration in declarations:

#         print(declaration["id_nomenclature_peuplement_paturage_statut"])
#         d = [
#             declaration['id_declaration'],
#             declaration['declarant'],
#             declaration['organisme'].strip() if declaration['organisme'] else "",
#             declaration['date'],

#             # Foret
#             declaration['label_foret'],
#             "Public" if declaration['b_statut_public'] else "Privée",
#             "Oui" if declaration['b_document'] else "Non",
#             ", ".join([a['label'] for a in get_areas_from_type_code(declaration['areas_localisation'], 'OEASC_SECTEUR')]),
#             ", ".join([a['area_name'] for a in get_areas_from_type_code(declaration['areas_foret'], 'OEASC_COMMUNE')]),
#             ", ".join([a['label']for a in
#                       get_areas_from_type_code(declaration['areas_localisation'], 'OEASC_ONF_PRF') +
#                       get_areas_from_type_code(declaration['areas_localisation'], 'OEASC_CADASTRE')]),
#             # Essence(s)
#             id_nomenclature_to_str(declaration["id_nomenclature_peuplement_essence_principale"]),
#             nomenclatures_to_str(declaration["nomenclatures_peuplement_essence_secondaire"]),
#             nomenclatures_to_str(declaration["nomenclatures_peuplement_essence_complementaire"]),

#             # Détails
#             id_nomenclature_to_str(declaration["id_nomenclature_peuplement_type"]),
#             id_nomenclature_to_str(declaration["id_nomenclature_peuplement_origine"]),
#             nomenclatures_to_str(declaration["nomenclatures_peuplement_maturite"]),

#             # Paturage
#             nomenclatures_to_str(declaration["nomenclatures_peuplement_paturage_type"]),
#             id_nomenclature_to_str(declaration["id_nomenclature_peuplement_paturage_statut"]),
#             id_nomenclature_to_str(declaration["id_nomenclature_peuplement_paturage_frequence"]),
#             nomenclatures_to_str(declaration["nomenclatures_peuplement_paturage_saison"]),

#             # Protection
#             nomenclatures_to_str(declaration["nomenclatures_peuplement_protection_type"]),
#             declaration.get('autre_protection', ""),

#             # Autres
#             nomenclatures_to_str(declaration["nomenclatures_peuplement_espece"]),
#             id_nomenclature_to_str(declaration["id_nomenclature_peuplement_acces"]),
#         ]

#         if type_csv == "degat":
#             for degat in declaration.get('degats', []):
#                 if degat.get('degat_essences'):
#                     for degat_essence in degat["degat_essences"]:
#                         deg = [
#                             id_nomenclature_to_str(degat["id_nomenclature_degat_type"]),
#                             id_nomenclature_to_str(degat_essence['id_nomenclature_degat_essence']),
#                             id_nomenclature_to_str(degat_essence.get('id_nomenclature_degat_gravite', '')),
#                             id_nomenclature_to_str(degat_essence.get('id_nomenclature_degat_etendue', '')),
#                             id_nomenclature_to_str(degat_essence.get('id_nomenclature_degat_anteriorite', '')),
#                         ]
#                         data.append(d + deg)

#                 else:
#                     deg = [
#                         id_nomenclature_to_str(degat["id_nomenclature_degat_type"]),
#                         "", "", "", ""
#                     ]

#                     data.append(d + deg)
#         else:
#             data.append(d)

#     return columns, data
