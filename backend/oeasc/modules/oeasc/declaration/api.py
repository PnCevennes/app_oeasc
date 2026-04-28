"""
liste des api pour les declarations
"""

from datetime import date, datetime, timedelta
from flask import Blueprint, request, current_app, session
from flask.helpers import send_from_directory
import json
from pathlib import Path
import geopandas as gpd  # pour l'export en gpkg
from shapely import wkb, wkt  # pour l'export en gpkg (verification de la géométrie)
import pandas as pd  # pour l'export en csv
from utils_flask_sqla.response import json_resp
from sqlalchemy import delete
from oeasc.utils.apiResponse import ApiResponse

from ..declaration.mail import (
    send_mail_validation_declaration,
    send_mail_alerte_renouvellement_declaration,
    send_mail_echec_renouvellement_declaration,
    send_mail_actualisation_declaration,
    send_mail_alerte_cloture_declaration,
)

from ..nomenclature import get_nomenclature_from_id
from .repository import (
    get_user,
    get_fiche_declaration,
    get_liste_declarations,
    create_or_update_declaration,
    get_foret_from_code,
    get_proprietaire_from_id,
    hide_proprietaire,
    get_form_declaration,
    check_token_renouvellement_declaration,
)
from ..user.utils import check_auth_redirect_login

from .all_stmt import (
    get_stmt_for_declarations_export,
    stmt_one_declaration_a_renouveler,
    stmt_change_statut_declaration,
    get_stmt_all_areas_declaration,
    get_stmt_for_resultats_degats,
)
from .models import TDeclaration
from ..declaration.schema import TProprietaireSchema, TForetSchema
from oeasc.ref_geo.schema import LAreasSchema

bp = Blueprint("declaration_api", __name__)


def get_config():
    return current_app.config


def get_db():
    return get_config()["DB"]


######################################################################################
#################   RECUPÉRATION DE DONNÉES (GET)     ################################
######################################################################################


# Cette route permet de récupérer les informations du propriétaire à partir de l'identifiant du déclarant.
# Elle est utilisée lorsqu'on souhaite afficher ou utiliser les données du propriétaire liées à un déclarant spécifique.
@bp.route("proprietaire_from_id/<int:id_declarant>", methods=["GET"])
@check_auth_redirect_login(1)
def api_get_proprietaire_from_id(id_declarant):
    # Appel de la fonction pour obtenir le propriétaire selon l'id du déclarant
    proprietaire = get_proprietaire_from_id(
        id_declarant, type_proprietaire="proprietaire"
    )
    # Sérialisation de l'objet propriétaire en dictionnaire
    proprietaire_dict = TProprietaireSchema().dump(proprietaire)

    # Retourne les informations du propriétaire au format JSON
    return proprietaire_dict


# Cette route permet de récupérer les informations du propriétaire à partir de l'identifiant du déclarant.
# Elle est utilisée lorsqu'on souhaite afficher ou utiliser les données du propriétaire liées à un déclarant spécifique,
# mais en passant par la fonction get_proprietaire_from_id qui peut différer de get_proprietaire_from_id selon la logique métier.
@bp.route("proprietaire_from_id_declarant/<int:id_declarant>", methods=["GET"])
@check_auth_redirect_login(1)
def api_get_proprietaire_from_id_declarant(id_declarant):
    # Appel de la fonction pour obtenir le propriétaire selon l'id du déclarant
    proprietaire = get_proprietaire_from_id(id_declarant, type_proprietaire="declarant")
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
    foret, proprietaire = get_foret_from_code(code_foret)
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


# Cette route permet de récupérer une déclaration complète, incluant les données de la forêt, du propriétaire,
# ainsi que toutes les zones ("areas") associées à la forêt et à la déclaration.
# Elle est utilisée notamment pour l'affichage détaillé d'une déclaration, par exemple dans le composant "voir_declaration.vue".
@bp.route("declaration", methods=["GET"])
# @bp.route("declaration", methods=["GET"], defaults={"id_declaration": None})
@check_auth_redirect_login(
    1
)  # Vérifie que l'utilisateur est authentifié (niveau 1 minimum)
# @json_resp_accept_empty_list  # Retourne une liste vide si aucune déclaration n'est trouvée
def api_get_declaration():
    """
    Récupère une déclaration complète avec toutes les informations nécessaires à l'affichage détaillé.
    Utilisée pour consulter ou afficher une déclaration avec ses zones géographiques.
    """
    id_declaration = request.args.get("id", type=int)
    apiResponse = get_form_declaration(id_declaration=id_declaration, session=session)
    # Retourne le dictionnaire de la déclaration complète au format JSON
    return apiResponse.response_to_frontend()


@bp.route("voir_declaration/<int:id_declaration>", methods=["GET"])
@check_auth_redirect_login(1)
@json_resp
def route_declaration(id_declaration):
    """
    Retourne la declaration d'id id_declaration
    utilisée pour la page "voir_declaration.vue" qui donne les informations détaillées et les géométries.
    """
    # Vérifie la présence d'un utilisateur dans la session et récupère l'objet utilisateur

    response = get_fiche_declaration(id_declaration=id_declaration, session=session)

    if response.success == False:
        return None

    return response.data


# pas d'authentification check_auth ici car on passe par un token
@bp.route("declaration_renouvellement", methods=["GET"])
# @json_resp_accept_empty_list
def api_get_declaration_renouvellement():
    """
    Récupère une déclaration complète pour le renouvellement, incluant les données de la forêt, du propriétaire,
    ainsi que toutes les zones ("areas") associées à la forêt et à la déclaration.
    Utilisée notamment pour l'affichage détaillé d'une déclaration lors du renouvellement, par exemple dans le composant "voir_declaration.vue".
    La sécurité de cette route est assurée par la vérification du token de renouvellement et de sa date d'expiration dans la fonction check_token_declaration.
    """
    id_declaration = request.args.get("id", type=int)
    token = request.args.get("token", type=str)

    response = check_token_renouvellement_declaration(id_declaration, token)
    if response.success == False:
        print(
            "Token de renouvellement invalide ou expiré. Accès refusé à la déclaration pour le renouvellement."
        )
        return response.response_to_frontend()
    else:

        # Création d'un utilisateur provisoire en session
        session["temp_user"] = {
            "token": token,
            "id_verification": id_declaration,
            "mode": "renouvellement_declaration",
        }

    response = get_form_declaration(id_declaration=id_declaration, session=session)

    # Retourne le dictionnaire de la déclaration complète au format JSON
    # response.data = declaration_dict
    return response.response_to_frontend()


@bp.route("all_areas_declaration", methods=["GET"])
@json_resp
def all_areas_declaration():
    """
    Retourne toutes les aires concernant une déclaration.
    Utilisée pour afficher la carte dans voir déclaration.
    """

    id_declaration = request.args.get("id", type=int)
    str_list_id_types = request.args.get("list_id_types", type=str)
    list_id_types = (
        [int(x) for x in str_list_id_types.split(",")] if str_list_id_types else []
    )
    stmt = get_stmt_all_areas_declaration(id_declaration, list_id_types)

    rows = get_db().session.execute(stmt).mappings().all()
    geojson_areas = LAreasSchema(
        many=True, as_geojson=True, feature_geometry="geom_4326"
    ).dump(rows)

    return geojson_areas


@bp.route("check_token_declaration", methods=["GET"])
@json_resp
def check_token_declaration():
    """
    Vérifie la validité d'un token de déclaration.
    Utilisée pour sécuriser l'accès à certaines fonctionnalités liées aux déclarations,
    par exemple lors de la consultation ou de la modification d'une déclaration spécifique.
    """

    # Récupère le token de déclaration depuis les paramètres de la requête
    token = request.args.get("token")
    if not token:
        return {"valid": False, "error": "Token manquant dans la requête"}, 400
    id_declaration = request.args.get("id")
    if not id_declaration:
        return {
            "valid": False,
            "error": "ID de déclaration manquant dans la requête",
        }, 400

    stmt = stmt_one_declaration_a_renouveler(id_declaration)
    result = get_db().session.execute(stmt).fetchone()
    if not result:
        return {"valid": False, "error": "Déclaration non trouvée"}, 404

    # Normalize row access to a mapping/dict for safety across SQLAlchemy versions
    row = result._mapping if hasattr(result, "_mapping") else dict(result)
    token_renouvellement = row.get("token_renouvellement")
    date_fin_token = row.get("date_fin_token")

    if token_renouvellement is None:
        return {
            "valid": False,
            "error": "Cette déclaration n'a pas de token de renouvellement",
        }, 404
    if date_fin_token is None:
        return {
            "valid": False,
            "error": "Cette déclaration n'a pas de date de fin de token",
        }, 404

    now = datetime.now()
    # If date_fin_token is a date (not datetime), convert to datetime for a proper comparison
    if isinstance(date_fin_token, date) and not isinstance(date_fin_token, datetime):
        date_fin_token = datetime.combine(date_fin_token, datetime.max.time())

    if now > date_fin_token:
        return {"valid": False, "error": "Le lien a expiré"}, 404

    if token != token_renouvellement:
        return {"valid": False, "error": "Token invalide"}, 404
    else:
        return {"valid": True, "message": "Token valide"}, 200


@bp.route("degats", methods=["GET"])
@json_resp
def degats():
    """
    Retourne les dégats pour la page 'résultats de suivis'-> alertes signaléés.
    Est appelé dans une page dynamique des résultats
    """
    stmt = get_stmt_for_resultats_degats()
    result = get_db().session.execute(stmt).mappings().all()
    if not result:
        return []
    data = [dict(row) for row in result]

    return data


@bp.route("declarations", methods=["GET"])
@json_resp
def declarations():
    """
    Liste des déclarations pour la page "alertes signalées". Utilise une vue PostgreSQL qui transforme les données
    en interne pour être directement affichées.
    Retourne aussi beaucoup de données uniquement intégrées dans l'export.
    Ne retourne que les déclarations de l'utilisateur.
    """

    # Vérifie la présence d'un utilisateur dans la session et récupère l'objet utilisateur
    user = (
        get_user(session["current_user"]["id_role"])
        if "current_user" in session and session["current_user"]
        else None
    )

    # Retourne la liste des déclarations accessibles à cet utilisateur
    return get_liste_declarations(user=user)


##############################################################################################
################## MODIIFICATION / CREATION DECLARATION  #####################################
###############################################################################################


def clean_declaration_data(declaration_data):
    """
    Nettoie la déclaration avant l'enregistrement en base de données.
    en retirant les champs liés au pâturage, à la protection ou à la maturité du peuplement dans certains cas particuliers
    """
    if not declaration_data:
        return

    # si il n'y a pas de presence de paturage, on s'assure de retirer les champs liés au pâturage qui auraient pu être remplis
    if declaration_data.get("b_peuplement_paturage_presence") is False:
        declaration_data["nomenclatures_peuplement_paturage_type"] = []
        declaration_data["id_nomenclature_peuplement_paturage_statut"] = None
        declaration_data["id_nomenclature_peuplement_paturage_frequence"] = None
        declaration_data["nomenclatures_peuplement_paturage_saison"] = []

    # si il n'y a pas de protection, on s'assure de retirer les champs liés à la protection qui auraient pu être remplis
    if declaration_data.get("b_peuplement_protection_existence") is False:
        declaration_data["nomenclatures_peuplement_protection_type"] = []

    # si le type de peuplement est "futaie irrégulière", on retire les champs liés à la maturité du peuplement
    if declaration_data.get("id_nomenclature_peuplement_type") == 525:
        declaration_data["nomenclatures_peuplement_maturite"] = []

    return declaration_data


# Cette route permet de modifier une déclaration existante via une requête PATCH.
# Elle est utilisée lorsqu'un utilisateur souhaite mettre à jour les informations d'une déclaration
# déjà enregistrée dans la base de données, par exemple pour corriger une erreur ou ajouter des précisions.
@bp.route("declaration", methods=["PATCH"])
# @check_auth_redirect_login(1)  # Vérifie que l'utilisateur est authentifié (niveau 1 minimum)
# @json_resp  # Retourne la réponse au format JSON
def api_patch_declaration():
    """
    Met à jour une déclaration existante.
    Utilisée lors de la modification d'une déclaration par un utilisateur autorisé.
    """

    # Récupère les données envoyées dans la requête PATCH (au format JSON)
    post_data = request.get_json()

    post_data = clean_declaration_data(post_data)

    # Appelle la fonction qui crée ou met à jour la déclaration dans la base de données
    # Ici, on suppose que l'identifiant de la déclaration existe déjà dans post_data
    result_declaration, response = create_or_update_declaration(post_data)
    # Envoie un mail de notification pour informer de la modification de la déclaration
    # (le second paramètre "False" indique qu'il ne s'agit pas d'une création mais d'une modification)
    send_mail_validation_declaration(result_declaration, False)
    # Retourne le résultat de la modification au format JSON
    response.data = result_declaration
    return response.response_to_frontend()


# Cette route permet de créer une nouvelle déclaration de dégât en forêt via une requête POST.
# Elle est utilisée lorsqu'un utilisateur souhaite enregistrer une nouvelle déclaration dans la base de données.
# Typiquement, cette route est appelée lors de la soumission d'un formulaire de déclaration par un utilisateur.
@bp.route("declaration", methods=["POST"])
@check_auth_redirect_login(
    1
)  # Vérifie que l'utilisateur est authentifié (niveau 1 minimum)
# @json_resp  # Retourne la réponse au format JSON
def api_post_declaration():
    """
    Crée une nouvelle déclaration de dégât en forêt.
    Utilisée lors de la soumission d'une déclaration par un utilisateur.
    """

    # Récupère les données envoyées dans la requête POST (au format JSON)
    post_data = request.get_json()
    post_data = clean_declaration_data(post_data)
    # Détermine s'il s'agit d'une création (True si aucun id_declaration n'est présent)
    b_create = not (post_data.get("id_declaration"))

    # Appelle la fonction qui crée ou met à jour la déclaration dans la base de données
    # Ici, on suppose que l'identifiant de la déclaration n'existe pas encore (création)
    post_data_arranged, response = create_or_update_declaration(post_data)

    # Envoie un mail de notification pour informer de la création de la déclaration
    # (décommenter la ligne ci-dessous pour activer l'envoi de mail après les tests)
    send_mail_validation_declaration(post_data_arranged, b_create)

    # Retourne le résultat de la création au format JSON
    response.data = post_data_arranged
    return response.response_to_frontend()


# renouvellement de déclaration. Ne pas utilser check_auth_redirect_login car cette route est appelée via un lien de renouvellement qui peut être utilisé par des utilisateurs non connectés ou avec des droits limités. La sécurité de cette route est assurée par la vérification du token de renouvellement et de sa date d'expiration dans la fonction check_token_declaration.
@bp.route("duplicate_declaration", methods=["POST"])
# @json_resp
@check_auth_redirect_login(1)
def duplicate_declaration():
    """
    Duplique une déclaration existante.
    Utilisée lorsqu'un utilisateur souhaite créer une nouvelle déclaration basée sur une déclaration existante.
    """

    apiResponse = ApiResponse(log_file="declarations.log", session=session)

    variables_path = (
        Path(get_config()["ROOT_DIR"]) / "config" / "variables" / "declaration.json"
    )
    with open(variables_path, "r", encoding="utf-8") as f:
        variables_declaration = json.load(f)

    statut_declaration = variables_declaration.get("STATUT_DECLARATION")
    nb_jours_validite_declaration = variables_declaration.get(
        "NB_JOURS_VALIDITE_DECLARATION"
    )

    post_data = request.get_json()
    post_data = clean_declaration_data(post_data)
    id_declaration = post_data.get("id_declaration")
    if not id_declaration:
        apiResponse.add_error(
            user_message="ID de déclaration manquant",
            system_error="ID de déclaration manquant dans la requête",
            status_code=200,
        )
        return apiResponse.response_to_frontend()
    post_data["id_declaration_originale"] = id_declaration
    post_data["id_declaration"] = None
    post_data["b_valid"] = False
    post_data["token_renouvellement"] = (
        None  # Le token de renouvellement doit être généré à nouveau pour la nouvelle déclaration
    )
    post_data["date_fin_token"] = (
        None  # La date de fin du token doit être réinitialisée pour la nouvelle déclaration
    )
    post_data["meta_create_date"] = str(
        datetime.now()
    )  # Met à jour la date de création pour la nouvelle déclaration
    post_data["meta_update_date"] = str(
        datetime.now()
    )  # Met à jour la date de mise à jour pour la nouvelle déclaration
    date_fin = datetime.now().date() + timedelta(days=nb_jours_validite_declaration)
    post_data["date_fin"] = str(
        date_fin
    )  # Met à jour la date de fin en fonction de la durée de validité définie dans les variables
    post_data["statut"] = statut_declaration.get(
        "Non validée"
    )  # Met à jour le statut de la déclaration renouvelée à "Active"

    # met la toutes les valeurs "id_declaration". "id_degat" et "id_degat_essence" à null dans post_data pour éviter les conflits avec la déclaration originale lors de la création de la nouvelle déclaration
    for degat in post_data["degats"]:
        degat["id_declaration"] = None
        degat["id_degat"] = None

        # Si la clé 'degat_essences' existe, on retire les id_degat et id_degat_essence pour éviter les conflits lors de la création de la nouvelle déclaration
        if "degat_essences" in degat:
            for degat_essence in degat["degat_essences"]:
                if "id_degat" in degat_essence:
                    degat_essence["id_degat"] = None
                if "id_degat_essence" in degat_essence:
                    degat_essence["id_degat_essence"] = None

    _, response = create_or_update_declaration(post_data)

    if response.success == False:
        print(
            "Erreur lors de la création de la nouvelle déclaration pour le renouvellement. Envoi du mail d'échec de renouvellement."
        )
        send_mail_echec_renouvellement_declaration(post_data)
        return response.response_to_frontend()

    new_declaration = response.data

    new_declaration["id_declaration_originale"] = id_declaration
    # new_declaration["prenom_role"] = session["current_user"]["prenom_role"]
    # new_declaration["nom_role"] = session["current_user"]["nom_role"]
    url_declaration = (
        f"{get_config()['URL_FRONTEND']}#/declaration/voir_declaration/{id_declaration}"
    )
    new_declaration["url_declaration"] = url_declaration
    url_new_declaration = f"{get_config()['URL_FRONTEND']}#/declaration/voir_declaration/{new_declaration['id_declaration']}"
    new_declaration["url_new_declaration"] = url_new_declaration

    try:
        # archivage de la déclaration original
        stmt_update_statut = stmt_change_statut_declaration(
            id_declaration, statut_declaration.get("Archivée")
        )
        get_db().session.execute(stmt_update_statut)
        get_db().session.commit()

        send_mail_alerte_renouvellement_declaration(new_declaration)

    except Exception as e:
        get_db().session.rollback()
        response.add_error(
            user_message="Erreur lors de l'archivage de la déclaration originale",
            system_error=str(e),
            status_code=500,
        )
        send_mail_echec_renouvellement_declaration(new_declaration)
        return response.response_to_frontend()

    # send_mail_validation_declaration(post_data_arranged, True)
    return response.response_to_frontend()


@bp.route("cloture_declaration", methods=["POST"])
@check_auth_redirect_login(1)
def cloture_declaration():
    """
    Clôture une déclaration existante.
    Utilisée lorsqu'un utilisateur souhaite clôturer une déclaration.
    """
    import json
    from datetime import timedelta
    from sqlalchemy import update
    from pathlib import Path

    variables_path = (
        Path(get_config()["ROOT_DIR"]) / "config" / "variables" / "declaration.json"
    )
    with open(variables_path, "r", encoding="utf-8") as f:
        variables_declaration = json.load(f)
    statut_declaration = variables_declaration.get("STATUT_DECLARATION")

    post_data = request.get_json()

    id_declaration = post_data.get("id_declaration", int)
    token = post_data.get("token_renouvellement", str)

    response = check_token_renouvellement_declaration(id_declaration, token)
    if response.success == False:
        response.add_error(
            user_message="Token de renouvellement invalide ou expiré. Seule la personne ayant effectué le dernier renouvellement peut clôturer la déclaration.",
            system_error="Token de renouvellement invalide ou expiré pour la clôture de la déclaration",
            status_code=200,
        )

        return response.response_to_frontend()

    if not id_declaration:
        response.add_error(
            user_message="ID de déclaration manquant",
            system_error="ID de déclaration manquant dans la requête",
            status_code=200,
        )

        return response.response_to_frontend()

    try:

        stmt = (
            update(TDeclaration)
            .where(TDeclaration.id_declaration == id_declaration)
            .values(
                b_valid=True,
                statut=statut_declaration.get("Archivée"),
            )
        )
        get_db().session.execute(stmt)
        get_db().session.commit()
        response.message = "Déclaration clôturée avec succès"
        post_data["url_declaration"] = (
            f"{get_config()['URL_FRONTEND']}#/declaration/voir_declaration/{id_declaration}"
        )
        send_mail_alerte_cloture_declaration(post_data)
    except Exception as e:
        get_db().session.rollback()
        response.add_error(
            user_message="Erreur lors de la clôture de la déclaration",
            system_error=str(e),
            status_code=500,
        )
        return response.response_to_frontend()

    return response.response_to_frontend()


@bp.route("delete_declaration/<int:id_declaration>", methods=["POST"])
@check_auth_redirect_login(4)
@json_resp
def delete_declaration(id_declaration):
    """
    Supprime une déclaration (id_déclaration) de la base de données.
    Non utilisé pour le moment.
    """

    # Création de la requête de suppression pour la déclaration d'id donné
    stmt = delete(TDeclaration).where(
        TDeclaration.id_declaration == id_declaration,
    )
    # Exécution de la requête sur la session de base de données
    get_db().session.execute(stmt)
    # Validation de la suppression en base
    get_db().session.commit()

    # Retourne "ok" pour confirmer la suppression
    return "ok"


@bp.route("validate_declaration", methods=["POST"])
@check_auth_redirect_login(4)
@json_resp
def validate_declaration():
    """
    Valide une déclaration (id_déclaration) en la mettant à jour dans la base de données.

    Utilisation :
    - Cette route est appelée lorsqu'un utilisateur authentifié (niveau d'accès 4 ou plus)
      souhaite valider une déclaration spécifique identifiée par son id.
    Elle est utilisée principalement dans le tableau des listes de déclarations.
    """
    data = request.get_json()

    id_declaration = data.get("id_declaration")
    b_valid = data.get("b_valid")
    dict_update = {"id_declaration": id_declaration, "b_valid": b_valid}

    stmt = (
        TDeclaration.__table__.update()
        .where(TDeclaration.id_declaration == id_declaration)
        .values(b_valid=b_valid, statut=1 if b_valid else 0)
    )
    get_db().session.execute(stmt)
    get_db().session.commit()

    # if not id_declaration:
    #     return {"error": "ID de déclaration manquant"}, 400

    # # Récupère la déclaration à valider
    # declaration = get_declaration(id_declaration)
    # if not declaration:
    #     return {"error": "Déclaration non trouvée"}, 404

    # # Met à jour le statut de la déclaration
    # declaration.b_valid = True
    # DB.session.commit()

    return dict_update


@bp.route("send_mail_renouvellement", methods=["GET"])
@check_auth_redirect_login(3)
def send_mail():
    """
    Envoie un mail de renouvellement de déclaration.
    Utilisée lorsqu'un utilisateur souhaite recevoir un mail pour renouveler une déclaration avant son expiration.
    """
    response = ApiResponse(log_file="declarations.log", session=session)
    id_declaration = request.args.get("id_declaration", type=int)

    reponse_declaration = get_fiche_declaration(
        id_declaration=id_declaration, session=session
    )

    if reponse_declaration.success == False:
        print("Déclaration non trouvée. Envoi du mail de renouvellement impossible.")
        response.add_error(
            user_message="Déclaration non trouvée. Envoi du mail de renouvellement impossible.",
            system_error="Déclaration non trouvée pour l'envoi du mail de renouvellement",
            status_code=404,
        )
        return response.response_to_frontend()

    if reponse_declaration.data["b_valid"] == False:
        print(
            "La déclaration n'est pas encore validée. Envoi du mail de renouvellement impossible."
        )
        response.add_log(
            message="La déclaration n'est pas encore validée. Envoi du mail de renouvellement impossible.",
            level="ERROR",
        )
        return response.response_to_frontend()

    try:
        send_mail_actualisation_declaration(
            reponse_declaration.data, change_statut=False
        )
        response.message = "Mail de renouvellement envoyé avec succès"
    except Exception as e:
        response.add_error(
            user_message="Erreur lors de l'envoi du mail de renouvellement",
            system_error=str(e),
            status_code=500,
        )

    return response.response_to_frontend()


##################################################################################
###################    EXPORT CSV / SHAPE  ########################################
###################################################################################


def get_file_name(type_out):
    """
    Génère le nom de fichier pour l'export des déclarations.

    Utilisation :
    - Cette fonction est utilisée lors de l'export des déclarations au format CSV ou SHAPE,
      notamment dans les routes 'declarations_csv' et 'declarations_shape'.

    Arguments :
    - type_out (str) : Type de déclaration à exporter. Peut être 'degat' pour les dégâts,
      ou tout autre valeur pour les alertes.

    Retour :
    - (str) : Nom du fichier généré, par exemple 'export_degats_12-06-2024' ou 'export_alertes_12-06-2024'.
    """
    file_name = "export_"
    if type_out == "degat":
        # Si le type est 'degat', on ajoute 'degats_' au nom du fichier
        file_name += "degats_"
    else:
        # Sinon, on considère qu'il s'agit d'alertes
        file_name += "alertes_"

    # Ajoute la date du jour au format JJ-MM-AAAA
    file_name += date.today().strftime("%d-%m-%Y")
    return file_name


@bp.route("export_liste_declarations", methods=["GET"])
@check_auth_redirect_login(1)
def export_declarations():
    """
    Exporte les déclarations au format CSV ou GeoPackage selon les paramètres de la requête.
     - type_out : 'degat' pour les dégâts, 'declaration' pour les alertes (toutes les déclarations)
     - type_file : 'gpkg' pour GeoPackage, 'csv' pour CSV
     Utilise la fonction get_stmt_for_declarations_export pour récupérer les données à exporter selon le type de déclaration et le format de fichier souhaité.
     Les fichiers exportés sont stockés dans des répertoires spécifiques selon leur format, et sont ensuite envoyés en téléchargement à l'utilisateur.
    """

    # Récupère le type de déclaration à exporter depuis les paramètres de la requête
    type_out = request.args.get("type_out")  # 'degat', 'declaration'
    type_file = request.args.get("type_file")  # 'gpkg', 'csv'
    if type_file not in ["gpkg", "csv"]:
        return {"error": "type_file doit être 'gpkg' ou 'csv'"}, 400
    if type_out not in ["degat", "declaration"]:
        return {"error": "type_out doit être 'degat' ou 'declaration'"}, 400

    file_name = get_file_name(type_out)

    # Définition du répertoire où seront stockés les fichiers shapefile
    if type_file == "gpkg":
        dir_path = str(get_config()["ROOT_DIR"] / "static/shapefiles")
        output_filename = f"{dir_path}/{file_name}.gpkg"
    elif type_file == "csv":
        dir_path = str(get_config()["ROOT_DIR"] / "static/data")
        output_filename = f"{dir_path}/{file_name}.csv"

    print(
        f"Export des déclarations : type_out={type_out}, type_file={type_file}, output_filename={output_filename}"
    )
    # Récupère les données à exporter selon l'utilisateur courant et le type d'export
    stmt_data = get_stmt_for_declarations_export(type_file=type_file, type_out=type_out)
    result_data = get_db().session.execute(stmt_data)

    # Exécution de la requête
    rows = result_data.fetchall()
    keys = result_data.keys()

    if not rows:
        print("Aucun résultat trouvé.")
        return

    # Conversion en DataFrame
    df = pd.DataFrame(rows, columns=keys)

    if type_file == "gpkg":
        # Conversion de la colonne geom en géométrie Shapely
        # Selon le format de votre colonne geom (WKB ou WKT)

        # Si la géométrie est en WKB (format binaire)
        if isinstance(df["geom"].iloc[0], bytes):
            df["geometry"] = df["geom"].apply(lambda x: wkb.loads(x) if x else None)

        # Si la géométrie est en WKT (format texte)
        elif isinstance(df["geom"].iloc[0], str):
            df["geometry"] = df["geom"].apply(lambda x: wkt.loads(x) if x else None)

        # Si la géométrie est déjà un objet Shapely ou autre
        else:
            df["geometry"] = df["geom"].apply(
                lambda x: wkb.loads(str(x), hex=True) if x else None
            )

        # Suppression de la colonne geom originale
        df = df.drop(columns=["geom"])

        # Création du GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry="geometry", crs="EPSG:4326")

        # Export en GeoPackage
        gdf.to_file(output_filename, layer="ma_couche", driver="GPKG")

    else:  # export en CSV
        df.to_csv(output_filename, index=False, encoding="utf-8-sig")

    return send_from_directory(
        dir_path, file_name + f".{type_file}", as_attachment=True
    )
