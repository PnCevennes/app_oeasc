from utils_flask_sqla.generic import GenericTable
from flask import request, current_app
from ..generic.repository import getlist
from ..resultat.repository import result_custom
from sqlalchemy import func, cast, select, Integer
from ..commons.models import TEspeces, TSecteurs
from sqlalchemy.exc import SQLAlchemyError
from .models import (
    TSaisons,
    TZoneCynegetiques,
    TZoneIndicatives,
    TAttributionMassifs,
    VPlanChasseRealisationBilan,
)

config = current_app.config
DB = config["DB"]


def chasse_process_args():
    """
    Traitement des arguments de requete pour la plupart des routes de l'api chasse
    met les arguments à choix multiple comme id_secteur, id_zone_cynegetique, id_zone_indicative sous forme de liste
    Si plusieurs type de zone sont définis, priorise zone indicative > zone cynegetique > secteur en vidant les listes des types de zone inférieurs
    retourne les arguments de requete en un dictionnaire.
    """
    # récupération des id dans la requête. Ces choix sont uniques
    id_espece = request.args.get("id_espece")
    id_saison = request.args.get("id_saison")
    poids_ou_dagues = request.args.get("poids_ou_dagues")
    if poids_ou_dagues is None:  # poids ou dagues est forcément un booléen
        poids_ou_dagues = False

    # récupération des id dans les paramètres de la requête sous forme de liste car le formulaire est à choix multiple
    id_secteur = getlist(request.args, "id_secteur")
    id_zone_cynegetique = getlist(request.args, "id_zone_cynegetique")
    id_zone_indicative = getlist(request.args, "id_zone_indicative")

    # conversion des id en int dans les listes
    id_secteur = list(map(lambda x: int(x), id_secteur))
    id_zone_cynegetique = list(map(lambda x: int(x), id_zone_cynegetique))
    id_zone_indicative = list(map(lambda x: int(x), id_zone_indicative))

    # priorisation ZI > ZC > Secteur
    # la zone indicative est définie, on supprime id_secteur et id_zone_cynegetique
    if len(id_zone_indicative) > 0:
        id_secteur = id_zone_cynegetique = []
    # id_zone_cynegetique est définie, on supprime id_secteur
    if len(id_zone_cynegetique) > 0:
        id_secteur = []

    return {
        "id_saison": id_saison,
        "id_espece": id_espece,
        "id_secteur": id_secteur,
        "id_zone_cynegetique": id_zone_cynegetique,
        "id_zone_indicative": id_zone_indicative,
        "poids_ou_dagues": poids_ou_dagues,
    }


def get_attribution_result(params):
    """
    Récupère les statistiques d'attribution à partir de la vue 'v_custom_result_attribution' dans la base de données.

    Cette fonction permet de calculer :
        - Le nombre total d'attributions.
        - Le nombre d'attributions réalisées (où 'id_realisation' n'est pas nul).
        - Le nombre de transferts ZC (où 'transfert_zc' est vrai).
        - Le nombre de transferts ZI (où 'transfert_zi' est vrai).
        - Le taux de réalisation (pourcentage d'attributions réalisées par rapport au total).

    Les filtres passés en paramètre permettent de restreindre les résultats selon les colonnes de la vue.
    Les filtres peuvent être des valeurs uniques ou des listes de valeurs.

    Args:
        params (dict): Dictionnaire de filtres à appliquer sur la vue. Les clés doivent correspondre aux noms de colonnes.

    Returns:
        dict: Un dictionnaire contenant les statistiques calculées :
            - 'nb_realisation' : Nombre d'attributions réalisées.
            - 'nb_attribution' : Nombre total d'attributions.
            - 'transfert_zc'   : Nombre de transferts ZC.
            - 'transfert_zi'   : Nombre de transferts ZI.
            - 'taux_realisation': Taux de réalisation en pourcentage.

    Utilisation :
        Cette fonction est généralement utilisée dans les endpoints d'API ou les services métiers pour afficher des statistiques
        sur les attributions, par exemple dans des tableaux de bord ou des rapports de suivi.
    """
    columns = GenericTable(
        "v_custom_result_attribution", "oeasc_chasse", DB.engine
    ).tableDef.columns

    stmt = select(
        func.count(columns.id_attribution),
        func.count(columns.id_attribution).filter(columns.id_realisation.is_not(None)),
        func.count(columns.transfert_zc).filter(columns.transfert_zc.is_(True)),
        func.count(columns.transfert_zi).filter(columns.transfert_zi.is_(True)),
    )

    for filter_key, filter_value in params.items():
        if not hasattr(columns, filter_key) or filter_value in [None, []]:
            continue
        if isinstance(filter_value, list):
            stmt = stmt.where(getattr(columns, filter_key).in_(filter_value))
        else:
            stmt = stmt.where(getattr(columns, filter_key) == filter_value)

    res = DB.session.execute(stmt).first()
    # res = res[0]

    return {
        "nb_realisation": res[1],
        "nb_attribution": res[0],
        "transfert_zc": res[2],
        "transfert_zi": res[3],
        "taux_realisation": (
            0 if not res[1] or not res[0] else round(res[1] / res[0] * 100)
        ),
    }


def chasse_get_infos():
    """
    Fonction appelée dans l'analyse détaillée de la chasse.
    Elle récupère des informations de base affichées en haut de page :
        - le nom de l'espèce,
        - le nom de la saison,
        - le nom et l'échelle de la zone (indicative, cynégétique ou secteur),
        - les 5 dernières saisons pour le graphique de comparaison,
        - les statistiques d'attribution et de réalisation via get_attribution_result.

    Cette fonction est typiquement utilisée dans les endpoints d'API ou les vues qui affichent un résumé
    ou une synthèse des données de chasse pour une espèce, une saison et une zone donnée.
    """

    # Récupération et traitement des arguments de la requête (GET)
    args = chasse_process_args()

    # Vérification de la présence de l'argument obligatoire id_espece
    id_espece = args.get("id_espece")
    if id_espece is None:
        raise ValueError("L'argument 'id_espece' est requis.")

    ####################### Récupération du nom de l'espèce #######################
    try:
        # Préparation de la requête SQL pour obtenir le nom de l'espèce
        stmt = select(TEspeces.nom_espece).where(TEspeces.id_espece == id_espece)
        # Exécution de la requête
        nom_espece = DB.session.scalar(stmt)
        # if nom_espece is None:
        #     print("Aucune espèce trouvée pour cet ID.")
    except SQLAlchemyError as e:
        print(f"Erreur lors de l'exécution de la requête : {e}")

    #################################################################################################
    # Détermination de l'échelle de la zone selon les arguments fournis (priorité : indicative > cynégétique > secteur)
    select_zones_echelle = None

    if args["id_zone_indicative"]:
        # Si une zone indicative est sélectionnée, on récupère son nom
        select_zones_echelle = select(TZoneIndicatives.nom_zone_indicative).where(
            TZoneIndicatives.id_zone_indicative.in_(args["id_zone_indicative"])
        )
    elif args["id_zone_cynegetique"]:
        # Sinon, si une zone cynégétique est sélectionnée, on récupère son nom
        select_zones_echelle = select(TZoneCynegetiques.nom_zone_cynegetique).where(
            TZoneCynegetiques.id_zone_cynegetique.in_(args["id_zone_cynegetique"])
        )
    elif args["id_secteur"]:
        # Sinon, si un secteur est sélectionné, on récupère son nom
        select_zones_echelle = select(TSecteurs.nom_secteur).where(
            TSecteurs.id_secteur.in_(args["id_secteur"])
        )
    else:
        # Si aucune zone n'est sélectionnée, on ne fait pas de requête
        query_zones_echelle = None

    # Exécution de la requête pour récupérer les noms des zones sélectionnées
    if not select_zones_echelle == None:
        query_zones_echelle = DB.session.execute(select_zones_echelle)

    # Formatage des noms des zones sous forme de chaîne séparée par des virgules
    nom_zones_echelle = (
        ", ".join(map(lambda x: x[0], query_zones_echelle.all()))
        if query_zones_echelle
        else ""
    )

    # Construction du texte d'échelle selon le type de zone sélectionné
    echelle = (
        f"Zone(s) indicative(s) : {nom_zones_echelle}"
        if args["id_zone_indicative"]
        else (
            f"Zone(s) Cynegetique(s) : {nom_zones_echelle}"
            if args["id_zone_cynegetique"]
            else f"Secteur(s): {nom_zones_echelle}" if args["id_secteur"] else "Cœur"
        )
    )

    # Récupération du nom de la saison à partir de son id
    select_saison = select(TSaisons.nom_saison).where(
        TSaisons.id_saison == args["id_saison"]
    )
    nom_saison = DB.session.scalar(select_saison)

    # Récupération des 5 dernières saisons (pour affichage dans un graphique comparatif)
    last_5_seasons_query = (
        select(TSaisons.id_saison)
        .where(TSaisons.nom_saison <= nom_saison)
        .order_by(TSaisons.nom_saison.desc())
        .limit(5)
    )
    last_5_id_saisons = [
        id_saison for id_saison in DB.session.scalars(last_5_seasons_query).all()
    ]

    # Retourne toutes les informations utiles pour l'affichage en haut de page et pour les graphiques
    return {
        "nom_saison": nom_saison,  # Nom de la saison sélectionnée
        "nom_espece": nom_espece,  # Nom de l'espèce sélectionnée
        "echelle": echelle,  # Texte décrivant l'échelle de la zone
        "last_5_id_saison": last_5_id_saisons,  # Liste des 5 dernières saisons (id)
        "nom_saison": nom_saison,  # (doublon, peut être nettoyé)
        **get_attribution_result(args),  # Statistiques d'attribution/réalisation
    }


def build_chasse_bilan_filters(params, stmt, tableModel):
    """
    Construit dynamiquement des filtres SQLAlchemy pour une requête sur le bilan de chasse,
    en fonction des paramètres fournis.

    Cette fonction est typiquement utilisée lors de la génération de rapports ou de bilans
    sur les activités de chasse, où il est nécessaire de filtrer les résultats selon
    différentes zones (indicative, cynégétique, secteur) et espèces.

    Args:
        params (dict): Dictionnaire contenant les paramètres de filtrage. Les clés attendues sont :
            - "id_zone_indicative" (list ou None) : Identifiants des zones indicatives à filtrer.
            - "id_zone_cynegetique" (list ou None) : Identifiants des zones cynégétiques à filtrer.
            - "id_secteur" (list ou None) : Identifiants des secteurs à filtrer.
            - "id_espece" (int ou None) : Identifiant de l'espèce à filtrer.
        stmt (sqlalchemy.sql.Select): L'objet de requête SQLAlchemy à enrichir avec les filtres.
        tableModel (DeclarativeMeta): Le modèle SQLAlchemy représentant la table principale à interroger.

    Returns:
        sqlalchemy.sql.Select: L'objet de requête enrichi avec les filtres appropriés.

    Note:
        - Les filtres sont appliqués selon la priorité suivante : zone indicative, puis zone cynégétique, puis secteur.
        - Si plusieurs paramètres sont fournis, seul le premier dans l'ordre de priorité est pris en compte pour les zones.
        - Le filtre sur l'espèce est toujours appliqué si présent.
    """

    if params["id_zone_indicative"]:
        stmt = stmt.where(
            tableModel.id_zone_indicative.in_(params["id_zone_indicative"])
        )
    elif params["id_zone_cynegetique"]:
        stmt = stmt.where(
            tableModel.id_zone_cynegetique.in_(params["id_zone_cynegetique"])
        )
    elif params["id_secteur"]:
        stmt = stmt.join(
            TZoneCynegetiques,
            TZoneCynegetiques.id_zone_cynegetique == tableModel.id_zone_cynegetique,
        ).where(TZoneCynegetiques.id_secteur.in_(params["id_secteur"]))

    if params["id_espece"]:
        stmt = stmt.where(tableModel.id_espece == params["id_espece"])

    return stmt


def get_chasse_bilan_realisation(params):
    """
    Fonction qui construit une requête SQLAlchemy pour obtenir le bilan de réalisation des plans de chasse,
    en fonction des paramètres de filtrage fournis.

    Cette fonction est utilisée dans les endpoints ou services qui doivent afficher ou exporter
    le bilan des réalisations et attributions de la chasse, par exemple dans des tableaux de bord,
    des rapports ou des exports ODS.

    Args:
        params (dict): Dictionnaire de filtres (id_zone_indicative, id_zone_cynegetique, id_secteur, id_espece, etc.)

    Returns:
        sqlalchemy.sql.Select: Requête SQLAlchemy prête à être exécutée pour récupérer le bilan.
    """

    # Cas où on filtre par zone indicative (ZI)
    # Les données historiques sont agrégées à la ZI pour la réalisation et à la ZC pour les attributions,
    # d'où l'utilisation de deux requêtes différentes selon le filtre demandé.
    if params["id_zone_indicative"]:
        # Construction de la requête principale pour la ZI :
        # On sélectionne le nom de la saison, l'id de l'espèce, et on agrège les colonnes d'attribution et de réalisation.
        stmt = (
            select(
                TSaisons.nom_saison,
                VPlanChasseRealisationBilan.id_espece,
                func.sum(VPlanChasseRealisationBilan.nb_affecte_min).label(
                    "nb_attribution_min"
                ),
                func.sum(VPlanChasseRealisationBilan.nb_affecte_max).label(
                    "nb_attribution_max"
                ),
                func.sum(VPlanChasseRealisationBilan.nb_realisation).label(
                    "nb_realisation"
                ),
                func.sum(VPlanChasseRealisationBilan.nb_realisation_avant_11).label(
                    "nb_realisation_avant_11"
                ),
            )
            .select_from(TSaisons)
            .join(
                VPlanChasseRealisationBilan,
                TSaisons.id_saison == VPlanChasseRealisationBilan.id_saison,
            )
        )
        # Application des filtres dynamiques selon les paramètres
        stmt = build_chasse_bilan_filters(params, stmt, VPlanChasseRealisationBilan)
        # Groupement par espèce et saison
        stmt = stmt.group_by(VPlanChasseRealisationBilan.id_espece, TSaisons.nom_saison)

    else:
        # Cas où on ne filtre pas par zone indicative (ZI)
        # On doit séparer la requête de réalisation et celle d'attribution, puis les joindre.

        # Sous-requête pour la réalisation :
        # On agrège les réalisations par espèce et saison.
        realisation_subq = select(
            VPlanChasseRealisationBilan.id_espece,
            VPlanChasseRealisationBilan.id_saison,
            func.sum(VPlanChasseRealisationBilan.nb_realisation).label(
                "nb_realisation"
            ),
            func.sum(VPlanChasseRealisationBilan.nb_realisation_avant_11).label(
                "nb_realisation_avant_11"
            ),
        ).group_by(
            VPlanChasseRealisationBilan.id_espece, VPlanChasseRealisationBilan.id_saison
        )
        # Application des filtres sur la sous-requête de réalisation
        realisation_subq = build_chasse_bilan_filters(
            params, realisation_subq, VPlanChasseRealisationBilan
        ).subquery()

        # Sous-requête pour l'attribution :
        # On agrège les attributions par espèce et saison.
        attribution_subq = select(
            TAttributionMassifs.id_espece,
            TAttributionMassifs.id_saison,
            func.sum(TAttributionMassifs.nb_affecte_min).label("nb_attribution_min"),
            func.sum(TAttributionMassifs.nb_affecte_max).label("nb_attribution_max"),
        ).group_by(TAttributionMassifs.id_espece, TAttributionMassifs.id_saison)
        # Application des filtres sur la sous-requête d'attribution
        attribution_subq = build_chasse_bilan_filters(
            params, attribution_subq, TAttributionMassifs
        ).subquery()

        # Requête principale : jointure des sous-requêtes sur la saison,
        # sélection du nom de la saison, des valeurs agrégées d'attribution et de réalisation.
        stmt = (
            select(
                TSaisons.nom_saison,
                attribution_subq.c.id_espece,
                attribution_subq.c.nb_attribution_min,
                attribution_subq.c.nb_attribution_max,
                realisation_subq.c.nb_realisation,
                realisation_subq.c.nb_realisation_avant_11,
            )
            .select_from(TSaisons)
            .join(realisation_subq, TSaisons.id_saison == realisation_subq.c.id_saison)
            .join(
                attribution_subq,
                attribution_subq.c.id_saison == realisation_subq.c.id_saison,
            )
        )

    # Tri des résultats par nom de saison (ordre chronologique)
    stmt = stmt.order_by(TSaisons.nom_saison)

    # La requête est retournée, prête à être exécutée (DB.session.execute(stmt))
    return stmt


def get_plain_text_data(params):
    """
    Fonction utilitaire qui récupère les noms "lisibles" (texte) des entités (espèce, saison, zone)
    à partir de leurs identifiants présents dans le dictionnaire de paramètres.
    Elle est utilisée pour enrichir les données de contexte affichées dans les bilans ou exports,
    afin d'afficher les noms des espèces, saisons et zones sélectionnées.

    Args:
        params (dict): Dictionnaire contenant les identifiants des entités à afficher.
            - "id_espece" : identifiant de l'espèce
            - "id_saison" : identifiant de la saison
            - "id_zone_indicative", "id_zone_cynegetique", "id_secteur" : listes d'identifiants de zones

    Returns:
        dict: Dictionnaire contenant les noms des entités (nom_espece, nom_saison, nom_zone_...)
    """

    out = {}

    # Récupération du nom de l'espèce à partir de son identifiant
    if "id_espece" in params:
        if params["id_espece"] is not None:
            # Utilisation de la session SQLAlchemy pour récupérer l'objet espèce
            res = DB.session.get(TEspeces, params["id_espece"])
            if res:
                out["nom_espece"] = res.nom_espece
            else:
                out["nom_espece"] = "???"
        # Si l'identifiant n'est pas fourni, on ne met rien

    # Récupération du nom de la saison à partir de son identifiant
    if "id_saison" in params:
        if params["id_saison"] is not None:
            res = DB.session.get(TSaisons, params["id_saison"])
            if res:
                out["nom_saison"] = res.nom_saison
            else:
                out["nom_saison"] = "???"
        else:
            out["nom_saison"] = "???"

    # Récupération du nom de la zone selon la priorité indicative > cynégétique > secteur
    zones = None
    if params["id_zone_indicative"]:
        # Si des zones indicatives sont sélectionnées, on récupère leurs noms
        zones = DB.session.scalars(
            select(TZoneIndicatives).where(
                TZoneIndicatives.id_zone_indicative.in_(params["id_zone_indicative"])
            )
        ).all()
        column_name = "nom_zone_indicative"
    elif params["id_zone_cynegetique"]:
        # Sinon, on regarde les zones cynégétiques
        zones = DB.session.scalars(
            select(TZoneCynegetiques).where(
                TZoneCynegetiques.id_zone_cynegetique.in_(params["id_zone_cynegetique"])
            )
        ).all()
        column_name = "nom_zone_cynegetique"
    elif params["id_secteur"]:
        # Sinon, on regarde les secteurs
        zones = DB.session.scalars(
            select(TSecteurs).where(TSecteurs.id_secteur.in_(params["id_secteur"]))
        ).all()
        column_name = "nom_secteur"

    # Si des zones ont été trouvées, on les concatène sous forme de chaîne séparée par des virgules
    if zones:
        out[column_name] = ", ".join([getattr(z, column_name) for z in zones])

    return out


# Cette fonction est typiquement utilisée dans les fonctions de génération de bilans ou d'exports
# (ex : get_chasse_bilan, get_data_export_ods) pour afficher les noms des entités sélectionnées
# dans l'interface utilisateur ou dans les fichiers exportés.


def get_chasse_bilan(params):
    """
    Récupère et formate les données de bilan de chasse pour une utilisation dans des graphiques (ex: Highcharts).

    Cette fonction exécute une requête SQL pour obtenir les réalisations et attributions de chasse sur différentes saisons,
    puis organise les résultats dans un format adapté à l'affichage graphique. Elle calcule également le taux de réalisation
    pour chaque saison et ajoute des informations contextuelles liées aux paramètres de la chasse.

    Args:
        params (dict): Dictionnaire de paramètres permettant de filtrer les données (ex: saison, espèce, zone).

    Returns:
        dict: Un dictionnaire contenant :
            - Les listes formatées pour chaque indicateur ("nb_attribution_min", "nb_attribution_max", "nb_realisation", "nb_realisation_avant_11"),
              chaque liste étant composée de couples [nom_saison, valeur].
            - Le taux de réalisation par saison ("taux_realisation").
            - Les données contextuelles pour l'affichage (ex: TSaisons, TZoneIndicatives, TZoneCynegetiques).

    Utilisation :
        Cette fonction est typiquement utilisée dans les endpoints d'API ou les vues backend pour fournir des données
        statistiques de chasse à des interfaces graphiques ou des tableaux de bord.
    """
    stmt = get_chasse_bilan_realisation(params)
    res = DB.session.execute(stmt).all()
    # res.all()
    # 0: nom_saison
    # 1: id_espece
    # 2: nb_affecte_min
    # 3: nb_affecte_max
    # 4: nb_realisation
    # 5: nb_realisation_avant_11
    columns_index = {
        "nom_saison": 0,
        "id_espece": 1,
        "nb_realisation": 4,
        "nb_realisation_avant_11": 5,
        "nb_attribution_min": 2,
        "nb_attribution_max": 3,
    }
    out = {}
    # Fonction permettant de formater les données pour highcharts
    # traitement des colones contenus dans res_keys
    #   "nb_realisation": [["2001-2002", 809], ["2002-2003", 702], ["2003-2004", 595], [...]],
    #   "nb_realisation_avant_11": [["2010-2011", 0], [...]],
    #   "nb_attribution_min": [["2010-2011", 0], [...]],
    #   "nb_attribution_max": [["2010-2011", 0], [...]]
    for key in [
        "nb_attribution_min",
        "nb_attribution_max",
        "nb_realisation",
        "nb_realisation_avant_11",
    ]:
        index_nom_saison = columns_index["nom_saison"]
        index_col = columns_index[key]
        out[key] = [
            [
                r[index_nom_saison],
                (int(r[index_col]) if r[index_col] is not None else 0),
            ]
            for r in res
        ]
    # Calcul du taux de réalisation
    out["taux_realisation"] = [
        [
            out["nb_realisation"][i][0],
            (
                out["nb_realisation"][i][1] / out["nb_attribution_max"][i][1]
                if out["nb_attribution_max"][i][1]
                else 0
            ),
        ]
        for i in range(len(out["nb_realisation"]))
    ]

    # Récupération des données d'affichage des paramètres
    # TSaisons, TZoneIndicatives, TZoneCynegetiques
    context_data = get_plain_text_data(params=params)
    return {**out, **context_data}


def get_details(nom_saison, nom_espece, filter={}):
    """
    Récupère et agrège des statistiques détaillées sur les résultats de chasse pour une saison et une espèce données.

    Cette fonction interroge différentes vues personnalisées de la base de données pour obtenir des comptages selon plusieurs critères :
    - Sexe (Mâle, Femelle, Indéterminé)
    - Mois de prélèvement (Sep., Oct., Nov., Déc., Jan., Fév.)
    - Classe d'âge (Adulte, Sub-adulte, Juvénile, Indéterminé)
    - Mode de chasse (Approche, Affut, Battue, Indéterminé)
    - Type de bracelet utilisé (CEM, CEFF, CEFFD)
    - Attribution des bracelets (CEM, CEFF, CEFFD)

    Pour chaque critère, la fonction extrait le nombre d'individus correspondant, et calcule également le pourcentage de réalisation par rapport à l'attribution des bracelets.

    Args:
        nom_saison (str): Le nom de la saison de chasse concernée.
        nom_espece (str): Le nom de l'espèce concernée.
        filter (dict, optionnel): Filtres additionnels à appliquer lors de la requête (ex: secteur, commune, etc.).

    Returns:
        dict: Un dictionnaire contenant les statistiques agrégées pour chaque critère.

    Utilisation :
        Cette fonction est typiquement utilisée dans les modules de reporting ou d'affichage de statistiques pour fournir une vue synthétique et détaillée des résultats de chasse, par exemple dans une API ou une interface utilisateur de suivi des prélèvements.
    """
    out = {}

    res_details = {}

    for field_name in [
        "label_sexe",
        "mois_txt",
        "label_classe_age",
        "label_mode_chasse",
        "bracelet",
    ]:
        res_details[field_name] = result_custom(
            {
                "view": "oeasc_chasse.v_custom_results",
                "field_name": field_name,
                "filters": {
                    "nom_saison": [nom_saison],
                    "nom_espece": [nom_espece],
                    **filter,
                },
            }
        )

    res_details["bracelet_attr"] = result_custom(
        {
            "view": "oeasc_chasse.v_custom_result_attribution",
            "field_name": field_name,
            "filters": {
                "nom_saison": [nom_saison],
                "nom_espece": [nom_espece],
                **filter,
            },
        }
    )

    out["nb_sexe_male"] = (
        next(
            (
                elem["count"]
                for elem in res_details["label_sexe"]
                if elem["text"] == "Mâle"
            ),
            0,
        )
        or ""
    )
    out["nb_sexe_femelle"] = (
        next(
            (
                elem["count"]
                for elem in res_details["label_sexe"]
                if elem["text"] == "Femelle"
            ),
            0,
        )
        or ""
    )
    out["nb_sexe_ind"] = (
        next(
            (
                elem["count"]
                for elem in res_details["label_sexe"]
                if elem["text"] == "Indéterminé"
            ),
            0,
        )
        or ""
    )
    out["nb_mois_sep"] = (
        next(
            (
                elem["count"]
                for elem in res_details["mois_txt"]
                if elem["text"] == "Sep."
            ),
            0,
        )
        or ""
    )
    out["nb_mois_oct"] = (
        next(
            (
                elem["count"]
                for elem in res_details["mois_txt"]
                if elem["text"] == "Oct."
            ),
            0,
        )
        or ""
    )
    out["nb_mois_nov"] = (
        next(
            (
                elem["count"]
                for elem in res_details["mois_txt"]
                if elem["text"] == "Nov."
            ),
            0,
        )
        or ""
    )
    out["nb_mois_dec"] = (
        next(
            (
                elem["count"]
                for elem in res_details["mois_txt"]
                if elem["text"] == "Déc."
            ),
            0,
        )
        or ""
    )
    out["nb_mois_jan"] = (
        next(
            (
                elem["count"]
                for elem in res_details["mois_txt"]
                if elem["text"] == "Jan."
            ),
            0,
        )
        or ""
    )
    out["nb_mois_fev"] = (
        next(
            (
                elem["count"]
                for elem in res_details["mois_txt"]
                if elem["text"] == "Fév."
            ),
            0,
        )
        or ""
    )
    out["nb_age_ad"] = (
        next(
            (
                elem["count"]
                for elem in res_details["label_classe_age"]
                if elem["text"] == "Adulte"
            ),
            0,
        )
        or ""
    )
    out["nb_age_ind"] = (
        next(
            (
                elem["count"]
                for elem in res_details["label_classe_age"]
                if elem["text"] == "Indéterminé"
            ),
            0,
        )
        or ""
    )
    out["nb_age_suba"] = (
        next(
            (
                elem["count"]
                for elem in res_details["label_classe_age"]
                if elem["text"] == "Sub-adulte"
            ),
            0,
        )
        or ""
    )
    out["nb_age_juv"] = (
        next(
            (
                elem["count"]
                for elem in res_details["label_classe_age"]
                if elem["text"] == "Juvénile"
            ),
            0,
        )
        or ""
    )
    out["nb_mode_chasse_app"] = (
        next(
            (
                elem["count"]
                for elem in res_details["label_mode_chasse"]
                if elem["text"] == "Approche"
            ),
            0,
        )
        or ""
    )
    out["nb_mode_chasse_aff"] = (
        next(
            (
                elem["count"]
                for elem in res_details["label_mode_chasse"]
                if elem["text"] == "Affut"
            ),
            0,
        )
        or ""
    )
    out["nb_mode_chasse_ind"] = (
        next(
            (
                elem["count"]
                for elem in res_details["label_mode_chasse"]
                if elem["text"] == "Indéterminé"
            ),
            0,
        )
        or ""
    )
    out["nb_mode_chasse_bat"] = (
        next(
            (
                elem["count"]
                for elem in res_details["label_mode_chasse"]
                if elem["text"] == "Battue"
            ),
            0,
        )
        or ""
    )
    out["nb_real_cem"] = (
        next(
            (
                elem["count"]
                for elem in res_details["bracelet"]
                if elem["text"] == "CEM"
            ),
            0,
        )
        or ""
    )
    out["nb_real_ceff"] = (
        next(
            (
                elem["count"]
                for elem in res_details["bracelet"]
                if elem["text"] == "CEFF"
            ),
            0,
        )
        or ""
    )
    out["nb_real_ceffd"] = (
        next(
            (
                elem["count"]
                for elem in res_details["bracelet"]
                if elem["text"] == "CEFFD"
            ),
            0,
        )
        or ""
    )
    out["nb_attr_cem"] = (
        next(
            (
                elem["count"]
                for elem in res_details["bracelet_attr"]
                if elem["text"] == "CEM"
            ),
            0,
        )
        or ""
    )
    out["nb_attr_ceff"] = (
        next(
            (
                elem["count"]
                for elem in res_details["bracelet_attr"]
                if elem["text"] == "CEFF"
            ),
            0,
        )
        or ""
    )
    out["nb_attr_ceffd"] = (
        next(
            (
                elem["count"]
                for elem in res_details["bracelet_attr"]
                if elem["text"] == "CEFFD"
            ),
            0,
        )
        or ""
    )
    out["pourcent_cem"] = (
        round(1.0 * out["nb_real_cem"] / out["nb_attr_cem"] * 100)
        if out["nb_real_cem"]
        else ""
    )
    out["pourcent_ceff"] = (
        round(1.0 * out["nb_real_ceff"] / out["nb_attr_ceff"] * 100)
        if out["nb_real_ceff"]
        else ""
    )
    out["pourcent_ceffd"] = (
        round(1.0 * out["nb_real_ceffd"] / out["nb_attr_ceffd"] * 100)
        if out["nb_real_ceffd"]
        else ""
    )
    return out


def get_data_export_ods(nom_saison, nom_espece):
    """
    Récupère et structure les données de bilan de chasse pour une espèce et une saison données,
    afin de les exporter dans un format adapté à l'ODS (OpenDocument Spreadsheet).

    Cette fonction interroge la vue 'v_pre_bilan_pretty' pour obtenir les données agrégées par zone cynégétique (ZC)
    et zone indicative (ZI), puis organise les résultats dans une structure imbriquée :
        - Pour chaque ZC, on liste les ZI associées et leurs statistiques.
        - On ajoute également les statistiques globales pour l'espèce sur la saison.

    Utilisation :
        Cette fonction est typiquement appelée lors de la génération d'exports ODS pour les bilans de chasse,
        par exemple dans un endpoint d'API ou un service backend qui prépare les données pour un export Excel/ODS.

    Args:
        nom_saison (str): Nom de la saison de chasse (ex: "2023-2024").
        nom_espece (str): Nom de l'espèce (ex: "Cerf").

    Returns:
        dict: Dictionnaire contenant les données structurées pour l'export ODS.
    """

    # Récupération de la définition des colonnes de la vue SQL
    columns = GenericTable(
        "v_pre_bilan_pretty", "oeasc_chasse", DB.engine
    ).tableDef.columns

    # Construction de la requête SQL pour filtrer sur la saison et l'espèce
    stmt = (
        select(*[c for c in columns])
        .where(columns.nom_saison == nom_saison)
        .where(columns.nom_espece == nom_espece)
        .order_by(cast(columns.code_zone_indicative, Integer))
    )

    # Exécution de la requête
    data_chasse = DB.session.execute(stmt)

    # Transformation des résultats en liste de dictionnaires (clé = nom de colonne)
    res = [
        {(str(col.key)): getattr(r, str(col.key)) for col in columns}
        for r in data_chasse.all()
    ]

    zcs = []  # Liste des zones cynégétiques (ZC) à remplir

    # Parcours des résultats pour regrouper les données par ZC et ZI
    for r in res:
        # Recherche si la ZC existe déjà dans la liste
        zc = next(
            (item for item in zcs if item["nom"] == r["nom_zone_cynegetique"]), None
        )
        if not zc:
            # Si la ZC n'existe pas, on la crée et on ajoute les statistiques globales pour la ZC
            zc = {
                "nom": r["nom_zone_cynegetique"],
                "mini": r["nb_attribution_min_zc"] or "",
                "maxi": r["nb_attribution_max_zc"] or "",
                "realisation": int(r["nb_realisation_zc"]) or "",
                "pourcent": round(
                    r["nb_realisation_zc"] / r["nb_attribution_max_zc"] * 100
                )
                or "",
                "zis": [],  # Liste des ZI associées à cette ZC
                # Ajout des statistiques détaillées pour la ZC
                **get_details(
                    nom_saison,
                    nom_espece,
                    {"nom_zone_cynegetique": [r["nom_zone_cynegetique"]]},
                ),
            }
            zcs.append(zc)
        # Ajout des données pour la ZI courante dans la ZC correspondante
        zc["zis"].append(
            {
                "nom": r["nom_zone_indicative"] or "",
                "code": r["code_zone_indicative"] or "",
                "mini": r["nb_attribution_min_zi"] or "",
                "maxi": r["nb_attribution_max_zi"] or "",
                "realisation": int(r["nb_realisation_zi"]) or "",
                "pourcent": round(
                    r["nb_realisation_zi"] / r["nb_attribution_max_zi"] * 100
                )
                or "",
                # Ajout des statistiques détaillées pour la ZI
                **get_details(
                    nom_saison,
                    nom_espece,
                    {"nom_zone_indicative": [r["nom_zone_indicative"]]},
                ),
            }
        )

    # Récupération des statistiques globales pour l'espèce sur la saison (dernière ligne du résultat)
    if res:
        last_r = res[-1]
        mini = last_r["nb_attribution_min_espece"] or ""
        maxi = last_r["nb_attribution_max_espece"] or ""
        realisation = int(last_r["nb_realisation_espece"]) or ""
        pourcent = (
            round(
                last_r["nb_realisation_espece"]
                / last_r["nb_attribution_max_espece"]
                * 100
            )
            if last_r["nb_attribution_max_espece"]
            else ""
        )
    else:
        mini = maxi = realisation = pourcent = ""

    # Construction du dictionnaire final à retourner
    data = {
        "nom_saison": nom_saison,  # Nom de la saison
        "nom_espece": nom_espece,  # Nom de l'espèce
        "mini": mini,  # Attribution minimale globale
        "maxi": maxi,  # Attribution maximale globale
        "realisation": realisation,  # Réalisation globale
        "pourcent": pourcent,  # Pourcentage de réalisation global
        "zcs": zcs,  # Liste des ZC et leurs ZI
        # Ajout des statistiques détaillées globales pour l'espèce/saison
        **get_details(nom_saison, nom_espece),
    }

    return data


def get_data_all_especes_export_ods(nom_saison):
    """
    Récupère les données d'exportation pour toutes les espèces de chasse pour une saison donnée.

    Cette fonction est utilisée lors de l'exportation des données de chasse vers un fichier ODS,
    afin de regrouper les informations pour chaque espèce ("Cerf", "Chevreuil", "Mouflon") pour la saison spécifiée.

    Args:
        nom_saison (str): Le nom de la saison pour laquelle les données doivent être récupérées.
            Si la valeur est "current", la fonction récupère automatiquement la saison en cours depuis la base de données.

    Returns:
        dict: Un dictionnaire contenant le nom de la saison et une liste des données d'exportation pour chaque espèce.
            Format :
            {
                "nom_saison": <nom de la saison>,
                "especes": [<données exportées pour chaque espèce>]
            }
    """
    if nom_saison == "current":
        stmt = select(TSaisons.nom_saison).where(TSaisons.current == True)
        nom_saison = DB.session.execute(stmt).scalar_one()
    data = {"nom_saison": nom_saison, "especes": []}
    for nom_espece in ["Cerf", "Chevreuil", "Mouflon"]:
        data["especes"].append(get_data_export_ods(nom_saison, nom_espece))

    return data
