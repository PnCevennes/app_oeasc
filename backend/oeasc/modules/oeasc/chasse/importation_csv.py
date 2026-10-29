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

import numpy as np
import pandas as pd
import json
import rapidfuzz as rpfz
from pyproj import Transformer

from marshmallow.exceptions import ValidationError

from sqlalchemy import func, select
from flask import request, current_app
from oeasc.utils.current_user import get_current_user

from oeasc.utils.apiResponse import ApiResponse
from oeasc.modules.oeasc.chasse.poids import poid_vide_depuis_entier

from oeasc.ref_geo_oeasc.models import BibAreasType, LAreas
from oeasc.modules.oeasc.chasse.models import (
    TAttributions,
    TZoneIndicatives,
    TZoneCynegetiques,
    TTypeBracelets,
    TSaisons,
    TRealisationsChasse,
    TLieuTirs,
    TLieuTirSynonymes,
)
from oeasc.modules.oeasc.chasse.schema import (
    TRealisationsChasseSchema,
)

config = current_app.config
from oeasc.utils.env import db as DB

# --- Contournement d'un coût inutile de marshmallow_sqlalchemy 1.4.1 ---
# _cast_data() est appelé à CHAQUE schema.load() et invoque
# importlib.metadata.version("marshmallow"), qui reparse le fichier METADATA
# du paquet (~1-2 ms par appel). Sur un import de plusieurs milliers de lignes
# (une réalisation = un schema.load), cela représente plusieurs secondes.
# La version de marshmallow ne change pas au runtime et _cast_data se contente
# d'un typing.cast (no-op) : on le remplace par l'identité.
try:
    import marshmallow_sqlalchemy.load_instance_mixin as _mm_sqla_load_mixin

    _mm_sqla_load_mixin._cast_data = lambda data: data
except Exception:  # pragma: no cover - dépend de la version installée
    pass


#####################################################################################################
####################              VARIABLES GLOBALES                            #####################
#####################################################################################################

# chemin du dossier où seront stockés les rapports d'erreurs à la fin du traitement. Si le dossier n'existe pas, il sera créé.
DOSSIER_RAPPORTS = Path(config["ROOT_DIR"]) / "static/erreurs_import_chasse/"
# création du dossier s'il n'existe pas
DOSSIER_RAPPORTS.mkdir(parents=True, exist_ok=True)

DOSSIER_ARCHIVES_LIEUX_DITS = Path(config["ROOT_DIR"]) / "data/archives_lieux_dits/"
# création du dossier s'il n'existe pas
DOSSIER_ARCHIVES_LIEUX_DITS.mkdir(parents=True, exist_ok=True)

#  rapidfuzz permet de reperer les erreurs de saisie dans les noms de lieux dits et communes.
#  Si le score de similarité est inférieur à ce seuil, on considère que les chaînes ne correspondent pas.
SCORE_MINIMUM_RAPIDFUZZ = 76

# Fourchettes de valeurs pour repérer les données aberrantes. Si une valeur est en dehors de ces fourchettes, on considère que c'est une erreur de saisie et on remplace par null.
NB_CORS_MINIMUM = 1  # en dessous de ce nombre, on considère que c'est une erreur de saisie et on remplace par null
NB_CORS_MAXIMUM = 24  # au dessus de ce nombre, on considère que c'est une erreur de saisie et on remplace par null

TAILLE_MINIMUM_DAGUES = {
    "CERF": {"ADULTE": 50, "SUBADULTE": 50, "INDÉTERMINÉ": 5, "JEUNE": 2, "FAON": 2},
    "CHEVREUIL": {"ADULTE": 10, "SUBADULTE": 1, "INDÉTERMINÉ": 1, "JEUNE": 1},
}
TAILLE_MAXIMUM_DAGUES = {
    "CERF": {
        "ADULTE": 650,
        "SUBADULTE": 500,
        "INDÉTERMINÉ": 600,
        "JEUNE": 200,
        "FAON": 200,
    },
    "CHEVREUIL": {"ADULTE": 200, "SUBADULTE": 150, "INDÉTERMINÉ": 200, "JEUNE": 100},
}

POIDS_VIDE_MINIMUM = {
    "CERF": {"ADULTE": 40, "SUBADULTE": 20, "INDÉTERMINÉ": 18, "JEUNE": 18, "FAON": 18},
    "CHEVREUIL": {"ADULTE": 7, "SUBADULTE": 7, "INDÉTERMINÉ": 7, "JEUNE": 7},
    "MOUFLON": {"ADULTE": 18, "SUBADULTE": 10, "INDÉTERMINÉ": 5, "JEUNE": 5},
}
POIDS_VIDE_MAXIMUM = {
    "CERF": {
        "ADULTE": 250,
        "SUBADULTE": 150,
        "INDÉTERMINÉ": 300,
        "JEUNE": 120,
        "FAON": 120,
    },
    "CHEVREUIL": {"ADULTE": 70, "SUBADULTE": 50, "INDÉTERMINÉ": 50, "JEUNE": 26},
    "MOUFLON": {"ADULTE": 55, "SUBADULTE": 30, "INDÉTERMINÉ": 35, "JEUNE": 35},
}

TAILLE_MINIMUM_MANDIBULES = 5
TAILLE_MAXIMUM_MANDIBULES = 300

# L'export geochasse provoque des décalages dans les noms de colonnes. La variable suivante les renomme correctement
# Mais il faudra la modifier le jour où geochasse corrigera le problème.
ERREUR_NOMS_COLONNES_GEOCHASSE = {
    "parc_nom_tireur": "auteur_tir_str",
    "parc_lieu_dit": "lieu_tir_txt",
    "long_cornes_G_isard": "cors_nb",
    "long_machoire_1": "long_mandibules_droite",
    "long_machoire_2": "long_mandibules_gauche",
    "commentaires": "commentaire",
}
# Pour les mouflons l'age est un entier
ERREUR_AGE = {"1": "ADULTE"}


# On définit les id de nomenclatures et le lien entre les codes de bracelet et les especes en dur
# Si il y a des changements majeurs dans la bdd , il faudra peut être les récupérer dynamiquement
LISTE_ESPECE = {
    "CEFF": [
        "CERF",
        ["FEMELLE", "INDÉTERMINÉ", "MALE"],
        ["ADULTE", "SUBADULTE", "INDÉTERMINÉ", "FAON"],
    ],
    "CEFFD": [
        "CERF",
        ["FEMELLE", "INDÉTERMINÉ", "MALE"],
        ["ADULTE", "SUBADULTE", "FAON"],
    ],
    "CEM": ["CERF", ["MALE"], ["ADULTE", "SUBADULTE", "INDÉTERMINÉ", "FAON"]],
    "CEMD": ["CERF", ["MALE"], ["JEUNE"]],
    "MOF": ["MOUFLON", ["FEMELLE"], ["ADULTE"]],
    "MOM": ["MOUFLON", ["MALE"], ["ADULTE"]],
    "MOM1": ["MOUFLON", ["MALE"], ["SUBADULTE"]],
    "MOI": ["MOUFLON", ["INDÉTERMINÉ"], ["JEUNE"]],
    "MOIJ": ["MOUFLON", ["FEMELLE", "MALE"], ["JEUNE"]],
    "CHI": [
        "CHEVREUIL",
        ["MALE", "INDÉTERMINÉ", "FEMELLE"],
        ["ADULTE", "SUBADULTE", "INDÉTERMINÉ", "JEUNE"],
    ],
}
LISTE_NOMENCLATURE_SEXE = {"FEMELLE": 168, "MALE": 169, "INDÉTERMINÉ": 167}
LISTE_NOMENCLATURE_AGE = {
    "ADULTE": 3,
    "SUBADULTE": 6,
    "INDÉTERMINÉ": 2,
    "JEUNE": 4,
    "FAON": 4,
}
LISTE_NOMENCLATURE_MODE_CHASSE = {
    "BATTUE": 575,
    "INDIVIDUEL": 588,
    "COLLECTIVE": 575,
    "AFFÛT": 573,
    "APPROCHE": 574,
}
LISTE_NOMENCLATURE_ESPECE = {"CERF": 1, "MOUFLON": 9, "CHEVREUIL": 2}


# nom des colonnes du csv exporté par geochasse. Si geochasse change les noms de colonnes, il faudra les modifier ici.

COLUMNS_NAME = {
    "id_geochasse": ["ID"],
    "numero": ["NUMERO"],
    "espece": ["ESPECE"],
    "age": ["AGE"],
    "sexe": ["SEXE"],
    "poids": ["POIDS"],
    "pesee": ["PESEE"],
    "risque_sanitaire": ["RISQUE SANITAIRE"],
    "type_chasse": ["TYPE CHASSE"],
    "ref_battue": ["REF_BATTUE"],
    "numero_battue": ["NUMERO_BATTUE"],
    "origine_bracelet": ["ORIGINE_BRACELET"],
    "ref_ug": ["REF_UG"],
    "ref_detenteur": ["REF_DETENTEUR"],
    "nom_detenteur": ["NOM_DETENTEUR"],
    "ref_equipe": ["REF_EQUIPE"],
    "nom_equipe": ["NOM_EQUIPE"],
    "ref_membre": ["REF_MEMBRE"],
    "date": ["DATE"],
    "heure": ["HEURE"],
    "date_saisie": ["DATE_SAISIE"],
    "commune": ["COMMUNE"],
    "insee_commune": ["INSEE_COMMUNE"],
    "lieu_dit": ["LIEU_DIT"],
    "territoire": ["TERRITOIRE"],
    "departement": ["DEPT"],
    "longitude": ["LON"],
    "latitude": ["LAT"],
    "photos": ["PHOTOS"],
    "commentaires": ["COMMENTAIRE"],
    "nom_tireur": ["NOM TIREUR"],
    "matin/apres_midi": ["MATIN/APRES-MIDI"],
    "tir_plomb": ["TIR PLOMB"],
    "serotheque": ["SEROTHEQUE"],
    "metatarse": ["METATARSE"],
    "long_pattes": ["LONG.PATTES"],
    "long_machoire_1": ["LONG.MACHOIRE 1"],
    "long_machoire_2": ["LONG.MACHOIRE 2"],
    "nb_cors": ["NB CORS"],
    "nb_tetines": ["NB TETINES"],
    "nb_embryons": ["NB EMBRYONS"],
    "long_cornes_G_isard": ["LONG CORNE G (ISARD)"],
    "long_cornes_D_isard": ["LONG CORNE D (ISARD)"],
    "circonf_corne_G_isard": ["CIRCONF CORNE G (ISARD)"],
    "circonf_corne_D_isard": ["CIRCONF CORNE D (ISARD)"],
    "hauteur_cornes_isard": ["HAUTEUR CORNES (ISARD)"],
    "ecart_cornes_isard": ["ECART CORNES (ISARD)"],
    "age_isard": ["AGE (ISARD)"],
    "long_corne_mouflon": ["LONG CORNES (MOUFLON)"],
    "diam_corne_mouflon": ["DIAM. CORNES (MOUFLON)"],
    "age_mouflon": ["AGE (MOUFLON)"],
    "long_dagues_gauche": ["LONG_DAGUE (1)", "LONG_DAGUE G", "LONG CORNE G"],
    "long_dagues_droite": ["LONG_DAGUE (2)", "LONG_DAGUE D", "LONG CORNE D"],
    "parc_nom_tireur": ["PARC_NOM_TIREUR"],
    "parc_lieu_dit": ["PARC_LIEU_DIT"],
    "parc_lieu_dit2": ["PARC_LIEU_DIT2"],
}


# noms des colonnes de geochasses inutiles. On les supprimera au début du traitement
COLUMNS_INUTILES = [
    "risque_sanitaire",
    "numero_battue",
    "ref_battue",
    "ref_ug",
    "ref_detenteur",
    "nom_detenteur",
    "ref_equipe",
    "nom_equipe",
    "ref_membre",
    "insee_commune",
    "territoire",
    "photos",
    "nom_tireur",
    "matin/apres_midi",
    "tir_plomb",
    "serotheque",
    "metatarse",
    "long_pattes",
    "nb_tetines",
    "nb_embryons",
    "circonf_corne_G_isard",
    "circonf_corne_D_isard",
    "ecart_cornes_isard",
    "age_isard",
    "long_corne_mouflon",
    "diam_corne_mouflon",
    "age_mouflon",
    "nb_cors",
    "long_cornes_D_isard",
    "hauteur_cornes_isard",
    "heure",
]

# noms des colonnes de la table realisations_chasse. Utilisé à la toute fin pour faire un clean du dataframe
COLUMNS_REALISATION = [
    "id_attribution",
    "id_zone_cynegetique_realisee",
    "id_zone_indicative_realisee",
    "id_lieu_tir_synonyme",
    "date_exacte",
    "date_enreg",
    "mortalite_hors_pc",
    "id_nomenclature_sexe",
    "id_nomenclature_classe_age",
    "poid_entier",
    "poid_vide",
    "poid_c_f_p",
    "long_dagues_droite",
    "long_dagues_gauche",
    "long_mandibules_droite",
    "long_mandibules_gauche",
    "cors_nb",
    "cors_commentaires",
    "gestation",
    "id_nomenclature_mode_chasse",
    "commentaire",
    "parcelle_onf",
    "poid_indique",
    "cors_indetermine",
    "long_mandibule_indetermine",
    "id_numerisateur",
    "meta_create_date",
    "meta_update_date",
    "id_nomenclature_categorie",
    "auteur_tir_str",
    "auteur_constat_str",
]


###################################################################################################
###################################################################################################


def get_columns_mapping(
    colonnes_csv: list[str],
    columns_name: dict = COLUMNS_NAME,
    seuil_similarite: int = 85,
) -> list[str]:
    """
    Permet de reperer les noms de colonnes du csv de geochasse en fonction de plusieurs synonymes.
    Geochasse à tendance à changer ses noms de colonnes. Cette fonction essaye de limiter les errreurs de correspondance.
    Utilise rapidfuzz pour reperer les similarités entre les noms de colonnes.

    Args:
        colonnes_csv      : Liste des colonnes lues dans le CSV (dans l'ordre)
        columns_name      : Dictionnaire {nom_souhaité: [synonymes_possibles]}
        seuil_similarite  : Score minimum RapidFuzz pour valider une correspondance

    Returns:
        liste_columns_result : Liste ordonnée des noms normalisés
                               (None si colonne non reconnue)
    """

    liste_columns_result = []

    for col_csv in colonnes_csv:
        meilleur_score = 0
        meilleur_nom = None

        # ── Pour chaque nom souhaité, on teste tous ses synonymes ───────────
        for nom_souhaite, synonymes in columns_name.items():

            resultat = rpfz.process.extractOne(
                query=col_csv,
                choices=synonymes,
                scorer=rpfz.fuzz.WRatio,
                score_cutoff=seuil_similarite,
            )

            if resultat:
                synonyme_trouve, score, _ = resultat
                # On garde la clé avec le score le plus élevé tous synonymes confondus
                if score > meilleur_score:
                    meilleur_score = score
                    meilleur_nom = nom_souhaite
                    # meilleur_synonyme = synonyme_trouve  # pour le log

        if meilleur_nom:
            liste_columns_result.append(meilleur_nom)
            # print(f"'{col_csv}' → '{meilleur_synonyme}' → '{meilleur_nom}' (score: {meilleur_score:.0f})")
        else:
            liste_columns_result.append(None)
            print(
                f" '{col_csv}' → non reconnue (score sous le seuil {seuil_similarite})"
            )

    return liste_columns_result


def uniformise_communes(serie):
    """Retire les accents, les tirets et met en majuscules une série de pandas.
    Utilisée pour comparer des champs texte entre l'import csv et la base de données."""
    serie = serie.str.upper()
    serie = serie.str.replace("-", " ")
    serie = serie.str.replace("É", "E")
    serie = serie.str.replace("Ç", "C")
    serie = serie.str.replace("È", "E")
    serie = serie.str.replace("Ê", "E")
    serie = serie.str.replace("À", "A")
    serie = serie.str.replace(r"\bST\b", "SAINT", regex=True)
    serie = serie.str.replace(r"\bSTE\b", "SAINTE", regex=True)
    serie = serie.str.replace(r"\bMT\b", "MONT", regex=True)
    # retrait du mot 30
    serie = serie.str.replace(r"\s*\b30\b\s*", " ", regex=True)

    # retrait des mots entres parenthèses
    # serie = serie.str.replace(r'\s*\(.*\)\s*', ' ', regex=True)

    serie = serie.str.replace("   ", " ")
    # retrait des espaces en début et fin de chaîne
    serie = serie.str.strip()

    return serie


def uniformise_lieu_dit(serie):
    """Retire les accents, les tirets et met en majuscules une série de pandas.
    Utilisée pour comparer des champs texte entre l'import csv et la base de données."""
    serie = serie.str.upper()
    serie = serie.str.replace("-", " ")
    serie = serie.str.replace("É", "E")
    serie = serie.str.replace("È", "E")
    serie = serie.str.replace("Ê", "E")
    serie = serie.str.replace("À", "A")
    # retrait des mots ZIC
    serie = serie.str.replace(r"\s*ZIC\s*", " ", regex=True)
    # retrait des mots BS
    serie = serie.str.replace(r"\s*BS\s*", " ", regex=True)
    # retrait des mots TCA
    serie = serie.str.replace(r"\s*TCA\s*", " ", regex=True)
    # retrait des mots ZT
    serie = serie.str.replace(r"\s*ZT\s*", " ", regex=True)
    serie = serie.str.replace(r"\bST\b", "SAINT", regex=True)
    serie = serie.str.replace(r"\bSTE\b", "SAINTE", regex=True)
    serie = serie.str.replace(r"\bMT\b", "MONT", regex=True)

    # retrait des mots entres parenthèses
    serie = serie.str.replace(r"\s*\(.*\)\s*", " ", regex=True)

    # retrait des mot "L'"
    serie = (
        serie.str.replace(r"\bL'", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    # retrait des mot "D'"
    serie = (
        serie.str.replace(r"\bD'", " ", regex=True)
        .str.replace(r"\s+", " ", regex=True)
        .str.strip()
    )
    # retrait des mot "LA"
    serie = serie.str.replace(r"\s*\bLA\b\s*", " ", regex=True)
    # retrait des mot "LES"
    serie = serie.str.replace(r"\s*\bLES\b\s*", " ", regex=True)
    # retrait des mot "LE"
    serie = serie.str.replace(r"\s*\bLE\b\s*", " ", regex=True)

    # retrait des  mot en chiffres romains
    serie = serie.str.replace(r"\s*\b[IVXLCDM]+\b\s*", " ", regex=True)

    serie = serie.str.replace("   ", " ")
    # retrait des espaces en début et fin de chaîne
    serie = serie.str.strip()

    return serie


def corrections_communes(serie_commune):
    """Corrige les cas particuliers de noms de communes qui sont différents entre geochasse et la base de données."""
    serie_commune = serie_commune.replace("LANUEJOLS 30", "LANUEJOLS GARD")
    serie_commune = uniformise_communes(serie_commune)

    corrections = {
        # 'ST ANDRE DE CAPCEZE': 'SAINT ANDRE CAPCEZE',
        "FRAISSINET DE FOURQUE": "FRAISSINET DE FOURQUES",
        "PONT DE MONTVERT SUD MONT LOZERE": "PONT DE MONTVERT SUD MONT LOZERE",
        "LE PONT DE MONTVERT SUD MONT LOZORE": "PONT DE MONTVERT SUD MONT LOZORE",
        "LE PONT DE MONTVERT": "PONT DE MONTVERT SUD MONT LOZORE",
        "FRAISSINET DE LOZERE": "PONT DE MONTVERT SUD MONT LOZORE",
        "PONT DE MONTVERT": "PONT DE MONTVERT SUD MONT LOZORE",
        "QUEZAC": "GORGES DU TARN CAUSSES",
        "FLORAC": "FLORAC TROIS RIVIERES",
        "BEDOUES": "BEDOUES COCURES",
        "VAL D AIGOUAL": "VAL D'AIGOUAL",
        "SAINT ANDRE DE CAPCEZE": "SAINT ANDRE CAPCEZE",
        "TREVES": "TRÈVES",
    }
    serie_commune = serie_commune.replace(corrections)

    return serie_commune


def clean_colonne_str(serie):
    """Retire les espaces en début et fin de chaîne et les espaces multiples d'une série de pandas."""
    mask_null = serie.isna()

    # Convertir en string
    serie = serie.astype(str)
    # Remplacer les espaces multiples par un seul espace
    serie = serie.str.replace(r"\s+", " ", regex=True)
    serie = serie.str.strip()

    # Remettre NaN aux positions originalement nulles
    serie = serie.where(~mask_null, other=None)
    return serie


def check_caracteres_invisibles(df):
    """Remplace par None toutes les valeurs du dataframe qui ne contiennent que des caractères invisibles (espaces, tabulations, retours à la ligne, etc.)."""
    for col in df.select_dtypes(include=["object"]).columns:
        df[col] = df[col].apply(
            lambda x: None if isinstance(x, str) and x.strip() == "" else x
        )
    return df


def uniformise_date(serie):
    """Repère si la date est sous un format indiqué dans "formats" et les uniformise au format aaaa-mm-jj.
    Si une date ne peut pas être convertie, elle est remplacée par None.
    Fonction créée car geochasse à changé ses formats de date à plusieurs reprises."""
    formats = [
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%Y-%m-%d",
        "%Y/%m/%d",
        "%Y.%m.%d",
        "%d/%m/%Y %H:%M",
        "%d-%m-%Y %H:%M",
        "%d.%m.%Y %H:%M",
        "%Y-%m-%d %H:%M",
        "%Y/%m/%d %H:%M",
        "%Y.%m.%d %H:%M",
    ]
    # Chaque format est essayé valeur par valeur : un fichier qui mélange
    # plusieurs formats n'invalide pas les dates convertibles.
    resultat = pd.Series(None, index=serie.index, dtype=object)
    restantes = serie.notna()
    for fmt in formats:
        if not restantes.any():
            break
        try:
            converties = pd.to_datetime(serie[restantes], format=fmt, errors="coerce")
        except (ValueError, TypeError):
            continue
        ok = converties.notna()
        resultat.loc[ok[ok].index] = converties[ok].dt.strftime("%Y-%m-%d")
        restantes.loc[ok[ok].index] = False
    if restantes.any():
        print(
            f"Impossible de convertir {restantes.sum()} date(s) avec les formats connus, "
            f"ex. '{serie[restantes].iloc[0]}'."
        )
    return resultat


def poid_vide_cerf(poids_entier_in):
    """Poids vide d'un cerf (CF) calculé à partir de son poids entier (None si non calculable)."""
    return poid_vide_depuis_entier("CF", poids_entier_in)


def poid_vide_chevreuil(poids_entier_in):
    """Poids vide d'un chevreuil (CH) calculé à partir de son poids entier (None si non calculable)."""
    return poid_vide_depuis_entier("CH", poids_entier_in)


def convert_str_to_float(serie):
    """Convertit une série de pandas de chaînes de caractères en nombres à virgule flottante.
    Si une valeur ne peut pas être convertie, elle est remplacée par None."""

    def convert_value(value):
        if pd.isna(value):
            return None
        if isinstance(value, str):
            value = value.replace(",", ".").replace(" ", "")
            try:
                return float(value)
            except ValueError:
                # print(f"Impossible de convertir la valeur '{value}' en float.")
                return None
        elif isinstance(value, (int, float)):
            return float(value)
        else:
            return None

    return serie.apply(convert_value)


def convert_to_int(serie):
    """Convertit une série de pandas en nombres entiers. Valeurs non convertibles -> None."""
    # conserver positions NA initiales
    mask_na = serie.isna()

    # normaliser en chaîne pour homogénéiser les formats (virgule décimale, espaces)
    cleaned = (
        serie.astype(str)
        .str.replace(",", ".", regex=False)
        .str.replace(" ", "", regex=False)
        .str.strip()
    )

    # traiter les chaînes vides / littérales 'nan' / 'None' comme NA
    cleaned = cleaned.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})

    # convertir en numérique (coerce transforme les valeurs invalides en NaN)
    numeric = pd.to_numeric(cleaned, errors="coerce")

    # convertir en int par troncature (comme int(float(x))) et garder None pour les NaN
    result = numeric.apply(lambda x: int(x) if pd.notna(x) else None)

    # remettre None aux positions initialement NA
    result = result.where(~mask_na, other=None)

    return result


##################################################################################
################ FONCTIONS ETAPES DE TRAITEMENT DE L'IMPORT CSV  ################
##################################################################################


def etape__récuperation_csv(apiResponse, source=None):
    """Check si les informations nécessaires à l'import sont présentes et récupère le csv exporté par geochasse.
     retourne un dataframe pandas et une ApiResponse avec les messages d'erreur et le journal de l'opération.
     Si une erreur est détectée, le dataframe retourné est vide et la ApiResponse contient les messages d'erreur et le journal de l'opération.
    Si aucune erreur n'est détectée, le dataframe retourné contient les données du csv et la ApiResponse contient le journal de l'opération.

    source : chemin de fichier (str/Path) ou objet fichier. Si None, on lit
    request.files["file"] (comportement historique en contexte de requête).
    """

    file = None
    fichier_ouvert_ici = False
    try:
        df = pd.DataFrame()

        if source is None:
            if "file" not in request.files:
                apiResponse.add_log(
                    "Aucun fichier trouvé dans la requête", type_log="ERROR"
                )
                apiResponse.add_error(
                    user_message="Aucun fichier trouvé dans la requête",
                    system_error="Aucun fichier trouvé dans la requête",
                )
                return pd.DataFrame(), apiResponse
            source = request.files["file"]

        if isinstance(source, (str, Path)):
            if not Path(source).is_file():
                apiResponse.add_log(f"Fichier introuvable: {source}", type_log="ERROR")
                apiResponse.add_error(
                    user_message="Le fichier importé est introuvable sur le serveur.",
                    system_error=f"Fichier introuvable: {source}",
                )
                return pd.DataFrame(), apiResponse
            file = open(source, "rb")
            fichier_ouvert_ici = True
        else:
            file = source
            if getattr(file, "filename", None) == "":
                apiResponse.add_log("Nom de fichier vide", type_log="ERROR")
                apiResponse.add_error(
                    user_message="Nom de fichier vide",
                    system_error="Nom de fichier vide",
                )
                return pd.DataFrame(), apiResponse

        file_save = file

        # repère le caratère de séparation utilisé dans le csv ("," ou ";") et utilise le bon séparateur pour lire le csv. Par défaut geochasse utilise ";" mais il arrive que le csv soit exporté avec "," comme séparateur.
        # On lit les 5 premières lignes du csv pour repérer le séparateur utilisé. Si le csv contient moins de 5 lignes, on lit toutes les lignes.
        sample = file.read(1024).decode(
            "utf-8-sig"
        )  # Lire les premiers 1024 octets du fichier pour détecter le séparateur
        file.seek(0)  # Revenir au début du fichier après la lecture de l'échantillon
        if sample.count(";") > sample.count(","):
            sep = ";"
        else:
            sep = ","

        colonnes_csv = pd.read_csv(file, nrows=0, sep=sep).columns.tolist()
        file.seek(
            0
        )  # Revenir au début du fichier: read_csv a pu avancer le curseur au-delà de la ligne d'en-tête (buffer interne du moteur C)
        liste_mapping = get_columns_mapping(
            colonnes_csv=colonnes_csv, columns_name=COLUMNS_NAME, seuil_similarite=90
        )

        # colonnes présentes dans le csv mais non reconnues : geochasse change parfois
        # ses noms de colonnes (cf ERREUR_NOMS_COLONNES_GEOCHASSE plus haut) sans que ça
        # provoque d'erreur — la colonne correspondante est alors silencieusement vide
        # (ex: "type_chasse" introuvable => mode de chasse toujours null en base).
        # On avertit systématiquement dans le journal pour que ce soit visible.
        colonnes_non_reconnues = [
            col_csv
            for col_csv, col_reconnue in zip(colonnes_csv, liste_mapping)
            if col_reconnue is None
        ]
        if colonnes_non_reconnues:
            apiResponse.add_log(
                "Colonne(s) du CSV non reconnue(s), ignorée(s) : "
                + ", ".join(f"'{c}'" for c in colonnes_non_reconnues)
                + ". Si l'une d'elles correspond à un champ attendu (ex: TYPE CHASSE), "
                "l'export geochasse a probablement changé de nom de colonne : ce champ "
                "restera vide pour toutes les lignes importées.",
                type_log="WARNING",
            )

        df = pd.read_csv(
            file_save,
            sep=sep,
            encoding="utf-8-sig",
            skiprows=1,
            names=liste_mapping,
            index_col=False,
        )

        if df.shape[0] == 0:
            apiResponse.add_log("Le fichier CSV est vide", type_log="ERROR")
            apiResponse.add_error(
                user_message="Le fichier CSV est vide",
                system_error="Le fichier CSV est vide",
            )
            return pd.DataFrame(), apiResponse

        return df, apiResponse
    except Exception as e:
        user_message = "Une erreur est survenue lors de la récupération du fichier CSV. Veuillez vérifier que le fichier est au bon format et réessayer."
        apiResponse.add_error(system_error=str(e), user_message=user_message)
        apiResponse.add_log(message=user_message, type_log="ERROR")
        return pd.DataFrame(), apiResponse
    finally:
        if fichier_ouvert_ici and file is not None:
            try:
                file.close()
            except Exception:
                pass


#################################################################################
#################################################################################


def initialisation_apiResponse(id_role=None, nom_complet=None):
    """Initialise une ApiResponse pour stocker les messages d'erreur et de succès, le journal de l'opération et les données à retourner à l'utilisateur.

    id_role / nom_complet : si fournis, on les utilise directement (cas d'un
    traitement lancé hors contexte de requête, ex. thread de fond). Sinon on lit
    la session Flask (comportement historique).
    """
    apiResponse = ApiResponse(log_file="import_geochasse.log")

    # si l'appelant n'a pas fourni l'utilisateur, on tente la session Flask
    # (uniquement en contexte de requête : la session n'existe pas dans un thread).
    if id_role is None or nom_complet is None:
        current_user = get_current_user()
        id_role = id_role if id_role is not None else current_user.get("id_role")
        nom_complet = (
            nom_complet if nom_complet is not None else current_user.get("nom_complet")
        )

    if id_role is None or nom_complet is None:
        # add_error marque la réponse en échec et journalise l'erreur système
        apiResponse.add_error(
            user_message="Tentative d'importation: Utilisateur non connecté. Veuillez vous connecter pour continuer.",
            system_error="Tentative d'importation: Utilisateur non connecté ou informations manquantes.",
            status_code=401,
        )
        return apiResponse

    apiResponse.id_role = id_role
    apiResponse.nom_complet = nom_complet
    apiResponse.return_journal = True
    date_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
    apiResponse.add_log(
        f"Utilisateur {apiResponse.nom_complet} (id_role: {apiResponse.id_role}) a lancé l'import des données de chasse depuis Geochasse à {date_time}.",
        with_timestamp=True,
    )

    return apiResponse


def etape__clean_csv(df, apiResponse):
    # """Nettoie le dataframe en supprimant les colonnes inutiles et en renommant les colonnes avec les bons noms."""
    try:

        # parcours COLUMNS_NAME. si un nom de colonne n'existe pas dans df_trie, on l'ajoute avec des valeurs None. Cela permet de s'assurer que toutes les colonnes nécessaires sont présentes dans le dataframe, même si elles ne sont pas toutes présentes dans le csv de geochasse.
        for col in COLUMNS_NAME.keys():
            if col not in df.columns:
                df[col] = None
        # On supprime les lignes où "id_geochasse" n'est pas un integer. Il arrive qu'un caractère invisible se glisse dans cette colonne
        df = df.loc[df["id_geochasse"].notna()]
        df = df[df["id_geochasse"].apply(lambda x: str(x).isdigit())]
        df["id_geochasse"] = df["id_geochasse"].astype(int)
        # Correction des bugs et autres particularités bizarre de l'export geochasse.
        df.rename(columns=ERREUR_NOMS_COLONNES_GEOCHASSE, inplace=True)

        # PREMIER TRI DES DONNÉES: on retire les sangliers et on ne garde que les colonnes qui nous intéressent
        df_trie = df.loc[(df["espece"] != "SANGLIER")]
        df_trie = df_trie.set_index("numero")
        # suppression des colonnes inutiles
        df_trie = df_trie.drop(columns=COLUMNS_INUTILES, errors="ignore")

        df_trie = check_caracteres_invisibles(df_trie)

        # si dans la modification du csv un caractère invisible s'est glissé on le corrige.
        df_trie["auteur_tir_str"] = clean_colonne_str(df_trie["auteur_tir_str"])
        df_trie["lieu_tir_txt"] = clean_colonne_str(df_trie["lieu_tir_txt"])
        df_trie["commune"] = clean_colonne_str(df_trie["commune"])
        df_trie["commentaire"] = clean_colonne_str(df_trie["commentaire"])
        df_trie["espece"] = clean_colonne_str(df_trie["espece"])
        df_trie["espece"] = df_trie["espece"].str.upper()
        df_trie["age"] = clean_colonne_str(df_trie["age"])
        df_trie["age"] = df_trie["age"].str.upper()
        df_trie["age"] = df_trie["age"].replace(
            ERREUR_AGE
        )  # Surtout pour le cas des mouflons
        df_trie["sexe"] = clean_colonne_str(df_trie["sexe"])
        df_trie["sexe"] = df_trie["sexe"].str.upper()
        df_trie["type_chasse"] = clean_colonne_str(df_trie["type_chasse"])
        df_trie["type_chasse"] = df_trie["type_chasse"].str.upper()
        df_trie["pesee"] = clean_colonne_str(df_trie["pesee"])
        df_trie["pesee"] = df_trie["pesee"].str.upper()

        df_trie["poids"] = convert_str_to_float(df_trie["poids"])
        df_trie["latitude"] = convert_str_to_float(df_trie["latitude"])
        df_trie["longitude"] = convert_str_to_float(df_trie["longitude"])

        df_trie["cors_nb"] = convert_str_to_float(df_trie["cors_nb"])

        df_trie["long_mandibules_gauche"] = convert_str_to_float(
            df_trie["long_mandibules_gauche"]
        )
        df_trie["long_mandibules_droite"] = convert_str_to_float(
            df_trie["long_mandibules_droite"]
        )

        df_trie["long_dagues_gauche"] = convert_str_to_float(
            df_trie["long_dagues_gauche"]
        )
        df_trie["long_dagues_droite"] = convert_str_to_float(
            df_trie["long_dagues_droite"]
        )

        df_trie["date"] = uniformise_date(df_trie["date"])
        df_trie["date_saisie"] = uniformise_date(df_trie["date_saisie"])

        df_trie["lieu_dit"] = clean_colonne_str(df_trie["lieu_dit"])
        df_trie["departement"] = clean_colonne_str(df_trie["departement"])
        df_trie["parc_lieu_dit2"] = clean_colonne_str(df_trie["parc_lieu_dit2"])

        df_trie["id_geochasse"] = convert_to_int(df_trie["id_geochasse"])
        df_trie["origine_bracelet"] = convert_to_int(df_trie["origine_bracelet"])

        return df_trie, apiResponse
    except Exception as e:
        user_message = "Une erreur est survenue lors du nettoyage du fichier CSV. Veuillez vérifier que le fichier est au bon format et réessayer."
        apiResponse.add_error(system_error=str(e), user_message=user_message)
        apiResponse.add_log(message=user_message, type_log="ERROR")
        return pd.DataFrame(), apiResponse


def etape__recupération_attributions(df, id_saison, update, apiResponse):
    """
    Vérifie que l'id_saison est renseigné et valide, puis récupère les attributions de la saison en cours.
    Retourne un dataframe qui contient le csv geochasse fusionné avec les attributions.
    L'index du dataframe retourné est le numéro de bracelet.
    update: non utilisé (toutes les attributions de la saison sont récupérées ; le tri insert / update se fait sur id_realisation).
    Si une erreur est détectée, le dataframe retourné est vide et la ApiResponse contient les messages d'erreur et le journal de l'opération. Si aucune erreur n'est détectée, le dataframe retourné contient les données des attributions et la ApiResponse contient le journal de l'opération.
    """
    try:
        if id_saison is None:
            message = "id_saison n'est pas renseigné. Veuillez renseigner un id_saison pour continuer."
            apiResponse.add_log(message, type_log="ERROR")
            apiResponse.add_error(user_message=message, system_error=message)
            return pd.DataFrame(), apiResponse

        # on fait une requete à la base de données pour trouver toutes les attributions de la saison id_saison
        with app.app_context():

            # Récupération directe des seules colonnes utiles.
            # Remplace un dump Marshmallow imbriqué (zones + géométries + réalisation)
            # suivi de N+1 lazy-loads, très coûteux sur plusieurs centaines d'attributions.
            # id_realisation / zones réalisées : on reproduit le column_property
            # TAttributions.id_realisation (la plus grande id_realisation de l'attribution)
            # et on lit les zones réalisées de cette même réalisation.
            stmt_attributions = (
                select(
                    TAttributions.numero_bracelet,
                    TAttributions.id_attribution,
                    TAttributions.id_saison,
                    TAttributions.id_zone_cynegetique_affectee,
                    TAttributions.id_zone_indicative_affectee,
                    TSaisons.date_debut.label("saison_date_debut"),
                    TSaisons.date_fin.label("saison_date_fin"),
                    TZoneCynegetiques.id_secteur.label("id_secteur_affectee"),
                    TTypeBracelets.code_type_bracelet,
                    TRealisationsChasse.id_realisation,
                    TRealisationsChasse.id_zone_indicative_realisee,
                    TRealisationsChasse.id_zone_cynegetique_realisee,
                )
                .select_from(TAttributions)
                .outerjoin(TSaisons, TSaisons.id_saison == TAttributions.id_saison)
                .outerjoin(
                    TZoneCynegetiques,
                    TZoneCynegetiques.id_zone_cynegetique
                    == TAttributions.id_zone_cynegetique_affectee,
                )
                .outerjoin(
                    TTypeBracelets,
                    TTypeBracelets.id_type_bracelet == TAttributions.id_type_bracelet,
                )
                .outerjoin(
                    TRealisationsChasse,
                    TRealisationsChasse.id_attribution == TAttributions.id_attribution,
                )
                .where(TAttributions.id_saison == id_saison)
            )

            df_attributions = pd.DataFrame(
                DB.session.execute(stmt_attributions).mappings().all()
            )

            if df_attributions.empty:
                apiResponse.add_log(
                    f"Aucune attribution trouvée pour la saison id_saison={id_saison}. "
                    "Vérifiez que la saison est correcte et qu'elle contient des attributions.",
                    type_log="ERROR",
                )
                apiResponse.add_error(
                    user_message="Aucune attribution n'existe pour la saison sélectionnée. Vérifiez la saison choisie.",
                    system_error=f"Aucune attribution pour id_saison={id_saison}",
                )
                return pd.DataFrame(), apiResponse

            # une attribution peut (anomalie) porter plusieurs réalisations : on ne
            # garde que la plus grande id_realisation, comme le column_property d'origine.
            df_attributions = df_attributions.sort_values(
                "id_realisation"
            ).drop_duplicates("id_attribution", keep="last")

            # Marshmallow sérialisait les dates de saison en chaînes "AAAA-MM-JJ" :
            # on garde ce format car la comparaison avec df["date"] se fait sur des str.
            for col in ("saison_date_debut", "saison_date_fin"):
                df_attributions[col] = df_attributions[col].apply(
                    lambda d: d.isoformat() if d is not None and pd.notna(d) else None
                )
            df_attributions = df_attributions.rename(
                columns={
                    "saison_date_debut": "saison.date_debut",
                    "saison_date_fin": "saison.date_fin",
                }
            )

            # pour comparer les attributions de la bdd avec celles du csv il faut remplacer les espaces par 00
            df_attributions["numero_bracelet"] = df_attributions[
                "numero_bracelet"
            ].str.replace(" ", "00")

            # un peu de clean du dataframe pour alléger. On ne garde que les colonnes qui nous intéressent
            df_attributions = df_attributions[
                [
                    "numero_bracelet",
                    "id_attribution",
                    "id_realisation",
                    "id_saison",
                    "saison.date_debut",
                    "saison.date_fin",
                    "id_zone_cynegetique_affectee",
                    "id_zone_indicative_affectee",
                    "id_zone_indicative_realisee",
                    "id_zone_cynegetique_realisee",
                    "id_secteur_affectee",
                    "code_type_bracelet",
                ]
            ]

            # index = numero_bracelet pour la jointure avec le csv geochasse
            df_attributions.index = df_attributions["numero_bracelet"]

            # fusion de df_trie et df_attributions_non_realisees sur l'index (numero_bracelet)
            # on utilise outer pour pouvoir repérer les bracelets existant dans le csv mais pas dans les attributions de la bdd.
            df_fusion = df.join(df_attributions, how="outer")
            df_fusion = df_fusion.loc[df_fusion["id_geochasse"].notna()].copy()

            # pour les nouvelles réalisations, on met la zone affectée comme zone réalisée.
            df_fusion.loc[
                (
                    df_fusion["id_zone_indicative_realisee"].isna()
                    | df_fusion["id_realisation"].isnull()
                ),
                "id_zone_indicative_realisee",
            ] = df_fusion["id_zone_indicative_affectee"]
            df_fusion.loc[
                (
                    df_fusion["id_zone_cynegetique_realisee"].isna()
                    | df_fusion["id_realisation"].isnull()
                ),
                "id_zone_cynegetique_realisee",
            ] = df_fusion["id_zone_cynegetique_affectee"]

            return df_fusion, apiResponse

    except Exception as e:
        user_message = "Une erreur lors de la récupération des attributions de la saison. Veuillez vérifier que l'id_saison est correct et réessayer."
        apiResponse.add_log(message=user_message, type_log="ERROR")
        apiResponse.add_error(system_error=str(e), user_message=user_message)
        return pd.DataFrame(), apiResponse


def _signaler(df, idx, message, bloquant=True):
    """Ajoute message aux commentaires_erreurs des lignes idx.
    bloquant=True : la ligne devient invalide (valide=False, elle ne sera pas enregistrée).
    bloquant=False : la ligne est enregistrée mais marquée à vérifier (a_verifier=True)."""
    if bloquant:
        df.loc[idx, "valide"] = False
    else:
        df.loc[idx, "a_verifier"] = True
    df.loc[idx, "commentaires_erreurs"] += message


def _idx_non_positifs(serie):
    """Index des valeurs non nulles qui ne sont pas des nombres positifs."""
    return serie[
        ~serie.apply(lambda x: (isinstance(x, (int, float)) and x >= 0) or pd.isnull(x))
    ].index


def _masque_seuil(df, col, seuils, depasse):
    """Masque des lignes dont df[col] dépasse le seuil seuils[espece][age].
    depasse(valeur, seuil) indique le sens de la comparaison."""
    return df.apply(
        lambda row: (
            row[col] is not None
            and row["age"] in seuils.get(row["espece"], {})
            and depasse(row[col], seuils[row["espece"]][row["age"]])
        ),
        axis=1,
    )


def _inferieur(valeur, seuil):
    return valeur < seuil


def _superieur(valeur, seuil):
    return valeur > seuil


def etape__verification_donnees_geochasse(df, apiResponse):
    """
    Vérifie que les données du csv geochasse sont cohérentes entre elles et avec les données de la base de données.
    ajoute des colonnes "valide" et "commentaires_erreurs" au dataframe pour indiquer si les données sont valides ou non et pour stocker les commentaires d'erreurs. On s'en servira pour faire un rapport final à l'utilisateur.
    Les erreurs bloquantes mettent valide à False, les valeurs aberrantes mettent a_verifier à True (cf. _signaler).
    """
    try:

        df["valide"] = True
        df["a_verifier"] = False
        df["commentaires_erreurs"] = ""

        ################################### VERIF DES BRACELETS EXISTANTS ##########################################
        # les bracelets du csv doivent exister dans les attributions de la saison.
        _signaler(
            df,
            df[df["id_attribution"].isnull()].index,
            "Le numéro de bracelet n'existe pas dans les attributions de la saison. ",
        )

        # un bracelet ne peut être réalisé qu'une fois (index unique sur id_attribution) :
        # toutes les lignes d'un bracelet en double sont écartées, sans deviner laquelle est la bonne.
        _signaler(
            df,
            df.index.duplicated(keep=False) & df["id_attribution"].notna().to_numpy(),
            "Le numéro de bracelet apparaît plusieurs fois dans le fichier. ",
        )

        ########################################   TRAITEMENT DE L'ESPÈCE  ############################################
        # id_nomenclature_espece permet de retrouver la catégorie de l'espèce (FAON, BICHETTE, DAGUET etc..)
        df["id_nomenclature_espece"] = df["espece"].map(LISTE_NOMENCLATURE_ESPECE)

        # LISTE_ESPECE[code_type_bracelet] = [espèce, sexes possibles, âges possibles]
        def theorique(position):
            return df["code_type_bracelet"].map(
                lambda k: LISTE_ESPECE.get(k)[position] if k in LISTE_ESPECE else None
            )

        # l'espèce du tir doit correspondre à l'espèce théorique du bracelet
        _signaler(
            df,
            df[df["espece"] != theorique(0)].index,
            "Espèce du tir ne correspond pas à l'espèce du bracelet. ",
        )

        ############################# TRAITEMENT DU SEXE  ############################################
        # le sexe du tir doit faire partie des sexes possibles pour le code du bracelet
        df["sexe_theorique"] = theorique(1)
        _signaler(
            df,
            df[
                ~df.apply(
                    lambda row: (
                        row["sexe"] in row["sexe_theorique"]
                        if row["sexe_theorique"] is not None
                        else True
                    ),
                    axis=1,
                )
            ].index,
            "Sexe du tir ne correspond pas au sexe du bracelet. ",
        )

        df["id_nomenclature_sexe"] = df["sexe"].map(LISTE_NOMENCLATURE_SEXE)
        _signaler(
            df,
            df[df["id_nomenclature_sexe"].isnull()].index,
            "Sexe du tir ne correspond à aucun sexe de la nomenclature. ",
        )

        ###########################   TRAITEMENT DE L'ÂGE  ############################################
        # pour les mouflons on repère l'âge avec le code_type_bracelet
        df.loc[df["espece"] == "MOUFLON", "age"] = df.loc[
            (df["espece"] == "MOUFLON"), "code_type_bracelet"
        ].map(lambda k: LISTE_ESPECE.get(k)[2][0] if k in LISTE_ESPECE else None)

        # l'âge du tir doit faire partie des âges possibles pour le code du bracelet
        df["age_theorique"] = theorique(2)
        _signaler(
            df,
            df[
                ~df.apply(
                    lambda row: (
                        row["age"] in row["age_theorique"]
                        if row["age_theorique"] is not None
                        else True
                    ),
                    axis=1,
                )
            ].index,
            "Âge du tir ne correspond pas à l'âge du bracelet. ",
        )

        df["id_nomenclature_classe_age"] = df["age"].map(LISTE_NOMENCLATURE_AGE)
        _signaler(
            df,
            df[df["id_nomenclature_classe_age"].isnull()].index,
            "Âge du tir ne correspond à aucun âge dans les nomenclatures de la bdd. ",
        )

        ##########################  TRAITEMENT DU POIDS ET DE LA PESEE  #####################################

        df["poid_c_f_p"] = None
        df["poid_indique"] = False

        # un poids renseigné doit être un nombre positif
        _signaler(
            df,
            df[
                (
                    ~df["poids"].apply(lambda x: isinstance(x, (int, float)) and x >= 0)
                    & (df["poids"].notnull())
                )
            ].index,
            "Poids du tir n'est pas un nombre ou est négatif. ",
        )

        df.loc[
            ((df["pesee"] == "PLEIN") & (df["poids"] > 0) & (df["poids"].notnull())),
            "poid_entier",
        ] = df["poids"]
        df.loc[
            ((df["pesee"] == "VIDÉ") & (df["poids"] > 0) & (df["poids"].notnull())),
            "poid_vide",
        ] = df["poids"]
        df.loc[((df["poids"].notnull()) & (df["poids"] > 0)), "poid_indique"] = True
        df.loc[
            (df["espece"] == "CERF")
            & (df["poid_entier"].notnull())
            & (df["poid_vide"].isnull()),
            "poid_vide",
        ] = df["poid_entier"].map(poid_vide_cerf)
        df.loc[
            (df["espece"] == "CHEVREUIL")
            & (df["poid_entier"].notnull())
            & (df["poid_vide"].isnull()),
            "poid_vide",
        ] = df["poid_entier"].map(poid_vide_chevreuil)

        # poids vide hors des fourchettes POIDS_VIDE_MINIMUM / MAXIMUM (par espèce et âge) : à vérifier
        _signaler(
            df,
            df[_masque_seuil(df, "poid_vide", POIDS_VIDE_MINIMUM, _inferieur)].index,
            "Poids vide inférieur au poids vide minimum pour l'espèce et l'âge. ",
            bloquant=False,
        )
        _signaler(
            df,
            df[_masque_seuil(df, "poid_vide", POIDS_VIDE_MAXIMUM, _superieur)].index,
            "Poids vide supérieur au poids vide maximum pour l'espèce et l'âge. ",
            bloquant=False,
        )

        df.drop(columns=["poids", "pesee"], inplace=True)

        ##########################  TRAITEMENT DU MODE DE CHASSE  ###########################################
        # type_chasse est égale à "INDIVIDUEL", "COLLECTIVE" ou "BATTUE"
        df["id_nomenclature_mode_chasse"] = None
        for type_chasse in ["INDIVIDUEL", "COLLECTIVE", "BATTUE"]:
            df.loc[df["type_chasse"] == type_chasse, "id_nomenclature_mode_chasse"] = (
                LISTE_NOMENCLATURE_MODE_CHASSE.get(type_chasse)
            )
        df.drop(columns=["type_chasse"], inplace=True)

        ##########################   TRAITEMENT DES DATES  ##################################################
        # la date a été mise au format aaaa-mm-jj par uniformise_date (None si non convertible)
        _signaler(
            df,
            df[df["date"].isnull()].index,
            "Date du tir au format incorrect ou manquante. ",
        )
        # date_exacte et date_enreg ne sont plus différentiées dans les dernières versions oeasc, on les mets à l'identique
        df["date_exacte"] = df["date"]
        df["date_enreg"] = df["date_exacte"]

        # la date du tir doit être comprise dans la saison (si la saison a des dates de début / fin)
        _signaler(
            df,
            df[
                (df["date"] < df["saison.date_debut"])
                & (df["saison.date_debut"].notnull())
            ].index,
            "Date du tir avant le début de la saison. ",
        )
        _signaler(
            df,
            df[
                (df["date"] > df["saison.date_fin"]) & (df["saison.date_fin"].notnull())
            ].index,
            "Date du tir après la fin de la saison. ",
        )

        df.drop(columns=["date"], inplace=True)

        ###########################   TRAITEMENT DES CORS   #############################################
        # un nombre de cors renseigné doit être un entier positif
        _signaler(
            df,
            df[
                ~df["cors_nb"].apply(
                    lambda x: (
                        isinstance(x, (int, float)) and x >= 0 and x.is_integer()
                    )
                    or pd.isnull(x)
                )
            ].index,
            "Nombre de cors n'est pas un nombre entier positif ou est différent de null. ",
        )
        _signaler(
            df,
            df[(df["espece"] == "MOUFLON") & (df["cors_nb"].notnull())].index,
            "Nombre de cors renseigné pour un mouflon. ",
        )
        _signaler(
            df,
            df[
                (df["cors_nb"] < NB_CORS_MINIMUM) | (df["cors_nb"] > NB_CORS_MAXIMUM)
            ].index,
            f"Nombre de cors aberrant (inférieur à {NB_CORS_MINIMUM} ou supérieur à {NB_CORS_MAXIMUM}). ",
            bloquant=False,
        )

        df["cors_indetermine"] = True
        df.loc[df["cors_nb"] >= 0, "cors_indetermine"] = False

        ######################### TRAITEMENT DES DAGUES  #############################################
        for cote in ["droite", "gauche"]:
            col = f"long_dagues_{cote}"
            # remplacement des 0 par null
            df.loc[(df[col] == 0), col] = None
            _signaler(
                df,
                _idx_non_positifs(df[col]),
                f"La longueur de dague {cote} n'est pas un nombre entier positif ou est différent de null. ",
            )

        _signaler(
            df,
            df[
                (df["sexe"] == "FEMELLE")
                & (
                    df["long_dagues_droite"].notnull()
                    | df["long_dagues_gauche"].notnull()
                )
            ].index,
            "Longueur de dague renseignée pour une femelle. ",
        )

        # longueur hors des fourchettes TAILLE_MINIMUM / MAXIMUM_DAGUES (par espèce et âge) : à vérifier
        for cote in ["gauche", "droite"]:
            col = f"long_dagues_{cote}"
            _signaler(
                df,
                df[
                    _masque_seuil(df, col, TAILLE_MINIMUM_DAGUES, _inferieur)
                    | _masque_seuil(df, col, TAILLE_MAXIMUM_DAGUES, _superieur)
                ].index,
                f"Longueur de dague {cote} aberrante (unité attendue : mm, vérifier une saisie en cm). ",
                bloquant=False,
            )

        df.drop(columns=["sexe", "sexe_theorique"], inplace=True)

        ######################## TRAITEMENT DES MANDIBULES  #############################################
        for cote in ["droite", "gauche"]:
            col = f"long_mandibules_{cote}"
            # remplacement des 0 par null
            df.loc[df[col] == 0, col] = None
        for cote in ["droite", "gauche"]:
            _signaler(
                df,
                _idx_non_positifs(df[f"long_mandibules_{cote}"]),
                f"La longueur de mandibule {cote} n'est pas un nombre entier positif ou est différent de null. ",
            )

        _signaler(
            df,
            df[
                (df["long_mandibules_droite"] > TAILLE_MAXIMUM_MANDIBULES)
                | (df["long_mandibules_droite"] < TAILLE_MINIMUM_MANDIBULES)
                | (df["long_mandibules_gauche"] < TAILLE_MINIMUM_MANDIBULES)
                | (df["long_mandibules_gauche"] > TAILLE_MAXIMUM_MANDIBULES)
            ].index,
            "Longueur de mandibules aberrante. ",
            bloquant=False,
        )

        ######################## TRAITEMENT LATITUDE ET LONGITUDE  #############################################
        for col, nom in [("latitude", "Latitude"), ("longitude", "Longitude")]:
            _signaler(
                df,
                df[
                    ~df[col].apply(lambda x: isinstance(x, (int, float)) or pd.isnull(x))
                ].index,
                f"{nom} n'est pas un nombre ou est différent de null. ",
            )

        # transformation des coordonnées wgs84 en lambert 93 pour pouvoir les comparer aux coordonnées des zones de chasse.
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:2154", always_xy=True)
        df["longitude"], df["latitude"] = transformer.transform(
            df["longitude"], df["latitude"]
        )

        ####################### TRAITEMENT DES AUTEURS ET LIEUX DE TIR  #############################################
        # l'auteur et le lieu de tir ne peuvent pas être des nombres
        for col, message in [
            ("auteur_tir_str", "L'auteur du tir ne peut pas être un nombre. "),
            ("lieu_tir_txt", "Le lieu de tir ne peut pas être un nombre. "),
        ]:
            _signaler(
                df,
                df[
                    ~df[col].apply(
                        lambda x: not isinstance(x, (int, float)) or pd.isnull(x)
                    )
                ].index,
                message,
            )

        df.drop(columns=["age", "age_theorique"], inplace=True)

        ####################### ID NUMERISATEUR  #############################################
        # on ajoute la colonne id_numerisateur qui correspond à l'id_role de l'utilisateur connecté
        df["id_numerisateur"] = apiResponse.id_role

        return df, apiResponse

    except Exception as e:
        user_message = "Une erreur est survenue lors de la vérification des données du fichier CSV. Veuillez vérifier que le fichier est au bon format et réessayer."
        apiResponse.add_log(message=user_message, type_log="ERROR")
        apiResponse.add_error(system_error=str(e), user_message=user_message)
        apiResponse.write_in_log_file()
        return pd.DataFrame(), apiResponse


def etape__ajout_colonnes_vides_pour_bdd(df, apiResponse, update=False):
    """Ajoute les colonnes vides nécessaires pour l'enregistrement en base de données. Ces colonnes étaient présentes dans l'ancienne
    version de l'oeasc lorsqu'il n'y avait pas d'import"""
    try:
        ###################### TRAITEMENT DES CATEGORIES (D'ESPECES)  ########################################
        ## les id_nomenclature_categorie sont enregistés via un trigger en bdd
        df["id_nomenclature_categorie"] = None

        ###################### AJOUT DE COLONNES DIVERSES POUR LA BDD  ########################################
        df["gestation"] = None
        df["parcelle_onf"] = None
        df["mortalite_hors_pc"] = False

        # il n'y a plus la possibilité de declarer un auteur de constat. On le met à None pour l'enregistrement en bdd
        df["auteur_constat_str"] = None

        # pour l'instant le données sur les mandibules sont toujours vide dans geochasse. Mais peut être ça changera un jour.
        df["long_mandibule_indetermine"] = True
        df.loc[
            df["long_mandibules_droite"].notnull()
            | df["long_mandibules_gauche"].notnull(),
            "long_mandibule_indetermine",
        ] = False

        df["cors_commentaires"] = (
            None  # n'est pas utilisé mais on le créé pour l'ajout en bdd
        )

        # pour la gestion des dates de creation et de modification on utilise le trigger de la bdd.
        if update == False:
            df["meta_create_date"] = pd.Timestamp.now()
        else:
            df["meta_create_date"] = None

        df["meta_update_date"] = pd.Timestamp.now()

        return df, apiResponse

    except Exception as e:
        user_message = "Une erreur est survenue lors de l'ajout des colonnes pour la base de données. Veuillez vérifier que le fichier est au bon format et réessayer."
        apiResponse.add_log(message=user_message, type_log="ERROR")
        apiResponse.add_error(system_error=str(e), user_message=user_message)
        return pd.DataFrame(), apiResponse


def etape__integration_communes_dans_df(df, apiResponse):
    """Récupère les communes de la bdd et fusionne les informations sur les communes dans le dataframe principal.
    La jointure se fait avec le nom de la commune en utilisant rapidfuzz pour trouver le nom de commune le plus similaire.
    Pour l'instant seulement utilisé pour retrouver une petite partie des lieu dits de tirs.
    """

    try:
        with app.app_context():
            # récupération des communes de la bdd.
            # Sélection explicite des colonnes utiles pour éviter d'invoquer
            # des colonnes absentes sur certaines bases (ex: description).
            # La géométrie n'est pas récupérée : le rapprochement se fait uniquement
            # sur le nom de la commune (rapidfuzz plus bas), et une géométrie complète
            # par commune alourdit inutilement la requête.
            stmt = (
                select(
                    LAreas.id_area,
                    LAreas.area_code,
                    LAreas.area_name,
                )
                .join(BibAreasType, LAreas.id_type == BibAreasType.id_type)
                .where(BibAreasType.type_code == "OEASC_COMMUNE")
            )

            rows = DB.session.execute(
                stmt
            ).all()  # retourne [(id_area, area_code, area_name), ...]
            liste = []
            for id_area, area_code, area_name in rows:
                d = {
                    "id_area": id_area,
                    "area_code": area_code,
                    "area_name": area_name,
                }
                liste.append(d)

            df_liste_commune_oeasc = pd.json_normalize(liste)
            df_liste_commune_oeasc = df_liste_commune_oeasc[
                ["id_area", "area_code", "area_name"]
            ]
            df_liste_commune_oeasc = df_liste_commune_oeasc.rename(
                columns={
                    "id_area": "commune_id_area",
                    "area_code": "insee_commune",
                    "area_name": "commune_name",
                }
            )

        # cas très particulier de lanuejols qui existe en lozère et dans le gard. On les différencie en ajoutant GARD

        df_liste_commune_oeasc["commune_name"] = uniformise_communes(
            df_liste_commune_oeasc["commune_name"]
        )

        # NB: "insee_commune" ici contient en réalité l'area_code (code SIREN de la commune),
        # pas le code INSEE à 5 chiffres. "213001399" est le code SIREN de Lanuéjols (Gard),
        # à distinguer de celui de Lanuéjols (Lozère, "214800815").
        df_liste_commune_oeasc.loc[
            (
                (df_liste_commune_oeasc["commune_name"] == "LANUEJOLS")
                & (df_liste_commune_oeasc["insee_commune"] == "213001399")
            ),
            "commune_name",
        ] = "LANUEJOLS GARD"

        # correction des quelques cas particuliers des noms de communes. Ils seront aussi uniformisés pour la comparaison avec commune_name de df_liste_commune_oeasc
        df["commune"] = corrections_communes(df["commune"])

        # on créé une liste des noms de communes pour pouvoir faire la comparaison avec rapidfuzz et trouver le nom de commune le plus similaire dans la liste des communes de la base de données pour chaque commune du csv. Si le score de similarité est supérieur à 90, on remplace le nom de la commune du csv par le nom de la commune de la base de données.
        liste_nom_communes = df_liste_commune_oeasc["commune_name"].to_list()
        liste_nom_communes.sort()

        # modifie la colonne commune de df en comparant avec rapidfuzz avec la liste des communes de df_liste_commune_oeasc et en remplaçant par le nom de la commune de df_liste_commune_oeasc si le score de similarité est supérieur à 95
        def trouver_commune_similaire(nom_commune, liste_nom_communes, seuil=90):
            """
            petite fonction utilisé en mapping de dataframe. Che le nom de commune le plus similaire dans la liste des
            communes de la base de données et remplace par ce nom si le score de similarité est supérieur à 90.
            Utilise rapidfuzz pour le calcul du score de similarité."""
            if pd.isna(nom_commune):
                return nom_commune
            resultat = rpfz.process.extractOne(
                nom_commune, liste_nom_communes, scorer=rpfz.fuzz.ratio
            )
            # si le score de similarité est supérieur au seuil, on remplace par le nom de la commune de la base de données. Sinon on garde le nom de commune du csv (même s'il est potentiellement mal orthographié) pour ne pas perdre l'information et permettre à l'utilisateur de corriger le nom de la commune dans le csv pour maximiser les correspondances avec la base de données.
            if resultat[1] >= seuil:
                # Si il existe plusieurs correspondances, on ne garde que la première (celle avec le score de similarité le plus élevé)
                return resultat[0]
            else:
                return ""

        # parcours les commune de l'importation csv et remplace par le nom de commune le plus similaire dans la liste des communes de la base de données si le score de similarité rapidfuzz est supérieur à 90
        df["commune"] = df["commune"].apply(
            lambda x: trouver_commune_similaire(x, liste_nom_communes)
        )

        # on intégre les données sur les communes dans le dataframe principal. Et on supprime la colonne commune_name qui n'est plus utile après la fusion. La fusion se fait en faisant correspondre la colonne commune de df avec la colonne commune_name de df_liste_commune_oeasc. On fait une jointure à gauche pour ne pas perdre les lignes du csv qui n'ont pas de correspondance dans la base de données (même si on a essayé de corriger les noms de communes pour maximiser les correspondances). Les lignes du csv qui n'ont pas de correspondance dans la base de données auront des valeurs nulles pour les colonnes communes à df_liste_commune_oeasc (commune_id_area, insee_commune).
        df_fusion = df.merge(
            df_liste_commune_oeasc,
            left_on="commune",
            right_on="commune_name",
            how="left",
        ).drop(columns=["commune_name"])

        # si il y a une ligne ou id_area est null après la fusion, cela signifie que la commune du csv n'a pas de correspondance dans la base de données. On met valide à False et on ajoute un commentaire d'erreur dans ce cas.
        idx_erreur_commune = df_fusion[df_fusion["commune_id_area"].isnull()].index
        df_fusion.loc[idx_erreur_commune, "valide"] = False
        df_fusion.loc[
            idx_erreur_commune, "commentaires_erreurs"
        ] += "La commune du tir n'a pas de correspondance dans la base de données. "

        return df_fusion, apiResponse
    except Exception as e:
        user_message = "Une erreur est survenue lors de l'intégration des communes dans le dataframe. Veuillez vérifier que le fichier est au bon format et réessayer."
        apiResponse.add_log(message=user_message, type_log="ERROR")
        apiResponse.add_error(system_error=str(e), user_message=user_message)
        return pd.DataFrame(), apiResponse


def etape__recherche_lieux_dits_de_tir_de_realisation(df, apiResponse):
    """Retrouve les id_lieu_tir_synonyme correspondant au lieu dit de tir saisi dans le csv d'importation en comparant avec les lieux de tir synonymes de la base de données.
     La comparaison se fait en vérifiant que le nom du lieu dit saisi dans le csv correspond au nom_lieu_tir_synonyme dans la base de données
    La recherche se fait uniquement dans la zone cynégétique du tir (la ZI et la commune sont trop larges, risque de faux positifs) :
    1. le lieu dit saisi est identique à un synonyme de la même zone cynegetique
    2. le lieu dit saisi est similaire à un synonyme de la même zone cynegetique

    tous les cas  sont enregistrés dans un dict de bilan qui permettra d'augmenter le nombre de synonymes de lieux de tir dans la bdd.
    On y gardera dans ce dict les id_zone_indicative_affectee, id_zone_cynegetique_affectee et id_commune, latitude et longitude pour créer des nouveaux lieux dits à l'avenir.
    """

    try:
        # on garde une trace du nom du lieu dit d'origine avant de le modifier pour les comparaisons.
        df["save_lieu_dit"] = df[
            "lieu_tir_txt"
        ].copy()  # on garde une trace du lieu dit saisie avant de le modifier pour les ajouter aux synonymes

        # on met les noms de lieux tir en majuscules pour faciliter la fusion avec les données de df_liste_commune_oeasc
        df["lieu_tir_txt"] = uniformise_lieu_dit(df["lieu_tir_txt"])

        # contiendra un historique des correspondances trouvées entre les lieux dits saisis dans le csv et les lieux de tir synonymes de la base de données. Utile pour faire un bilan à l'utilisateur et pour augmenter la base de données des lieux de tir synonymes à l'avenir.
        # contiendra: numero_bracelet, nom_lieu_csv, correspondance (nom de lieu correspondant), id_correspondance, raison, id_zone_indicative_realisee, id_zone_cynegetique_realisee, id_commune, id_lieu_tir, nom_lieu_tir, latitude, longitude
        dict_bilan_synonymes = {}

        # récupération des lieux de tir synonymes de la base de données avec les informations sur les lieux de tir associés, les zones indicatives et les zones cynégétiques
        with app.app_context():
            # Récupération directe des colonnes utiles (remplace un dump Marshmallow
            # imbriqué lieu_tir -> zone_indicative -> zone_cynegetique sur ~1800 synonymes).
            # order_by explicite : plusieurs branches prennent le "premier" résultat
            # (.iloc[0]), il faut donc un ordre stable et déterministe.
            stmt_liste_lieu_tirs_synonymes = (
                select(
                    TLieuTirSynonymes.id_lieu_tir_synonyme,
                    TLieuTirSynonymes.id_lieu_tir,
                    TLieuTirSynonymes.nom_lieu_tir_synonyme,
                    TLieuTirs.nom_lieu_tir.label("nom_lieu_tir"),
                    TLieuTirs.id_zone_indicative.label("id_zi_lieu_tir"),
                    TZoneIndicatives.id_zone_cynegetique.label("id_zc_lieu_tir"),
                    TLieuTirs.id_area_commune.label("id_area_commune_lieu_tir"),
                )
                .select_from(TLieuTirSynonymes)
                .outerjoin(
                    TLieuTirs, TLieuTirs.id_lieu_tir == TLieuTirSynonymes.id_lieu_tir
                )
                .outerjoin(
                    TZoneIndicatives,
                    TZoneIndicatives.id_zone_indicative == TLieuTirs.id_zone_indicative,
                )
                .order_by(TLieuTirSynonymes.id_lieu_tir_synonyme)
            )
            df_lts = pd.DataFrame(
                DB.session.execute(stmt_liste_lieu_tirs_synonymes).mappings().all()
            )

            # mettre les noms en majuscules et uniformiser les champs texte
            df_lts["nom_lieu_tir_synonyme_origin"] = df_lts[
                "nom_lieu_tir_synonyme"
            ].copy()  # on garde une trace du nom du lieu de tir synonyme avant de le modifier pour les ajouter aux synonymes
            df_lts["nom_lieu_tir_synonyme"] = uniformise_lieu_dit(
                df_lts["nom_lieu_tir_synonyme"]
            )

            # retrait des lignes qui ont le meme nom_lieu_tir_synonyme et le meme id_lieu_tir pour ne garder que les synonymes différents du nom du lieu de tir
            df_lts = df_lts.loc[
                ~(
                    (df_lts["nom_lieu_tir_synonyme"] == df_lts["nom_lieu_tir"])
                    & (df_lts["id_lieu_tir_synonyme"] == df_lts["id_lieu_tir"])
                )
            ]

        # --- Pré-indexation de df_lts ---
        # Les recherches ci-dessous étaient faites par un masque booléen pandas
        # pour CHAQUE ligne du csv (O(lignes x synonymes)). On précalcule une fois
        # des groupby / index pour ramener chaque recherche à un accès O(1).
        for _col in (
            "id_zi_lieu_tir",
            "id_zc_lieu_tir",
            "id_area_commune_lieu_tir",
        ):
            df_lts[_col] = pd.to_numeric(df_lts[_col], errors="coerce")

        _EMPTY_LTS = df_lts.iloc[0:0]
        _groups_zc = df_lts.groupby(
            ["id_zc_lieu_tir", "nom_lieu_tir_synonyme"], sort=False
        )
        _names_by_zc = (
            df_lts.groupby("id_zc_lieu_tir", sort=False)["nom_lieu_tir_synonyme"]
            .apply(list)
            .to_dict()
        )
        _lts_by_synid = df_lts.set_index("id_lieu_tir_synonyme", drop=False)

        def _grp(groupby_obj, key):
            """get_group tolérant : renvoie un df vide si la clé est absente."""
            try:
                return groupby_obj.get_group(key)
            except KeyError:
                return _EMPTY_LTS

        # les futurs id_lieu_tir_synonyme et nom_lieu_tir_synonyme seront mis dans ces colonnes
        df["id_lieu_tir_synonyme"] = None
        df["nom_lieu_tir_synonyme"] = None

        def entree_bilan(row, type_correspondance, raison, synonyme=None):
            """Entrée du dict de bilan des synonymes pour le tir row.
            synonyme : ligne de df_lts retenue comme correspondance (None si aucune)."""
            return {
                "nom_lieu_csv": row["save_lieu_dit"],
                "correspondance": (
                    None
                    if synonyme is None
                    else synonyme["nom_lieu_tir_synonyme_origin"]
                ),
                "id_correspondance": (
                    None if synonyme is None else synonyme["id_lieu_tir_synonyme"]
                ),
                "type_correspondance": type_correspondance,
                "raison": raison,
                "id_zone_indicative_realisee": row["id_zone_indicative_realisee"],
                "id_zone_cynegetique_realisee": row["id_zone_cynegetique_realisee"],
                "id_commune": row["commune_id_area"],
                "id_lieu_tir": None if synonyme is None else synonyme["id_lieu_tir"],
                "nom_lieu_tir": None if synonyme is None else synonyme["nom_lieu_tir"],
                "lattitude": row["latitude"],
                "longitude": row["longitude"],
            }

        def meilleur_similaire(groups, names_by, cle_zone, nom):
            """Synonyme (ligne de df_lts) le plus similaire à nom parmi ceux de la zone cle_zone,
            si le score rapidfuzz atteint SCORE_MINIMUM_RAPIDFUZZ.
            Retourne (synonyme, nom_trouve) ; (None, None) si aucun nom dans la zone ;
            (False, None) si des noms existent mais aucun n'est assez similaire."""
            noms = names_by.get(cle_zone, [])
            if not noms:
                return None, None
            resultat = rpfz.process.extractOne(nom, noms, scorer=rpfz.fuzz.ratio)
            if resultat[1] < SCORE_MINIMUM_RAPIDFUZZ:
                return False, None
            meilleur_match = resultat[0]
            id_synonyme = _grp(groups, (cle_zone, meilleur_match))[
                "id_lieu_tir_synonyme"
            ].values[0]
            return _lts_by_synid.loc[id_synonyme], meilleur_match

        def affecter(index, synonyme):
            df.at[index, "id_lieu_tir_synonyme"] = synonyme["id_lieu_tir_synonyme"]
            df.at[index, "nom_lieu_tir_synonyme"] = synonyme[
                "nom_lieu_tir_synonyme_origin"
            ]

        # parcours de df pour trouver l'id_lieu_tir_synonyme correspondant à lieu_tir_txt.
        # Recherche en cascade dans la ZC uniquement : nom exact puis similaire.
        # La ZI et la commune ne sont pas utilisées (trop de risque de faux positifs).
        # NB : une ZC sans synonyme n'est pas une erreur, le tir finit en "AUCUNE" dans le bilan.
        for index, row in df.iterrows():
            id_zone_cynegetique_realisee = row["id_zone_cynegetique_realisee"]
            nom_parc_lieu_dit = row["lieu_tir_txt"]
            # nom du lieu dit d'origine en majuscules pour les commentaires
            nom_save_lieu_dit = (
                row["save_lieu_dit"].upper()
                if isinstance(row["save_lieu_dit"], str)
                else row["save_lieu_dit"]
            )
            if pd.isna(nom_parc_lieu_dit):  # pas de lieu dit saisi dans geochasse.
                continue
            numero_bracelet = row["numero_bracelet"]

            # 1. nom exact dans la même ZC
            df_result = _grp(
                _groups_zc, (id_zone_cynegetique_realisee, nom_parc_lieu_dit)
            )
            if df_result.shape[0] >= 1:
                synonyme = df_result.iloc[0]
                affecter(index, synonyme)
                if df_result.shape[0] == 1:
                    dict_bilan_synonymes[numero_bracelet] = entree_bilan(
                        row, "EXACTE_ZC", "Nom exact retrouvé dans la ZC", synonyme
                    )
                else:
                    # plusieurs correspondances exactes : on prend la première et on le signale
                    liste_nom_lieu_tir_synonyme = df_result["nom_lieu_tir"].tolist()
                    df.at[
                        index, "commentaires_erreurs"
                    ] += f"{df_result.shape[0]} correspondances trouvées dans les lieux de tir synonymes pour le lieu dit {nom_save_lieu_dit} dans la ZC: {liste_nom_lieu_tir_synonyme}"
                    dict_bilan_synonymes[numero_bracelet] = entree_bilan(
                        row,
                        "EXACTE_MULTIPLE_ZC",
                        "Plusieurs noms exacts retrouvés dans la ZC",
                        synonyme,
                    )
                continue

            # 2. nom similaire dans la même ZC
            synonyme, meilleur_match = meilleur_similaire(
                _groups_zc,
                _names_by_zc,
                id_zone_cynegetique_realisee,
                nom_parc_lieu_dit,
            )
            if synonyme is not None and synonyme is not False:
                affecter(index, synonyme)
                df.at[
                    index, "commentaires_erreurs"
                ] += f"Lieu tir {nom_save_lieu_dit}: nom similaire trouvé dans la même ZC: {meilleur_match} "
                dict_bilan_synonymes[numero_bracelet] = entree_bilan(
                    row, "SIMILAIRE_ZC", "Nom similaire retrouvé dans la ZC", synonyme
                )
                continue

            # 3. aucune correspondance : erreur de saisie ou lieu dit absent de la bdd (à ajouter comme synonyme)
            df.at[
                index, "commentaires_erreurs"
            ] += f"Aucun lieu de tir synonyme trouvé pour le lieu dit {nom_save_lieu_dit} dans la ZC. "
            dict_bilan_synonymes[numero_bracelet] = entree_bilan(
                row, "AUCUNE", "Aucun nom similaire retrouvé"
            )

        df["lieu_tir_txt"] = df["save_lieu_dit"].copy()

        return df, apiResponse, dict_bilan_synonymes

    except Exception as e:
        user_message = "Une erreur est survenue lors de la recherche des lieux dits de tir de réalisation. Veuillez vérifier que le fichier est au bon format et réessayer."
        apiResponse.add_log(message=user_message, type_log="ERROR")
        apiResponse.add_error(system_error=str(e), user_message=user_message)
        return pd.DataFrame(), apiResponse, {}


def etape_save_bilan_synonymes_in_csv(dict_bilan_synonymes, apiResponse):
    """Sauvegarde du bilan synonymes dans un fichier csv. Pour garder ces informations
    en vue de créer plus tard une meilleure géolocalisation.
    Si la procédure plante on ne créé pas d'erreur qui stop l'importation."""

    try:
        if dict_bilan_synonymes:
            df_bilan_synonymes = pd.DataFrame.from_dict(
                dict_bilan_synonymes, orient="index"
            )
            nom_fichier = f"{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')}_bilan_synonymes_import_geochasse.csv"
            chemin_fichier = Path(DOSSIER_ARCHIVES_LIEUX_DITS) / nom_fichier
            df_bilan_synonymes.to_csv(chemin_fichier, index=False)
            # apiResponse.add_log(message=f"Bilan des synonymes sauvegardé: {nom_fichier}", type_log="INFO")

        return apiResponse

    except Exception as e:
        user_message = (
            "Une erreur est survenue lors de la sauvegarde du bilan des synonymes."
        )
        apiResponse.add_log(message=user_message, type_log="ERROR")
        return apiResponse


def etape__remplissage_commentaires(df, apiResponse):
    """On ajoute aux commentaires des lignes valides les commentaires d'erreurs."""
    try:
        # équivalent vectorisé de la boucle iterrows d'origine :
        # pour chaque ligne valide, commentaire = "<commentaire> \n <commentaires_erreurs>"
        mask = (df["valide"] == True) & df["commentaires_erreurs"].notna()
        commentaire_base = (
            df["commentaire"].where(df["commentaire"].notna(), "").astype(str)
        )
        nouveau = commentaire_base + " \n " + df["commentaires_erreurs"].astype(str)
        df["commentaire"] = df["commentaire"].mask(mask, nouveau)
        return df, apiResponse
    except Exception as e:
        user_message = f"Une erreur est survenue lors du remplissage des commentaires d'erreurs. {e}"
        apiResponse.add_log(message=user_message, type_log="ERROR")
        apiResponse.add_error(system_error=str(e), user_message=user_message)
        return pd.DataFrame(), apiResponse


def etape__insert_new_realisations(df, apiResponse):
    """Vérifie la validité de chaque ligne avant de les insérer dans la base de données. On enregistre en bdd les lignes valides.
    Les lignes invalides sont retournées dans un dataframe pour être corrigé par l'utilisateur.
    """
    with app.app_context():
        df_insert = df.loc[
            ((df["id_realisation"].isna()) & (df["valide"] == True))
        ].copy()
        nb_inserts = df_insert.shape[0]
        nb_total_inserts = df.loc[df["id_realisation"].isna()].shape[0]
        nb_erreurs = nb_total_inserts - nb_inserts
        # sauvegarde des lignes qui on été écartées durant les test faient en amont.
        df_insert_erreurs = df.loc[
            ((df["id_realisation"].isna()) & (df["valide"] == False))
        ].copy()

        df_insert = df_insert.replace({np.nan: None})

        if nb_inserts > 0:  # il existe des données à insérer dans la base de données

            schema = TRealisationsChasseSchema()
            lignes_valides = []  # celles qui seront enregistrées.

            # 1. Validation ligne par ligne
            for index, row in df_insert.iterrows():
                data = row.to_dict()
                data = json.loads(
                    json.dumps(data, default=str)
                )  # Convertit les NaN en null et les dates en string pour que ce soit compatible avec Marshmallow

                try:
                    instance = schema.load(data)
                    lignes_valides.append(instance)
                    # ligne valide, elle est ajoutée.

                except ValidationError as e:
                    df_insert.at[
                        index, "commentaires_erreurs"
                    ] += f"Erreur de validation INSERT: {e.messages}. "
                    df_insert.at[index, "valide"] = False
                    # ligne invalide, on ajoute le code erreur dans les commentaires.

            # 2. Insertion des lignes valides
            if lignes_valides:
                DB.session.add_all(lignes_valides)
                DB.session.commit()
                apiResponse.add_log(
                    message=f"{len(lignes_valides)} lignes insérées avec succès.",
                    type_log="INFO",
                )
            else:
                apiResponse.add_log(message="0 ligne insérée. ", type_log="INFO")

            # 3. DataFrame des lignes invalides. Seulement celles qui viennent d'être mise à False.
            df_invalides = df_insert.loc[(df_insert["valide"] == False)].copy()

            if df_invalides.shape[0] > 0:
                # Si des erreurs de validation ont été trouvées, on les ajoute au dataframe des erreurs d'insertion.
                df_insert_erreurs = pd.concat(
                    [df_insert_erreurs, df_invalides], ignore_index=True
                )
                apiResponse.add_log(
                    message=f" {df_invalides.shape[0]} lignes invalides.",
                    type_log="ERROR",
                )

        else:
            apiResponse.add_log(
                message="0 nouvelle réalisation à insérer.", type_log="INFO"
            )

        if nb_erreurs > 0:
            apiResponse.add_log(
                message=f" {nb_erreurs} erreur(s) dans le csv pour l'insertion",
                type_log="ERROR",
            )
        else:
            apiResponse.add_log(
                message="Aucune erreur dans le csv pour l'insertion", type_log="INFO"
            )

        return apiResponse, df_insert_erreurs


def etape__update_realisations(df, apiResponse):
    try:
        # on crée une liste de dicts à partir du dataframe en ne gardant que les colonnes qui nous intéressent pour créer les objets à ajouter à la base de données.

        df_update = df.loc[
            ((df["id_realisation"].notna()) & (df["valide"] == True))
        ].copy()
        df_update.set_index("id_realisation", inplace=True)

        df_erreurs_update = df.loc[
            ((df["id_realisation"].notna()) & (df["valide"] == False))
        ].copy()

        # pour afficher dans les log nb_réussi / nb_total mis à jour
        nb_updates = df_update.shape[0]
        nb_total_updates = df.loc[df["id_realisation"].notna()].shape[0]
        nb_erreurs = nb_total_updates - nb_updates
        liste_id_erreurs = []

        if nb_updates > 0:
            # meta_create_date est exclue : la renvoyer (même à None) la ferait
            # réécrire par le trigger fct_trg_meta_dates_change
            df_update = df_update[
                [c for c in COLUMNS_REALISATION if c != "meta_create_date"]
            ].copy()
            df_update = df_update.replace({np.nan: None})

            list_id_realisations = df_update.index.tolist()

            with app.app_context():
                # 1. Récupérer toutes les instances
                instances = (
                    DB.session.execute(
                        select(TRealisationsChasse).where(
                            TRealisationsChasse.id_realisation.in_(list_id_realisations)
                        )
                    )
                    .scalars()
                    .all()
                )

                # 2. Indexer par ID
                instances_by_id = {inst.id_realisation: inst for inst in instances}

                # 3. Boucle de mise à jour
                schema = TRealisationsChasseSchema()

                for index_realisation, row in df_update.iterrows():
                    data = row.to_dict()
                    # reconvertis certaines valeurs en string pour s'adapter à marshmallow
                    data = json.loads(json.dumps(data, default=str))
                    id_real = index_realisation

                    instance = instances_by_id.get(id_real)
                    if not instance:
                        message_erreur = (
                            f"ID de réalisation {id_real} non trouvé. Ignoré."
                        )
                        apiResponse.add_log(message=message_erreur, type_log="ERROR")
                        liste_id_erreurs.append(id_real)
                        continue

                    try:
                        schema.load(data, instance=instance, partial=True)
                    except ValidationError as e:
                        apiResponse.add_log(
                            message=f"Erreur de validation UPDATE: id_realisation={id_real} => {e.messages}",
                            type_log="ERROR",
                        )
                        liste_id_erreurs.append(id_real)
                        df_update.at[
                            index_realisation, "commentaires_erreurs"
                        ] += f"Erreur de validation UPDATE: {e.messages}. "
                        df_update.at[index_realisation, "valide"] = False

                # 4. Commit dans le même contexte
                DB.session.commit()

        apiResponse.add_log(
            message=f"{nb_updates} réalisations mises à jour avec succès.",
            type_log="INFO",
        )
        if nb_erreurs > 0:
            apiResponse.add_log(
                message=f"{nb_erreurs} erreur(s) venant du csv", type_log="ERROR"
            )
        else:
            apiResponse.add_log(
                message="Aucune erreur venant du csv pour la mise à jour",
                type_log="INFO",
            )

        if len(liste_id_erreurs) > 0:
            apiResponse.add_log(
                message=f" {len(liste_id_erreurs)} bug(s) de validation en BDD par marshmallow",
                type_log="ERROR",
            )
            df_erreurs_validation = df_update.loc[df_update["valide"] == False].copy()
            df_erreurs_update = pd.concat(
                [df_erreurs_update, df_erreurs_validation], ignore_index=True
            )

        return apiResponse, df_erreurs_update

    except Exception as e:
        user_message = "Une erreur lors de la mise à jour de réalisations dans la BDD."
        apiResponse.add_error(system_error=str(e), user_message=user_message)
        apiResponse.add_log(message=user_message, type_log="ERROR")
        return apiResponse, pd.DataFrame()


def _ecrire_rapport(df_original, commentaires, suffixe):
    """Écrit dans DOSSIER_RAPPORTS les lignes du csv d'origine présentes dans commentaires
    (série commentaires_erreurs indexée par id_geochasse), avec ce commentaire en dernière colonne.
    Retourne le nom du fichier, sous la forme AAAA-MM-JJ_HH-MM-SS_<suffixe>.csv"""
    # on sort le numéro de bracelet de l'index pour le remplacer par id_geochasse
    df_origin = df_original.copy()
    df_origin["numero"] = df_origin.index
    df_origin.set_index("id_geochasse", inplace=True)
    # on ne garde que les lignes concernées
    df_origin = df_origin.join(commentaires, how="inner")

    nom_fichier = f"{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')}_{suffixe}.csv"
    df_origin.to_csv(Path(DOSSIER_RAPPORTS) / nom_fichier, index=False)
    return nom_fichier


def etape__creation_dataframe_erreurs(
    df_original, df_insert_erreurs, df_update_erreurs, apiResponse
):
    df_erreurs = df_insert_erreurs
    try:
        if df_update_erreurs.shape[0] > 0:
            df_erreurs = pd.concat(
                [df_insert_erreurs, df_update_erreurs], ignore_index=True
            )

        if df_erreurs.shape[0] > 0:  # si il existe des erreurs
            df_erreurs = df_erreurs.set_index("id_geochasse")["commentaires_erreurs"]
            nom_fichier = _ecrire_rapport(
                df_original, df_erreurs, "erreurs_import_geochasse"
            )
            # type_log FILE permettra d'indiquer au frontend que c'est le nom d'un fichier à télécharger
            apiResponse.add_log(message=f"{nom_fichier}", type_log="FILE")

        return df_erreurs, apiResponse

    except Exception as e:
        user_message = f"Une erreur est survenue lors de la création du rapport CSV des erreurs. {e}"
        apiResponse.add_log(message=user_message, type_log="ERROR")
        apiResponse.add_error(system_error=str(e), user_message=user_message)
        return df_erreurs, apiResponse


def etape__creation_csv_a_verifier(df, df_original, apiResponse):
    df_verif = df.loc[df["a_verifier"] == True]
    try:
        if df_verif.shape[0] > 0:  # si il existe des données aberrantes
            df_verif = df_verif.set_index("id_geochasse")["commentaires_erreurs"]
            nom_fichier = _ecrire_rapport(df_original, df_verif, "a_verifier")
            apiResponse.add_log(
                message=f"{df_verif.shape[0]} lignes avec des données aberrantes: à vérifier",
                type_log="WARNING",
            )
            # type_log FILE permettra d'indiquer au frontend que c'est le nom d'un fichier à télécharger
            apiResponse.add_log(message=f"{nom_fichier}", type_log="FILE")

        return df_verif, apiResponse
    except Exception as e:
        user_message = f"Une erreur est survenue lors de la création du rapport CSV des erreurs. {e}"
        apiResponse.add_log(message=user_message, type_log="ERROR")
        apiResponse.add_error(system_error=str(e), user_message=user_message)
        return df_verif, apiResponse


################################################################################################
####################      FONCTION PRINCIPALE DE TRAITEMENT DE L'IMPORT CSV     ################
################################################################################################


def traitement_import_realisation_chasse(
    path_csv,
    id_saison,
    update,
    id_role=None,
    nom_complet=None,
    progress_callback=None,
):
    """Fonction principale de traitement de l'import csv.
    Retourne un objet ApiResponse avec les messages, le journal de l'opération et les données à retourner à l'utilisateur.

    path_csv : chemin du fichier CSV sur disque, ou objet fichier, ou None
               (dans ce dernier cas on lit request.files["file"] — contexte requête).
    id_role / nom_complet : utilisateur à l'origine de l'import (obligatoire hors
               contexte de requête).
    progress_callback : appelé avec (apiResponse, etape_label, num, total) après
               chaque étape pour permettre à l'appelant de persister l'avancement
               (thread de fond + polling).
    """
    if update == "true":
        update = True
    elif update == "false":
        update = False

    _TOTAL_ETAPES = 10
    _compteur = {"n": 0}

    def _progress(api, label=""):
        _compteur["n"] += 1
        if progress_callback is not None:
            try:
                progress_callback(api, label, _compteur["n"], _TOTAL_ETAPES)
            except Exception:
                pass

    apiResponse = initialisation_apiResponse(id_role=id_role, nom_complet=nom_complet)
    if apiResponse.success == False:
        apiResponse.print_all()
        _progress(apiResponse, "Authentification")
        return apiResponse

    df, apiResponse = etape__récuperation_csv(apiResponse, source=path_csv)
    _progress(apiResponse, "Lecture du fichier CSV")
    if apiResponse.success == False:
        return apiResponse
    df, apiResponse = etape__clean_csv(df, apiResponse)
    df_original = (
        df.copy()
    )  # on garde une copie du dataframe original pour pouvoir faire des comparaisons à l'avenir si besoin et pour garder une trace de ce qui a été saisi dans le csv.
    _progress(apiResponse, "Nettoyage des données")
    if apiResponse.success == False:
        return apiResponse
    df, apiResponse = etape__recupération_attributions(
        df, id_saison, update, apiResponse
    )
    _progress(apiResponse, "Récupération des attributions")
    if apiResponse.success == False:
        return apiResponse
    df, apiResponse = etape__verification_donnees_geochasse(df, apiResponse)
    _progress(apiResponse, "Vérification de la cohérence des données")
    if apiResponse.success == False:
        return apiResponse
    df, apiResponse = etape__ajout_colonnes_vides_pour_bdd(df, apiResponse, update)
    _progress(apiResponse, "Préparation des données")
    if apiResponse.success == False:
        return apiResponse
    df, apiResponse = etape__integration_communes_dans_df(df, apiResponse)
    _progress(apiResponse, "Rapprochement des communes")
    if apiResponse.success == False:
        return apiResponse
    # dict_bilan_synonymes contiendra un bilan des correspondances trouvées entre les lieux dits saisis dans le csv et les lieux de tir synonymes de la bdd
    df, apiResponse, dict_bilan_synonymes = (
        etape__recherche_lieux_dits_de_tir_de_realisation(df, apiResponse)
    )
    _progress(apiResponse, "Recherche des lieux de tir")
    if apiResponse.success == False:
        return apiResponse

    apiResponse = etape_save_bilan_synonymes_in_csv(dict_bilan_synonymes, apiResponse)

    df, apiResponse = etape__remplissage_commentaires(df, apiResponse)
    _progress(apiResponse, "Consolidation des commentaires")
    if apiResponse.success == False:
        return apiResponse

    # insertion puis mise à jour, on fait les 2 avant de vérifier si il y a des erreurs.
    apiResponse, df_erreurs_insert = etape__insert_new_realisations(df, apiResponse)
    _progress(apiResponse, "Insertion des nouvelles réalisations")
    if update == True:
        apiResponse, df_erreurs_update = etape__update_realisations(df, apiResponse)
        _progress(apiResponse, "Mise à jour des réalisations existantes")
    else:
        df_erreurs_update = (
            pd.DataFrame()
        )  # si ce n'est pas une mise à jour, il n'y a pas d'erreurs de mise à jour.

    if apiResponse.success == False:
        return apiResponse

    _, apiResponse = etape__creation_dataframe_erreurs(
        df_original, df_erreurs_insert, df_erreurs_update, apiResponse
    )

    _, apiResponse = etape__creation_csv_a_verifier(df, df_original, apiResponse)

    # enregiste les logs dans un fichier
    apiResponse.write_in_log_file()
    _progress(apiResponse, "Génération des rapports")

    # apiResponse.print_all() # pour le débug
    # print (df)

    return apiResponse
