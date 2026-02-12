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

from pypnnomenclature.models import TNomenclatures
from pypnnomenclature.schemas import NomenclatureSchema

from ..generic.definitions import GenericRouteDefinitions
from ..generic.repository import getlist
from flask import Blueprint, current_app, request, send_file
from utils_flask_sqla.response import json_resp, csv_resp
from utils_flask_sqla.generic import GenericQuery
from .repositories import (
    get_chasse_bilan,
    get_attribution_result,
    chasse_process_args,
    chasse_get_infos,
    # get_data_export_ods,
    get_data_all_especes_export_ods,
    filtrage_stmt_secteur_zi_zc
)
from sqlalchemy import  func, select
from sqlalchemy.orm import aliased
import datetime

# from oeasc.utils.env import ROOT_DIR
from py3o.template import Template
from .importation_csv import api_import_traitement_csv

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
# la route est par exemple de la forme <blueprint>/chasse/saison/ pour accéder à la table TSaisons
definitions = {
    "personne": {"model": TPersonnes, "droits": droits, "schema": TPersonnesSchema},
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


@bp.route("export/csv/", methods=["GET"])
@csv_resp
def api_result_export():
    """
    Route pour exporter des données au format CSV.
    Cette API permet d'exporter les réalisations de chasse sous forme de fichier CSV, selon les paramètres fournis dans la requête GET.
    Utilisation typique : extraction des données pour analyse ou archivage.
    """

    # Récupère le type de données à exporter depuis les paramètres de la requête (ex: 'realisation')
    data_type = request.args.get("data_type")
    # Récupère les filtres éventuels appliqués à l'export (ex: filtrer par saison, espèce, etc.)
    filters = getlist(request.args, "filters")

    # Dictionnaire associant le type de données à la vue SQL correspondante
    views = {"realisation": "oeasc_chasse.v_export_realisation_csv"}

    # Sélectionne la vue à utiliser selon le type de données demandé
    view = views.get(data_type)
    # Extrait le nom du schéma et de la table (vue) à partir de la chaîne
    schema_name = view.split(".")[0]
    table_name = view.split(".")[1]

    # Exécute la requête sur la vue SQL avec les filtres éventuels, limite à 1 million de lignes
    results = GenericQuery(
        DB, schemaName=schema_name, tableName=table_name, filters=filters, limit=1e6
    ).return_query()

    # Récupère les données extraites
    data = results["items"]
    # Génère le nom du fichier CSV en fonction du type de données et de la date/heure d'export
    file_name = "export_{}_{}".format(
        data_type, datetime.datetime.now().strftime("%Y-%m-%d_%H_%M_%s")
    )
    # Retourne le fichier CSV : nom, données, entêtes de colonnes, séparateur
    return (file_name, data, data[0].keys(), ";")


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



@bp.route("count_categorie_realisations/", methods=["GET"])
@json_resp
def api_count_categorie_realisations():
    """
    pour l'affichage des camemberts dans chasse -> analyse detaillée
    Retourne le nombre de realisation par classe d'age et sexe pour une espece donnee
    """

    # récupère les paramètres de la requête et les traite
    args = chasse_process_args()

    id_espece = args.get('id_espece')
    id_saison = args.get('id_saison')
    list_id_secteur = args.get('id_secteur')
    list_id_zc = args.get('id_zone_cynegetique')
    list_id_zi = args.get('id_zone_indicative')

    


    # create a single alias instance for the 'sexe' nomenclature and reuse it in the join
    sexe = aliased(TNomenclatures, name="sexe")
    classe_age = aliased(TNomenclatures, name="classe_age")

    stmt = select(
        classe_age.label_fr,
        sexe.label_fr,
        func.count().label("count")
    ).select_from(
        TRealisationsChasse
    ).join(
        TAttributions, TRealisationsChasse.id_attribution == TAttributions.id_attribution
    ).join(
        TTypeBracelets, TAttributions.id_type_bracelet == TTypeBracelets.id_type_bracelet
    ).join(
        TNomenclatures, TNomenclatures.id_nomenclature == TRealisationsChasse.id_nomenclature_classe_age
    ).join(
        sexe, sexe.id_nomenclature == TRealisationsChasse.id_nomenclature_sexe
    ).join(
        classe_age, classe_age.id_nomenclature == TRealisationsChasse.id_nomenclature_classe_age
    )
    

    if id_espece:
        stmt = stmt.where(TTypeBracelets.id_espece == id_espece)


    if id_saison:
        stmt = stmt.where(TAttributions.id_saison == id_saison)
    
    # Filtrage par zones. Les zones indicatives ont la priorité sur les zones cynégétiques, qui ont elles même la priorité sur les secteurs
    stmt = filtrage_stmt_secteur_zi_zc(stmt, list_id_secteur, list_id_zc, list_id_zi)

    stmt = stmt.group_by(
        classe_age.label_fr,
        sexe.label_fr
    )


    res = DB.session.execute(stmt).all()

    res = sorted(res, key=lambda x: (x[1], x[0]))  # trier par sexe puis par classe d'age
    
    # formatage des données avec les clés text et count pour s'adapter au camembert highcharts
    data = [
        {
            "text": row[1]+" - "+row[0],
            "count": row[2],
        }
        for row in res
    ]



    return data
