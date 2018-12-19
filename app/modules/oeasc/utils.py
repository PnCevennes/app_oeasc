from dateutil import parser


from app.utils.utilssqlalchemy import as_dict

from werkzeug.datastructures import Headers
from flask import Response

from app.ref_geo.models import TAreas

from pypnusershub.db.models import User

from .models import (
    TForet,
    TProprietaire
)

from .repository import (

    nomenclature_oeasc,
    get_nomenclature_from_id,
    get_nomenclature,
    get_db,
    get_dict_nomenclature_areas,
    get_foret_type,
)

from flask import request, current_app
from functools import wraps
from pypnusershub import routes as fnauth

from sqlalchemy import func

config = current_app.config
DB = config['DB']


def check_auth_redirect_login(level):
    '''
        use fnauth.check_auth to check user auth
        if not auth redirect to the login page with the requested url as request argument
    '''
    def _check_auth_redirect_login(f):
        @wraps(f)
        def __check_auth_redirect_login(*args, **kwargs):
            redirect_url = 'user/login?redirect="' + request.url + '"'
            return fnauth.check_auth(level, False, redirect_url)(f)(*args, **kwargs)
        return __check_auth_redirect_login
    return _check_auth_redirect_login


def get_listes_essences(declaration):
    '''
        retourne un dictionnaire conenant des liste d'essences pour la creation du formulaire
            selected : liste des essence selectionnnee dans principale, secondaires et complementaire
            feuillus : liste des id_nomenclature pour les feuillus a laquelle on enleve les selectionnee
            resineux ...
            degats.id_nomenclature_degat_type: pour un type de degat :
                les essence selectionnées en global (selected) moins les essences concernant ce type de degat
    '''

    print(declaration)
    nomenclature = nomenclature_oeasc()

    listes_essences = {}

    listes_essences["feuillus"] = []
    listes_essences["resineux"] = []
    listes_essences["selected"] = []
    listes_essences["selected_degat"] = []

    d = declaration.get("id_nomenclature_peuplement_essence_principale", None)

    if d:
        listes_essences["selected"].append(d["id_nomenclature"])
        listes_essences["selected_degat"].append(d["id_nomenclature"])

    for d in declaration["nomenclatures_peuplement_essence_secondaire"]:
        listes_essences["selected"].append(d["id_nomenclature"])
        listes_essences["selected_degat"].append(d["id_nomenclature"])

    for d in declaration["nomenclatures_peuplement_essence_complementaire"]:
        listes_essences["selected"].append(d["id_nomenclature"])

    b_feuillus = True

    for elem in nomenclature["OEASC_PEUPLEMENT_ESSENCE"]["values"]:

        id = elem['id_nomenclature']

        if id not in listes_essences['selected']:

            if b_feuillus:

                listes_essences["feuillus"].append(id)

            else:

                listes_essences["resineux"].append(id)

        b_feuillus = b_feuillus and (elem['cd_nomenclature'] != "AF")  # PeuplementEssence_AutresFeuillus

    listes_essences["degats"] = {}

    for degat in declaration["degats"]:

        id_nomenclature_degat_type = degat["id_nomenclature_degat_type"]["id_nomenclature"]

        listes_essences["degats"][id_nomenclature_degat_type] = [e for e in listes_essences["selected_degat"]]

        for degat_essence in degat.get('degat_essences', []):

            if degat_essence != {} and degat_essence["id_nomenclature_degat_essence"] and degat_essence["id_nomenclature_degat_essence"]["id_nomenclature"] in listes_essences["degats"][id_nomenclature_degat_type]:

                listes_essences["degats"][id_nomenclature_degat_type].remove(degat_essence["id_nomenclature_degat_essence"]["id_nomenclature"])

    for key in listes_essences:

        if key == "degats":

            for key_ in listes_essences["degats"]:

                v = []

                for e in listes_essences["degats"][key_]:

                    elem = get_nomenclature_from_id(e)
                    v.append(elem)

                listes_essences["degats"][key_] = v

        else:

            v = []

            for e in listes_essences[key]:

                elem = get_nomenclature_from_id(e)
                v.append(elem)

            listes_essences[key] = v

    return listes_essences


def copy_list(liste):

    return [elem for elem in liste]


def check_massif(declaration_dict):
    '''
        renseigne le massif dans declaration_dict['areas_localisation'] si non renseigné
    '''

    areas = get_areas_from_type_code(declaration_dict['areas_localisation'], 'OEASC_CADASTRE')
    areas += get_areas_from_type_code(declaration_dict['areas_localisation'], 'OEASC_ONF_UG')
    areas += get_areas_from_type_code(declaration_dict['areas_localisation'], 'OEASC_ONF_PRF')

    if not areas:

        return

    areas_massif = get_areas_from_type_code(declaration_dict['areas_localisation'], 'OEASC_SECTEUR')

    if areas_massif:

        return

    id_areas = [area['id_area'] for area in areas]

    area = DB.session.query(TAreas).filter(TAreas.id_area == func.ref_geo.get_massif(id_areas)).first()

    if not area:

        return

    dict_massif = {'areas_localisation': [{'id_area': area.id_area}]}
    get_dict_nomenclature_areas(dict_massif)
    # declaration_dict['areas_localisation'].append({'id_area': area.id_area})
    declaration_dict['areas_localisation'].append(dict_massif['areas_localisation'][0])

    return area.id_area
    # get_dict_nomenclature_areas(declaration_dict)


def check_proprietaire(declaration_dict):
    '''
        Dans le cas ou le propretaire est le declarant
    '''

    if declaration_dict['foret'].get('b_document', None) != False or declaration_dict['foret'].get('b_statut_public', None) != False:
        return -1

    # si le proprietaire est déjà renseigné
    if declaration_dict['foret']['id_proprietaire']:

        return -1

    proprietaire_dict = declaration_dict['foret']['proprietaire']

    # si les champs sont déjà tous remplis
    cond = proprietaire_dict["nom_proprietaire"] \
        and proprietaire_dict["email"] \
        and proprietaire_dict["id_declarant"] \
        and proprietaire_dict["adresse"] \
        and proprietaire_dict["s_code_postal"] \
        and proprietaire_dict["s_commune_proprietaire"] \
        and proprietaire_dict["id_nomenclature_proprietaire_type"]

    if cond:

        return -1

    if not declaration_dict['id_nomenclature_proprietaire_declarant']:

        return -1

    cd_nomenclature = declaration_dict['id_nomenclature_proprietaire_declarant']['cd_nomenclature']

    # si le declarant n'est pas le proprietaire
    if cd_nomenclature != 'P_D_O_NP':

        declaration_dict['foret']['proprietaire'] = TProprietaire().as_dict()
        return -1

    # sinon  on recherche le proprietaire correspondant a l'id declarant
    id_declarant_proprietaire = declaration_dict['foret']['proprietaire']['id_declarant']

    if id_declarant_proprietaire:

        proprietaire = DB.session.query(TProprietaire).filter(id_declarant_proprietaire == TProprietaire.id_declarant).first()
        if proprietaire:
            declaration_dict['foret']['proprietaire'] = proprietaire.as_dict(True)

            return 1

        # on retourne juste les infos contenues dans user
        else:

            user = DB.session.query(User).filter(User.id_role == id_declarant_proprietaire).first()

            if not user:

                return -1

            user_dict = as_dict(user)

            proprietaire_dict = TProprietaire().as_dict()
            proprietaire_dict["nom_proprietaire"] = user_dict["nom_role"] + " " + user_dict["prenom_role"]
            proprietaire_dict["email"] = user_dict["email"]
            proprietaire_dict["id_declarant"] = user_dict["id_role"]
            proprietaire_dict["id_nomenclature_proprietaire_type"] = get_nomenclature('cd_nomenclature', 'PT_PRI', 'OEASC_PROPRIETAIRE_TYPE')
            declaration_dict['foret']['proprietaire'] = proprietaire_dict
            return 1

    return -1


def get_foret_from_name(nom_foret):

    data = DB.session.query(TForet).filter(TForet.nom_foret == nom_foret).first()

    if not data:

        return None

    return data.as_dict(True)


def check_foret(declaration_dict):
    '''
        recherche une foret quand une aire de type ONF_FRT ou DGD est renseignée
    '''

    nomenclature = nomenclature_oeasc()

    foret_dict = declaration_dict.get("foret", None)

    if not foret_dict:

        return False

    id_foret = foret_dict.get("id_foret", None)
    areas_foret = foret_dict.get("areas_foret", None)

    if id_foret or not areas_foret:

        return False

    v_type_code = ["OEASC_ONF_FRT", "OEASC_DGD"]

    areas_foret = list(filter(lambda x: x.get("type_code", None) in v_type_code, areas_foret))

    if not areas_foret:

        return False

    nom_foret = areas_foret[0].get('area_name', "")

    foret = get_foret_from_name(nom_foret)

    if not foret:

        return False

    # declaration_dict['foret'] = foret

    id_proprietaire = foret.get('id_proprietaire', None)

    if not id_proprietaire:

        return False

    proprietaire = DB.session.query(TProprietaire).filter(
        id_proprietaire == TProprietaire.id_proprietaire).first()

    if not proprietaire:

        return False

    foret['proprietaire'] = proprietaire.as_dict(True)
    get_dict_nomenclature_areas(foret)

    declaration_dict["foret"] = foret


def print_date(s_date):
    """
        pour affichage dans tableau
    """
    return parser.parse(s_date).strftime("%Y-%m-%d")


def print_commune(s_commune):

    return '-'.join(s_commune.split('-')[1:])


def print_parcelle(s_parcelle):

    if s_parcelle[-1] == '-':

        return s_parcelle[:-1]

    return s_parcelle


def arrays_to_csv(filename, data, columns, separator):

    outdata = [separator.join(columns)]

    headers = Headers()
    headers.add('Content-Type', 'text/plain')
    headers.add(
        'Content-Disposition',
        'attachment',
        filename='export_%s.csv' % filename
    )

    for l in data:
        outdata.append(
            separator.join(
                '"%s"' % (str(e)) for e in l
            )
        )

    out = '\r\n'.join(outdata)

    return Response(out, headers=headers)


def get_areas_from_type_code(areas, type_code):

    out = []

    for area in areas:

        if area['type_code'] == type_code:

            out.append(area)

    return out


def get_some_config(config_text):

    keys = [
        "ID_APP",
        "MODE_TEST",
        "URL_USERHUB",
        "URL_APPLICATION",
    ]

    return {k: v for k, v in config_text.items() if k in keys}


utils_dict = {
    "copy_list": copy_list,
    "get_db": get_db,
    "get_nomenclature_from_id": get_nomenclature_from_id,
    'print_date': print_date,
    'print_commune': print_commune,
    'print_parcelle': print_parcelle,
    'get_areas_from_type_code': get_areas_from_type_code,
    'get_foret_type': get_foret_type,
    'get_some_config': get_some_config,
}
