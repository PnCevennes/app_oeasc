"""
api chasse
"""

from .models import (
    TZoneCynegetiques,
    TZoneIndicatives,
    TLieuTirs,
    TLieuTirSynonymes,
    TSaisons,
    TSaisonDates,
    TAttributionMassifs,
    TTypeBracelets,
    TAttributions,
    TRealisationsChasse,
    VPlanChasseRealisationBilan,
    VChasseBilan,
)

from .schema import (
    TZoneCynegetiquesSchema,
    TZoneIndicativesSchema,
    TLieuTirsSchema,
    TLieuTirSynonymesSchema,
    TSaisonsSchema,
    TSaisonDatesSchema,
    TAttributionMassifsSchema,
    TTypeBraceletsSchema,
    TAttributionsSchema,
    TRealisationsChasseSchema,
    VPlanChasseRealisationBilanSchema,
    VChasseBilanSchema,
)

from ..generic.definitions import GenericRouteDefinitions
from ..generic.repository import getlist
from flask import Blueprint, current_app, request, send_file
from utils_flask_sqla.response import json_resp, csv_resp
from utils_flask_sqla.generic import GenericQuery
from ..user.utils import check_auth_redirect_login
from .repositories import (
    get_chasse_bilan,
    get_attribution_result,
    chasse_process_args,
    chasse_get_infos,
)
from .export_chasse import (
    exportation_attributions_realises_chasse,
    get_data_all_especes_export_ods,
)
from .importation_csv import traitement_import_realisation_chasse
from sqlalchemy import func
import datetime

from py3o.template import Template

config = current_app.config
DB = config["DB"]


bp = Blueprint("chasse_api", __name__)

############################################################################################
########### ROUTES DYNAMIQUES POUR ACCEDER AUX MODELES DE LA BASE DE DONNEES ##############
############################################################################################

# générateur de routes situé dans le module generic (c'est un singleton). L'objet grd est partagé entre toutes les instances de la classe
# les definitions suivantes seront ajoutées à celles des autres modules oeasc
grd = GenericRouteDefinitions()

# définis les droit pour chaque route (C: create, R: read, U: update, D: delete)
droits = {"C": 4, "R": 0, "U": 4, "D": 4}

# routes dynamiques pour accéder aux modèles de la base de données
# la route est par exemple de la forme <blueprint>/chasse/personne/ pour accéder à la table TPersonnes
definitions = {
    "zone_cynegetique": {
        "model": TZoneCynegetiques,
        "droits": droits,
        "schema": TZoneCynegetiquesSchema,
    },
    "zone_cynegetique": {
        "model": TZoneCynegetiques,
        "droits": droits,
        "schema": TZoneCynegetiquesSchema,
    },
    "zone_indicative": {
        "model": TZoneIndicatives,
        "droits": droits,
        "schema": TZoneIndicativesSchema,
    },
    "lieu_tir": {"model": TLieuTirs, "droits": droits, "schema": TLieuTirsSchema},
    "lieu_tir_synonyme": {
        "model": TLieuTirSynonymes,
        "droits": droits,
        "schema": TLieuTirSynonymesSchema,
    },
    "saison": {"model": TSaisons, "droits": droits, "schema": TSaisonsSchema},
    "saison_date": {
        "model": TSaisonDates,
        "droits": droits,
        "schema": TSaisonDatesSchema,
    },
    "attribution_massif": {
        "model": TAttributionMassifs,
        "droits": droits,
        "schema": TAttributionMassifsSchema,
    },
    "type_bracelet": {
        "model": TTypeBracelets,
        "droits": droits,
        "schema": TTypeBraceletsSchema,
    },
    "attribution": {
        "model": TAttributions,
        "droits": droits,
        "schema": TAttributionsSchema,
    },
    "realisation": {
        "model": TRealisationsChasse,
        "droits": droits,
        "schema": TRealisationsChasseSchema,
    },
    "plan_chasse_realisation_bilan": {
        "model": VPlanChasseRealisationBilan,
        "droits": droits,
        "schema": VPlanChasseRealisationBilanSchema,
    },
    "chasse_bilan": {
        "model": VChasseBilan,
        "droits": droits,
        "schema": VChasseBilanSchema,
    },
}
# ajout des définition dans le singleton grd
grd.add_generic_routes("chasse", definitions)


@bp.route("results/bilan", methods=["GET"])
@json_resp
def chasse_bilan():
    """
    route pour le bilan chasse
    """
    # traitement des paramètres dans la requete. définie la zone prioritaire et retourne un dictionnaire de type
    # return {
    #     "id_saison": id_saison,
    #     "id_espece": id_espece,
    #     "id_secteur": id_secteur, (liste)
    #     "id_zone_cynegetique": id_zone_cynegetique, (liste)
    #     "id_zone_indicative": id_zone_indicative, (liste)
    #     "poids_ou_dagues": poids_ou_dagues,
    # }
    params = chasse_process_args()

    return get_chasse_bilan(params)


@bp.route("results/ice", methods=["GET"])
@json_resp
def api_result_ice():
    """
    Route pour le calcul ICE (Indice de Chasse Ecologique).
    Utilisée pour retourner le résultat du calcul ICE en fonction des paramètres fournis dans la requête GET.
    Les paramètres sont extraits via chasse_process_args() et transmis à la fonction SQL fct_calcul_ice_mc.
    En cas d'erreur ou de données insuffisantes, un message d'erreur est retourné.
    """
    # Récupère les paramètres de la requête (id_espece, id_zone_indicative, id_zone_cynegetique, id_secteur, poids_ou_dagues)
    params = chasse_process_args()

    try:
        # Appelle la fonction SQL pour calculer l'ICE avec les paramètres récupérés
        req = func.oeasc_chasse.fct_calcul_ice_mc(
            params["id_espece"],
            params["id_zone_indicative"],
            params["id_zone_cynegetique"],
            params["id_secteur"],
            params["poids_ou_dagues"],
        )

        # Exécute la requête et récupère le premier résultat
        res = DB.session.execute(req).first()

        # Si aucun résultat n'est retourné, renvoie une erreur avec code 204
        if res is None or res[0] is None:
            return {
                "error": "Aucun résultat calculé - données insuffisantes",
                "code": 204,
            }

        # Retourne le résultat du calcul ICE
        return res[0]

    except Exception as e:
        # En cas d'erreur lors du calcul, log l'erreur et retourne un message d'erreur avec code 500
        current_app.logger.error(f"Erreur calcul ICE: {str(e)}")
        return {"error": "Erreur lors du calcul ICE", "details": str(e), "code": 500}


# @bp.route('results/realisation', methods=['GET'])
# @json_resp
# def api_result_realisation():
#     params = chasse_process_args()
#     columns = GenericTable('v_pre_bilan_pretty', 'oeasc_chasse', DB.engine).tableDef.columns


@bp.route("results/infos", methods=["GET"])
@json_resp
def api_chasse_result_info():
    """ """
    return chasse_get_infos()


@bp.route("results/attribution_bracelet", methods=["GET"])
@json_resp
def api_result_custom():
    """
    Route pour obtenir les résultats d'attribution des bracelets de chasse.
    Utilisée pour retourner les résultats d'attribution pour chaque type de bracelet (CEM, CEFF, CEFFD).
    Les paramètres de la requête sont traités par chasse_process_args().
    Pour chaque type de bracelet, la fonction get_attribution_result est appelée avec les paramètres adaptés.
    Retourne un dictionnaire contenant les résultats pour chaque type de bracelet.
    """
    # Récupère les paramètres de la requête GET
    params = chasse_process_args()

    out = {}

    # Pour chaque type de bracelet, calcule et stocke le résultat d'attribution
    for bracelet in ["CEM", "CEFF", "CEFFD"]:
        params["bracelet"] = bracelet
        data = get_attribution_result(params)
        out[bracelet] = data
    return out


##########################    EXPORT    ###########################


@bp.route("export/ods", methods=["GET"])
def api_chasse_ods():
    """
    Route pour exporter le bilan de chasse au format ODS (OpenDocument Spreadsheet).
    Cette API génère un fichier ODS à partir d'un template et des données de chasse pour une saison donnée.
    Utilisation typique : extraction du bilan de chasse pour archivage ou diffusion sous format tableur.
    """

    # Chemin du template ODS utilisé pour générer le fichier final
    template_path = (
        config["ROOT_DIR"] / "backend/oeasc/templates/ods/template_bilan_chasse.ods"
    )
    # Chemin du fichier ODS généré (dans le dossier static/export)
    output_path = config["ROOT_DIR"] / "static/export/test.ods"
    # Récupère le nom de la saison depuis les paramètres de la requête GET, "current" par défaut
    nom_saison = request.args.get("saison", "current")

    # Récupère les données à exporter pour toutes les espèces et la saison demandée
    # Fonction utilisée lors de l'export ODS pour préparer les données à injecter dans le template
    data = get_data_all_especes_export_ods(nom_saison)

    # Crée le dossier de sortie s'il n'existe pas (pour éviter les erreurs d'écriture)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    # Initialise le template ODS avec le chemin du template et du fichier de sortie
    t = Template(template_path, output_path)
    # Injecte les données dans le template et génère le fichier ODS
    t.render(data)

    # Retourne le fichier ODS généré en pièce jointe, avec un nom personnalisé selon la saison
    return send_file(
        output_path,
        as_attachment=True,
        download_name=f"bilan_chasse_{nom_saison}.ods",
    )


@bp.route("export/csv/", methods=["GET"])
@csv_resp
def api_result_export():
    """
    Route pour exporter des données au format CSV.
    Cette API permet d'exporter les réalisations de chasse sous forme de fichier CSV, selon les paramètres fournis dans la requête GET.
    Utilisation typique : extraction des données pour analyse ou archivage.
    """
    print("Requête reçue pour l'export CSV des réalisations de chasse")
    df = exportation_attributions_realises_chasse()

    # Retourne un tuple attendu par csv_resp (filename, data, columns, separator)
    data = df.to_dict(orient="records")
    columns = list(df.columns)
    file_name = "export_realisation_chasse_{}".format(
        datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%s")
    )
    return (file_name, data, columns, ";")


############################    IMPORT    ###########################


@bp.route("import/traitement-csv", methods=["POST"])
@check_auth_redirect_login(4)
def traitement_csv():
    """Route pour traiter l'importation d'un fichier CSV contenant les réalisations de chasse.
    Les paramètres de la requête POST doivent inclure :
    - saison : la saison pour laquelle les données sont importées
    - update : indique si les données existantes doivent être mises à jour ("true" ou "false")
    - file : le fichier CSV à importer
    """
    saison = request.form.get("saison")
    update = request.form.get("update")  # sera une string "true" ou "false"
    file = request.files.get("file")
    apiResponse = traitement_import_realisation_chasse(file, saison, update)
    if apiResponse.success == False:
        apiResponse.print_all()

    return apiResponse.response_to_frontend()


@bp.route("import/download-erreurs-csv/<file_name>", methods=["GET"])
def download_erreurs_csv(file_name):
    """Route pour télécharger le fichier CSV contenant les erreurs d'importation des réalisations de chasse.
    Le nom du fichier est passé en paramètre dans l'URL. Le fichier doit être situé dans le dossier static/erreurs_import_chasse.
    """
    file_name = request.view_args.get("file_name")
    # Chemin du fichier CSV généré (dans le dossier static/erreurs_import_chasse)
    output_path = config["ROOT_DIR"] / "static/erreurs_import_chasse" / file_name
    # Retourne le fichier CSV généré en pièce jointe, avec un nom personnalisé selon la saison
    return send_file(
        output_path,
        as_attachment=True,
        download_name=f"{file_name}",
        mimetype="text/csv",
    )
