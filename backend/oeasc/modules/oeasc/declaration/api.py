"""
liste des api pour les declarations
"""

# import copy
import os
import zipfile
from datetime import date, datetime
from flask import Blueprint, request, current_app, session
from flask.helpers import send_from_directory
from utils_flask_sqla.response import csv_resp, json_resp_accept_empty_list
from utils_flask_sqla_geo.generic import GenericTableGeo
import geopandas as gpd  # pour l'export en gpkg
from shapely import wkb, wkt  # pour l'export en gpkg (verification de la géométrie)
import pandas as pd  # pour l'export en csv

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
    get_degats_for_resultats_suivi,
)
from ..user.utils import check_auth_redirect_login

from .all_stmt import (
    get_stmt_for_declarations_export,
    stmt_one_declaration_a_renouveler
)
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
@bp.route("declaration", methods=["GET"])
# @bp.route("declaration", methods=["GET"], defaults={"id_declaration": None})
@check_auth_redirect_login(
    1
)  # Vérifie que l'utilisateur est authentifié (niveau 1 minimum)
@json_resp_accept_empty_list  # Retourne une liste vide si aucune déclaration n'est trouvée
def api_get_declaration():
    """
    Récupère une déclaration complète avec toutes les informations nécessaires à l'affichage détaillé.
    Utilisée pour consulter ou afficher une déclaration avec ses zones géographiques.
    """
    id_declaration = request.args.get("id", type=int)
    if not id_declaration:
        schemaDeclaration = TDeclarationSchema()
        return schemaDeclaration.dump(TDeclaration())


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
        return {"error": "Token manquant"}, 400
    id_declaration = request.args.get("id")
    if not id_declaration:
        return {"error": "ID de déclaration manquant"}, 400

    stmt = stmt_one_declaration_a_renouveler(id_declaration)
    result = DB.session.execute(stmt).fetchone()
    if not result:
        return {"error": "Déclaration non trouvée"}, 404
    now = datetime.now()

    if now > result["date_fin_token"]:
        return {"error": "Le lien a expiré"}, 404
    
    if token != result["token_renouvellement"]:
        return {"error": "Token invalide"}, 404
    else:
        return {"message": "Token valide"}, 200
    


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
        dir_path = str(config["ROOT_DIR"] / "static/shapefiles")
        output_filename = f"{dir_path}/{file_name}.gpkg"
    elif type_file == "csv":
        dir_path = str(config["ROOT_DIR"] / "static/data")
        output_filename = f"{dir_path}/{file_name}.csv"

    print(
        f"Export des déclarations : type_out={type_out}, type_file={type_file}, output_filename={output_filename}"
    )
    # Récupère les données à exporter selon l'utilisateur courant et le type d'export
    stmt_data = get_stmt_for_declarations_export(type_file=type_file, type_out=type_out)
    result_data = DB.session.execute(stmt_data)

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

    # print(f"Export réussi : {output_filename} (layer: ma_couche)")
    return send_from_directory(
        dir_path, file_name + f".{type_file}", as_attachment=True
    )


@bp.route("degats", methods=["GET"])
@json_resp
def degats():
    """ """
    result = get_degats_for_resultats_suivi()
    return result
