"""
liste des api pour les declarations
"""

# import copy
import os
import zipfile
from datetime import date
from flask import Blueprint, request, current_app, session
from flask.helpers import send_from_directory
from utils_flask_sqla.response import csv_resp, json_resp_accept_empty_list
from utils_flask_sqla_geo.generic import GenericTableGeo

from ..declaration.mail import send_mail_validation_declaration

# from oeasc.modules.oeasc.nomenclature import nomenclature_oeasc
from utils_flask_sqla.response import json_resp
from sqlalchemy import delete

# from oeasc.utils.env import ROOT_DIR
from ..nomenclature import get_area_from_id, get_nomenclature_from_id
from .repository import (
    get_user,
    get_fiche_declaration,
    get_liste_declarations,
    create_or_update_declaration,
    get_declaration,
    get_id_area,
    get_id_areas,
    get_foret_from_code,
    get_proprietaire_from_id,
    get_declarations_view,
    hide_proprietaire,
)

from ..user.utils import check_auth_redirect_login

# from .mail import send_mail_validation_declaration
from .models import TDeclaration
from ..declaration.schema import TProprietaireSchema, TForetSchema, TDeclarationSchema

config = current_app.config
DB = config["DB"]
bp = Blueprint("declaration_api", __name__)


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


@bp.route("voir_declaration/<int:id_declaration>", methods=["GET"])
@check_auth_redirect_login(1)
@json_resp
def route_declaration(id_declaration):
    """
    Retourne la declaration d'id id_declaration
    utilisée pour la page "voir_declaration.vue" qui donne les informations détaillées et les géométries.

    """
    # Vérifie la présence d'un utilisateur dans la session et récupère l'objet utilisateur
    user = (
        get_user(session["current_user"]["id_role"])
        if "current_user" in session and session["current_user"]
        else None
    )
    declaration = get_fiche_declaration(id_declaration=id_declaration, user=user)[0]

    if not declaration:
        return None

    return declaration


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
    # print ("data validate_declaration", data)  # Debug : affiche les données reçues dans la requête
    id_declaration = data.get("id_declaration")
    b_valid = data.get(
        "b_valid"
    )  # Par défaut, on considère que la validation est pour valider (True)
    dict_update = {"id_declaration": id_declaration, "b_valid": b_valid}
    print("dict_update", dict_update)  # Debug : affiche le dictionnaire de mise à jour

    stmt = (
        TDeclaration.__table__.update()
        .where(TDeclaration.id_declaration == id_declaration)
        .values(b_valid=b_valid)
    )
    DB.session.execute(stmt)
    DB.session.commit()

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


######################################################################################
######################################################################################
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
@bp.route("declaration/<int:id_declaration>", methods=["GET"])
# @bp.route("declaration", methods=["GET"], defaults={"id_declaration": None})
@check_auth_redirect_login(
    1
)  # Vérifie que l'utilisateur est authentifié (niveau 1 minimum)
@json_resp_accept_empty_list  # Retourne une liste vide si aucune déclaration n'est trouvée
def api_get_declaration(id_declaration):
    """
    Récupère une déclaration complète avec toutes les informations nécessaires à l'affichage détaillé.
    Utilisée pour consulter ou afficher une déclaration avec ses zones géographiques.
    """

    # Récupère la déclaration, la forêt et le propriétaire associés à l'identifiant donné
    declaration, foret, proprietaire = get_declaration(id_declaration)

    # Si aucune déclaration n'est trouvée, retourne une réponse vide
    if not declaration:
        return

    # Sérialise l'objet déclaration en dictionnaire
    declaration_dict = TDeclarationSchema().dump(declaration)
    # print ("declaration_dict après sérialisation:", declaration_dict)

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
    # print ("declaration_dict avant transformation des nomenclatures:", declaration_dict)
    for key in declaration_dict:
        if key == "centroid":  # les centroid sont en array et non en list
            declaration_dict[key] = {
                "x": declaration_dict[key][0],
                "y": declaration_dict[key][1],
            }
        else:  # pour les list on applatit les nomenclatures
            if (
                isinstance(declaration_dict[key], list)
                and len(declaration_dict[key]) > 0
                and "id_nomenclature" in declaration_dict[key][0]
            ):
                # regroupe les id_nomenclature dans une liste simple.
                declaration_dict[key] = [
                    e["id_nomenclature"] for e in declaration_dict[key]
                ]

    # Récupère et classe les zones ("areas") de la forêt selon leur type
    areas_foret = [
        get_area_from_id(area["id_area"])
        for area in declaration_dict.get("areas_foret", [])
    ]
    declaration_dict["areas_foret_onf"] = get_id_area(areas_foret, ["OEASC_ONF_FRT"])
    declaration_dict["areas_foret_dgd"] = get_id_area(areas_foret, ["OEASC_DGD"])
    declaration_dict["areas_foret_communes"] = get_id_areas(
        areas_foret, ["OEASC_COMMUNE"]
    )
    declaration_dict["areas_foret_sections"] = get_id_areas(
        areas_foret, ["OEASC_SECTION"]
    )

    # Récupère et classe les zones ("areas") de la déclaration selon leur type
    areas_localisation = [
        get_area_from_id(area["id_area"])
        for area in declaration_dict.get("areas_localisation", [])
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
    if (
        (current_user is not None)
        and (current_user["max_level_profil"] < 4)
        and (current_user["id_role"] != declaration_dict["id_declarant"])
    ):
        hide_proprietaire(declaration_dict)

    # Retourne le dictionnaire de la déclaration complète au format JSON
    return declaration_dict


# Cette route permet de modifier une déclaration existante via une requête PATCH.
# Elle est utilisée lorsqu'un utilisateur souhaite mettre à jour les informations d'une déclaration
# déjà enregistrée dans la base de données, par exemple pour corriger une erreur ou ajouter des précisions.
@bp.route("declaration", methods=["PATCH"])
@check_auth_redirect_login(
    1
)  # Vérifie que l'utilisateur est authentifié (niveau 1 minimum)
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
@check_auth_redirect_login(
    1
)  # Vérifie que l'utilisateur est authentifié (niveau 1 minimum)
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
    send_mail_validation_declaration(post_data_arranged, b_create)

    # Retourne le résultat de la création au format JSON
    return post_data_arranged


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
    DB.session.execute(stmt)
    # Validation de la suppression en base
    DB.session.commit()

    # Retourne "ok" pour confirmer la suppression
    return "ok"


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


@bp.route("declarations_csv", methods=["GET"])
@check_auth_redirect_login(1)
@csv_resp
def declarations_csv():
    """
    Route Flask permettant d'exporter la liste des déclarations au format CSV.

    Utilisation :
    - Cette route est appelée lorsqu'un utilisateur authentifié souhaite télécharger
      les déclarations (dégâts ou alertes) sous forme de fichier CSV.
    - Elle est utilisée notamment dans l'interface d'administration ou de suivi
      pour faciliter l'analyse ou l'archivage des données.

    Fonctionnement :
    - Le paramètre 'type_out' dans la requête GET permet de filtrer le type de déclaration
      à exporter : 'degat' pour les dégâts, ou autre pour les alertes.
    - Le nom du fichier exporté est généré dynamiquement via la fonction get_file_name(type_out).
    - Les données sont récupérées via la fonction get_declarations, qui prend en compte
      l'utilisateur courant et le type d'export.
    - Les colonnes du CSV sont déterminées à partir des clés du premier élément des données.
    - Le séparateur utilisé dans le CSV est le point-virgule (';').
    - Le décorateur @csv_resp gère la conversion du retour en fichier CSV téléchargeable.

    Retour :
    - Un tuple (file_name, data, columns, separator) utilisé par @csv_resp pour générer le fichier.
    """

    separator = ";"  # Définition du séparateur pour le CSV

    # Récupère le type de déclaration à exporter depuis les paramètres de la requête
    type_out = request.args.get("type_out")  # 'degat', ''

    # Génère le nom du fichier exporté en fonction du type et de la date
    file_name = get_file_name(type_out)

    # Récupère les données à exporter selon l'utilisateur courant et le type d'export
    data = get_declarations_view(
        user=get_user(session["current_user"]["id_role"]),
        type_export="csv",
        type_out=type_out,
    )

    # Détermine les colonnes du CSV à partir des clés du premier élément des données
    columns = list(data[0].keys())

    # Retourne les informations nécessaires à la génération du CSV
    return (file_name, data, columns, separator)


@bp.route("declarations_shape", methods=["GET"])
@check_auth_redirect_login(1)
def declarations_shape():
    """
    Utilisation :
    - Cette route est appelée lorsqu'un utilisateur authentifié souhaite télécharger
      les déclarations (dégâts ou alertes) sous forme de fichier Shapefile pour une utilisation SIG.
    - Elle est utilisée notamment pour l'analyse spatiale ou l'intégration dans des outils cartographiques.

    Fonctionnement :
    - Le paramètre 'type_out' dans la requête GET permet de filtrer le type de déclaration
      à exporter : 'degat' pour les dégâts, ou autre pour les alertes.
    - Le nom du fichier exporté est généré dynamiquement via la fonction get_file_name(type_out).
    - Les données sont récupérées via la fonction get_declarations, qui prend en compte
      l'utilisateur courant et le type d'export.
    - La classe GenericTableGeo est utilisée pour générer le Shapefile à partir des données.
    - Le fichier ZIP généré est nettoyé et renommé pour supprimer le préfixe "POLYGON_" des fichiers.
    - Le fichier ZIP final est envoyé en téléchargement à l'utilisateur.

    Retour :
    - Un fichier ZIP contenant le Shapefile des déclarations, prêt à être téléchargé.
    """

    # Récupère le type de déclaration à exporter depuis les paramètres de la requête
    type_out = request.args.get("type_out")  # 'degat', ''

    # Définition du nom de fichier initial (sera modifié plus bas)
    file_name = "export_declarations_shape"

    # Définition du répertoire où seront stockés les fichiers shapefile
    dir_path = str(config["ROOT_DIR"] / "static/shapefiles")

    # Détermine la vue SQL à utiliser selon le type de déclaration
    view_name = (
        "v_export_declaration_degats_shape"
        if type_out == "degat"
        else "v_export_declarations_shape"
    )

    # Génère le nom du fichier exporté en fonction du type et de la date
    file_name = get_file_name(type_out)

    # Instancie la classe GenericTableGeo pour gérer l'export spatial
    export_view = GenericTableGeo(
        view_name, "oeasc_declarations", DB.engine, geometry_field="geom", srid=4326
    )

    # Récupère les données à exporter selon l'utilisateur courant et le type d'export
    data = get_declarations_view(
        user=get_user(session["current_user"]["id_role"]),
        type_export="shape",
        type_out=type_out,
    )

    # Exporte les données au format Shapefile dans le répertoire spécifié
    export_view.as_shape(
        export_view.db_cols, data=data, dir_path=dir_path, file_name=file_name
    )

    # Chemin du fichier ZIP généré par l'export
    zip_file_name = dir_path + "/" + file_name + ".zip"

    # Ouvre le fichier ZIP pour traiter les fichiers internes
    z = zipfile.ZipFile(zip_file_name)
    file_names = []
    # Parcourt les fichiers du ZIP pour supprimer le préfixe "POLYGON_" dans les noms
    for _, f in enumerate(z.filelist):
        f.filename = f.filename.replace("POLYGON_", "")
        file_names.append(f.filename)
        z.extract(f, dir_path)  # Extrait le fichier dans le répertoire cible

    # Supprime le ZIP original
    os.remove(zip_file_name)
    # Crée un nouveau ZIP avec les fichiers renommés
    z = zipfile.ZipFile(zip_file_name, "w")
    for sfile_name in file_names:
        z.write(dir_path + "/" + sfile_name, sfile_name)

    z.close()

    # Retourne le fichier ZIP final en téléchargement à l'utilisateur
    return send_from_directory(dir_path, file_name + ".zip", as_attachment=True)


@bp.route("degats", methods=["GET"])
@json_resp
def degats():
    """
    Route Flask permettant de récupérer la liste des déclarations de type 'dégât' accessibles pour le déclarant.

    Utilisation :
    - Cette route est appelée lorsqu'un utilisateur souhaite consulter uniquement les déclarations
      de type 'dégât' qui lui sont accessibles, généralement dans l'interface dédiée aux déclarants.
    - Elle est utilisée pour filtrer les déclarations selon le rôle et les droits du déclarant.

    Fonctionnement :
    - La fonction appelle get_declarations avec les paramètres type_out="degat" pour ne récupérer
      que les déclarations de type 'dégât', et restrict=True pour limiter l'accès selon le déclarant.
    - Le filtrage des données dépend de l'implémentation de get_declarations et des droits de l'utilisateur.

    Retour :
    - La liste des déclarations de type 'dégât' accessibles au déclarant, au format JSON.
    """

    return get_declarations_view(type_out="degat", restrict=True)
