########################################################################################################
################# TRAITEMENT DE L'IMPORTATION CSV DE GEOCHASSE AVEC PYTHON ET PANDAS  ##################
########################################################################################################
# fait un clean du csv exporté par geochasse, ( certaines colonnes sont décalées et d'autres sont inutiles)
# récupère les attributions de la saison sélectionnée par l'utilisateur
# fusionne le csv avec les attributions grâce au numéro de bracelet,
# vérifie que les données sont cohérentes et complètes,
# Cherche des correspondances pour les lieux de tir.
#   Les correspondances sont validées si elles sont dans la même Zi ou même commune
#   Si une correspondance est trouvée dans la même ZC on ne la propose qu'en commentaire
# Insert les nouvelles données puis fait une mise à jour des données existante
# Créé un csv des lignes en erreur pour que l'utilisateur puisse les corriger.
# retourne une apiResponse qui affichera toutes les étapes réussies ou échouées au frontend.


##########################################################################################################
################# POUR AMÉLIORER LA GESTION DES LIEUX DIT ################################################
# Pour les lieux dits qui ont des correspondances dans la même commune, il faudrait faire une  buffer zone autour de la geometrie de la zi et vérifier si ça croise la geometrie des lieux dits trouvés en correspondance. Si ça croise, on peut considérer que c'est une correspondance valide, même si le nom n'est pas exactement le même.
# Pour les lieux dits trouvés dans la même ZC, il faudrait vérifier que la geometrie de chaques correspondance se trouve proche autour de la geometrie de la ZI
# Une fois traité, il faudrait enregistrer tous les nouveaux synonymes des lieux de tir


import sys

# ensure project root is on sys.path so `import config.config` works
sys.path.append("/home/thibaut/appli/app_oeasc")
sys.path.append("/home/thibaut/appli/app_oeasc/backend")
from pathlib import Path

from app import app

# from utils_flask_sqla.generic import GenericTable
# from flask import request, current_app, jsonify

# import numpy as np
import pandas as pd

# import json
# import rapidfuzz as fuzz
# from pyproj import Transformer

# from marshmallow.exceptions import ValidationError

from sqlalchemy import func, select
from sqlalchemy.orm import aliased
from flask import request, current_app, session

# from oeasc.utils.apiResponse import ApiResponse

from utils_flask_sqla.generic import GenericTable
from flask import request, current_app

# from ..generic.repository import getlist
from ..resultat.repository import result_custom
from sqlalchemy import func, cast, select, Integer
from ..commons.models import TEspeces, TSecteurs


from oeasc.modules.oeasc.commons.models import TEspeces, TSecteurs


from oeasc.modules.oeasc.chasse.models import (
    TSaisons,
    TAttributions,
    TTypeBracelets,
    TZoneCynegetiques,
    TZoneIndicatives,
    TRealisationsChasse,
    TLieuTirs,
    TLieuTirSynonymes,
)


from .models import (
    TSaisons,
    TZoneCynegetiques,
    TZoneIndicatives,
    # TAttributionMassifs,
    # VPlanChasseRealisationBilan,
)

from pypnnomenclature.models import (
    TNomenclatures,
    # BibNomenclaturesTypes
)

# from pypnnomenclature.schemas import NomenclatureSchema, BibNomenclaturesTypesSchema


# Initialisation de l'ApiResponse pour stocker les messages, le journal de l'opération et les données à retourner à l'utilisateur.
# apiResponse = ApiResponse()


config = current_app.config
DB = config["DB"]
SESSION = session
# chemin du dossier où seront stockés les rapports d'erreurs à la fin du traitement. Si le dossier n'existe pas, il sera créé.
DOSSIER_RAPPORTS = Path(config["ROOT_DIR"]) / "static/erreurs_import_chasse/"


#################################################################################
################### CREATION D'UN EXPORT ODS POUR LIBREOFFICE  ##################
###############################################################################


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


##################################################################################
#################### EXPORTATION DES REALISATIONS DE CHASSE EN CSV  ##############
###############################################################################


def exportation_attributions_realises_chasse():
    """
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

    with app.app_context():
        data = DB.session.execute(stmt).all()
    df_export = pd.DataFrame(data)

    return df_export
