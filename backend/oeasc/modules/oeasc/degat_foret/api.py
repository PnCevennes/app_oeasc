f"""
    degat module api
"""

from flask import Blueprint, request, current_app, session
from ..nomenclature import get_area_from_id, get_nomenclature_from_id
from utils_flask_sqla.response import json_resp, json_resp_accept_empty_list
from ..user.utils import check_auth_redirect_login
from .repository import (
    create_or_update_declaration,
    get_declaration,
    get_id_area,
    get_id_areas,
    get_foret_from_code,
    get_proprietaire_from_id_declarant,
    get_declarations,
    hide_proprietaire,
)
from ..declaration.mail import send_mail_validation_declaration
from ..declaration.repository import get_user
from ..declaration.schema import TProprietaireSchema, TForetSchema, TDeclarationSchema


bp = Blueprint("degat_foret_api", __name__)


@bp.route("proprietaire_from_id_declarant/<int:id_declarant>", methods=["GET"])
@check_auth_redirect_login(1)
def api_get_proprietaire_from_id_declarant(id_declarant):
    (proprietaire) = get_proprietaire_from_id_declarant(id_declarant)
    proprietaire_dict = TProprietaireSchema().dump(proprietaire)

    return proprietaire_dict


@bp.route("foret_from_code/<string:code_foret>", methods=["GET"])
@check_auth_redirect_login(1)
def api_get_foret_from_code(code_foret):
    (foret, proprietaire) = get_foret_from_code(code_foret)
    foret_dict = TForetSchema().dump(foret)
    proprietaire_dict = TProprietaireSchema().dump(proprietaire)
    
    # out = foret.as_dict(fields=["areas_foret"])
    foret_dict.update(proprietaire_dict)
    # out.update(proprietaire.as_dict())

    nomenclature = get_nomenclature_from_id(
        proprietaire.id_nomenclature_proprietaire_type
    )
    if nomenclature["cd_nomenclature"] == "PT_PRI":
        hide_proprietaire(foret_dict)

    return foret_dict


@bp.route("declarations/", methods=["GET"])
@check_auth_redirect_login(1)
@json_resp_accept_empty_list
# est appelé à l'initialisation du serveur. Mais 
def api_get_declarations():
    return get_declarations()


@bp.route("declaration/<int:id_declaration>", methods=["GET"])
@bp.route("declaration/", methods=["GET"], defaults={"id_declaration": None})
@check_auth_redirect_login(1)
@json_resp_accept_empty_list
def api_get_declaration(id_declaration):
    """
    api_get_declaraiton
    """

    (declaration, foret, proprietaire) = get_declaration(id_declaration)

    if not declaration:
        return

    declaration_dict = TDeclarationSchema().dump(declaration)
    # out = declaration.as_dict(fields=[
    #             "areas_localisation",
    #             "nomenclatures_peuplement_essence_secondaire",
    #             "nomenclatures_peuplement_essence_complementaire",
    #             "nomenclatures_peuplement_maturite",
    #             "nomenclatures_peuplement_protection_type",
    #             "nomenclatures_peuplement_paturage_type",
    #             "nomenclatures_peuplement_paturage_saison",
    #             "nomenclatures_peuplement_espece",
    #             "nomenclatures_peuplement_origine2",
    #             "degats",
    #             "degats.degat_essences"
    #             ])

    # flat data

    foret_dict = TForetSchema().dump(foret) if foret else {}
    declaration_dict.update(foret_dict)

    


    proprietaire_dict = TProprietaireSchema().dump(proprietaire) if proprietaire else {}

    declaration_dict.update(proprietaire_dict)
    # out.update(proprietaire.as_dict())
    
    id_declarant = declaration.id_declarant
    declaration_dict["id_declarant"] = id_declarant

    # nomenclature
    for key in declaration_dict:
        if (
            isinstance(declaration_dict[key], list)
            and len(declaration_dict[key]) > 0
            and "id_nomenclature" in declaration_dict[key][0]
        ):
            declaration_dict[key] = [e["id_nomenclature"] for e in declaration_dict[key]]

    # id_areas TODO in front

    #   foret
    areas_foret = [
        get_area_from_id(area["id_area"]) for area in declaration_dict.get("areas_foret", [])
    ]

    declaration_dict["areas_foret_onf"] = get_id_area(areas_foret, ["OEASC_ONF_FRT"])
    declaration_dict["areas_foret_dgd"] = get_id_area(areas_foret, ["OEASC_DGD"])
    declaration_dict["areas_foret_communes"] = get_id_areas(areas_foret, ["OEASC_COMMUNE"])
    declaration_dict["areas_foret_sections"] = get_id_areas(areas_foret, ["OEASC_SECTION"])

    #   declaration
    areas_localisation = [
        get_area_from_id(area["id_area"]) for area in declaration_dict.get("areas_localisation", [])
    ]
    declaration_dict["areas_localisation_cadastre"] = get_id_areas(
        areas_localisation, ["OEASC_CADASTRE"]
    )
    declaration_dict["areas_localisation_onf_prf"] = get_id_areas(
        areas_localisation, ["OEASC_ONF_PRF"]
    )
    declaration_dict["areas_localisation_onf_ug"] = get_id_areas(
        areas_localisation, ["OEASC_ONF_UG"]
    )

    # hide proprietaire
    current_user = session.get("current_user", None)
    
    if (current_user["max_level_profil"] < 4) and (
        current_user["id_role"] != declaration_dict["id_declarant"]
    ):
        hide_proprietaire(declaration_dict)

    return declaration_dict


@bp.route("declaration", methods=["PATCH"])
@check_auth_redirect_login(1)
@json_resp
def api_post_declaration():
    """
    api_post_declaration
    """

    post_data = request.get_json()
    result_declaration = create_or_update_declaration(post_data)
    send_mail_validation_declaration(result_declaration, False)
    return result_declaration


@bp.route("declaration", methods=["POST"])
@check_auth_redirect_login(1)
@json_resp
def api_patch_declaration():
    """
    api_post_declaration
    """
    post_data = request.get_json()
    b_create = not (post_data.get("id_declaration"))
    post_data_arranged = create_or_update_declaration(post_data)
    # remettre après l'envoi de mail. Enlevez pour ne pas spammer pendant les test
    # send_mail_validation_declaration(post_data_arranged, b_create)

    print ("post_data_arranged", post_data_arranged)
    return post_data_arranged
