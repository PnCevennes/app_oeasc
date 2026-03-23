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
from ..user.utils import check_auth_redirect_login
from .repositories import (
    get_chasse_bilan,
    get_attribution_result,
    chasse_process_args,
    chasse_get_infos,
    filtrage_stmt_secteur_zi_zc,
)
from .export_chasse import (
    exportation_attributions_realises_chasse,
    get_data_all_especes_export_ods,
)
from .importation_csv import traitement_import_realisation_chasse
from sqlalchemy import func, select
from sqlalchemy.orm import aliased
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

# pour certains graphiques on modifiera le numéro de mois par son nom.
MOIS_MAPPING = {
    "01": "Jan.",
    "02": "Fév.",
    "03": "Mar.",
    "04": "Avr.",
    "05": "Mai",
    "06": "Juin",
    "07": "Juil.",
    "08": "Aou.",
    "09": "Sep.",
    "10": "Oct.",
    "11": "Nov.",
    "12": "Déc.",
}

# pour trier les mois dans l'ordre de la saison de chasse (de septembre à aout)
MOIS_ORDER = [
    "Sep.",
    "Oct.",
    "Nov.",
    "Déc.",
    "Jan.",
    "Fév.",
    "Mar.",
    "Avr.",
    "Mai",
    "Juin",
    "Juil.",
    "Aou.",
]

# routes dynamiques pour accéder aux modèles de la base de données
# la route est par exemple de la forme <blueprint>/chasse/saison/ pour accéder à la table TSaisons
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


###################################################################################################
########### REQUETES POUR LES GRAPHIQUES D'ANALYSE DETAILLEE DANS LE BILAN DE CHASSE ##############
####################################################################################################


@bp.route("count_categorie_realisations/", methods=["GET"])
@json_resp
def api_count_categorie_realisations():
    """
    pour l'affichage des camemberts dans chasse -> analyse detaillée
    Retourne le nombre de realisation par classe d'age et sexe pour une espece donnee
    """

    # récupère les paramètres de la requête et les traite
    args = chasse_process_args()

    id_espece = args.get("id_espece")
    id_saison = args.get("id_saison")
    list_id_secteur = args.get("id_secteur")
    list_id_zc = args.get("id_zone_cynegetique")
    list_id_zi = args.get("id_zone_indicative")

    # create a single alias instance for the 'sexe' nomenclature and reuse it in the join
    sexe = aliased(TNomenclatures, name="sexe")
    classe_age = aliased(TNomenclatures, name="classe_age")

    stmt = (
        select(classe_age.label_fr, sexe.label_fr, func.count().label("count"))
        .select_from(TRealisationsChasse)
        .join(
            TAttributions,
            TRealisationsChasse.id_attribution == TAttributions.id_attribution,
        )
        .join(
            TTypeBracelets,
            TAttributions.id_type_bracelet == TTypeBracelets.id_type_bracelet,
        )
        .join(
            TNomenclatures,
            TNomenclatures.id_nomenclature
            == TRealisationsChasse.id_nomenclature_classe_age,
        )
        .join(
            TZoneCynegetiques,
            TZoneCynegetiques.id_zone_cynegetique
            == TAttributions.id_zone_cynegetique_affectee,
        )
        .join(sexe, sexe.id_nomenclature == TRealisationsChasse.id_nomenclature_sexe)
        .join(
            classe_age,
            classe_age.id_nomenclature
            == TRealisationsChasse.id_nomenclature_classe_age,
        )
    )

    if id_espece:
        stmt = stmt.where(TTypeBracelets.id_espece == id_espece)

    if id_saison:
        stmt = stmt.where(TAttributions.id_saison == id_saison)

    # Filtrage par zones. Les zones indicatives ont la priorité sur les zones cynégétiques, qui ont elles même la priorité sur les secteurs
    stmt = filtrage_stmt_secteur_zi_zc(stmt, list_id_zi, list_id_zc, list_id_secteur)

    stmt = stmt.group_by(classe_age.label_fr, sexe.label_fr)

    res = DB.session.execute(stmt).all()

    res = sorted(
        res, key=lambda x: (x[1], x[0])
    )  # trier par sexe puis par classe d'age

    # formatage des données avec les clés text et count pour s'adapter au camembert highcharts
    data = [
        {
            "text": row[1] + " - " + row[0],
            "count": row[2],
        }
        for row in res
    ]

    return data


@bp.route("count_mode_chasse_realisations/", methods=["GET"])
@json_resp
def api_count_mode_chasse_realisations():
    args = chasse_process_args()

    id_espece = args.get("id_espece")
    id_saison = args.get("id_saison")
    list_id_secteur = args.get("id_secteur")
    list_id_zc = args.get("id_zone_cynegetique")
    list_id_zi = args.get("id_zone_indicative")

    stmt = (
        select(TNomenclatures.label_fr, func.count().label("count"))
        .select_from(TRealisationsChasse)
        .join(
            TAttributions,
            TRealisationsChasse.id_attribution == TAttributions.id_attribution,
        )
        .join(
            TTypeBracelets,
            TAttributions.id_type_bracelet == TTypeBracelets.id_type_bracelet,
        )
        .join(
            TNomenclatures,
            TNomenclatures.id_nomenclature
            == TRealisationsChasse.id_nomenclature_mode_chasse,
        )
        .join(
            TZoneCynegetiques,
            TZoneCynegetiques.id_zone_cynegetique
            == TAttributions.id_zone_cynegetique_affectee,
        )
        .where(TRealisationsChasse.id_nomenclature_mode_chasse != None)
    )

    if id_espece:
        stmt = stmt.where(TTypeBracelets.id_espece == id_espece)

    if id_saison:
        stmt = stmt.where(TAttributions.id_saison == id_saison)

    # Filtrage par zones. Les zones indicatives ont la priorité sur les zones cynégétiques, qui ont elles même la priorité sur les secteurs
    stmt = filtrage_stmt_secteur_zi_zc(stmt, list_id_zi, list_id_zc, list_id_secteur)

    stmt = stmt.group_by(TNomenclatures.label_fr)

    res = DB.session.execute(stmt).all()
    data = [
        {
            "text": row[0],
            "count": row[1],
        }
        for row in res
    ]
    return data


# pas utlisé, c'était la requête initiale pour le graph mulitiligne mais je l'ai simplifiée
@bp.route("realisations_par_mois_sur_dernieres_saisons_par_mois/", methods=["GET"])
@json_resp
def api_realisations_par_mois_sur_dernieres_saisons_par_mois():
    """ """
    args = chasse_process_args()

    id_espece = args.get("id_espece")
    list_id_secteur = args.get("id_secteur")
    list_id_zc = args.get("id_zone_cynegetique")
    list_id_zi = args.get("id_zone_indicative")
    # nb_saison = int(args.get("nb_saison", 5))

    nb_saison = request.args.get("nb_saison")
    print("nombre de saison : ", nb_saison)

    mois = func.to_char(TRealisationsChasse.date_exacte, "MM").label("mois")

    stmt = (
        select(
            mois,
            func.count().label("nb_realisations"),
            TSaisons.nom_saison,
            TSaisons.id_saison,
        )
        .select_from(TRealisationsChasse)
        .join(
            TAttributions,
            TRealisationsChasse.id_attribution == TAttributions.id_attribution,
        )
        .join(
            TTypeBracelets,
            TAttributions.id_type_bracelet == TTypeBracelets.id_type_bracelet,
        )
        .join(
            TZoneCynegetiques,
            TZoneCynegetiques.id_zone_cynegetique
            == TAttributions.id_zone_cynegetique_affectee,
        )
        .join(
            TZoneIndicatives,
            TZoneIndicatives.id_zone_indicative
            == TAttributions.id_zone_indicative_affectee,
        )
        .join(TSaisons, TSaisons.id_saison == TAttributions.id_saison)
        .where(
            TSaisons.id_saison.in_(
                select(TSaisons.id_saison)
                .order_by(TSaisons.nom_saison.desc())
                .limit(nb_saison)
            )
        )
        .group_by(mois, TSaisons.nom_saison, TSaisons.id_saison)
        .order_by(mois, TSaisons.id_saison)
    )

    if id_espece:
        stmt = stmt.where(TTypeBracelets.id_espece == id_espece)

    # Filtrage par zones. Les zones indicatives ont la priorité sur les zones cynégétiques, qui ont elles même la priorité sur les secteurs
    stmt = filtrage_stmt_secteur_zi_zc(stmt, list_id_zi, list_id_zc, list_id_secteur)

    res = DB.session.execute(stmt).all()

    # on regroupe  les resutat par mois puis par saison. On commence par le mois de septembre (début de la saison de chasse)
    #  pour finir par mars (fin de la saison de chasse) pour que les saisons soient regroupées de septembre à aout
    # le resuttat final sera de la forme
    # [
    #     {
    #       "text": "Sep.",
    #       "count": 150,
    #       "data": [
    #         {
    #           "count": 50,
    #           "text": "2023-2024",
    #         },
    #         {
    #           "count": 100,
    #           "text": "2022-2023",
    #         },
    #       ]
    #     }, ...
    #     ...
    # ]

    data = []
    for mois, nb_realisations, nom_saison, id_saison in res:
        mois_txt = MOIS_MAPPING.get(mois, mois)
        saison_data = {
            "nom_saison": nom_saison,
            "nb_realisations": nb_realisations,
        }
        mois_entry = next((item for item in data if item["mois"] == mois_txt), None)
        if mois_entry:
            mois_entry["data"].append(saison_data)
            mois_entry["nb_realisations_totale"] += nb_realisations
        else:
            data.append(
                {
                    "mois": mois_txt,
                    "nb_realisations_totale": nb_realisations,
                    "data": [saison_data],
                }
            )
    # on trie les mois pour que l'affichage soit de septembre à aout
    MOIS_ORDER = [
        "Sep.",
        "Oct.",
        "Nov.",
        "Déc.",
        "Jan.",
        "Fév.",
        "Mar.",
        "Avr.",
        "Mai",
        "Juin",
        "Juil.",
        "Aou.",
    ]
    data = sorted(data, key=lambda x: MOIS_ORDER.index(x["mois"]))
    return data


# pour le graph multilignes sur la chronologie des prélevements sur n nombre de saisons
@bp.route("realisations_par_mois_sur_dernieres_saisons/", methods=["GET"])
@json_resp
def api_realisations_par_mois_sur_dernieres_saisons():
    """ """
    args = chasse_process_args()

    id_espece = args.get("id_espece")
    list_id_secteur = args.get("id_secteur")
    list_id_zc = args.get("id_zone_cynegetique")
    list_id_zi = args.get("id_zone_indicative")

    nb_saison = request.args.get("nb_saison")

    mois = func.to_char(TRealisationsChasse.date_exacte, "MM").label("mois")

    stmt = (
        select(
            mois,
            func.count().label("nb_realisations"),
            TSaisons.nom_saison,
            TSaisons.id_saison,
        )
        .select_from(TRealisationsChasse)
        .join(
            TAttributions,
            TRealisationsChasse.id_attribution == TAttributions.id_attribution,
        )
        .join(
            TTypeBracelets,
            TAttributions.id_type_bracelet == TTypeBracelets.id_type_bracelet,
        )
        .join(
            TZoneCynegetiques,
            TZoneCynegetiques.id_zone_cynegetique
            == TAttributions.id_zone_cynegetique_affectee,
        )
        .join(
            TZoneIndicatives,
            TZoneIndicatives.id_zone_indicative
            == TAttributions.id_zone_indicative_affectee,
        )
        .join(TSaisons, TSaisons.id_saison == TAttributions.id_saison)
        .where(
            TSaisons.id_saison.in_(
                select(TSaisons.id_saison)
                .order_by(TSaisons.nom_saison.desc())
                .limit(nb_saison)
            )
        )
        .group_by(TSaisons.id_saison, TSaisons.nom_saison, mois)
        .order_by(TSaisons.nom_saison.desc(), mois)
    )

    if id_espece:
        stmt = stmt.where(TTypeBracelets.id_espece == id_espece)

    # Filtrage par zones. Les zones indicatives ont la priorité sur les zones cynégétiques, qui ont elles même la priorité sur les secteurs
    stmt = filtrage_stmt_secteur_zi_zc(stmt, list_id_zi, list_id_zc, list_id_secteur)

    res = DB.session.execute(stmt).all()

    # on regroupe  les resutat par saison puis par mois. On commence par le mois de septembre (début de la saison de chasse)
    #  pour finir par mars (fin de la saison de chasse) pour que les saisons soient regroupées de septembre à aout
    # le resuttat final sera de la forme
    # [
    #     {
    #       "text": "2023-2024",
    #       "count": 150,
    #       "data": [
    #         {
    #           "count": 50,
    #           "text": "sept.",
    #         },
    #         {
    #           "count": 100,
    #           "text": "oct.",
    #         },
    #       ]
    #     }, ...
    #     ...
    # ]

    data = []

    for mois, nb_realisations, nom_saison, id_saison in res:
        mois_txt = MOIS_MAPPING.get(mois, mois)
        # saison_data = {
        #     "nom_saison": nom_saison,
        #     "nb_realisations": nb_realisations,
        # }
        saison_entry = next(
            (item for item in data if item["nom_saison"] == nom_saison), None
        )
        if saison_entry:
            saison_entry["data"].append(
                {
                    "mois": mois_txt,
                    "nb_realisations": nb_realisations,
                }
            )
            # saison_entry["nb_realisations_totale"] += nb_realisations
        else:
            data.append(
                {
                    "nom_saison": nom_saison,
                    # "nb_realisations_totale": nb_realisations,
                    "data": [
                        {
                            "mois": mois_txt,
                            "nb_realisations": nb_realisations,
                        }
                    ],
                }
            )
    # on trie les mois en commençant par septembre pour que les saisons soient regroupées de septembre à aout

    for saison in data:
        saison["data"] = sorted(
            saison["data"], key=lambda x: MOIS_ORDER.index(x["mois"])
        )
    return data


@bp.route("count_realisations_par_type_de_bracelet/", methods=["GET"])
@json_resp
def api_count_realisations_par_type_de_bracelet():
    """
    pour l'affichage des camemberts dans chasse -> analyse detaillée
    Retourne le nombre de realisation par type de bracelet pour une espece donnee
    """

    # récupère les paramètres de la requête et les traite
    args = chasse_process_args()

    id_espece = args.get("id_espece")
    id_saison = args.get("id_saison")
    list_id_secteur = args.get("id_secteur")
    list_id_zc = args.get("id_zone_cynegetique")
    list_id_zi = args.get("id_zone_indicative")

    stmt = (
        select(TTypeBracelets.code_type_bracelet, func.count().label("count"))
        .select_from(TRealisationsChasse)
        .join(
            TAttributions,
            TRealisationsChasse.id_attribution == TAttributions.id_attribution,
        )
        .join(
            TTypeBracelets,
            TAttributions.id_type_bracelet == TTypeBracelets.id_type_bracelet,
        )
        .join(
            TZoneCynegetiques,
            TZoneCynegetiques.id_zone_cynegetique
            == TAttributions.id_zone_cynegetique_affectee,
        )
        .join(
            TZoneIndicatives,
            TZoneIndicatives.id_zone_indicative
            == TAttributions.id_zone_indicative_affectee,
        )
        .where(TTypeBracelets.id_espece == id_espece)
    )

    if id_saison:
        stmt = stmt.where(TAttributions.id_saison == id_saison)

    # Filtrage par zones. Les zones indicatives ont la priorité sur les zones cynégétiques, qui ont elles même la priorité sur les secteurs
    stmt = filtrage_stmt_secteur_zi_zc(stmt, list_id_zi, list_id_zc, list_id_secteur)

    stmt = stmt.group_by(TTypeBracelets.code_type_bracelet)

    res = DB.session.execute(stmt).all()

    # formatage des données avec les clés text et count pour s'adapter au camembert highcharts
    data = [
        {
            "type_bracelet": row[0],
            "nb_bracelet": row[1],
        }
        for row in res
    ]

    return data


@bp.route("difference_nbRealisations_nbAttributions/", methods=["GET"])
@json_resp
def api_difference_nbRealisations_nbAttributions():
    """
    pour l'affichage des graphiques dans chasse -> analyse detaillée
    Retourne le nombre de realisations et le nombre d'attributions par type de bracelet (code_type_bracelet) pour une saison pour une espece donnée
    """

    # récupère les paramètres de la requête et les traite
    args = chasse_process_args()

    id_espece = args.get("id_espece")
    id_saison = args.get("id_saison")
    list_id_secteur = args.get("id_secteur")
    list_id_zc = args.get("id_zone_cynegetique")
    list_id_zi = args.get("id_zone_indicative")

    # on fait une requete pour récupérer le nombre d'attribution par type de bracelet
    stmt_attribution = (
        select(TTypeBracelets.code_type_bracelet, func.count().label("nb_attributions"))
        .select_from(TAttributions)
        .join(
            TTypeBracelets,
            TAttributions.id_type_bracelet == TTypeBracelets.id_type_bracelet,
        )
        .join(
            TZoneCynegetiques,
            TZoneCynegetiques.id_zone_cynegetique
            == TAttributions.id_zone_cynegetique_affectee,
        )
        .join(
            TZoneIndicatives,
            TZoneIndicatives.id_zone_indicative
            == TAttributions.id_zone_indicative_affectee,
        )
        .where(TTypeBracelets.id_espece == id_espece)
    )
    if id_saison:
        stmt_attribution = stmt_attribution.where(TAttributions.id_saison == id_saison)
    # Filtrage par zones. Les zones indicatives ont la priorité sur les zones cynégétiques, qui ont elles même la priorité sur les secteurs
    # stmt_attribution = filtrage_stmt_secteur_zi_zc(stmt_attribution, list_id_zi, list_id_zc, list_id_secteur)
    if list_id_zi:
        stmt_attribution = stmt_attribution.where(
            TAttributions.id_zone_indicative_affectee.in_(list_id_zi)
        )
    elif list_id_zc:
        stmt_attribution = stmt_attribution.where(
            TAttributions.id_zone_cynegetique_affectee.in_(list_id_zc)
        )
    elif list_id_secteur:
        stmt_attribution = stmt_attribution.where(
            TZoneCynegetiques.id_secteur.in_(list_id_secteur)
        )

    stmt_attribution = stmt_attribution.group_by(TTypeBracelets.code_type_bracelet)
    res_attribution = DB.session.execute(stmt_attribution).all()

    # on fait une requete pour récupérer le nombre de realisation par type de bracelet
    stmt_realisation = (
        select(TTypeBracelets.code_type_bracelet, func.count().label("nb_realisations"))
        .select_from(TRealisationsChasse)
        .join(
            TAttributions,
            TRealisationsChasse.id_attribution == TAttributions.id_attribution,
        )
        .join(
            TTypeBracelets,
            TAttributions.id_type_bracelet == TTypeBracelets.id_type_bracelet,
        )
        .join(
            TZoneCynegetiques,
            TZoneCynegetiques.id_zone_cynegetique
            == TAttributions.id_zone_cynegetique_affectee,
        )
        .join(
            TZoneIndicatives,
            TZoneIndicatives.id_zone_indicative
            == TAttributions.id_zone_indicative_affectee,
        )
        .where(TTypeBracelets.id_espece == id_espece)
    )
    if id_saison:
        stmt_realisation = stmt_realisation.where(TAttributions.id_saison == id_saison)
    # Filtrage par zones. Les zones indicatives ont la priorité sur les zones cynégétiques, qui ont elles même la priorité sur les secteurs
    stmt_realisation = filtrage_stmt_secteur_zi_zc(
        stmt_realisation, list_id_zi, list_id_zc, list_id_secteur
    )
    stmt_realisation = stmt_realisation.group_by(TTypeBracelets.code_type_bracelet)
    res_realisation = DB.session.execute(stmt_realisation).all()

    # on merge les deux resultats pour avoir le nombre d'attribution et de realisation par type de bracelet
    data = []

    # retourne les data sous le format [
    #     {
    #         "type_bracelet": "CEM",
    #         "nb_attributions": 100,
    #         "nb_realisations": 80,
    #     },
    # ]

    for row_attribution in res_attribution:
        type_bracelet = row_attribution[0]
        nb_attributions = row_attribution[1]
        nb_realisations = 0
        for row_realisation in res_realisation:
            if row_realisation[0] == type_bracelet:
                nb_realisations = row_realisation[1]
                break
        data.append(
            {
                "type_bracelet": type_bracelet,
                "nb_attributions": nb_attributions,
                "nb_realisations": nb_realisations,
            }
        )

    return data


@bp.route("count_realisations_par_par_mois_par_type_bracelet/", methods=["GET"])
@json_resp
def api_count_realisations_par_par_mois_par_type_bracelet():
    """
    pour l'affichage des graphiques dans chasse -> analyse detaillée
    Retourne le nombre de realisations par mois et par type de bracelet pour une saison pour une espece donnée
    """

    # récupère les paramètres de la requête et les traite
    args = chasse_process_args()

    id_espece = args.get("id_espece")
    id_saison = args.get("id_saison")
    list_id_secteur = args.get("id_secteur")
    list_id_zc = args.get("id_zone_cynegetique")
    list_id_zi = args.get("id_zone_indicative")

    mois = func.to_char(TRealisationsChasse.date_exacte, "MM").label("mois")

    stmt = (
        select(
            mois,
            TTypeBracelets.code_type_bracelet,
            func.count().label("nb_realisations"),
        )
        .select_from(TRealisationsChasse)
        .join(
            TAttributions,
            TRealisationsChasse.id_attribution == TAttributions.id_attribution,
        )
        .join(
            TTypeBracelets,
            TAttributions.id_type_bracelet == TTypeBracelets.id_type_bracelet,
        )
        .join(
            TZoneCynegetiques,
            TZoneCynegetiques.id_zone_cynegetique
            == TAttributions.id_zone_cynegetique_affectee,
        )
        .join(
            TZoneIndicatives,
            TZoneIndicatives.id_zone_indicative
            == TAttributions.id_zone_indicative_affectee,
        )
        .where(TTypeBracelets.id_espece == id_espece)
    )

    if id_saison:
        stmt = stmt.where(TAttributions.id_saison == id_saison)

    # Filtrage par zones. Les zones indicatives ont la priorité sur les zones cynégétiques, qui ont elles même la priorité sur les secteurs
    stmt = filtrage_stmt_secteur_zi_zc(stmt, list_id_zi, list_id_zc, list_id_secteur)

    stmt = stmt.group_by(mois, TTypeBracelets.code_type_bracelet)

    res = DB.session.execute(stmt).all()

    # on regroupe les résultats par mois puis par type de bracelet. On commence par le mois de septembre (début de la saison de chasse)
    #  pour finir par mars (fin de la saison de chasse) pour que les saisons soient regroupées de septembre à aout
    # le résultat final sera de la forme
    # [
    #     {
    #       "text": "Sep.",
    #       "data": [
    #         {
    #           "type_bracelet": "CEM",
    #           "nb_realisations": 50,
    #         },
    #         {
    #           "type_bracelet": "CEFF",
    #           "nb_realisations": 100,
    #         },
    #       ]
    #     }, ...
    #     ...
    # ]
    data = []
    for mois, type_bracelet, nb_realisations in res:
        mois_txt = MOIS_MAPPING.get(mois, mois)
        bracelet_data = {
            "type de bracelet": type_bracelet,
            "réalisations": nb_realisations,
        }
        mois_entry = next((item for item in data if item["mois"] == mois_txt), None)
        if mois_entry:
            mois_entry["data"].append(bracelet_data)
            mois_entry["réalisations_totale"] += nb_realisations
        else:
            data.append(
                {
                    "mois": mois_txt,
                    "réalisations_totale": nb_realisations,
                    "data": [bracelet_data],
                }
            )
    # on trie les mois pour que l'affichage soit de septembre à aout

    data = sorted(data, key=lambda x: MOIS_ORDER.index(x["mois"]))
    return data


@bp.route("count_mode_chasse_par_type_bracelet/", methods=["GET"])
@json_resp
def api_count_mode_chasse_par_type_bracelet():
    """
    pour l'affichage des graphiques dans chasse -> analyse detaillée
    Retourne le nombre de realisations par mode de chasse et par type de bracelet pour une saison pour une espece donnée
    """

    # récupère les paramètres de la requête et les traite
    args = chasse_process_args()

    id_espece = args.get("id_espece")
    id_saison = args.get("id_saison")
    list_id_secteur = args.get("id_secteur")
    list_id_zc = args.get("id_zone_cynegetique")
    list_id_zi = args.get("id_zone_indicative")

    stmt = (
        select(
            TNomenclatures.label_fr,
            TTypeBracelets.code_type_bracelet,
            func.count().label("nb_realisations"),
        )
        .select_from(TRealisationsChasse)
        .join(
            TAttributions,
            TRealisationsChasse.id_attribution == TAttributions.id_attribution,
        )
        .join(
            TTypeBracelets,
            TAttributions.id_type_bracelet == TTypeBracelets.id_type_bracelet,
        )
        .join(
            TNomenclatures,
            TNomenclatures.id_nomenclature
            == TRealisationsChasse.id_nomenclature_mode_chasse,
        )
        .join(
            TZoneCynegetiques,
            TZoneCynegetiques.id_zone_cynegetique
            == TAttributions.id_zone_cynegetique_affectee,
        )
        .join(
            TZoneIndicatives,
            TZoneIndicatives.id_zone_indicative
            == TAttributions.id_zone_indicative_affectee,
        )
        .where(TTypeBracelets.id_espece == id_espece)
        .where(TRealisationsChasse.id_nomenclature_mode_chasse != None)
    )

    if id_saison:
        stmt = stmt.where(TAttributions.id_saison == id_saison)

    # Filtrage par zones. Les zones indicatives ont la priorité sur les zones cynégétiques, qui ont elles même la priorité sur les secteurs
    stmt = filtrage_stmt_secteur_zi_zc(stmt, list_id_zi, list_id_zc, list_id_secteur)

    stmt = stmt.group_by(TNomenclatures.label_fr, TTypeBracelets.code_type_bracelet)
    stmt = stmt.order_by(func.count().desc())
    res = DB.session.execute(stmt).all()
    # on regroupe les résultats par mode de chasse puis par type de bracelet
    # le résultat final sera de la forme
    # [
    #     {
    #       "text": "Battue",
    #       "data": [
    #         {
    #           "type_bracelet": "CEM",
    #           "nb_realisations": 50,
    #         },
    #         {
    #           "type_bracelet": "CEFF",
    #           "nb_realisations": 100,
    #         },
    #       ]
    #     }, ...
    #     ...
    # ]
    data = []
    for mode_chasse, type_bracelet, nb_realisations in res:
        mode_chasse_data = {
            "type de bracelet": type_bracelet,
            "réalisations": nb_realisations,
        }
        mode_chasse_entry = next(
            (item for item in data if item["mode_chasse"] == mode_chasse), None
        )
        if mode_chasse_entry:
            mode_chasse_entry["data"].append(mode_chasse_data)
            mode_chasse_entry["réalisations_totale"] += nb_realisations
        else:
            data.append(
                {
                    "mode_chasse": mode_chasse,
                    "réalisations_totale": nb_realisations,
                    "data": [mode_chasse_data],
                }
            )

    return data


@bp.route("count_realisations_par_age_par_type_bracelet/", methods=["GET"])
@json_resp
def api_count_realisations_par_age_par_type_bracelet():
    """
    pour l'affichage des graphiques dans chasse -> analyse detaillée
    Retourne le nombre de realisations par classe d'age et par type de bracelet pour une saison pour une espece donnée
    """

    # récupère les paramètres de la requête et les traite
    args = chasse_process_args()

    id_espece = args.get("id_espece")
    id_saison = args.get("id_saison")
    list_id_secteur = args.get("id_secteur")
    list_id_zc = args.get("id_zone_cynegetique")
    list_id_zi = args.get("id_zone_indicative")

    # create a single alias instance for the 'classe_age' nomenclature and reuse it in the join
    classe_age = aliased(TNomenclatures, name="classe_age")

    stmt = (
        select(
            classe_age.label_fr,
            TTypeBracelets.code_type_bracelet,
            func.count().label("nb_realisations"),
        )
        .select_from(TRealisationsChasse)
        .join(
            TAttributions,
            TRealisationsChasse.id_attribution == TAttributions.id_attribution,
        )
        .join(
            TTypeBracelets,
            TAttributions.id_type_bracelet == TTypeBracelets.id_type_bracelet,
        )
        .join(
            TNomenclatures,
            TNomenclatures.id_nomenclature
            == TRealisationsChasse.id_nomenclature_classe_age,
        )
        .join(
            TZoneCynegetiques,
            TZoneCynegetiques.id_zone_cynegetique
            == TAttributions.id_zone_cynegetique_affectee,
        )
        .join(
            TZoneIndicatives,
            TZoneIndicatives.id_zone_indicative
            == TAttributions.id_zone_indicative_affectee,
        )
        .join(
            classe_age,
            classe_age.id_nomenclature
            == TRealisationsChasse.id_nomenclature_classe_age,
        )
        .where(TTypeBracelets.id_espece == id_espece)
    )

    if id_saison:
        stmt = stmt.where(TAttributions.id_saison == id_saison)

    # Filtrage par zones. Les zones indicatives ont la priorité sur les zones cynégétiques, qui ont elles même la priorité sur les secteurs
    stmt = filtrage_stmt_secteur_zi_zc(stmt, list_id_zi, list_id_zc, list_id_secteur)

    stmt = stmt.group_by(classe_age.label_fr, TTypeBracelets.code_type_bracelet)
    stmt = stmt.order_by(func.count().desc())
    res = DB.session.execute(stmt).all()
    # on regroupe les résultats par classe d'age puis par type de bracelet
    # le résultat final sera de la forme
    # [
    #     {
    #       "type_bracelet": "CEM",
    #       "data": [
    #         {
    #           "classe_age": "Juvenile",
    #           "nb_realisations": 50,
    #         },
    #         {
    #           "classe_age": "Adulte",
    #           "nb_realisations": 100,
    #         },
    #       ]
    #     }, ...
    #     ...
    # ]
    data = []
    for classe_age, type_bracelet, nb_realisations in res:
        classe_age_data = {
            "classe_age": classe_age,
            "réalisations": nb_realisations,
        }
        classe_age_entry = next(
            (item for item in data if item["type_bracelet"] == type_bracelet), None
        )
        if classe_age_entry:
            classe_age_entry["data"].append(classe_age_data)
            classe_age_entry["réalisations_totale"] += nb_realisations
        else:
            data.append(
                {
                    "type_bracelet": type_bracelet,
                    "réalisations_totale": nb_realisations,
                    "data": [classe_age_data],
                }
            )

    return data
