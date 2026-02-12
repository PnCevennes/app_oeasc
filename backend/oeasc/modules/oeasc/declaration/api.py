"""
liste des api pour les declarations
"""

# import copy
import os
import zipfile
from datetime import date
from flask import Blueprint, request, current_app, session
from flask.helpers import send_from_directory
from utils_flask_sqla.response import csv_resp
from utils_flask_sqla_geo.generic import GenericTableGeo

# from oeasc.modules.oeasc.nomenclature import nomenclature_oeasc
from utils_flask_sqla.response import json_resp
from sqlalchemy import delete

# from sqlalchemy.orm import Session

# from oeasc.utils.env import ROOT_DIR

from .repository import (
    get_user,
    get_declarations,
    # get_declaration,
    # f_create_or_update_declaration,
    # get_dict_nomenclature_areas,
    # get_declaration_table,
)

# from .declaration_sample import declaration_dict_random_sample

# from .utils import (
#     get_listes_essences,
#     check_foret,
#     check_proprietaire,
#     check_massif,
# )

from ..user.utils import check_auth_redirect_login

# from .mail import send_mail_validation_declaration
from .models import TDeclaration

bp = Blueprint("declaration_api", __name__)

config = current_app.config
DB = config["DB"]


@bp.route("degats/", methods=["GET"])
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

    return get_declarations(type_out="degat", restrict=True)


@bp.route("declarations/", methods=["GET"])
@json_resp
def declarations():
    """
    Route Flask permettant de récupérer la liste des déclarations accessibles pour l'utilisateur courant.

    Utilisation :
    - Cette route est appelée lorsqu'un utilisateur authentifié souhaite consulter les déclarations
      auxquelles il a accès, selon son rôle et ses droits.
    - Elle est utilisée dans l'interface principale pour afficher la liste des déclarations
      (dégâts ou alertes) filtrées selon l'utilisateur connecté.

    Fonctionnement :
    - La fonction vérifie si un utilisateur est présent dans la session (clé 'current_user').
    - Si oui, elle récupère l'objet utilisateur via la fonction get_user en utilisant l'id_role.
    - Elle appelle ensuite la fonction get_declarations, qui retourne la liste des déclarations
      accessibles à cet utilisateur.
    - Si aucun utilisateur n'est connecté, elle passe None à get_declarations, ce qui peut
      limiter ou empêcher l'accès aux données selon l'implémentation de get_declarations.

    Retour :
    - La liste des déclarations accessibles à l'utilisateur courant, au format JSON.
    """

    # Vérifie la présence d'un utilisateur dans la session et récupère l'objet utilisateur
    user = (
        get_user(session["current_user"]["id_role"])
        if "current_user" in session and session["current_user"]
        else None
    )

    # Retourne la liste des déclarations accessibles à cet utilisateur
    return get_declarations(user=user)


@bp.route("declaration/<int:id_declaration>", methods=["GET"])
@check_auth_redirect_login(1)
@json_resp
def route_declaration(id_declaration):
    """
    Retourne la declaration d'id id_declaration
    """
    # Vérifie la présence d'un utilisateur dans la session et récupère l'objet utilisateur
    user = (
        get_user(session["current_user"]["id_role"])
        if "current_user" in session and session["current_user"]
        else None
    )
    declaration = get_declarations(id_declaration=id_declaration, user=user)[0]

    if not declaration:
        return None

    return declaration


# @bp.route("declaration_html/<int:id_declaration>", methods=["GET", "POST"])
# @check_auth_redirect_login(1)
# @json_resp
# def declaration_html(id_declaration):
#     """
#     Retourne la declaration en html d'id id_declaration
#     """

#     btn_action = request.args.get("btn_action", "")
#     map_display = request.args.get("map_display", "")

#     declaration = get_declaration(id_declaration)

#     if not declaration:
#         return None

#     return render_template(
#         "modules/oeasc/entity/declaration_table.html",
#         declaration_table=declaration,
#         id_declaration=id_declaration,
#         nomenclature=nomenclature_oeasc(),
#         btn_action=btn_action,
#         map_display=map_display,
#     )


# @bp.route("get_form_declaration", methods=["POST"])
# @check_auth_redirect_login(1)
# @json_resp
# def get_form_declaration():
#     """
#     Retourne le formulaire correspondant
#     à la déclaration envoyée en post dans data['declaration']
#     """
#     data = request.get_json()

#     nomenclature = nomenclature_oeasc()
#     declaration_dict = data["declaration"]
#     id_form = data["id_form"]

#     # recherche de la  foret le cas echeant (apres un choix de foret documentee)
#     get_dict_nomenclature_areas(declaration_dict)

#     check_foret(declaration_dict)

#     check_proprietaire(declaration_dict)

#     check_massif(declaration_dict)

#     listes_essences = get_listes_essences(declaration_dict)

#     declaration_table = get_declaration_table(declaration_dict)

#     return render_template(
#         "modules/oeasc/form/form_declaration.html",
#         declaration=declaration_dict,
#         declaration_table=declaration_table,
#         nomenclature=nomenclature,
#         listes_essences=listes_essences,
#         id_form=id_form,
#     )


@bp.route("delete_declaration/<int:id_declaration>", methods=["POST"])
@check_auth_redirect_login(4)
@json_resp
def delete_declaration(id_declaration):
    """
    Supprime une déclaration (id_déclaration) de la base de données.

    Utilisation :
    - Cette route est appelée lorsqu'un utilisateur authentifié (niveau d'accès 4 ou plus)
      souhaite supprimer une déclaration spécifique identifiée par son id.
    - Elle est utilisée principalement dans l'interface d'administration ou par les gestionnaires
      habilités à effectuer des suppressions de données sensibles.

    Fonctionnement :
    - La fonction reçoit l'identifiant de la déclaration à supprimer via l'URL.
    - Elle construit une requête SQLAlchemy pour supprimer la déclaration correspondante
      dans la table TDeclaration.
    - La suppression est exécutée et validée en base via commit().
    - La réponse "ok" est retournée au format JSON pour indiquer le succès de l'opération.
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


# @bp.route("random_declaration", methods=["GET"])
# @check_auth_redirect_login(5)
# @json_resp
# def random_declaration():
#     """
#     Renvoie une déclaration crée aléatoirement
#     """

#     declaration_dict = declaration_dict_random_sample()
#     get_dict_nomenclature_areas(declaration_dict)
#     return declaration_dict


# @bp.route("random_populate", defaults={"nb": 1}, methods=["GET"])
# @bp.route("random_populate/<int:nb>", methods=["GET"])
# @check_auth_redirect_login(5)
# @json_resp
# def random_populate(nb):
#     """
#     Crée et ajoute en base nb déclarations
#     """

#     for i in range(nb):
#         declaration_dict = declaration_dict_random_sample()

#         if not declaration_dict:
#             continue

#         declaration_dict_2 = copy.deepcopy(declaration_dict)
#         get_dict_nomenclature_areas(declaration_dict_2)

#         id_area = check_massif(declaration_dict_2)
#         if not id_area:
#             continue

#         declaration_dict["areas_localisation"].append({"id_area": id_area})
#         # check_foret(declaration_dict, nomenclature)
#         # check_proprietaire(declaration_dict, nomenclature)
#         declaration_dict = f_create_or_update_declaration(declaration_dict)

#     return "ok"


# @bp.route("create_or_update_declaration", methods=["POST"])
# @check_auth_redirect_login(1)
# @json_resp
# def create_or_update_declaration():
#     """
#     cree une nvlle déclaration quand id déclaration est renseigné
#     ou
#     update une declaration existante
#     """

#     data = request.get_json()
#     b_create = data["declaration"].get("id_declaration")
#     declaration_dict = data["declaration"]
#     d = f_create_or_update_declaration(declaration_dict)

#     send_mail_validation_declaration(d, b_create)

#     return d


def get_file_name(type_out):
    """
    Génère le nom de fichier pour l'export des déclarations.

    Utilisation :
    - Cette fonction est utilisée lors de l'export des déclarations au format CSV ou SHAPE,
      notamment dans les routes 'declarations_csv' et 'declarations_shape'.
    - Elle permet de nommer dynamiquement le fichier exporté selon le type de déclaration
      ('degat' ou autre) et la date du jour.

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


@bp.route("declarations_csv/", methods=["GET"])
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
    data = get_declarations(
        user=get_user(session["current_user"]["id_role"]),
        type_export="csv",
        type_out=type_out,
    )

    # Détermine les colonnes du CSV à partir des clés du premier élément des données
    columns = list(data[0].keys())

    # Retourne les informations nécessaires à la génération du CSV
    return (file_name, data, columns, separator)


@bp.route("declarations_shape/", methods=["GET"])
@check_auth_redirect_login(1)
def declarations_shape():
    """
    Route Flask permettant d'exporter la liste des déclarations au format Shapefile (SHP).

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
    data = get_declarations(
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
