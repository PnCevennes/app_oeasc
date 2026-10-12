"""
api dégâts agricoles
"""

import datetime

from flask import Blueprint, request, session, jsonify
from flask_login import current_user as login_user
from werkzeug.utils import secure_filename

from oeasc.ref_geo_oeasc.models import TCommunesArea
from .models import TSaisonAgricole, TTypeCulture, TDeclarationAgricole
from .schema import (
    TSaisonAgricoleSchema,
    TTypeCultureSchema,
    TDeclarationAgricoleSchema,
    TCommunesAreaSchema,
)
from .importation import EXTENSIONS_ACCEPTEES
from .repository import (
    ZONE,
    get_saison,
    get_bilan_saisons,
    get_bilan_cultures,
    get_bilan_communes_geojson,
)
from ..generic.definitions import GenericRouteDefinitions
from ..user.utils import check_auth_redirect_login
from ..chasse.import_async import (
    creer_suivi,
    lancer_import_async,
    lire_suivi,
    DOSSIER_SUIVI,
)

bp = Blueprint("agricole_api", __name__)

# routes dynamiques (module generic) pour accéder aux modèles de la base de données
# ex : api/generic/agricole/declarations
grd = GenericRouteDefinitions()

# définis les droit pour chaque route (C: create, R: read, U: update, D: delete)
droits = {"C": 5, "R": 5, "U": 5, "D": 5}

definitions = {
    "declaration": {
        "model": TDeclarationAgricole,
        "droits": droits,
        "schema": TDeclarationAgricoleSchema,
    },
    "saison": {
        "model": TSaisonAgricole,
        "droits": droits,
        "schema": TSaisonAgricoleSchema,
    },
    "type_culture": {
        "model": TTypeCulture,
        "droits": droits,
        "schema": TTypeCultureSchema,
    },
    # communes de l'observatoire (ref_geo.communes_aoa) : lecture seule, pour les
    # listes de choix. Sans droit C/U/D défini, ces routes sont fermées.
    "commune": {
        "model": TCommunesArea,
        "droits": {"R": 5},
        "schema": TCommunesAreaSchema,
    },
}
grd.add_generic_routes("agricole", definitions)


@bp.route("import", methods=["POST"])
@check_auth_redirect_login(5)
def import_degats_agricoles():
    """Lance l'importation d'un fichier de dégâts agricoles en tâche de fond.

    Le fichier est enregistré sur disque, un fichier de suivi JSON est créé, et le
    traitement est délégué à un thread. La réponse (202) contient `id_import` ;
    le frontend suit l'avancement via `GET import/status/<id_import>`.

    Paramètres POST (multipart) : update ("true"/"false"), file (csv, xls ou ods).
    """
    update = request.form.get("update") == "true"
    file = request.files.get("file")

    session_user = session.get("current_user") or {}
    id_role = session_user.get("id_role")
    nom_complet = session_user.get("nom_complet")
    # repli sur l'utilisateur du token (flask-login) si la session ne le porte pas
    if id_role is None and getattr(login_user, "is_authenticated", False):
        id_role = getattr(login_user, "id_role", None)
        nom_complet = nom_complet or " ".join(
            p
            for p in (
                getattr(login_user, "prenom_role", None),
                getattr(login_user, "nom_role", None),
            )
            if p
        )

    if file is None or file.filename == "":
        return jsonify({"success": False, "user_message": "Aucun fichier fourni."}), 400

    nom_sur = secure_filename(file.filename) or "import.csv"
    if not nom_sur.lower().endswith(EXTENSIONS_ACCEPTEES):
        return (
            jsonify(
                {
                    "success": False,
                    "user_message": "Format de fichier non pris en charge. "
                    "Formats acceptés : " + ", ".join(EXTENSIONS_ACCEPTEES),
                }
            ),
            400,
        )

    horodatage = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    chemin_fichier = DOSSIER_SUIVI / f"{horodatage}_degats_agricoles_{nom_sur}"
    file.save(chemin_fichier)

    id_import = creer_suivi(
        id_saison=None,
        do_update=update,
        nom_fichier=file.filename,
        chemin_fichier=chemin_fichier,
        id_role=id_role,
        nom_complet=nom_complet,
        type_import="degats_agricoles",
    )
    lancer_import_async(
        id_import=id_import,
        chemin_fichier=str(chemin_fichier),
        id_saison=None,
        do_update=update,
        id_role=id_role,
        nom_complet=nom_complet,
        type_import="degats_agricoles",
    )

    return (
        jsonify({"success": True, "id_import": id_import, "statut": "EN_ATTENTE"}),
        202,
    )


@bp.route("import/status/<id_import>", methods=["GET"])
@check_auth_redirect_login(5)
def import_status(id_import):
    """Renvoie l'état d'un import lancé en tâche de fond (statut, journal, success)."""
    etat = lire_suivi(id_import)
    if etat is None or etat.get("type_import") != "degats_agricoles":
        return (
            jsonify({"success": False, "user_message": "Import introuvable."}),
            404,
        )
    return jsonify({"success": True, "import_status": etat})


############################################################################################
########### RESTITUTION : routes publiques (page « Dégâts agricoles ») #####################
############################################################################################


def _saison_from_args():
    """Saison désignée par le paramètre `id_saison`, ou (None, réponse d'erreur)."""
    valeur = request.args.get("id_saison")
    try:
        id_saison = int(valeur)
    except (TypeError, ValueError):
        return None, (
            jsonify(
                {
                    "success": False,
                    "message": "Paramètre id_saison manquant ou invalide.",
                }
            ),
            400,
        )
    saison = get_saison(id_saison)
    if saison is None:
        return None, (jsonify({"success": False, "message": "Saison inconnue."}), 404)
    return saison, None


@bp.route("results/saisons", methods=["GET"])
def results_saisons():
    """Indicateurs par saison : montant indemnisé, nombre de déclarations et de
    dossiers, surfaces détruite et ressemée (ha)."""
    return jsonify({"zone": ZONE, "items": get_bilan_saisons()})


@bp.route("results/cultures", methods=["GET"])
def results_cultures():
    """Indicateurs par type de culture pour la saison `id_saison`."""
    saison, erreur = _saison_from_args()
    if erreur:
        return erreur
    return jsonify(
        {
            "zone": ZONE,
            "id_saison": saison.id_saison,
            "nom_saison": saison.nom_saison,
            "items": get_bilan_cultures(saison.id_saison),
        }
    )


@bp.route("results/communes", methods=["GET"])
def results_communes():
    """GeoJSON des communes de la zone OEASC avec les indicateurs de la saison
    `id_saison` (surface détruite, montant indemnisé, nombre de dossiers)."""
    saison, erreur = _saison_from_args()
    if erreur:
        return erreur
    geojson = get_bilan_communes_geojson(saison.id_saison)
    geojson.update(zone=ZONE, id_saison=saison.id_saison, nom_saison=saison.nom_saison)
    return jsonify(geojson)
