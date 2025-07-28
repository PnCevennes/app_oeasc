# from posixpath import normpath
# import json
# from psycopg2 import paramstyle
from utils_flask_sqla.generic import GenericTable
from flask import request, current_app
from ..generic.repository import getlist
from ..resultat.repository import result_custom

# from sqlalchemy import column, select, func, table, distinct, over, cast
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
    if poids_ou_dagues is None: # poids ou dagues est forcément un booléen
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
    """Fonction appelé dans chasse analyse détaillée. Récupère des infos de base affichés en haut de page.
    il y a le noms d'especes, de saisons et de zones
    Récupère aussi les 5 dernières saisons pour le graphique de comparaison.
    retourne aussi les infos de get_attribution_result qui donne les quantité d'attribution et de réalisation
    """

    args = chasse_process_args()

    # Vérification de la présence de l'argument
    id_espece = args.get("id_espece")

    if id_espece is None:
        raise ValueError("L'argument 'id_espece' est requis.")

    ####################### Nom de l'espèce #######################
    try:
        # Préparation de la requête
        stmt = select(TEspeces.nom_espece).where(TEspeces.id_espece == id_espece)
        # Exécution de la requête
        nom_espece = DB.session.scalar(stmt)
        print(f"Nom de l'espèce : {nom_espece}")
        if nom_espece is None:
            print("Aucune espèce trouvée pour cet ID.")
    except SQLAlchemyError as e:
        print(f"Erreur lors de l'exécution de la requête : {e}")

    #################################################################################################
    ####  définis l'echelle de la zone en fonction de l'id_zone_indicative, id_zone_cynegetique ou id_secteur

    select_zones_echelle = None

    if args["id_zone_indicative"]:
        select_zones_echelle = select(TZoneIndicatives.nom_zone_indicative).where(
            TZoneIndicatives.id_zone_indicative.in_(args["id_zone_indicative"])
        )
    elif args["id_zone_cynegetique"]:
        select_zones_echelle = select(TZoneCynegetiques.nom_zone_cynegetique).where(
            TZoneCynegetiques.id_zone_cynegetique.in_(args["id_zone_cynegetique"])
        )
    elif args["id_secteur"]:
        select_zones_echelle = select(TSecteurs.nom_secteur).where(
            TSecteurs.id_secteur.in_(args["id_secteur"])
        )
    else:
        # None fera qu'on récupère toutes les zones
        query_zones_echelle = None
        # select_zones_echelle = select(TSecteurs.nom_secteur)

    if not select_zones_echelle == None:
        query_zones_echelle = DB.session.execute(select_zones_echelle)

    nom_zones_echelle = (
        ", ".join(map(lambda x: x[0], query_zones_echelle.all()))
        if query_zones_echelle
        else ""
    )

    echelle = (
        f"Zone(s) indicative(s) : {nom_zones_echelle}"
        if args["id_zone_indicative"]
        else (
            f"Zone(s) Cynegetique(s) : {nom_zones_echelle}"
            if args["id_zone_cynegetique"]
            else f"Secteur(s): {nom_zones_echelle}" if args["id_secteur"] else "Cœur"
        )
    )

    # taux_realisation = get_chasse_bilan(args)['taux_realisation'][-1][1]

    select_saison = select(TSaisons.nom_saison).where(
        TSaisons.id_saison == args["id_saison"]
    )
    nom_saison = DB.session.scalar(select_saison)

    # recupère l'id des 5 saisons avec nom_saison (il faut que nom_saison soit du type 2022-2023 ou 2025)

    last_5_seasons_query = (
        select(TSaisons.id_saison)
        .where(TSaisons.nom_saison <= nom_saison)
        .order_by(TSaisons.nom_saison.desc())
        .limit(5)
    )

    # Récpère les 5 dernières saisons pour un des graphique qui fera un comparatif
    last_5_id_saisons = [
        id_saison for id_saison in DB.session.scalars(last_5_seasons_query).all()
    ]

    return {
        "nom_saison": nom_saison,
        "nom_espece": nom_espece,
        "echelle": echelle,
        "last_5_id_saison": last_5_id_saisons,
        "nom_saison": nom_saison,
        **get_attribution_result(args),
    }


def build_chasse_bilan_filters(params, stmt, tableModel):

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
    # Fonction de représentation de la réalisation des plans de chasse
    # Pb dans les données, les données historiques sont aggrégés à la zi pour la réalisation et à la zc pour les attributions
    # D'où le fait d'utiliser 2 requêtes différentes en fonction du filtre demandé


    if params["id_zone_indicative"]:

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
        stmt = build_chasse_bilan_filters(params, stmt, VPlanChasseRealisationBilan)
        # group by
        stmt = stmt.group_by(
            VPlanChasseRealisationBilan.id_espece, TSaisons.nom_saison
        )

    else:

        realisation_subq = (
            select(
            VPlanChasseRealisationBilan.id_espece,
            VPlanChasseRealisationBilan.id_saison,
            func.sum(VPlanChasseRealisationBilan.nb_realisation).label("nb_realisation"),
            func.sum(VPlanChasseRealisationBilan.nb_realisation_avant_11).label("nb_realisation_avant_11"),
            )
            .group_by(
            VPlanChasseRealisationBilan.id_espece, VPlanChasseRealisationBilan.id_saison
            )
        )

        realisation_subq = build_chasse_bilan_filters(
            params, realisation_subq, VPlanChasseRealisationBilan
        ).subquery()


        attribution_subq = (
            select(
            TAttributionMassifs.id_espece,
            TAttributionMassifs.id_saison,
            func.sum(TAttributionMassifs.nb_affecte_min).label("nb_attribution_min"),
            func.sum(TAttributionMassifs.nb_affecte_max).label("nb_attribution_max"),
            )
            .group_by(
            TAttributionMassifs.id_espece, TAttributionMassifs.id_saison
            )
        )

        attribution_subq = build_chasse_bilan_filters(
            params, attribution_subq, TAttributionMassifs
        ).subquery()


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
            .join(
            realisation_subq,
            TSaisons.id_saison == realisation_subq.c.id_saison
            )
            .join(
            attribution_subq,
            attribution_subq.c.id_saison == realisation_subq.c.id_saison
            )
        )



    stmt = stmt.order_by(TSaisons.nom_saison)

    return stmt


def get_plain_text_data(params):
    # Espèces
    out = {}
    if "id_espece" in params:
        # res = TEspeces.query.get(params["id_espece"])
        if params["id_espece"] is not None:
            res = DB.session.get(TEspeces, params["id_espece"])
            if res:
                out["nom_espece"] = res.nom_espece
            else:
                out["nom_espece"] = "???"
    # Saison
    if "id_saison" in params:
        # res = TSaisons.query.get(params["id_saison"])
        if params["id_saison"] is not None:
            res = DB.session.get(TSaisons, params["id_saison"])
            if res:
                out["nom_saison"] = res.nom_saison
            else:
                out["nom_saison"] = "???"
        else:
            out["nom_saison"] = "???"
    # Nom zone
    zones = None
    if params["id_zone_indicative"]:
        zones = DB.session.scalars(
            select(TZoneIndicatives).where(
            TZoneIndicatives.id_zone_indicative.in_(params["id_zone_indicative"])
            )
        ).all()
        column_name = "nom_zone_indicative"
    elif params["id_zone_cynegetique"]:

        zones = DB.session.scalars(
            select(TZoneCynegetiques).where(
                TZoneCynegetiques.id_zone_cynegetique.in_(params["id_zone_cynegetique"]
                )
            )
        ).all()

        column_name = "nom_zone_cynegetique"
    elif params["id_secteur"]:

        zones = DB.session.scalars(
            select(TSecteurs).where(
                TSecteurs.id_secteur.in_(params["id_secteur"]
                )
            )
        ).all()

        column_name = "nom_secteur"

    if zones:
        out[column_name] = ", ".join([getattr(z, column_name) for z in zones])

    return out


def get_chasse_bilan(params):
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
    columns = GenericTable(
        "v_pre_bilan_pretty", "oeasc_chasse", DB.engine
    ).tableDef.columns

    stmt = (
        select(*[c for c in columns])
        .where(columns.nom_saison == nom_saison)
        .where(columns.nom_espece == nom_espece)
        .order_by(cast(columns.code_zone_indicative, Integer))
    )

    data_chasse = DB.session.execute(stmt)

    res = [
        {(str(col.key)): getattr(r, str(col.key)) for col in columns}
        for r in data_chasse.all()
    ]

    zcs = []

    for r in res:
        zc = next(
            (item for item in zcs if item["nom"] == r["nom_zone_cynegetique"]), None
        )
        if not zc:
            zc = {
                "nom": r["nom_zone_cynegetique"],
                "mini": r["nb_attribution_min_zc"] or "",
                "maxi": r["nb_attribution_max_zc"] or "",
                "realisation": int(r["nb_realisation_zc"]) or "",
                "pourcent": round(
                    r["nb_realisation_zc"] / r["nb_attribution_max_zc"] * 100
                )
                or "",
                "zis": [],
                **get_details(
                    nom_saison,
                    nom_espece,
                    {"nom_zone_cynegetique": [r["nom_zone_cynegetique"]]},
                ),
            }
            zcs.append(zc)
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
                **get_details(
                    nom_saison,
                    nom_espece,
                    {"nom_zone_indicative": [r["nom_zone_indicative"]]},
                ),
            }
        )

    if res:
        last_r = res[-1]
        mini = last_r["nb_attribution_min_espece"] or ""
        maxi = last_r["nb_attribution_max_espece"] or ""
        realisation = int(last_r["nb_realisation_espece"]) or ""
        pourcent = (
            round(last_r["nb_realisation_espece"] / last_r["nb_attribution_max_espece"] * 100)
            if last_r["nb_attribution_max_espece"] else ""
        )
    else:
        mini = maxi = realisation = pourcent = ""

    data = {
        "nom_saison": nom_saison,
        "nom_espece": nom_espece,
        "mini": mini,
        "maxi": maxi,
        "realisation": realisation,
        "pourcent": pourcent,
        "zcs": zcs,
        **get_details(nom_saison, nom_espece),
    }

    return data


def get_data_all_especes_export_ods(nom_saison):
    if nom_saison == "current":
        stmt = select(TSaisons.nom_saison).where(TSaisons.current == True)
        nom_saison = DB.session.execute(stmt).scalar_one()
    data = {"nom_saison": nom_saison, "especes": []}
    for nom_espece in ["Cerf", "Chevreuil", "Mouflon"]:
        data["especes"].append(get_data_export_ods(nom_saison, nom_espece))

    return data
