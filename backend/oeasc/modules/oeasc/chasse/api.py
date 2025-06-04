"""
api chasse
"""

from .models import (
    TPersonnes,
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
    TPersonnesSchema,
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
from flask import Blueprint, current_app, request, send_file, jsonify
from utils_flask_sqla.response import json_resp, csv_resp
from utils_flask_sqla.generic import GenericQuery, GenericTable
from .repositories import (
    get_chasse_bilan,
    get_attribution_result,
    chasse_process_args,
    chasse_get_infos,
    get_data_export_ods,
    get_data_all_especes_export_ods,
)
from sqlalchemy import column, select, func, table, distinct, over
import json
import datetime

# from oeasc.utils.env import ROOT_DIR
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
    "personne": {"model": TPersonnes, "droits": droits, "schema": TPersonnesSchema},
    "zone_cynegetique": {"model": TZoneCynegetiques, "droits": droits, "schema": TZoneCynegetiquesSchema},
    "zone_cynegetique": {"model": TZoneCynegetiques, "droits": droits, "schema": TZoneCynegetiquesSchema},
    "zone_indicative": {"model": TZoneIndicatives, "droits": droits, "schema": TZoneIndicativesSchema},
    "lieu_tir": {"model": TLieuTirs, "droits": droits, "schema": TLieuTirsSchema},
    "lieu_tir_synonyme": {"model": TLieuTirSynonymes, "droits": droits, "schema": TLieuTirSynonymesSchema},
    "saison": {"model": TSaisons, "droits": droits, "schema": TSaisonsSchema},
    "saison_date": {"model": TSaisonDates, "droits": droits, "schema": TSaisonDatesSchema},
    "attribution_massif": {"model": TAttributionMassifs, "droits": droits, "schema": TAttributionMassifsSchema},
    "type_bracelet": {"model": TTypeBracelets, "droits": droits, "schema": TTypeBraceletsSchema},
    "attribution": {"model": TAttributions, "droits": droits, "schema": TAttributionsSchema},
    "realisation": {"model": TRealisationsChasse, "droits": droits, "schema": TRealisationsChasseSchema},
    "plan_chasse_realisation_bilan": {
        "model": VPlanChasseRealisationBilan,
        "droits": droits,
        "schema": VPlanChasseRealisationBilanSchema,
    },
    "chasse_bilan": {"model": VChasseBilan, "droits": droits, "schema": VChasseBilanSchema},
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
    API ICE
    """

    params = chasse_process_args()

    req = func.oeasc_chasse.fct_calcul_ice_mc(
        params["id_espece"],
        params["id_zone_indicative"],
        params["id_zone_cynegetique"],
        params["id_secteur"],
        params["poids_ou_dagues"],
    )
    # res = DB.engine.execute(req).first()[0]

    res = DB.session.execute(req).first()[0]

    # res = DB.session.execute(req).first()[0]
    return res


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
    API CUSTOM
    """

    params = chasse_process_args()

    out = {}

    for bracelet in ["CEM", "CEFF", "CEFFD"]:
        params["bracelet"] = bracelet
        data = get_attribution_result(params)
        out[bracelet] = data
    return out


@bp.route("export/csv/", methods=["GET"])
@csv_resp
def api_result_export():
    """
    API CUSTOM
    """

    # gestion paramètres
    data_type = request.args.get("data_type")
    filters = getlist(request.args, "filters")

    views = {"realisation": "oeasc_chasse.v_export_realisation_csv"}

    view = views.get(data_type)
    schema_name = view.split(".")[0]
    table_name = view.split(".")[1]

    # view + filters
    results = GenericQuery(
        DB, schemaName=schema_name, tableName=table_name, filters=filters, limit=1e6
    ).return_query()

    data = results["items"]
    file_name = "export_{}_{}".format(
        data_type, datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%s")
    )
    return (file_name, data, data[0].keys(), ";")


@bp.route("export/ods", methods=["GET"])
def api_chasse_ods():
    """
    test export ods
    """

    template_path = config["ROOT_DIR"] / "backend/oeasc/templates/ods/template_bilan_chasse.ods"
    output_path = config["ROOT_DIR"] / "static/export/test.ods"
    nom_saison = request.args.get("saison", "current")

    data = get_data_all_especes_export_ods(nom_saison)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    t = Template(template_path, output_path)
    t.render(data)

    return send_file(
        output_path,
        as_attachment=True,
        download_name=f"bilan_chasse_{nom_saison}.ods",
    )
