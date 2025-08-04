f"""
    degat module api
"""

from flask import Blueprint, request, session
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
    get_proprietaire_from_id,
    get_declarations,
    hide_proprietaire,
)
from ..declaration.mail import send_mail_validation_declaration
# from ..declaration.repository import get_user
from ..declaration.schema import TProprietaireSchema, TForetSchema, TDeclarationSchema


bp = Blueprint("degat_foret_api", __name__)


# Cette route permet de récupérer les informations du propriétaire à partir de l'identifiant du déclarant.
# Elle est utilisée lorsqu'on souhaite afficher ou utiliser les données du propriétaire liées à un déclarant spécifique.
@bp.route("proprietaire_from_id/<int:id_declarant>", methods=["GET"])
@check_auth_redirect_login(1)
def api_get_proprietaire_from_id(id_declarant):
    # Appel de la fonction pour obtenir le propriétaire selon l'id du déclarant
    (proprietaire) = get_proprietaire_from_id(id_declarant)
    # Sérialisation de l'objet propriétaire en dictionnaire
    proprietaire_dict = TProprietaireSchema().dump(proprietaire)

    # Retourne les informations du propriétaire au format JSON
    return proprietaire_dict



# Cette route permet de récupérer les informations du propriétaire à partir de l'identifiant du déclarant.
# Elle est utilisée lorsqu'on souhaite afficher ou utiliser les données du propriétaire liées à un déclarant spécifique,
# mais en passant par la fonction get_proprietaire_from_id_declarant qui peut différer de get_proprietaire_from_id selon la logique métier.
@bp.route("proprietaire_from_id_declarant/<int:id_declarant>", methods=["GET"])
@check_auth_redirect_login(1)
def api_get_proprietaire_from_id_declarant(id_declarant):
    # Appel de la fonction pour obtenir le propriétaire selon l'id du déclarant
    (proprietaire) = get_proprietaire_from_id_declarant(id_declarant)
    # Sérialisation de l'objet propriétaire en dictionnaire
    proprietaire_dict = TProprietaireSchema().dump(proprietaire)

    # Retourne les informations du propriétaire au format JSON
    return proprietaire_dict




# Cette route permet de récupérer les informations de la forêt à partir de son code.
# Elle est utilisée lorsqu'on souhaite afficher ou utiliser les données d'une forêt spécifique,
# ainsi que celles de son propriétaire. Elle cache le nom du propriétaire si celui-ci est privé.
@bp.route("foret_from_code/<string:code_foret>", methods=["GET"])
@check_auth_redirect_login(1)
def api_get_foret_from_code(code_foret):
    # Récupère la forêt et son propriétaire à partir du code de la forêt
    (foret, proprietaire) = get_foret_from_code(code_foret)
    # Sérialise l'objet forêt en dictionnaire
    foret_dict = TForetSchema().dump(foret)
    # Sérialise l'objet propriétaire en dictionnaire
    proprietaire_dict = TProprietaireSchema().dump(proprietaire)
    
    # Fusionne les informations du propriétaire dans le dictionnaire de la forêt
    foret_dict.update(proprietaire_dict)

    # Récupère la nomenclature du type de propriétaire
    nomenclature = get_nomenclature_from_id(
        proprietaire.id_nomenclature_proprietaire_type
    )
    # Si le propriétaire est privé, on cache ses informations personnelles
    if nomenclature["cd_nomenclature"] == "PT_PRI":
        hide_proprietaire(foret_dict)

    # Retourne les informations de la forêt (et du propriétaire) au format JSON
    return foret_dict


# Cette route permet de récupérer la liste de toutes les déclarations de dégâts en forêt.
# Elle est généralement utilisée lors de l'affichage d'une liste globale des déclarations,
# par exemple dans une page d'administration ou pour un utilisateur ayant les droits nécessaires.
# Elle est appelée à l'initialisation du serveur ou lors de la consultation de l'ensemble des déclarations.
@bp.route("declarations/", methods=["GET"])
@check_auth_redirect_login(1)  # Vérifie que l'utilisateur est authentifié (niveau 1 minimum)
@json_resp_accept_empty_list   # Retourne une liste vide si aucune déclaration n'est trouvée
def api_get_declarations():
    # Appelle la fonction qui récupère toutes les déclarations depuis la base de données
    return get_declarations()



# Cette route permet de récupérer une déclaration simple, sans les informations détaillées des zones ("areas").
# Elle est utilisée lorsqu'on souhaite afficher ou utiliser les données principales d'une déclaration,
# sans avoir besoin des détails géographiques ou cadastraux associés.
# Typiquement, cette route est appelée pour un affichage rapide ou une consultation simplifiée d'une déclaration.
@bp.route("declaration_simple/<int:id_declaration>", methods=["GET"])
@bp.route("declaration_simple/", methods=["GET"], defaults={"id_declaration": None})
@check_auth_redirect_login(1)  # Vérifie que l'utilisateur est authentifié (niveau 1 minimum)
@json_resp_accept_empty_list   # Retourne une liste vide si aucune déclaration n'est trouvée
def api_get_declaration_simple(id_declaration):
    """
    Récupère une déclaration simple (sans les areas), ainsi que les données de la forêt et du propriétaire.
    Utilisé pour l'affichage ou la consultation rapide d'une déclaration.
    """

    # Récupère la déclaration, la forêt et le propriétaire associés à l'identifiant donné
    (declaration, foret, proprietaire) = get_declaration(id_declaration)

    # Si aucune déclaration n'est trouvée, retourne une réponse vide
    if not declaration:
        return

    # Sérialise l'objet déclaration en dictionnaire
    declaration_dict = TDeclarationSchema().dump(declaration)
 
    # Sérialise l'objet forêt en dictionnaire et fusionne avec la déclaration
    foret_dict = TForetSchema().dump(foret) if foret else {}
    declaration_dict.update(foret_dict)

    # Sérialise l'objet propriétaire en dictionnaire et fusionne avec la déclaration
    proprietaire_dict = TProprietaireSchema().dump(proprietaire) if proprietaire else {}
    declaration_dict.update(proprietaire_dict)

    # Ajoute l'identifiant du déclarant dans le dictionnaire de la déclaration
    id_declarant = declaration.id_declarant
    declaration_dict["id_declarant"] = id_declarant

    # Pour chaque clé du dictionnaire, si la valeur est une liste d'objets contenant "id_nomenclature",
    # on transforme cette liste en une liste d'identifiants de nomenclature uniquement.
    # Cela permet de simplifier la structure des données retournées.
    for key in declaration_dict:
        if (
            isinstance(declaration_dict[key], list)
            and len(declaration_dict[key]) > 0
            and "id_nomenclature" in declaration_dict[key][0]
        ):
            declaration_dict[key] = [e["id_nomenclature"] for e in declaration_dict[key]]

    # Cache les informations personnelles du propriétaire si l'utilisateur n'est pas le déclarant
    # ou si son niveau d'accès est inférieur à 4 (donc pas administrateur).
    # Ceci permet de protéger la vie privée du propriétaire.
    current_user = session.get("current_user", None)
    if (current_user["max_level_profil"] < 4) and (
        current_user["id_role"] != declaration_dict["id_declarant"]
    ):
        hide_proprietaire(declaration_dict)

    # Retourne le dictionnaire de la déclaration au format JSON
    return declaration_dict



# Cette route permet de récupérer une déclaration complète, incluant les données de la forêt, du propriétaire,
# ainsi que toutes les zones ("areas") associées à la forêt et à la déclaration.
# Elle est utilisée notamment pour l'affichage détaillé d'une déclaration, par exemple dans le composant "voir_declaration.vue".
@bp.route("declaration/<int:id_declaration>", methods=["GET"])
@bp.route("declaration/", methods=["GET"], defaults={"id_declaration": None})
@check_auth_redirect_login(1)  # Vérifie que l'utilisateur est authentifié (niveau 1 minimum)
@json_resp_accept_empty_list   # Retourne une liste vide si aucune déclaration n'est trouvée
def api_get_declaration(id_declaration):
    """
    Récupère une déclaration complète avec toutes les informations nécessaires à l'affichage détaillé.
    Utilisée pour consulter ou afficher une déclaration avec ses zones géographiques.
    """

    # Récupère la déclaration, la forêt et le propriétaire associés à l'identifiant donné
    (declaration, foret, proprietaire) = get_declaration(id_declaration)

    # Si aucune déclaration n'est trouvée, retourne une réponse vide
    if not declaration:
        return

    # Sérialise l'objet déclaration en dictionnaire
    declaration_dict = TDeclarationSchema().dump(declaration)

    # Sérialise l'objet forêt en dictionnaire et fusionne avec la déclaration
    foret_dict = TForetSchema().dump(foret) if foret else {}
    declaration_dict.update(foret_dict)

    # Sérialise l'objet propriétaire en dictionnaire et fusionne avec la déclaration
    proprietaire_dict = TProprietaireSchema().dump(proprietaire) if proprietaire else {}
    declaration_dict.update(proprietaire_dict)
    
    # Ajoute l'identifiant du déclarant dans le dictionnaire de la déclaration
    id_declarant = declaration.id_declarant
    declaration_dict["id_declarant"] = id_declarant

    # Pour chaque clé du dictionnaire, si la valeur est une liste d'objets contenant "id_nomenclature",
    # on transforme cette liste en une liste d'identifiants de nomenclature uniquement.
    # Cela permet de simplifier la structure des données retournées.
    for key in declaration_dict:
        if (
            isinstance(declaration_dict[key], list)
            and len(declaration_dict[key]) > 0
            and "id_nomenclature" in declaration_dict[key][0]
        ):
            declaration_dict[key] = [e["id_nomenclature"] for e in declaration_dict[key]]

    # Récupère et classe les zones ("areas") de la forêt selon leur type
    areas_foret = [
        get_area_from_id(area["id_area"]) for area in declaration_dict.get("areas_foret", [])
    ]
    declaration_dict["areas_foret_onf"] = get_id_area(areas_foret, ["OEASC_ONF_FRT"])
    declaration_dict["areas_foret_dgd"] = get_id_area(areas_foret, ["OEASC_DGD"])
    declaration_dict["areas_foret_communes"] = get_id_areas(areas_foret, ["OEASC_COMMUNE"])
    declaration_dict["areas_foret_sections"] = get_id_areas(areas_foret, ["OEASC_SECTION"])

    # Récupère et classe les zones ("areas") de la déclaration selon leur type
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

    # Cache les informations personnelles du propriétaire si l'utilisateur n'est pas le déclarant
    # ou si son niveau d'accès est inférieur à 4 (donc pas administrateur).
    # Ceci permet de protéger la vie privée du propriétaire.
    current_user = session.get("current_user", None)
    if ((current_user is not None) and (current_user["max_level_profil"] < 4) and (
        current_user["id_role"] != declaration_dict["id_declarant"]
    )):
        hide_proprietaire(declaration_dict)

    # Retourne le dictionnaire de la déclaration complète au format JSON
    return declaration_dict


# Cette route permet de modifier une déclaration existante via une requête PATCH.
# Elle est utilisée lorsqu'un utilisateur souhaite mettre à jour les informations d'une déclaration
# déjà enregistrée dans la base de données, par exemple pour corriger une erreur ou ajouter des précisions.
@bp.route("declaration", methods=["PATCH"])
@check_auth_redirect_login(1)  # Vérifie que l'utilisateur est authentifié (niveau 1 minimum)
@json_resp  # Retourne la réponse au format JSON
def api_post_declaration():
    """
    Met à jour une déclaration existante.
    Utilisée lors de la modification d'une déclaration par un utilisateur autorisé.
    """

    # Récupère les données envoyées dans la requête PATCH (au format JSON)
    post_data = request.get_json()
    # Appelle la fonction qui crée ou met à jour la déclaration dans la base de données
    # Ici, on suppose que l'identifiant de la déclaration existe déjà dans post_data
    result_declaration = create_or_update_declaration(post_data)
    # Envoie un mail de notification pour informer de la modification de la déclaration
    # (le second paramètre "False" indique qu'il ne s'agit pas d'une création mais d'une modification)
    send_mail_validation_declaration(result_declaration, False)
    # Retourne le résultat de la modification au format JSON
    return result_declaration


# Cette route permet de créer une nouvelle déclaration de dégât en forêt via une requête POST.
# Elle est utilisée lorsqu'un utilisateur souhaite enregistrer une nouvelle déclaration dans la base de données.
# Typiquement, cette route est appelée lors de la soumission d'un formulaire de déclaration par un utilisateur.
@bp.route("declaration", methods=["POST"])
@check_auth_redirect_login(1)  # Vérifie que l'utilisateur est authentifié (niveau 1 minimum)
@json_resp  # Retourne la réponse au format JSON
def api_patch_declaration():
    """
    Crée une nouvelle déclaration de dégât en forêt.
    Utilisée lors de la soumission d'une déclaration par un utilisateur.
    """

    # Récupère les données envoyées dans la requête POST (au format JSON)
    post_data = request.get_json()

    # Détermine s'il s'agit d'une création (True si aucun id_declaration n'est présent)
    b_create = not (post_data.get("id_declaration"))

    # Appelle la fonction qui crée ou met à jour la déclaration dans la base de données
    # Ici, on suppose que l'identifiant de la déclaration n'existe pas encore (création)
    post_data_arranged = create_or_update_declaration(post_data)

    # Envoie un mail de notification pour informer de la création de la déclaration
    # (décommenter la ligne ci-dessous pour activer l'envoi de mail après les tests)
    # send_mail_validation_declaration(post_data_arranged, b_create)

    # Affiche dans la console les données arrangées pour vérification lors des tests
    print("post_data_arranged", post_data_arranged)

    # Retourne le résultat de la création au format JSON
    return post_data_arranged
