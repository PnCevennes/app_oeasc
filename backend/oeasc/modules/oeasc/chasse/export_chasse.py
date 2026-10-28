########################################################################################################
######################## EXPORTS DU PLAN DE CHASSE (ODS ET CSV) ########################################
########################################################################################################
# - get_data_all_especes_export_ods : données du bilan de chasse injectées dans le template ODS
# - exportation_attributions_realises_chasse : export CSV des attributions / réalisations


import pandas as pd

from sqlalchemy import func, cast, select, Integer
from sqlalchemy import table as sa_table, column as sa_column
from sqlalchemy.orm import aliased

from utils_flask_sqla.generic import GenericTable
from pypnnomenclature.models import TNomenclatures

from oeasc.utils.env import db as DB
from ..resultat.repository import result_custom
from ..commons.models import TEspeces, TSecteurs
from .models import (
    TSaisons,
    TAttributions,
    TTypeBracelets,
    TZoneCynegetiques,
    TZoneIndicatives,
    TRealisationsChasse,
    TLieuTirs,
    TLieuTirSynonymes,
)


#################################################################################
################### CREATION D'UN EXPORT ODS POUR LIBREOFFICE  ##################
###############################################################################

# clé du template ODS -> (champ de la vue, libellé recherché)
# "bracelet_attr" désigne le champ "bracelet" de la vue des attributions
DETAILS_ODS = {
    "nb_sexe_male": ("label_sexe", "Mâle"),
    "nb_sexe_femelle": ("label_sexe", "Femelle"),
    "nb_sexe_ind": ("label_sexe", "Indéterminé"),
    "nb_mois_sep": ("mois_txt", "Sep."),
    "nb_mois_oct": ("mois_txt", "Oct."),
    "nb_mois_nov": ("mois_txt", "Nov."),
    "nb_mois_dec": ("mois_txt", "Déc."),
    "nb_mois_jan": ("mois_txt", "Jan."),
    "nb_mois_fev": ("mois_txt", "Fév."),
    "nb_age_ad": ("label_classe_age", "Adulte"),
    "nb_age_ind": ("label_classe_age", "Indéterminé"),
    "nb_age_suba": ("label_classe_age", "Sub-adulte"),
    "nb_age_juv": ("label_classe_age", "Juvénile"),
    "nb_mode_chasse_app": ("label_mode_chasse", "Approche"),
    "nb_mode_chasse_aff": ("label_mode_chasse", "Affut"),
    "nb_mode_chasse_ind": ("label_mode_chasse", "Indéterminé"),
    "nb_mode_chasse_bat": ("label_mode_chasse", "Battue"),
    "nb_real_cem": ("bracelet", "CEM"),
    "nb_real_ceff": ("bracelet", "CEFF"),
    "nb_real_ceffd": ("bracelet", "CEFFD"),
    "nb_attr_cem": ("bracelet_attr", "CEM"),
    "nb_attr_ceff": ("bracelet_attr", "CEFF"),
    "nb_attr_ceffd": ("bracelet_attr", "CEFFD"),
}


def get_details(nom_saison, nom_espece, filter=None):
    """
    Récupère et agrège des statistiques détaillées sur les résultats de chasse pour une saison et une espèce données.

    Cette fonction interroge différentes vues personnalisées de la base de données pour obtenir des comptages selon plusieurs critères :
    - Sexe (Mâle, Femelle, Indéterminé)
    - Mois de prélèvement (Sep., Oct., Nov., Déc., Jan., Fév.)
    - Classe d'âge (Adulte, Sub-adulte, Juvénile, Indéterminé)
    - Mode de chasse (Approche, Affut, Battue, Indéterminé)
    - Type de bracelet utilisé (CEM, CEFF, CEFFD)
    - Attribution des bracelets (CEM, CEFF, CEFFD)

    Pour chaque critère, la fonction extrait le nombre d'individus correspondant (cf. DETAILS_ODS), et calcule également le pourcentage de réalisation par rapport à l'attribution des bracelets.

    Args:
        nom_saison (str): Le nom de la saison de chasse concernée.
        nom_espece (str): Le nom de l'espèce concernée.
        filter (dict, optionnel): Filtres additionnels à appliquer lors de la requête (ex: secteur, commune, etc.).

    Returns:
        dict: Un dictionnaire contenant les statistiques agrégées pour chaque critère.
    """
    filters = {
        "nom_saison": [nom_saison],
        "nom_espece": [nom_espece],
        **(filter or {}),
    }

    res_details = {
        field_name: result_custom(
            {
                "view": "oeasc_chasse.v_custom_results",
                "field_name": field_name,
                "filters": filters,
            }
        )
        for field_name in [
            "label_sexe",
            "mois_txt",
            "label_classe_age",
            "label_mode_chasse",
            "bracelet",
        ]
    }
    res_details["bracelet_attr"] = result_custom(
        {
            "view": "oeasc_chasse.v_custom_result_attribution",
            "field_name": "bracelet",
            "filters": filters,
        }
    )

    out = {
        key: next(
            (elem["count"] for elem in res_details[field] if elem["text"] == text),
            0,
        )
        or ""
        for key, (field, text) in DETAILS_ODS.items()
    }

    for bracelet in ["cem", "ceff", "ceffd"]:
        nb_real = out[f"nb_real_{bracelet}"]
        out[f"pourcent_{bracelet}"] = (
            round(1.0 * nb_real / out[f"nb_attr_{bracelet}"] * 100) if nb_real else ""
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


##################################################################################
#################### EXPORTATION DES REALISATIONS DE CHASSE EN CSV  ##############
###############################################################################


def _bilan_historique(nom_saison_debut=None, nom_saison_fin=None):
    """
    Totaux historiques (t_bilan_chasse_historique) par saison, espèce et zone indicative.
    Colonnes alignées sur celles de l'export détaillé (zones « attribuées »).
    """
    historique = sa_table(
        "t_bilan_chasse_historique",
        sa_column("id_saison"),
        sa_column("id_espece"),
        sa_column("id_zone_indicative"),
        sa_column("nb_affecte_max"),
        sa_column("nb_realise"),
        sa_column("nb_realise_avant_11"),
        schema="oeasc_chasse",
    )
    stmt = (
        select(
            TSaisons.nom_saison,
            TEspeces.nom_espece,
            TEspeces.code_espece,
            TEspeces.cd_nom,
            TSecteurs.nom_secteur,
            TSecteurs.code_secteur,
            TZoneCynegetiques.nom_zone_cynegetique.label(
                "nom_zone_cynegetique_attribuee"
            ),
            TZoneCynegetiques.code_zone_cynegetique.label(
                "code_zone_cynegetique_attribuee"
            ),
            TZoneIndicatives.nom_zone_indicative.label("nom_zone_indicative_attribuee"),
            TZoneIndicatives.code_zone_indicative.label(
                "code_zone_indicative_attribuee"
            ),
            historique.c.nb_affecte_max,
            historique.c.nb_realise,
            historique.c.nb_realise_avant_11,
        )
        .select_from(historique)
        .join(TSaisons, TSaisons.id_saison == historique.c.id_saison)
        .join(TEspeces, TEspeces.id_espece == historique.c.id_espece)
        .join(
            TZoneIndicatives,
            TZoneIndicatives.id_zone_indicative == historique.c.id_zone_indicative,
        )
        .join(
            TZoneCynegetiques,
            TZoneCynegetiques.id_zone_cynegetique
            == TZoneIndicatives.id_zone_cynegetique,
        )
        .outerjoin(TSecteurs, TSecteurs.id_secteur == TZoneCynegetiques.id_secteur)
        .where(
            *([TSaisons.nom_saison >= nom_saison_debut] if nom_saison_debut else []),
            *([TSaisons.nom_saison <= nom_saison_fin] if nom_saison_fin else []),
        )
        .order_by(TSaisons.nom_saison.desc(), TEspeces.nom_espece)
    )
    df = pd.DataFrame(DB.session.execute(stmt).all())
    if len(df):
        df.insert(0, "type_ligne", "historique_agrege")
    return df


def exportation_attributions_realises_chasse(id_saison_debut=None, id_saison_fin=None):
    """
    id_saison_debut / id_saison_fin : bornes (incluses) de la période exportée, None = pas de borne.
    Récupèration des données pertinentes en BDD.
    Plusieurs traitements de données sont faits pour afficher des données lisibles.
    retourne un dataframe
    Cette fonction remplace l'ancienne fonction d'export qui utilisait une vue sql qui n'est plus compatible
    avec le nouveau modèle de la bdd.
    """

    tzcr = aliased(TZoneCynegetiques)
    tzca = aliased(TZoneCynegetiques)
    tzir = aliased(TZoneIndicatives)
    tzia = aliased(TZoneIndicatives)
    tns = aliased(TNomenclatures)
    tnca = aliased(TNomenclatures)
    tnmc = aliased(TNomenclatures)

    # Les id_saison ne sont pas chronologiques : on borne sur nom_saison ("AAAA-AAAA")
    def _nom_saison(id_saison):
        if not id_saison:
            return None
        return DB.session.execute(
            select(TSaisons.nom_saison).where(TSaisons.id_saison == id_saison)
        ).scalar_one_or_none()

    nom_saison_debut = _nom_saison(id_saison_debut)
    nom_saison_fin = _nom_saison(id_saison_fin)

    stmt = (
        select(
            (TRealisationsChasse.id_realisation.isnot(None)).label(
                "realisee"
            ),  # Boolean indiquant si la réalisation de chasse existe ou pas
            TAttributions.numero_bracelet,
            TTypeBracelets.code_type_bracelet,
            TEspeces.nom_espece,
            TEspeces.code_espece,
            TEspeces.cd_nom,  # code taxonomique de l'espece
            TSaisons.nom_saison,
            TSecteurs.nom_secteur,
            TSecteurs.code_secteur,
            tzcr.nom_zone_cynegetique.label(
                "nom_zone_cynegetique_realisee"
            ),  # Nom de la zone cynégétique réalisée
            tzcr.code_zone_cynegetique.label(
                "code_zone_cynegetique_realisee"
            ),  # Code de la zone cynégétique réalisée
            tzir.nom_zone_indicative.label(
                "nom_zone_indicative_realisee"
            ),  # Nom de la zone indicative réalisée
            tzir.code_zone_indicative.label(
                "code_zone_indicative_realisee"
            ),  # Code de la zone indicative réalisée
            tzca.nom_zone_cynegetique.label(
                "nom_zone_cynegetique_attribuee"
            ),  # Nom de la zone cynégétique attribuée
            tzca.code_zone_cynegetique.label(
                "code_zone_cynegetique_attribuee"
            ),  # Code de la zone cynégétique attribuée
            tzia.nom_zone_indicative.label(
                "nom_zone_indicative_attribuee"
            ),  # Nom de la zone indicative attribuée
            tzia.code_zone_indicative.label(
                "code_zone_indicative_attribuee"
            ),  # Code de la zone indicative attribuée
            TRealisationsChasse.date_exacte,
            TRealisationsChasse.date_enreg,
            TRealisationsChasse.mortalite_hors_pc,  # Boolean indiquant si la mortalité est hors plan de chasse
            tns.label_fr.label("sexe"),  # Sexe de l'animal
            tnmc.label_fr.label("mode_chasse"),  # Mode de chasse
            tnca.label_fr.label("classe_age"),  # Classe d'âge
            TRealisationsChasse.poid_entier,
            TRealisationsChasse.poid_vide,
            TRealisationsChasse.poid_c_f_p,
            TRealisationsChasse.long_dagues_droite,
            TRealisationsChasse.long_dagues_gauche,
            TRealisationsChasse.long_mandibules_droite,
            TRealisationsChasse.long_mandibules_gauche,
            TRealisationsChasse.cors_nb,
            TRealisationsChasse.cors_commentaires,
            TRealisationsChasse.gestation,
            TRealisationsChasse.commentaire,
            TRealisationsChasse.parcelle_onf,
            TRealisationsChasse.poid_indique,
            TRealisationsChasse.cors_indetermine,
            TRealisationsChasse.long_mandibule_indetermine,
            func.ST_X(func.ST_Centroid(func.ST_Transform(TLieuTirs.geom, 4326))).label(
                "x"
            ),  # Coordonnée X du centre du lieu de tir. Centroid du lieu dit de tir
            func.ST_Y(func.ST_Centroid(func.ST_Transform(TLieuTirs.geom, 4326))).label(
                "y"
            ),  # Coordonnée Y du centre du lieu de tir
        )
        .select_from(TAttributions)
        .outerjoin(
            TRealisationsChasse,
            TRealisationsChasse.id_attribution == TAttributions.id_attribution,
        )
        .outerjoin(
            tzcr,
            tzcr.id_zone_cynegetique
            == TRealisationsChasse.id_zone_cynegetique_realisee,
        )
        .outerjoin(
            tzir,
            tzir.id_zone_indicative == TRealisationsChasse.id_zone_indicative_realisee,
        )
        .outerjoin(TSecteurs, TSecteurs.id_secteur == tzcr.id_secteur)
        .outerjoin(
            TLieuTirSynonymes,
            TLieuTirSynonymes.id_lieu_tir_synonyme
            == TRealisationsChasse.id_lieu_tir_synonyme,
        )
        .outerjoin(TLieuTirs, TLieuTirs.id_lieu_tir == TLieuTirSynonymes.id_lieu_tir)
        .outerjoin(TSaisons, TSaisons.id_saison == TAttributions.id_saison)
        .outerjoin(
            tzca, tzca.id_zone_cynegetique == TAttributions.id_zone_cynegetique_affectee
        )
        .outerjoin(
            tzia, tzia.id_zone_indicative == TAttributions.id_zone_indicative_affectee
        )
        .outerjoin(
            TTypeBracelets,
            TTypeBracelets.id_type_bracelet == TAttributions.id_type_bracelet,
        )
        .outerjoin(TEspeces, TEspeces.id_espece == TTypeBracelets.id_espece)
        .outerjoin(tns, tns.id_nomenclature == TRealisationsChasse.id_nomenclature_sexe)
        .outerjoin(
            tnca, tnca.id_nomenclature == TRealisationsChasse.id_nomenclature_classe_age
        )
        .outerjoin(
            tnmc,
            tnmc.id_nomenclature == TRealisationsChasse.id_nomenclature_mode_chasse,
        )
        .where(
            *(
                [TSaisons.nom_saison >= nom_saison_debut]
                if nom_saison_debut
                else []
            ),
            *([TSaisons.nom_saison <= nom_saison_fin] if nom_saison_fin else []),
        )
        .order_by(
            TSaisons.nom_saison.desc(),
            "realisee",
            TAttributions.numero_bracelet,
            TSecteurs.code_secteur,
            tzca.code_zone_cynegetique,
            tzia.code_zone_indicative,
            tns.label_fr,
            tnca.label_fr,
        )
    )

    data = DB.session.execute(stmt).all()
    df_historique = _bilan_historique(nom_saison_debut, nom_saison_fin)
    df_export = pd.DataFrame(data)
    df_export.insert(0, "type_ligne", "detail")

    # Saisons antérieures aux données détaillées : totaux agrégés (pas de détail par tir)
    if len(df_historique):
        df_export = pd.concat([df_export, df_historique], ignore_index=True)

    return df_export
