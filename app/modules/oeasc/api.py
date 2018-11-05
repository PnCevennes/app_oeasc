# -*- coding: utf-8 -*
from flask import (
    Blueprint, render_template, request
)

from .repository import (
    nomenclature_oeasc,
    get_declarations,
    get_db,
    f_create_or_update_declaration,
    get_dict_nomenclature_areas,
)

from .declaration_sample import declaration_dict_random_sample

from .utils import (
    get_listes_essences,
    check_foret,
    check_proprietaire
)

from .models import (
    TDeclaration,
    TForet
)

from app.utils.env import DB

from app.utils.utilssqlalchemy import json_resp

from app.ref_geo.models import LAreas

from .mail import send_mail_validation_declaration

from .utils import check_auth_redirect_login


bp = Blueprint('oeasc_api', __name__)


@bp.route('get_nomenclature_oeasc', methods=['GET'])
@json_resp
def get_nomenclature_oeasc():
    '''
        Retourne un dictionnaire contenant toutes les nomenclatures concernant l'oeasc

        Exemple:

        nomenclature = nomenclature_oeasc()
        for elem in nomenclature["OEASC_PEUPLEMENT_ESSENCE"]["values"]:
            print(elem.label_fr)
    '''

    return nomenclature_oeasc()


@bp.route('declarations/', defaults={'id_declarant': -1}, methods=['GET'])
@bp.route('declarations/<int:id_declarant>', methods=['GET'])
@json_resp
def declarations(id_declarant):
    '''
        Retourne les declarations accessible pour le declarant de id_role id_declarant
    '''

    b_synthese = id_declarant == -1

    return get_declarations(b_synthese, id_declarant)


@bp.route('declaration/<int:id_declaration>', methods=['GET'])
@json_resp
def declaration(id_declaration):
    '''
        Retourne la declaration d'id id_declaration
    '''

    declaration = DB.session.query(TDeclaration).filter(TDeclaration.id_declaration == id_declaration).first()

    if not declaration:

        return "La déclaration d'identifiant : " + str(id_declaration) + " n'existe pas."

    return declaration.as_dict(True)


@bp.route('get_form_declaration', methods=['POST'])
@check_auth_redirect_login(1)
@json_resp
def get_form_declaration():
    '''
        Retourne le formulaire correspondant à la déclaration envoyée en post dans data['declaration']
    '''

    data = request.get_json()

    nomenclature = nomenclature_oeasc()

    declaration_dict = data['declaration']
    id_form = data['id_form']

    # recherche de la  foret le cas echeant (apres un choix de foret documentee)
    get_dict_nomenclature_areas(declaration_dict)

    check_foret(declaration_dict)
    check_proprietaire(declaration_dict)

    listes_essences = get_listes_essences(declaration_dict)

    return render_template('modules/oeasc/form/form_declaration.html', declaration=declaration_dict, nomenclature=nomenclature, listes_essences=listes_essences, id_form=id_form)


@bp.route('delete_declaration/<int:id_declaration>', methods=['POST'])
@check_auth_redirect_login(4)
@json_resp
def delete_declaration(id_declaration):
    '''
        Supprime une déclaration (id_déclaration)
    '''

    DB.session.query(
        TDeclaration).filter(
        TDeclaration.id_declaration == id_declaration).delete()

    DB.session.commit()

    return "ok"


@bp.route('random_declaration', methods=['GET'])
@check_auth_redirect_login(5)
@json_resp
def random_declaration():
    '''
        Renvoie une déclaration crée aléatoirement
    '''

    declaration_dict = declaration_dict_random_sample()

    return declaration_dict


@bp.route('random_populate', defaults={'nb': 1}, methods=['GET'])
@bp.route('random_populate/<int:nb>', methods=['GET'])
@check_auth_redirect_login(5)
@json_resp
def random_populate(nb):
    '''
        Crée et ajoute en base nb déclarations
    '''
    print(nb)

    for i in range(nb):

        declaration_dict = declaration_dict_random_sample()
        print(i, declaration_dict)

        if not declaration_dict:

            continue

        nomenclature = nomenclature_oeasc()

        # check_foret(declaration_dict, nomenclature)
        # check_proprietaire(declaration_dict, nomenclature)
        declaration_dict = f_create_or_update_declaration(declaration_dict)

        print("i", i, nb, declaration_dict["id_declaration"], declaration_dict["foret"]["nom_foret"], "public", declaration_dict["foret"]["b_statut_public"], "documenté", declaration_dict["foret"]["b_document"])

    return "ok"


@bp.route('create_or_update_declaration', methods=['POST'])
@check_auth_redirect_login(1)
@json_resp
def create_or_update_declaration():
    '''
        cree une nvlle déclaration quand id déclaration est renseigné
        ou
        update une declaration existante
    '''

    data = request.get_json()

    declaration_dict = data["declaration"]

    d = f_create_or_update_declaration(declaration_dict)

    send_mail_validation_declaration(declaration_dict)

    return d


@bp.route('get_db/<type>/<key>/<val>', methods=['GET'])
@json_resp
def api_get_db(type, key, val):
    '''
        pfff
    '''
    return get_db(type, key, val)


@bp.route('declaration_areas/<int:id_declaration>/<string:type>', methods=['GET'])
@json_resp
def declaration_areas(id_declaration, type):
    '''
        renvoie les aires forêt (Commune, Section, DGD, ONF_FRT) ou localisation (ONF_PRF, ONF_UG, CADASTRE).
    '''

    declaration = DB.session.query(TDeclaration).filter(TDeclaration.id_declaration == id_declaration).first()

    id_foret = declaration.id_foret

    foret = DB.session.query(TForet).filter(TForet.id_foret == id_foret).first()

    areas = []

    if type == "foret":

        areas = foret.areas_foret

    else:

        areas = declaration.areas_localisation

    v = [a.id_area for a in areas]

    out = []

    for id_area in v:

        data = DB.session.query(LAreas).filter(LAreas.id_area == id_area).first()
        out.append(data.get_geofeature())

    return out
