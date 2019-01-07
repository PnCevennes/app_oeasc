from flask import Blueprint, render_template, request, current_app, session
import copy
from app.modules.oeasc.nomenclature import nomenclature_oeasc

from .repository import (
    get_declarations,
    get_declaration,
    f_create_or_update_declaration,
    get_dict_nomenclature_areas,
)

from .declaration_sample import declaration_dict_random_sample

from .utils import (
    get_listes_essences,
    check_foret,
    check_proprietaire,
    check_massif,
)

from .models import (
    TDeclaration,
)

# from app.utils.env import DB

from app.utils.utilssqlalchemy import json_resp

from .mail import send_mail_validation_declaration

from ..user.utils import check_auth_redirect_login
bp = Blueprint('declaration_api', __name__)

config = current_app.config
DB = config['DB']


@bp.route('declarations/', defaults={'id_declarant': -1}, methods=['GET'])
@bp.route('declarations/<int:id_declarant>', methods=['GET'])
@json_resp
def declarations(id_declarant):
    '''
        Retourne les declarations accessible pour le declarant de id_role id_declarant
    '''

    b_synthese = (id_declarant == -1)

    return get_declarations(b_synthese, id_declarant)


@bp.route('declaration/<int:id_declaration>', methods=['GET'])
@check_auth_redirect_login(1)
@json_resp
def declaration(id_declaration):
    '''
        Retourne la declaration d'id id_declaration
    '''

    declaration = get_declaration(id_declaration, session.current_user)

    if not declaration:
        return None

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
    check_massif(declaration_dict)

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
    get_dict_nomenclature_areas(declaration_dict)
    return declaration_dict['degats']


@bp.route('random_populate', defaults={'nb': 1}, methods=['GET'])
@bp.route('random_populate/<int:nb>', methods=['GET'])
@check_auth_redirect_login(5)
@json_resp
def random_populate(nb):
    '''
        Crée et ajoute en base nb déclarations
    '''

    for i in range(nb):

        declaration_dict = declaration_dict_random_sample()

        if not declaration_dict:
            continue

        declaration_dict_2 = copy.deepcopy(declaration_dict)
        get_dict_nomenclature_areas(declaration_dict_2)

        id_area = check_massif(declaration_dict_2)
        if not id_area:
            continue

        declaration_dict['areas_localisation'].append({'id_area': id_area})
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
    send_mail_validation_declaration(d)

    return d
