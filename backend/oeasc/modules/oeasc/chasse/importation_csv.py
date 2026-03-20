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

import math
import numpy as np
import pandas as pd
import json
import rapidfuzz as rpfz
from pyproj import Transformer

from marshmallow.exceptions import ValidationError

from sqlalchemy import func, select
from flask import request, current_app, session

from oeasc.utils.apiResponse import ApiResponse

from oeasc.ref_geo.models import BibAreasType, LAreas
from oeasc.modules.oeasc.chasse.models import (
    TAttributions,
    TZoneIndicatives,
    TRealisationsChasse,
    TLieuTirSynonymes,
)
from oeasc.modules.oeasc.chasse.schema import (
    TAttributionsSchema,
    TRealisationsChasseSchema,
    TZoneIndicativesSchema,
    TLieuTirSynonymesSchema,
)

config = current_app.config
DB = config["DB"]


# from pypnnomenclature.models import TNomenclatures, BibNomenclaturesTypes
# from pypnnomenclature.schemas import NomenclatureSchema, BibNomenclaturesTypesSchema
#####################################################################################################
####################              VARIABLES GLOBALES                            #####################
#####################################################################################################

# Initialisation de l'ApiResponse pour stocker les messages, le journal de l'opération et les données à retourner à l'utilisateur.
apiResponse = ApiResponse()

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

TAILLE_MINIMUM_DAGUES ={
    "CERF": {"ADULTE": 10, "SUBADULTE": 10, "INDÉTERMINÉ": 5, "JEUNE": 2, "FAON": 2},
    "CHEVREUIL": {"ADULTE": 10, "SUBADULTE": 1, "INDÉTERMINÉ": 1, "JEUNE": 1},
}
TAILLE_MAXIMUM_DAGUES ={
    "CERF": {"ADULTE": 650, "SUBADULTE": 500, "INDÉTERMINÉ": 600, "JEUNE": 200, "FAON": 200},
    "CHEVREUIL": {"ADULTE": 200, "SUBADULTE": 150, "INDÉTERMINÉ": 200, "JEUNE": 100},
}

POIDS_VIDE_MINIMUM = {"CERF": {"ADULTE": 40, "SUBADULTE": 20, "INDÉTERMINÉ": 18, "JEUNE": 18, "FAON": 18},
                "CHEVREUIL": {"ADULTE": 7, "SUBADULTE": 7, "INDÉTERMINÉ": 7, "JEUNE": 7},
                "MOUFLON": {"ADULTE": 18, "SUBADULTE": 10, "INDÉTERMINÉ": 5, "JEUNE": 5}
                }
POIDS_VIDE_MAXIMUM = {"CERF": {"ADULTE": 250, "SUBADULTE": 150, "INDÉTERMINÉ": 300, "JEUNE": 120, "FAON": 120},
                "CHEVREUIL": {"ADULTE": 70, "SUBADULTE": 50, "INDÉTERMINÉ": 50, "JEUNE": 26},
                "MOUFLON": {"ADULTE": 55, "SUBADULTE": 30, "INDÉTERMINÉ": 35, "JEUNE": 35}
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
ERREUR_AGE = { "1" : "ADULTE"}


# On définit les id de nomenclatures et le lien entre les codes de bracelet et les especes en dur
# Si il y a des changements majeurs dans la bdd , il faudra peut être les récupérer dynamiquement
LISTE_ESPECE = {"CEFF": ["CERF", ["FEMELLE","INDÉTERMINÉ", "MALE"], ["ADULTE", "SUBADULTE", "INDÉTERMINÉ", "FAON"]],
                "CEFFD": ["CERF", ["FEMELLE", "INDÉTERMINÉ", "MALE"], ["ADULTE", "SUBADULTE", "FAON"]],
                "CEM": ["CERF", ["MALE"], ["ADULTE", "SUBADULTE", "INDÉTERMINÉ", "FAON"]],
                "CEMD": ["CERF", ["MALE"], ["JEUNE"]],

                "MOF": ["MOUFLON", ["FEMELLE"], ["ADULTE"]],
                "MOM": ["MOUFLON", ["MALE"], ["ADULTE"]],
                "MOM1": ["MOUFLON", ["MALE"], ["SUBADULTE"]],
                "MOI": ["MOUFLON", ["INDÉTERMINÉ"], ["JEUNE"]],
                "MOIJ": ["MOUFLON", ["FEMELLE", "MALE"], ["JEUNE"]],
                "CHI": ["CHEVREUIL", ["MALE", "INDÉTERMINÉ", "FEMELLE"], ["ADULTE", "SUBADULTE", "INDÉTERMINÉ", "JEUNE"]],
                }
LISTE_NOMENCLATURE_SEXE = {"FEMELLE": 168, "MALE": 169, "INDÉTERMINÉ": 167}
LISTE_NOMENCLATURE_AGE = {"ADULTE": 3, "SUBADULTE": 6, "INDÉTERMINÉ": 2, "JEUNE": 4, "FAON": 4}
LISTE_NOMENCLATURE_MODE_CHASSE = {"BATTUE": 575, "INDIVIDUEL": 588, "COLLECTIVE": 575, "AFFÛT": 573, "APPROCHE": 574}
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
        "long_dagues_gauche": ["LONG_DAGUE (1)", "LONG_DAGUE G"],
        "long_dagues_droite": ["LONG_DAGUE (2)", "LONG_DAGUE D"],
        "parc_nom_tireur": ["PARC_NOM_TIREUR"],
        "parc_lieu_dit": ["PARC_LIEU_DIT"],
        "parc_lieu_dit2": ["PARC_LIEU_DIT2"]
}


# noms des colonnes de geochasses inutiles. On les supprimera au début du traitement
COLUMNS_INUTILES = ['risque_sanitaire', 'numero_battue', 'ref_battue', 'ref_ug', 'ref_detenteur', 'nom_detenteur', 'ref_equipe',
    'nom_equipe', 'ref_membre', 'insee_commune', 'territoire', 'photos', 'nom_tireur', 'matin/apres_midi', 'tir_plomb',
    'serotheque', 'metatarse', 'long_pattes', 'nb_tetines', 'nb_embryons', 'circonf_corne_G_isard', 'circonf_corne_D_isard',
    'ecart_cornes_isard', 'age_isard', 'long_corne_mouflon', 'diam_corne_mouflon', 'age_mouflon', 
    'nb_cors', 'long_cornes_D_isard', 'hauteur_cornes_isard', 'heure'
    ]

# noms des colonnes de la table realisations_chasse. Utilisé à la toute fin pour faire un clean du dataframe
COLUMNS_REALISATION = [
    'id_attribution', 'id_zone_cynegetique_realisee', 'id_zone_indicative_realisee',
    'id_lieu_tir_synonyme', 'date_exacte', 'date_enreg', 'mortalite_hors_pc', 'id_nomenclature_sexe',
    'id_nomenclature_classe_age', 'poid_entier', 'poid_vide', 'poid_c_f_p', 'long_dagues_droite',
    'long_dagues_gauche', 'long_mandibules_droite', 'long_mandibules_gauche', 'cors_nb', 'cors_commentaires',
    'gestation', 'id_nomenclature_mode_chasse', 'commentaire', 'parcelle_onf', 'poid_indique', 'cors_indetermine',
    'long_mandibule_indetermine', 'id_numerisateur', 'meta_create_date', 'meta_update_date', 'id_nomenclature_categorie',
    'auteur_tir_str', 'auteur_constat_str'] 


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

    # ── Étape 1 : construire un dict inversé {synonyme → nom_souhaité} ──────
    # Un synonyme peut matcher plusieurs clés, on garde la relation directe
    synonymes_vers_nom = {}
    for nom_souhaite, synonymes in columns_name.items():
        for synonyme in synonymes:
            synonymes_vers_nom[synonyme] = nom_souhaite

    tous_les_synonymes = list(synonymes_vers_nom.keys())

    # ── Étape 2 : pour chaque colonne CSV, trouver le meilleur synonyme ─────
    liste_columns_result = []

    for col_csv in colonnes_csv:
        resultat = rpfz.process.extractOne(
            query=col_csv,
            choices=tous_les_synonymes,
            scorer=rpfz.fuzz.WRatio,
            score_cutoff=seuil_similarite,
        )

        if resultat:
            synonyme_trouve, score, _ = resultat
            nom_normalise = synonymes_vers_nom[synonyme_trouve]
            liste_columns_result.append(nom_normalise)
            # print(f"'{col_csv}' → '{synonyme_trouve}' → '{nom_normalise}' (score: {score:.0f})")
        else:
            # Colonne non reconnue : on conserve None pour ne pas la perdre
            liste_columns_result.append(None)
            print(f" '{col_csv}' → non reconnue (score sous le seuil {seuil_similarite})")

    return liste_columns_result

def uniformise_communes(serie):
    """ Retire les accents, les tirets et met en majuscules une série de pandas.
     Utilisée pour comparer des champs texte entre l'import csv et la base de données. """
    serie= serie.str.upper()
    serie = serie.str.replace("-", " ")
    serie = serie.str.replace("É", "E")
    serie = serie.str.replace("Ç", "C")
    serie = serie.str.replace("È", "E")
    serie = serie.str.replace("Ê", "E")
    serie = serie.str.replace("À", "A")
    serie = serie.str.replace(r'\bST\b', 'SAINT', regex=True)
    serie = serie.str.replace(r'\bSTE\b', 'SAINTE', regex=True)
    serie = serie.str.replace(r'\bMT\b', 'MONT', regex=True)
    # retrait du mot 30
    serie = serie.str.replace(r'\s*\b30\b\s*', ' ', regex=True)


    # retrait des mots entres parenthèses
    # serie = serie.str.replace(r'\s*\(.*\)\s*', ' ', regex=True)

    serie = serie.str.replace("   ", " ")
    # retrait des espaces en début et fin de chaîne
    serie = serie.str.strip()
    
    return serie

def uniformise_lieu_dit(serie):
    """ Retire les accents, les tirets et met en majuscules une série de pandas.
     Utilisée pour comparer des champs texte entre l'import csv et la base de données. """
    serie= serie.str.upper()
    serie = serie.str.replace("-", " ")
    serie = serie.str.replace("É", "E")
    serie = serie.str.replace("È", "E")
    serie = serie.str.replace("Ê", "E")
    serie = serie.str.replace("À", "A")
    # retrait des mots ZIC
    serie = serie.str.replace(r'\s*ZIC\s*', ' ', regex=True)
    # retrait des mots BS
    serie = serie.str.replace(r'\s*BS\s*', ' ', regex=True)
    # retrait des mots TCA
    serie = serie.str.replace(r'\s*TCA\s*', ' ', regex=True)
    # retrait des mots ZT
    serie = serie.str.replace(r'\s*ZT\s*', ' ', regex=True)
    serie = serie.str.replace(r'\bST\b', 'SAINT', regex=True)
    serie = serie.str.replace(r'\bSTE\b', 'SAINTE', regex=True)
    serie = serie.str.replace(r'\bMT\b', 'MONT', regex=True)

    # retrait des mots entres parenthèses
    serie = serie.str.replace(r'\s*\(.*\)\s*', ' ', regex=True)

    # retrait des mot "L'"
    serie = serie.str.replace(r"\bL'", " ", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()
    # retrait des mot "D'"
    serie = serie.str.replace(r"\bD'", " ", regex=True).str.replace(r"\s+", " ", regex=True).str.strip()
    # retrait des mot "LA"
    serie = serie.str.replace(r'\s*\bLA\b\s*', ' ', regex=True)
    # retrait des mot "LES"
    serie = serie.str.replace(r'\s*\bLES\b\s*', ' ', regex=True)
    # retrait des mot "LE"
    serie = serie.str.replace(r'\s*\bLE\b\s*', ' ', regex=True)


    # retrait des  mot en chiffres romains
    serie = serie.str.replace(r'\s*\b[IVXLCDM]+\b\s*', ' ', regex=True)

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
        'FRAISSINET DE FOURQUE': 'FRAISSINET DE FOURQUES',
        'PONT DE MONTVERT SUD MONT LOZERE': 'PONT DE MONTVERT SUD MONT LOZERE',
        'LE PONT DE MONTVERT SUD MONT LOZORE': 'PONT DE MONTVERT SUD MONT LOZORE',
        'LE PONT DE MONTVERT': 'PONT DE MONTVERT SUD MONT LOZORE',
        'FRAISSINET DE LOZERE': 'PONT DE MONTVERT SUD MONT LOZORE',
        'PONT DE MONTVERT': 'PONT DE MONTVERT SUD MONT LOZORE',
        'QUEZAC': 'GORGES DU TARN CAUSSES',
        'FLORAC': 'FLORAC TROIS RIVIERES',
        'BEDOUES': 'BEDOUES COCURES',
        'VAL D AIGOUAL': "VAL D'AIGOUAL",
        'SAINT ANDRE DE CAPCEZE': 'SAINT ANDRE CAPCEZE',
        'TREVES': 'TRÈVES',
    }
    serie_commune = serie_commune.replace(corrections)

    return serie_commune

def clean_colonne_str(serie):
    """ Retire les espaces en début et fin de chaîne et les espaces multiples d'une série de pandas.
    """
    mask_null = serie.isna()
    
    # Convertir en string
    serie = serie.astype(str)
    # Remplacer les espaces multiples par un seul espace
    serie = serie.str.replace(r'\s+', ' ', regex=True)
    serie = serie.str.strip()

    # Remettre NaN aux positions originalement nulles
    serie = serie.where(~mask_null, other=None)
    return serie

def check_caracteres_invisibles(df):
    """Remplace par None toutes les valeurs du dataframe qui ne contiennent que des caractères invisibles (espaces, tabulations, retours à la ligne, etc.)."""
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(lambda x: None if isinstance(x, str) and x.strip() == '' else x)
    return df

def uniformise_date(serie):
    """Repère si la date est sous un format indiqué dans "formats" et les uniformise au format aaaa-mm-jj.
      Si une date ne peut pas être convertie, elle est remplacée par None.
      Fonction créée car geochasse à changé ses formats de date à plusieurs reprises."""
    formats = ["%d/%m/%Y", "%d-%m-%Y", "%d.%m.%Y", "%Y-%m-%d", "%Y/%m/%d", "%Y.%m.%d",
               "%d/%m/%Y %H:%M", "%d-%m-%Y %H:%M", "%d.%m.%Y %H:%M", "%Y-%m-%d %H:%M", "%Y/%m/%d %H:%M", "%Y.%m.%d %H:%M",
               ]
    for fmt in formats:
        try:
            return pd.to_datetime(serie, format=fmt).dt.strftime("%Y-%m-%d")
        except (ValueError, TypeError):
            continue
    print(f"Impossible de convertir la date '{serie}' avec les formats connus.")
    return None

def poid_vide_cerf(poids_entier_in):
    """
    Calcule le poids vide d'un cerf (CF) à partir de son poids entier.

    Args:
        poids_entier_in (float): Poids entier du cerf

    Returns:
        int: Poids vide calculé

    Raises:
        ValueError: Si le poids entier n'est pas fourni
    """
    try:
        if poids_entier_in is None:
            return None
        pe_exp = -0.3948
        pe_puis = 1.0247
        result = round((math.exp(pe_exp) * (poids_entier_in ** pe_puis)), 2)
        return result
    except Exception:
        return None

def poid_vide_chevreuil(poids_entier_in):
    """
    Calcule le poids vide d'un chevreuil (CH) à partir de son poids entier.

    Args:
        poids_entier_in (float): Poids entier du chevreuil

    Returns:
        int: Poids vide calculé

    Raises:
        ValueError: Si le poids entier n'est pas fourni
    """
    try:
        if poids_entier_in is None:
            return None

        pe_exp = -0.3572
        pe_puis = 1.023
        result = round((math.exp(pe_exp) * (poids_entier_in ** pe_puis)), 2)
        return result
    except Exception:
        return None

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
    cleaned = serie.astype(str).str.replace(",", ".", regex=False).str.replace(" ", "", regex=False).str.strip()

    # traiter les chaînes vides / littérales 'nan' / 'None' comme NA
    cleaned = cleaned.replace({'': pd.NA, 'nan': pd.NA, 'None': pd.NA})

    # convertir en numérique (coerce transforme les valeurs invalides en NaN)
    numeric = pd.to_numeric(cleaned, errors='coerce')

    # convertir en int par troncature (comme int(float(x))) et garder None pour les NaN
    result = numeric.apply(lambda x: int(x) if pd.notna(x) else None)

    # remettre None aux positions initialement NA
    result = result.where(~mask_na, other=None)

    return result


##################################################################################
################ FONCTIONS ETAPES DE TRAITEMENT DE L'IMPORT CSV  ################
##################################################################################

def etape__récuperation_csv(apiResponse):
    """Check si les informations nécessaires à l'import sont présentes et récupère le csv exporté par geochasse.
     retourne un dataframe pandas et une ApiResponse avec les messages d'erreur et le journal de l'opération.
     Si une erreur est détectée, le dataframe retourné est vide et la ApiResponse contient les messages d'erreur et le journal de l'opération.
    Si aucune erreur n'est détectée, le dataframe retourné contient les données du csv et la ApiResponse contient le journal de l'opération.
    """

    try:
        df = pd.DataFrame()

        if "file" not in request.files:
            apiResponse.add_log(
                "Aucun fichier trouvé dans la requête", type_log="ERROR"
            )
            apiResponse.add_error(
                user_message="Aucun fichier trouvé dans la requête",
                system_error="Aucun fichier trouvé dans la requête",
            )
            return apiResponse

        file = request.files["file"]

        if file.filename == "":
            apiResponse.add_log("Nom de fichier vide", type_log="ERROR")
            apiResponse.add_error(
                user_message="Nom de fichier vide", system_error="Nom de fichier vide"
            )
            return apiResponse

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
        liste_mapping = get_columns_mapping(colonnes_csv=colonnes_csv, columns_name=COLUMNS_NAME, seuil_similarite=SCORE_MINIMUM_RAPIDFUZZ)


        df = pd.read_csv(
            file,
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
            return apiResponse

        return df, apiResponse
    except Exception as e:
        user_message = "Une erreur est survenue lors de la récupération du fichier CSV. Veuillez vérifier que le fichier est au bon format et réessayer."
        apiResponse.add_error(system_error=str(e), user_message=user_message)
        apiResponse.add_log(message=user_message, type_log="ERROR")
        return pd.DataFrame(), apiResponse

#################################################################################
#################################################################################



def initialisation_apiResponse():
    """Initialise une ApiResponse pour stocker les messages d'erreur et de succès, le journal de l'opération et les données à retourner à l'utilisateur."""
    apiResponse = ApiResponse(log_file="import_geochasse.log")

    if "current_user" not in session:
        # revois les droit pour id_role
        apiResponse.add_log(
            "Tentative d'importation: Utilisateur non connecté. Veuillez vous connecter pour continuer.",
            type_log="ERROR",
            with_timestamp=True,
        )
        apiResponse.success = False
        apiResponse.status_code = 401
        apiResponse.add_error(
            user_message="Tentative d'importation: Utilisateur non connecté. Veuillez vous connecter pour continuer.",
            system_error="Tentative d'importation: Utilisateur non connecté. Veuillez vous connecter pour continuer.",
        )
        return apiResponse
    else:
        id_role = session.get("current_user")["id_role"]
        # print(f"id_role from session: {id_role}")
        nom_complet = session.get("current_user")["nom_complet"]
        # print(f"nom_complet from session: {nom_complet}")
        if (id_role is None) or (nom_complet is None):
            apiResponse.add_log(
                "Tentative d'importation: Informations utilisateur manquantes. Veuillez vous reconnecter.",
                type_log="ERROR",
                with_timestamp=True,
            )
            apiResponse.success = False
            apiResponse.status_code = 401
            apiResponse.add_error(
                user_message="Tentative d'importation: Informations utilisateur manquantes. Veuillez vous reconnecter.",
                system_error="Tentative d'importation: Informations utilisateur manquantes. Veuillez vous reconnecter.",
            )
            return apiResponse
        else:
            apiResponse.id_role = session["current_user"]["id_role"]
            apiResponse.nom_complet = session["current_user"]["nom_complet"]
            apiResponse.return_journal = True
            date_time = pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")
            apiResponse.add_log(
                f"Utilisateur {apiResponse.nom_complet} (id_role: {apiResponse.id_role}) a lancé l'import des données de chasse depuis Geochasse à {date_time}.",
                with_timestamp=True,
            )

    return apiResponse


def etape__clean_csv(df, apiResponse):
    # """Nettoie le dataframe en supprimant les colonnes inutiles et en renommant les colonnes avec les bons noms."""
    # try:
        
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
        # renommage des colonnes avec les bons noms
        df_trie = df_trie.rename(columns=ERREUR_NOMS_COLONNES_GEOCHASSE)

        df_trie = check_caracteres_invisibles(df_trie)

        # si dans la modification du csv un caractère invisible s'est glissé on le corrige.
        df_trie["auteur_tir_str"] = clean_colonne_str(df_trie["auteur_tir_str"])
        df_trie["lieu_tir_txt"] = clean_colonne_str(df_trie["lieu_tir_txt"])
        df_trie["commune"] = clean_colonne_str(df_trie["commune"])
        df_trie["commentaire"] = clean_colonne_str(df_trie["commentaire"])
        df_trie["espece"] = clean_colonne_str(df_trie["espece"])
        df_trie['espece'] = df_trie['espece'].str.upper()
        df_trie["age"] = clean_colonne_str(df_trie["age"])
        df_trie["age"] = df_trie["age"].str.upper()
        df_trie["age"] = df_trie["age"].replace(ERREUR_AGE) # Surtout pour le cas des mouflons
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
        
        df_trie["long_mandibules_gauche"] = convert_str_to_float(df_trie["long_mandibules_gauche"])
        df_trie["long_mandibules_droite"] = convert_str_to_float(df_trie["long_mandibules_droite"])

        df_trie["long_dagues_gauche"] = convert_str_to_float(df_trie["long_dagues_gauche"])
        df_trie["long_dagues_droite"] = convert_str_to_float(df_trie["long_dagues_droite"])

        df_trie["date"] = uniformise_date(df_trie["date"])
        df_trie["date_saisie"] = uniformise_date(df_trie["date_saisie"])

        df_trie["commune"] = clean_colonne_str(df_trie["commune"])
        df_trie["lieu_dit"] = clean_colonne_str(df_trie["lieu_dit"])
        df_trie["departement"] = clean_colonne_str(df_trie["departement"])
        df_trie["parc_lieu_dit2"] = clean_colonne_str(df_trie["parc_lieu_dit2"])

        df_trie['id_geochasse'] = convert_to_int(df_trie['id_geochasse'])
        df_trie['origine_bracelet'] = convert_to_int(df_trie['origine_bracelet'])


        return df_trie, apiResponse
    # except Exception as e:
    #     user_message = "Une erreur est survenue lors du nettoyage du fichier CSV. Veuillez vérifier que le fichier est au bon format et réessayer."
    #     apiResponse.add_error(system_error=str(e), user_message=user_message)
    #     apiResponse.add_log(message=user_message, type_log="ERROR")
    #     return pd.DataFrame(), apiResponse


def etape__recupération_attributions(df, id_saison, update, apiResponse):
    """
    Vérifie que l'id_saison est renseigné et valide, puis récupère les attributions de la saison en cours.
    Retourne un dataframe qui contient le csv geochasse fusionné avec les attributions.
    L'index du dataframe retourné est le numéro de bracelet.
    update: bool qui indique si on doit récupérer toutes les attributions de la saison (update=True) ou seulement celles qui n'ont pas de réalisations associées (update=False).
    Si une erreur est détectée, le dataframe retourné est vide et la ApiResponse contient les messages d'erreur et le journal de l'opération. Si aucune erreur n'est détectée, le dataframe retourné contient les données des attributions et la ApiResponse contient le journal de l'opération.
    """
    try:
        if id_saison is None:
            apiResponse.add_log(
                "id_saison n'est pas renseigné. Veuillez renseigner un id_saison pour continuer.",
                type_log="ERROR",
            )
            return df, apiResponse

        # on fait une requete à la base de données pour trouver toutes les attributions de la saison id_saison qui n'ont pas de réalisations
        with app.app_context():

            stmt_attributions = select(TAttributions).where(
                    TAttributions.id_saison == id_saison,
                )
            

            attributions_result = DB.session.execute(stmt_attributions).scalars().all()
            attributions_dict = TAttributionsSchema().dump(
                attributions_result, many=True
            )
            df_attributions = pd.json_normalize(attributions_dict)

            # pour comparer les attributions de la bdd avec celles du csv il faut remplacer les espaces par 00
            df_attributions["numero_bracelet"] = df_attributions[
                "numero_bracelet"
            ].str.replace(" ", "00")

            # renommage des colonnes trop longues pour faciliter le travail dessus.
            df_attributions["id_zone_cynegetique_realisee"] = df_attributions[
                "zone_cynegetique_affectee.id_zone_cynegetique"
            ]
            df_attributions["id_zone_indicative_realisee"] = df_attributions[
                "zone_indicative_affectee.id_zone_indicative"
            ]
            df_attributions["id_secteur_realisee"] = df_attributions[
                "zone_cynegetique_affectee.id_secteur"
            ]
            df_attributions["code_type_bracelet"] = df_attributions[
                "type_bracelet.code_type_bracelet"
            ]
            # df_attributions['description_type_bracelet'] = df_attributions['type_bracelet.description_type_bracelet']
            # df_attributions['type_bracelet_id_espece'] = df_attributions['type_bracelet.espece.id_espece']

            # un peu de clean du dataframe pour alléger. On ne garde que les colonnes qui nous intéressent
            df_attributions = df_attributions[
                [
                    "numero_bracelet",
                    "id_attribution",
                    "id_realisation",
                    "id_saison",
                    "saison.date_debut",
                    "saison.date_fin",
                    "id_zone_cynegetique_realisee",
                    "id_zone_indicative_realisee",
                    "id_secteur_realisee",
                    "code_type_bracelet",
                    # 'description_type_bracelet',
                    # 'type_bracelet_id_espece',
                ]
            ]

            # df_attributions.set_index('numero_bracelet', inplace=True)
            df_attributions = df_attributions.reset_index()
            df_attributions.index = df_attributions["numero_bracelet"]


            # fusion de df_trie et df_attributions_non_realisees sur l'index (numero_bracelet)
            # on utilise outer pour pouvoir repérer les bracelets existant dans le csv mais pas dans les attributions de la bdd.
            df_fusion = df.join(df_attributions, how="outer")
            if update == True:
                df_fusion = df_fusion.loc[df_fusion["id_geochasse"].notna()].copy()
            else:
                df_fusion = df_fusion.loc[(df_fusion["id_geochasse"].notna()) & (df_fusion['id_realisation'].isna())].copy()

            return df_fusion, apiResponse

    except Exception as e:
        user_message = "Une erreur lors de la récupération des attributions de la saison. Veuillez vérifier que l'id_saison est correct et réessayer."
        apiResponse.add_log(message=user_message, type_log="ERROR")
        apiResponse.add_error(system_error=str(e), user_message=user_message)
        return pd.DataFrame(), apiResponse


def etape__verification_donnees_geochasse(df, apiResponse):
    """
    Vérifie que les données du csv geochasse sont cohérentes entre elles et avec les données de la base de données.
    ajoute des colonnes "valide" et "commentaires_erreurs" au dataframe pour indiquer si les données sont valides ou non et pour stocker les commentaires d'erreurs. On s'en servira pour faire un rapport final à l'utilisateur.

    """
    try:

        # on peut faire une première validation : vérifier que l'espèce du bracelet correspond à l'espèce du tir
        df["valide"] = True
        df['a_verifier'] = False
        df["commentaires_erreurs"] = ""

        ################################### VERIF DES BRACELETS EXISTANTS ##########################################
        # on vérifie que les bracelets du csv existent dans les attributions de la saison.
        # Met valide à False et ajoute un commentaire d'erreur si un bracelet du csv n'existe pas dans les attributions de la saison.
        idx_erreur = df[df["id_attribution"].isnull()].index
        df.loc[idx_erreur, "valide"] = False
        df.loc[idx_erreur, "commentaires_erreurs"] += "Le numéro de bracelet n'existe pas dans les attributions de la saison. "
        del idx_erreur

        ########################################   TRAITEMENT DE L'ESPÈCE  ############################################
        # on créé id_nomenclature_espece en fonction de la colonne espece pour retrouver la catégorie de l'éspece (FAON, BICHETTE, DAGUET etc..)
        #  L'id correspondant est trouvé dans la table LISTE_NOMENCLATURE_ESPECE.
        df["id_nomenclature_espece"] = df["espece"].map(LISTE_NOMENCLATURE_ESPECE)

        # utiliser le code du bracelet pour retrouver l'espèce théorique depuis la table LISTE_ESPECE
        # Met valide à False et ajoute un commentaire d'erreur si l'espèce du tir ne correspond pas à l'espèce théorique du bracelet
        df["espece_theorique"] = df["code_type_bracelet"].map(
            lambda k: LISTE_ESPECE.get(k)[0] if k in LISTE_ESPECE else None
        )
        idx_erreur = df[
            df["espece"] != df["espece_theorique"]
        ].index
        df.loc[idx_erreur, "valide"] = False
        df.loc[idx_erreur, "commentaires_erreurs"] += "Espèce du tir ne correspond pas à l'espèce du bracelet. "
        df.drop(columns=["espece_theorique"], inplace=True)
        del idx_erreur

        ############################# TRAITEMENT DU SEXE  ############################################
        # verification que le sexe du tir se trouve dans la liste des sexes du code du bracelet dans LISTE_ESPECE.
        #  Met valide à False en commentaire l'erreur
        df["sexe_theorique"] = df["code_type_bracelet"].map(
            lambda k: LISTE_ESPECE.get(k)[1] if k in LISTE_ESPECE else None
        )
        idx_erreur = df[
            ~df.apply(
                lambda row: (
                    row["sexe"] in row["sexe_theorique"]
                    if row["sexe_theorique"] is not None
                    else True
                ),
                axis=1,
            )
        ].index
        df.loc[idx_erreur, "valide"] = False
        df.loc[idx_erreur, "commentaires_erreurs"] += "Sexe du tir ne correspond pas au sexe du bracelet. "
        del idx_erreur

        # Changement de la colonne sexe en id_nomenclature_sexe en fonction de la table LISTE_NOMENCLATURE_SEXE.
        # Met valide à False et ajoute un commentaire d'erreur si le sexe du tir ne correspond à aucun sexe de la nomenclature
        df["id_nomenclature_sexe"] = df["sexe"].map(LISTE_NOMENCLATURE_SEXE)
        idx_erreur = df[df["id_nomenclature_sexe"].isnull()].index
        df.loc[idx_erreur, "valide"] = False
        df.loc[idx_erreur, "commentaires_erreurs"] += "Sexe du tir ne correspond à aucun sexe de la nomenclature. "
        del idx_erreur

        ###########################   TRAITEMENT DE L'ÂGE  ############################################
        # verification que l'âge du tir se trouve dans la liste des âges du code du bracelet dans LISTE_ESPECE.
        #  Met valide à False en commentaire l'erreur

        # pour les mouflons en repère l'age avec le code du code_type_bracelet
        df.loc[df["espece"] == "MOUFLON", "age"] = df.loc[
            (df["espece"] == "MOUFLON"), "code_type_bracelet"
        ].map(lambda k: LISTE_ESPECE.get(k)[2][0] if k in LISTE_ESPECE else None)
        df["age_theorique"] = df["code_type_bracelet"].map(
            lambda k: LISTE_ESPECE.get(k)[2] if k in LISTE_ESPECE else None
        )

        idx_espece_age_incoherente = df[
            ~df.apply(
                lambda row: (
                    row["age"] in row["age_theorique"]
                    if row["age_theorique"] is not None
                    else True
                ),
                axis=1,
            )
        ].index
        df.loc[idx_espece_age_incoherente, "valide"] = False
        df.loc[idx_espece_age_incoherente, "commentaires_erreurs"] += "Âge du tir ne correspond pas à l'âge du bracelet. "
        del idx_espece_age_incoherente

        # Changement de la colonne age en id_nomenclature_classe_age en fonction de la table LISTE_NOMENCLATURE_AGE.
        # Met valide à False et ajoute un commentaire d'erreur si l'âge du tir ne correspond à aucun âge de la nomenclature
        df["id_nomenclature_classe_age"] = df["age"].map(LISTE_NOMENCLATURE_AGE)
        idx_erreur = df[df["id_nomenclature_classe_age"].isnull()].index
        df.loc[idx_erreur, "valide"] = False
        df.loc[idx_erreur, "commentaires_erreurs"] += "Âge du tir ne correspond à aucun âge dans les nomenclatures de la bdd. "
        del idx_erreur
        

        ##########################  TRAITEMENT DU POIDS ET DE LA PESÉE  #####################################

        df["poid_c_f_p"] = None
        df["poid_indique"] = False

        # les lignes où "poid" n'est pas un nombre ou est négatif et est différent de None, alors elles sont considérées comme des erreurs. On met valide à False et on ajoute un commentaire d'erreur dans ce cas.
        idx_erreur_poids = df[
            (
                ~df["poids"].apply(lambda x: isinstance(x, (int, float)) and x >= 0)
                & (df["poids"].notnull())
            )
        ].index
        df.loc[idx_erreur_poids, "valide"] = False
        df.loc[idx_erreur_poids, "commentaires_erreurs"] += "Poids du tir n'est pas un nombre ou est négatif. "
        del idx_erreur_poids

        df.loc[((df["pesee"] == "PLEIN") & (df["poids"] > 0) & (df["poids"].notnull())), "poid_entier"] = df["poids"]
        df.loc[((df["pesee"] == "VIDÉ") & (df["poids"] > 0) & (df["poids"].notnull())), "poid_vide"] = df["poids"]
        df.loc[((df['poids'].notnull()) & (df['poids'] > 0)), "poid_indique"] = True
        df.loc[(df['espece'] == 'CERF') & (df['poid_entier'].notnull()) & (df['poid_vide'].isnull()), 'poid_vide'] = df.apply(lambda row: poid_vide_cerf(row['poid_entier']), axis=1)
        df.loc[(df['espece'] == 'CHEVREUIL') & (df['poid_entier'].notnull()) & (df['poid_vide'].isnull()), 'poid_vide'] = df.apply(lambda row: poid_vide_chevreuil(row['poid_entier']), axis=1)
        
        # on cherche les poids inférieurs a la valeur dans POIDS_VIDE_MINIMUM pour chaque espèce en fonction de l'age. Si le poids est inférieur à cette valeur, on considère que c'est une erreur. On ajoute un commentaire d'erreur dans ce cas.
        idx_poids_minimum_aberrant = df[
            df.apply(
                lambda row: (
                    row["poid_vide"] is not None and row["age"] in POIDS_VIDE_MINIMUM.get(row["espece"], {}) and row["poid_vide"] < POIDS_VIDE_MINIMUM[row["espece"]][row["age"]]
                ), axis=1,
            )].index
        df.loc[idx_poids_minimum_aberrant, "commentaires_erreurs"] += "Poids vide inférieur au poids vide minimum pour l'espèce et l'âge. "
        df.loc[idx_poids_minimum_aberrant, "a_verifier"] = True
        del idx_poids_minimum_aberrant

        idx_poids_maximum_aberrant = df[
            df.apply(
                lambda row: (
                    row["poid_vide"] is not None and row["age"] in POIDS_VIDE_MAXIMUM.get(row["espece"], {}) and row["poid_vide"] > POIDS_VIDE_MAXIMUM[row["espece"]][row["age"]]
                ), axis=1,
            )].index
        df.loc[idx_poids_maximum_aberrant, "commentaires_erreurs"] += "Poids vide supérieur au poids vide maximum pour l'espèce et l'âge. "
        df.loc[idx_poids_maximum_aberrant, "a_verifier"] = True
        del idx_poids_maximum_aberrant

        df.drop(columns=["poids", "pesee"], inplace=True)



        ##########################  TRAITEMENT DU MODE DE CHASSE  ###########################################
        # on indique l'id_nomenclature_mode_chasse en fonction de la colonne type_chasse. L'id correspondant est trouvé dans la table LISTE_NOMENCLATURE_MODE_CHASSE
        # type_chasse est égale à "INDIVIDUEL", "COLLECTIVE" ou "BATTUE "
        df["id_nomenclature_mode_chasse"] = None
        df.loc[df["type_chasse"] == "INDIVIDUEL", "id_nomenclature_mode_chasse"] = (
            LISTE_NOMENCLATURE_MODE_CHASSE.get("INDIVIDUEL")
        )
        df.loc[df["type_chasse"] == "COLLECTIVE", "id_nomenclature_mode_chasse"] = (
            LISTE_NOMENCLATURE_MODE_CHASSE.get("COLLECTIVE")
        )
        df.loc[df["type_chasse"] == "BATTUE", "id_nomenclature_mode_chasse"] = (
            LISTE_NOMENCLATURE_MODE_CHASSE.get("BATTUE")
        )
        df.drop(columns=["type_chasse"], inplace=True)

        ##########################   TRAITEMENT DES DATES  ##################################################

        # on verifie que la date est un string au format aaaa-mm-jj. Si ce n'est pas le cas, on met valide à False et on ajoute un commentaire d'erreur

        idx_erreur = df[df["date"].isnull()].index
        df.loc[idx_erreur, "valide"] = False
        df.loc[idx_erreur, "commentaires_erreurs"] += "Date du tir au format incorrect ou manquante. "
        del idx_erreur
        df["date_exacte"] = df["date"]
        df["date_enreg"] = df["date_exacte"]

        # Traitement des dates: on vérifie si la date d'enregistrement du tir se trouve entre la date de début et la date de fin de la saison. Met valide à False et ajoute un commentaire d'erreur si ce n'est pas le cas
        # Si la saison n'a pas de date de début ou de fin, on ne fait pas la vérification et on considère que la date est valide (on ne met pas valide à False)
        # date_exacte et date_enreg ne sont plus différentiées dans les dernières versions oeasc, on les mets à l'identique
        idx_erreur_date_debut = df[
            ((df["date"] < df["saison.date_debut"]) & (df["saison.date_debut"].notnull()))
        ].index
        df.loc[idx_erreur_date_debut, "valide"] = False
        df.loc[idx_erreur_date_debut, "commentaires_erreurs"] += "Date du tir avant le début de la saison. "
        del idx_erreur_date_debut


        idx_erreur_date_fin = df[
            ((df["date"] > df["saison.date_fin"]) & (df["saison.date_fin"].notnull()))
        ].index
        df.loc[idx_erreur_date_fin, "valide"] = False
        df.loc[idx_erreur_date_fin, "commentaires_erreurs"] += "Date du tir après la fin de la saison. "
        del idx_erreur_date_fin

        # suppression des colonnes désormais inutiles
        df.drop(columns=["date"], inplace=True)

        ###########################   TRAITEMENT DES CORS   #############################################

        # si le nb de cors n'est pas None et ce n'est pas un float dont la valeur est positive et égale à un entier, alors on considère que c'est une erreur. On met valide à False et on ajoute un commentaire d'erreur dans ce cas.

        idx_erreur_cors = df[
            ~df["cors_nb"].apply(
                lambda x: (isinstance(x, (int, float)) and x >= 0 and x.is_integer())
                or pd.isnull(x)
            )
        ].index
        df.loc[idx_erreur_cors, "valide"] = False
        df.loc[idx_erreur_cors, "commentaires_erreurs"] += "Nombre de cors n'est pas un nombre entier positif ou est différent de null. "
        del idx_erreur_cors

        # si le nb de cors est différent de null pour les mouflons on retourne une erreur
        idx_erreur_cors_mouflon = df[(df["espece"] == "MOUFLON") & (df["cors_nb"].notnull())].index
        df.loc[idx_erreur_cors_mouflon, "valide"] = False
        df.loc[idx_erreur_cors_mouflon, "commentaires_erreurs"] += "Nombre de cors renseigné pour un mouflon. "
        del idx_erreur_cors_mouflon

        # Si le nb de cors est aberrant
        idx_erreur_nb_cors = df[
            (df["cors_nb"] < NB_CORS_MINIMUM) |
            (df["cors_nb"] > NB_CORS_MAXIMUM)
        ].index
        df.loc[idx_erreur_nb_cors, "commentaires_erreurs"] += f"Nombre de cors aberrant (inférieur à {NB_CORS_MINIMUM} ou supérieur à {NB_CORS_MAXIMUM}). "
        df.loc[idx_erreur_nb_cors, "a_verifier"] = True
        del idx_erreur_nb_cors

        # création du champs cor_indetermine
        df["cors_indetermine"] = True
        df.loc[df["cors_nb"] >= 0, "cors_indetermine"] = False

        ######################### TRAITEMENT DES DAGUES  #############################################
        # remplacement des 0 par null pour les longueurs de dagues
        
        df.loc[(df["long_dagues_droite"] == 0), "long_dagues_droite"] = None
        df.loc[(df["long_dagues_gauche"] == 0), "long_dagues_gauche"] = None

        # si la longueur de dagues n'est pas None et ce n'est pas un float dont la valeur est positive, alors on considère que c'est une erreur. On met valide à False et on ajoute un commentaire d'erreur dans ce cas.
        idx_erreur_dagues_droite = df[
            ~df["long_dagues_droite"].apply(
                lambda x: (isinstance(x, (int, float)) and x >= 0) or pd.isnull(x)
            )
        ].index
        df.loc[idx_erreur_dagues_droite, "valide"] = False
        df.loc[idx_erreur_dagues_droite, "commentaires_erreurs"] += "La longueur de dague droite n'est pas un nombre entier positif ou est différent de null. "
        del idx_erreur_dagues_droite

        idx_erreur_dagues_gauche = df[
            ~df["long_dagues_gauche"].apply(
                lambda x: (isinstance(x, (int, float)) and x >= 0) or pd.isnull(x)
            )
        ].index
        df.loc[idx_erreur_dagues_gauche, "valide"] = False
        df.loc[idx_erreur_dagues_gauche, "commentaires_erreurs"] += "La longueur de dague gauche n'est pas un nombre entier positif ou est différent de null. "
        del idx_erreur_dagues_gauche

        # si le sexe est FEMELLE et que les longueurs de dagues sont renseignées, on retourne une erreur
        idx_erreur_dagues_femelle = df[
            (df["sexe"] == "FEMELLE")
            & (df["long_dagues_droite"].notnull() | df["long_dagues_gauche"].notnull())
        ].index
        df.loc[idx_erreur_dagues_femelle, "valide"] = False
        df.loc[idx_erreur_dagues_femelle, "commentaires_erreurs"] += "Longueur de dague renseignée pour une femelle. "
        del idx_erreur_dagues_femelle

        # met la valeur des dagues en commentaire d'erreur si la longueur est aberrante
        idx_erreur_dagues_aberrantes_gauche = df[
            df.apply(
                lambda row: (
                    (row["long_dagues_gauche"] is not None and row["age"] in TAILLE_MINIMUM_DAGUES.get(row["espece"], {}) and row["long_dagues_gauche"] < TAILLE_MINIMUM_DAGUES[row["espece"]][row["age"]])
                    or (row["long_dagues_gauche"] is not None and row["age"] in TAILLE_MAXIMUM_DAGUES.get(row["espece"], {}) and row["long_dagues_gauche"] > TAILLE_MAXIMUM_DAGUES[row["espece"]][row["age"]])
                ), axis=1,
            )].index
        df.loc[idx_erreur_dagues_aberrantes_gauche, "commentaires_erreurs"] += f"Longueur de dague gauche aberrante. "   
        df.loc[idx_erreur_dagues_aberrantes_gauche, "a_verifier"] = True
        del idx_erreur_dagues_aberrantes_gauche

        idx_erreur_dagues_aberrantes_droite = df[
            df.apply(
                lambda row: (
                    (row["long_dagues_droite"] is not None and row["age"] in TAILLE_MINIMUM_DAGUES.get(row["espece"], {}) and row["long_dagues_droite"] < TAILLE_MINIMUM_DAGUES[row["espece"]][row["age"]])
                    or (row["long_dagues_droite"] is not None and row["age"] in TAILLE_MAXIMUM_DAGUES.get(row["espece"], {}) and row["long_dagues_droite"] > TAILLE_MAXIMUM_DAGUES[row["espece"]][row["age"]])
                ), axis=1,
            )].index
        df.loc[idx_erreur_dagues_aberrantes_droite, "commentaires_erreurs"] += f"Longueur de dague droite aberrante. "  
        df.loc[idx_erreur_dagues_aberrantes_droite, "a_verifier"] = True
        del idx_erreur_dagues_aberrantes_droite
 

        df.drop(columns=["sexe", "sexe_theorique"], inplace=True)


        ######################## TRAITEMENT DES MANDIBULES  #############################################
        # remplacement des 0 par null pour les longueurs de mandibules
        df.loc[df["long_mandibules_droite"] == 0, "long_mandibules_droite"] = None
        df.loc[df["long_mandibules_gauche"] == 0, "long_mandibules_gauche"] = None

        # si la longueur de mandibules n'est pas None et ce n'est pas un float dont la valeur est positive, alors on considère que c'est une erreur. On met valide à False et on ajoute un commentaire d'erreur dans ce cas.
        idx_erreur_mandibules = df[
            ~df["long_mandibules_droite"].apply(
                lambda x: (isinstance(x, (int, float)) and x >= 0) or pd.isnull(x)
            )
        ].index
        df.loc[idx_erreur_mandibules, "valide"] = False
        df.loc[idx_erreur_mandibules, "commentaires_erreurs"] += "La longueur de mandibule droite n'est pas un nombre entier positif ou est différent de null. "
        del idx_erreur_mandibules
        idx_erreur_mandibules = df[
            ~df["long_mandibules_gauche"].apply(
                lambda x: (isinstance(x, (int, float)) and x >= 0) or pd.isnull(x)
            )
        ].index
        df.loc[idx_erreur_mandibules, "valide"] = False
        df.loc[idx_erreur_mandibules, "commentaires_erreurs"] += "La longueur de mandibule gauche n'est pas un nombre entier positif ou est différent de null. "
        del idx_erreur_mandibules

        # si la longueur de mandibules est aberrante (inférieure à la valeur dans TAILLE_MINIMUM_MANDIBULES ou supérieure à la valeur dans TAILLE_MAXIMUM_MANDIBULES), on ajoute un commentaire d'erreur et on met a_verifier à True pour que l'utilisateur puisse vérifier la valeur. Les valeurs de taille minimum et maximum sont définies en fonction de l'espèce et de l'âge dans les dictionnaires TAILLE_MINIMUM_MANDIBULES et TAILLE_MAXIMUM_MANDIBULES.
        index_erreur_taille_mandibules = df[
                (df["long_mandibules_droite"] > TAILLE_MAXIMUM_MANDIBULES) |
                (df["long_mandibules_droite"] < TAILLE_MINIMUM_MANDIBULES) |
                (df["long_mandibules_gauche"] < TAILLE_MINIMUM_MANDIBULES) |
                (df["long_mandibules_gauche"] > TAILLE_MAXIMUM_MANDIBULES)
            ].index
        df.loc[index_erreur_taille_mandibules, "commentaires_erreurs"] += "Longueur de mandibules aberrante. "
        df.loc[index_erreur_taille_mandibules, "a_verifier"] = True
        del index_erreur_taille_mandibules


        ######################## TRAITEMENT LATITUDE ET LONGITUDE  #############################################
        # verification que les latitude et longitude sont des floats si elles ne sont pas nulles. Met valide à False et ajoute un commentaire d'erreur si ce n'est pas le cas.
        idx_erreur_latitude = df[
            ~df["latitude"].apply(lambda x: isinstance(x, (int, float)) or pd.isnull(x))
        ].index
        df.loc[idx_erreur_latitude, "valide"] = False
        df.loc[idx_erreur_latitude, "commentaires_erreurs"] += "Latitude n'est pas un nombre ou est différent de null. "
        del idx_erreur_latitude
        idx_erreur_longitude = df[
            ~df["longitude"].apply(
                lambda x: isinstance(x, (int, float)) or pd.isnull(x)
            )
        ].index
        df.loc[idx_erreur_longitude, "valide"] = False
        df.loc[idx_erreur_longitude, "commentaires_erreurs"] += "Longitude n'est pas un nombre ou est différent de null. "
        del idx_erreur_longitude

        # transformation des latitude et longitude qui sont en ws84 en coordonnée lambert 93 pour pouvoir les comparer aux coordonnées des zones de chasse.
        # pour la transformation on utilise la bibliothèque pyproj
        transformer = Transformer.from_crs("EPSG:4326", "EPSG:2154", always_xy=True)
        # on applique la transformation aux colonnes longitude et latitude pour obtenir des colonnes x et y en lambert 93
        df["longitude"], df["latitude"] = transformer.transform(
            df["longitude"], df["latitude"]
        )

        ####################### TRAITEMENT DES AUTEURS DE TIR  #############################################
        # Si l'auteur du tir n'est pas None et est un nombre, on considère que que c'est une erreur
        idx_erreur_auteur_tir = df[
            ~df["auteur_tir_str"].apply(
                lambda x: not isinstance(x, (int, float)) or pd.isnull(x)
            )
        ].index
        df.loc[idx_erreur_auteur_tir, "valide"] = False
        df.loc[idx_erreur_auteur_tir, "commentaires_erreurs"] += "L'auteur du tir ne peut pas être un nombre. "
        del idx_erreur_auteur_tir

        ####################### TRAITEMENT DES LIEUX DE TIR #############################################
        # Si le lieu de tir n'est pas None et est un nombre, on considère que que c'est une erreur
        idx_erreur_lieu_tir = df[
            ~df["lieu_tir_txt"].apply(
                lambda x: not isinstance(x, (int, float)) or pd.isnull(x)
            )
        ].index
        df.loc[idx_erreur_lieu_tir, "valide"] = False
        df.loc[idx_erreur_lieu_tir, "commentaires_erreurs"] += "Le lieu de tir ne peut pas être un nombre. "
        del idx_erreur_lieu_tir


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
    # """Récupère les communes de la bdd et fusionne les informations sur les communes dans le dataframe principal.
    # La jointure se fait avec le nom de la commune en utilisant rapidfuzz pour trouver le nom de commune le plus similaire.
    # Pour l'instant seulement utilisé pour retrouver une petite partie des lieu dits de tirs.
    # """

    try:
        with app.app_context():
            # récupération des communes de la bdd avec leur géométrie en geojson.
            # Sélection explicite des colonnes utiles pour éviter d'invoquer
            # des colonnes absentes sur certaines bases (ex: description)
            stmt = (
                select(
                    LAreas.id_area,
                    LAreas.area_code,
                    LAreas.area_name,
                    func.ST_AsGeoJSON(func.ST_Transform(LAreas.geom_4326, 4326)).label(
                        "geom_4326"
                    ),
                )
                .join(BibAreasType, LAreas.id_type == BibAreasType.id_type)
                .where(BibAreasType.type_code == "OEASC_COMMUNE")
            )

            rows = DB.session.execute(
                stmt
            ).all()  # retourne [(id_area, area_code, area_name, geom_4326), ...]
            liste = []
            for id_area, area_code, area_name, geom_json in rows:
                d = {
                    "id_area": id_area,
                    "area_code": area_code,
                    "area_name": area_name,
                    "geom_4326": geom_json,
                }
                liste.append(d)

            df_liste_commune_oeasc = pd.json_normalize(liste)
            df_liste_commune_oeasc = df_liste_commune_oeasc[
                ["id_area", "area_code", "area_name", "geom_4326"]
            ]
            df_liste_commune_oeasc = df_liste_commune_oeasc.rename(
                columns={
                    "id_area": "commune_id_area",
                    "area_code": "insee_commune",
                    "area_name": "commune_name",
                    "geom_4326": "commune_geom",
                }
            )

        # cas très particulier de lanuejols qui existe en lozère et dans le gard. On les différencie en ajoutant GARD

        df_liste_commune_oeasc["commune_name"] = uniformise_communes(
            df_liste_commune_oeasc["commune_name"]
        )

        df_liste_commune_oeasc.loc[
            (
                (df_liste_commune_oeasc["commune_name"] == "LANUEJOLS")
                & (df_liste_commune_oeasc["insee_commune"] == "30139")
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

        # on intégre les données sur les communes dans le dataframe principal. Et on supprime la colonne commune_name qui n'est plus utile après la fusion. La fusion se fait en faisant correspondre la colonne commune de df avec la colonne commune_name de df_liste_commune_oeasc. On fait une jointure à gauche pour ne pas perdre les lignes du csv qui n'ont pas de correspondance dans la base de données (même si on a essayé de corriger les noms de communes pour maximiser les correspondances). Les lignes du csv qui n'ont pas de correspondance dans la base de données auront des valeurs nulles pour les colonnes communes à df_liste_commune_oeasc (commune_id_area, insee_commune, commune_geom).
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


def etape__integration_zones_dans_df(df, apiResponse):
    """Intégration des données sur les zones indicative avec leurs géométries dans la dataframe.
    La jointure se fait avec l'id_zone_indicative_realisee qui est présent dans le dataframe
    Pas utilisé pour l'instant mais pourrait permettre de vérifier qu'une latitude et longitude du lieu de tir se trouve
    bien dans la zone indicative. Je garde ça sous le coude.
    """

    try:
        liste_zone_indicative = df["id_zone_indicative_realisee"].to_list()
        liste_zone_indicative = list(set(liste_zone_indicative))

        with app.app_context():
            stmt_zone_indicative = select(
                TZoneIndicatives,
                func.ST_AsGeoJSON(func.ST_Transform(TZoneIndicatives.geom, 4326)).label(
                    "geom"
                ),
            ).where(TZoneIndicatives.id_zone_indicative.in_(liste_zone_indicative))
            rows = DB.session.execute(
                stmt_zone_indicative
            ).all()  # retourne [(TZoneIndicatives, geom), ...]
            liste = []
            for area, geom_json in rows:
                d = TZoneIndicativesSchema().dump(area)
                d["geom"] = geom_json
                liste.append(d)
            df_zones_indicatives = pd.json_normalize(liste)
            # df_zones_indicatives = df_zones_indicatives.set_index('id_zone_indicative')
            df_zones_indicatives = df_zones_indicatives[["id_zone_indicative", "geom"]]

            df_zones_indicatives = df_zones_indicatives.rename(
                columns={"geom": "zi_geom"}
            )
            df_fusion = df.merge(
                df_zones_indicatives,
                left_on="id_zone_indicative_realisee",
                right_on="id_zone_indicative",
                how="left",
            ).drop(columns=["id_zone_indicative"])
            return df_fusion, apiResponse

    except Exception as e:
        user_message = "Une erreur est survenue lors de l'intégration des zones indicatives dans le dataframe. Veuillez vérifier que le fichier est au bon format et réessayer."
        apiResponse.add_log(message=user_message, type_log="ERROR")
        apiResponse.add_error(system_error=str(e), user_message=user_message)
        return pd.DataFrame(), apiResponse


def etape__recherche_lieux_dits_de_tir_de_realisation(df, apiResponse):
    """Retrouve les id_lieu_tir_synonyme correspondant au lieu dit de tir saisi dans le csv d'importation en comparant avec les lieux de tir synonymes de la base de données.
     La comparaison se fait en vérifiant que le nom du lieu dit saisi dans le csv correspond au nom_lieu_tir_synonyme dans la base de données
    Il y a plusieurs étapes dans cette comparaison: :
    1. le lieu dit saisi est identique et est dans la même zone indicative
    2. le lieu dit saisi est similaire et est dans la même zone indicative
    3. le lieu dit saisi est identique et est dans une même zone cynegetique
    4. le lieu dit saisi est similaire et est dans une même zone cynegetique
    5. le lieu dit saisi est identique et est dans une même commune
    6. le lieu dit saisi est similaire et est dans une même commune

    tous les cas  sont enregistrés dans un dict de bilan qui permettra d'augmenter le nombre de synonymes de lieux de tir dans la bdd.
    On y gardera dans ce dict les id_zone_indicative_realisee, id_zone_cynegetique_realisee et id_commune, latitude et longitude pour créer des nouveaux lieux dits à l'avenir.
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
            stmt_liste_lieu_tirs_synonymes = select(TLieuTirSynonymes)
            rows = DB.session.execute(stmt_liste_lieu_tirs_synonymes).scalars().all()
            df_lts = TLieuTirSynonymesSchema().dump(rows, many=True)
            df_lts = pd.json_normalize(df_lts)
            # on ne garde que les colonnes qui nous intéressent pour alléger les calculs sur le dataframe.
            df_lts = df_lts[
                [
                    "id_lieu_tir_synonyme",
                    "id_lieu_tir",
                    "nom_lieu_tir_synonyme",
                    "lieu_tir.nom_lieu_tir",
                    "lieu_tir.zone_indicative.id_zone_indicative",
                    "lieu_tir.zone_indicative.zone_cynegetique.id_zone_cynegetique",
                    "lieu_tir.id_area_commune",
                ]
            ]
            # renommage des colonnes pour faciliter le travail dessus
            df_lts = df_lts.rename(
                columns={
                    "lieu_tir.nom_lieu_tir": "nom_lieu_tir",
                    "lieu_tir.zone_indicative.id_zone_indicative": "id_zi_lieu_tir",
                    "lieu_tir.zone_indicative.zone_cynegetique.id_zone_cynegetique": "id_zc_lieu_tir",
                    "lieu_tir.id_area_commune": "id_area_commune_lieu_tir",
                }
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

        # les futurs id_lieu_tir_synonyme et nom_lieu_tir_synonyme seront mis dans ces colonnes
        df["id_lieu_tir_synonyme"] = None
        df["nom_lieu_tir_synonyme"] = None

        # parcours de df pour trouver l'id_lieu_tir_synonyme correspondant à lieu_tir_txt. Il faut que l'id_zone_indicative_realisee du tir corresponde à l'id_zi_lieu_tir du lieu de tir synonyme, et que le nom du lieu dit corresponde au nom_lieu_tir_synonyme du lieu de tir synonyme
        for index, row in df.iterrows():
            df_result = pd.DataFrame()
            id_zone_indicative_realisee = row["id_zone_indicative_realisee"]
            nom_parc_lieu_dit = row["lieu_tir_txt"]
            nom_save_lieu_dit = (
                row["save_lieu_dit"].upper()
                if isinstance(row["save_lieu_dit"], str)
                else row["save_lieu_dit"]
            )  # on met aussi le nom du lieu dit d'origine en majuscules pour l'ajouter au dict de bilan des synonymes
            if pd.isna(nom_parc_lieu_dit):  # pas de lieu dit saisi dans geochasse.
                continue
            else:
                # on recherche d'abord les correspondances exactes dans les lieux de tir synonymes qui ont la même zone indicative que le tir réalisé
                df_result = df_lts.loc[
                    (
                        (df_lts["id_zi_lieu_tir"] == id_zone_indicative_realisee)
                        & (df_lts["nom_lieu_tir_synonyme"] == nom_parc_lieu_dit)
                    )
                ]
                if df_result.shape[0] == 1:
                    # il existe une seule correspondance exacte. On la prend.
                    df.at[index, "id_lieu_tir_synonyme"] = df_result.iloc[0][
                        "id_lieu_tir_synonyme"
                    ]
                    df.at[index, "nom_lieu_tir_synonyme"] = df_result.iloc[0][
                        "nom_lieu_tir_synonyme_origin"
                    ]
                    # enregistrement de ce cas dans le dict de bilan de synonymes
                    dict_bilan_synonymes[row["numero_bracelet"]] = {
                        "nom_lieu_csv": df.at[index, "save_lieu_dit"],
                        "correspondance": df_result.iloc[0][
                            "nom_lieu_tir_synonyme_origin"
                        ],
                        "id_correspondance": df_result.iloc[0]["id_lieu_tir_synonyme"],
                        "type_correspondance": "EXACTE_ZI",
                        "raison": "Nom exact retrouvé dans la ZI",
                        "id_zone_indicative_realisee": id_zone_indicative_realisee,
                        "id_zone_cynegetique_realisee": row[
                            "id_zone_cynegetique_realisee"
                        ],
                        "id_commune": row["commune_id_area"],
                        "id_lieu_tir": df_result.iloc[0]["id_lieu_tir"],
                        "nom_lieu_tir": df_result.iloc[0]["nom_lieu_tir"],
                        "lattitude": row["latitude"],
                        "longitude": row["longitude"],
                    }
                elif df_result.shape[0] > 1:
                    # il existe plusieurs correspondances exactes. On prend la première mais on ajoute un commentaire d'erreur pour indiquer qu'il y a plusieurs correspondances et qu'il faut vérifier laquelle est la bonne. On garde aussi dans le dict de bilan des synonymes les différentes correspondances trouvées pour pouvoir les ajouter à la base de données des lieux de tir synonymes à l'avenir.
                    liste_nom_lieu_tir_synonyme = df_result["nom_lieu_tir"].tolist()
                    df.at[
                        index, "commentaires_erreurs"
                    ] += f"{df_result.shape[0]} correspondances trouvées dans les lieux de tir synonymes pour le lieu dit {nom_save_lieu_dit} dans la ZI: {liste_nom_lieu_tir_synonyme}"
                    df.at[index, "id_lieu_tir_synonyme"] = df_result.iloc[0][
                        "id_lieu_tir_synonyme"
                    ]
                    df.at[index, "nom_lieu_tir_synonyme"] = df_result.iloc[0][
                        "nom_lieu_tir_synonyme_origin"
                    ]
                    # enregistrement de ce cas dans le dict de bilan de synonymes
                    dict_bilan_synonymes[row["numero_bracelet"]] = {
                        "nom_lieu_csv": df.at[index, "save_lieu_dit"],
                        "correspondance": df_result.iloc[0][
                            "nom_lieu_tir_synonyme_origin"
                        ],
                        "id_correspondance": df_result.iloc[0]["id_lieu_tir_synonyme"],
                        "type_correspondance": "EXACTE_MULTIPLE_ZI",
                        "raison": "Plusieurs noms exacts retrouvés dans la ZI",
                        "id_zone_indicative_realisee": id_zone_indicative_realisee,
                        "id_zone_cynegetique_realisee": row[
                            "id_zone_cynegetique_realisee"
                        ],
                        "id_commune": row["commune_id_area"],
                        "id_lieu_tir": df_result.iloc[0]["id_lieu_tir"],
                        "nom_lieu_tir": df_result.iloc[0]["nom_lieu_tir"],
                        "lattitude": row["latitude"],
                        "longitude": row["longitude"],
                    }
                else:
                    # Pas de nom exact retrouvé, on recherche avec rapidfuzz les lieu tir synonymes qui sont le plus similaires au nom_parc_lieu_dit parmi les lieux de tir synonymes qui ont la même zone indicative
                    liste_nom_lieu_tir_synonyme_in_zi = df_lts.loc[
                        df_lts["id_zi_lieu_tir"] == id_zone_indicative_realisee
                    ]["nom_lieu_tir_synonyme"].tolist()
                    if liste_nom_lieu_tir_synonyme_in_zi:
                        resultat = rpfz.process.extractOne(
                            nom_parc_lieu_dit,
                            liste_nom_lieu_tir_synonyme_in_zi,
                            scorer=rpfz.fuzz.ratio,
                        )
                        # si le score de similarité contenu dans resultat[1] est supérieur à 80, on considère que c'est une correspondance et on prend le meilleur match
                        if resultat[1] >= SCORE_MINIMUM_RAPIDFUZZ:
                            meilleur_match = resultat[
                                0
                            ]  # resultat[0] contient le nom du lieu de tir synonyme qui est le plus similaire au nom_parc_lieu_dit parmi les lieux de tir synonymes qui ont la même zone indicative
                            # On considère que le lieu trouvé est le bon, on enregitre son id et nom et on ajoute un commentaire d'erreur pour indiquer que c'est une correspondance trouvée avec une similarité de nom qui sera indiqué à l'utilisateur.
                            id_new_lieu_tir_synonyme = df_lts.loc[
                                (
                                    (df_lts["nom_lieu_tir_synonyme"] == meilleur_match)
                                    & (
                                        df_lts["id_zi_lieu_tir"]
                                        == id_zone_indicative_realisee
                                    )
                                ),
                                "id_lieu_tir_synonyme",
                            ].values[0]
                            df.at[index, "id_lieu_tir_synonyme"] = (
                                id_new_lieu_tir_synonyme
                            )
                            df.at[index, "nom_lieu_tir_synonyme"] = df_lts.loc[
                                (
                                    df_lts["id_lieu_tir_synonyme"]
                                    == id_new_lieu_tir_synonyme
                                ),
                                "nom_lieu_tir_synonyme_origin",
                            ].values[0]
                            df.at[index, "commentaires_erreurs"] += (
                                f"Lieu tir {nom_save_lieu_dit}: nom similaire trouvé dans la même ZI: {meilleur_match} "
                            )
                            # enregistrement de ce cas dans le dict de bilan de synonymes
                            dict_bilan_synonymes[row["numero_bracelet"]] = {
                                "nom_lieu_csv": df.at[index, "save_lieu_dit"],
                                "correspondance": df.at[index, "nom_lieu_tir_synonyme"],
                                "id_correspondance": df.at[
                                    index, "id_lieu_tir_synonyme"
                                ],
                                "type_correspondance": "SIMILAIRE_ZI",
                                "raison": "Nom similaire retrouvé dans la ZI",
                                "id_zone_indicative_realisee": id_zone_indicative_realisee,
                                "id_zone_cynegetique_realisee": row[
                                    "id_zone_cynegetique_realisee"
                                ],
                                "id_commune": row["commune_id_area"],
                                "id_lieu_tir": df_lts.loc[
                                    (
                                        df_lts["id_lieu_tir_synonyme"]
                                        == id_new_lieu_tir_synonyme
                                    ),
                                    "id_lieu_tir",
                                ].values[0],
                                "nom_lieu_tir": df_lts.loc[
                                    (
                                        df_lts["id_lieu_tir_synonyme"]
                                        == id_new_lieu_tir_synonyme
                                    ),
                                    "nom_lieu_tir",
                                ].values[0],
                                "lattitude": row["latitude"],
                                "longitude": row["longitude"],
                            }

                        else:

                            # rien n'a été trouvé dans la même zone indicative, on élargit la recherche à la commune.
                            # on recherche d'abord les correspondances exactes dans les lieux de tir synonymes qui ont la même commune que le lieu de tir réalisé
                            id_commune = row["commune_id_area"]
                            df_result = df_lts.loc[
                                (
                                    (df_lts["id_area_commune_lieu_tir"] == id_commune)
                                    & (
                                        df_lts["nom_lieu_tir_synonyme"]
                                        == nom_parc_lieu_dit
                                    )
                                )
                            ]
                            if df_result.shape[0] >= 1:
                                # des nom exactes ont été trouvés on garde le premier résultat et on indique en commentaire les raisons.
                                df.at[index, "id_lieu_tir_synonyme"] = df_result.iloc[
                                    0
                                ]["id_lieu_tir_synonyme"]
                                df.at[index, "nom_lieu_tir_synonyme"] = df_result.iloc[
                                    0
                                ]["nom_lieu_tir_synonyme_origin"]
                                df.at[index, "commentaires_erreurs"] += (
                                    f"Lieu tir {nom_save_lieu_dit}: Un même lieu dit a été trouvé dans la commune mais pas dans la ZI."
                                )
                                # enregistrement de ce cas dans le dict de bilan de synonymes
                                dict_bilan_synonymes[row["numero_bracelet"]] = {
                                    "nom_lieu_csv": df.at[index, "save_lieu_dit"],
                                    "correspondance": df_result.iloc[0][
                                        "nom_lieu_tir_synonyme_origin"
                                    ],
                                    "id_correspondance": df_result.iloc[0][
                                        "id_lieu_tir_synonyme"
                                    ],
                                    "type_correspondance": "EXACTE_COMMUNE",
                                    "raison": "Nom exact retrouvé dans la commune",
                                    "id_zone_indicative_realisee": id_zone_indicative_realisee,
                                    "id_zone_cynegetique_realisee": id_zone_cynegetique_realisee,
                                    "id_commune": id_commune,
                                    "id_lieu_tir": df_result.iloc[0]["id_lieu_tir"],
                                    "nom_lieu_tir": df_result.iloc[0]["nom_lieu_tir"],
                                    "lattitude": row["latitude"],
                                    "longitude": row["longitude"],
                                }
                            else:
                                # pas de nom exact retrouvé dans la même commune, on recherche avec rapidfuzz les lieu tir synonymes qui sont le plus similaires dans la même commune
                                liste_nom_lieu_tir_synonyme_in_commune = df_lts.loc[
                                    df_lts["id_area_commune_lieu_tir"] == id_commune
                                ]["nom_lieu_tir_synonyme"].tolist()
                                if liste_nom_lieu_tir_synonyme_in_commune:
                                    resultat = rpfz.process.extractOne(
                                        nom_parc_lieu_dit,
                                        liste_nom_lieu_tir_synonyme_in_commune,
                                        scorer=rpfz.fuzz.ratio,
                                    )
                                    if resultat[1] >= SCORE_MINIMUM_RAPIDFUZZ:
                                        # des résultats similaires ont été trouvés, on les prend.
                                        meilleur_match = resultat[0]
                                        id_new_lieu_tir_synonyme = df_lts.loc[
                                            (
                                                (
                                                    df_lts["nom_lieu_tir_synonyme"]
                                                    == meilleur_match
                                                )
                                                & (
                                                    df_lts["id_area_commune_lieu_tir"]
                                                    == id_commune
                                                )
                                            ),
                                            "id_lieu_tir_synonyme",
                                        ].values[0]
                                        df.at[index, "id_lieu_tir_synonyme"] = (
                                            id_new_lieu_tir_synonyme
                                        )
                                        df.at[index, "nom_lieu_tir_synonyme"] = (
                                            df_lts.loc[
                                                df_lts["id_lieu_tir_synonyme"]
                                                == id_new_lieu_tir_synonyme,
                                                "nom_lieu_tir_synonyme_origin",
                                            ].values[0]
                                        )
                                        df.at[
                                            index, "commentaires_erreurs"
                                        ] += f" Lieu tir {nom_save_lieu_dit}: Nom similaire trouvé dans la commune: {meilleur_match}  mais pas dans la ZI. "
                                        # enregistrement de ce cas dans le dict de bilan de synonymes
                                        dict_bilan_synonymes[row["numero_bracelet"]] = {
                                            "nom_lieu_csv": df.at[
                                                index, "save_lieu_dit"
                                            ],
                                            "correspondance": df.at[
                                                index, "nom_lieu_tir_synonyme"
                                            ],
                                            "id_correspondance": df.at[
                                                index, "id_lieu_tir_synonyme"
                                            ],
                                            "type_correspondance": "SIMILAIRE_COMMUNE",
                                            "raison": "Nom similaire retrouvé dans la commune",
                                            "id_zone_indicative_realisee": id_zone_indicative_realisee,
                                            "id_zone_cynegetique_realisee": id_zone_cynegetique_realisee,
                                            "id_commune": id_commune,
                                            "id_lieu_tir": df_lts.loc[
                                                df_lts["id_lieu_tir_synonyme"]
                                                == id_new_lieu_tir_synonyme,
                                                "id_lieu_tir",
                                            ].values[0],
                                            "nom_lieu_tir": df_lts.loc[
                                                df_lts["id_lieu_tir_synonyme"]
                                                == id_new_lieu_tir_synonyme,
                                                "nom_lieu_tir",
                                            ].values[0],
                                            "lattitude": row["latitude"],
                                            "longitude": row["longitude"],
                                        }

                                    else:

                                        # rien n'a été trouvé dans la même commune, on élargit la recherche aux zones cynégétiques.
                                        # On recherche d'abord les correspondances exactes dans les lieux de tir synonymes qui ont la même zone cynégétique que le tir réalisé
                                        id_zone_cynegetique_realisee = row[
                                            "id_zone_cynegetique_realisee"
                                        ]
                                        df_result = df_lts.loc[
                                            (
                                                (
                                                    df_lts["id_zc_lieu_tir"]
                                                    == id_zone_cynegetique_realisee
                                                )
                                                & (
                                                    df_lts["nom_lieu_tir_synonyme"]
                                                    == nom_parc_lieu_dit
                                                )
                                            )
                                        ]
                                        if df_result.shape[0] >= 1:
                                            # des nom exactes ont été trouvés on garde le premier résultat et on indique en commentaire les raisons.
                                            df.at[index, "id_lieu_tir_synonyme"] = None
                                            df.at[index, "nom_lieu_tir_synonyme"] = None
                                            df.at[index, "commentaires_erreurs"] += (
                                                f"Lieu tir {nom_save_lieu_dit} déclaré: Un même lieu dit a été trouvé dans la même ZC mais pas dans la ZI."
                                            )
                                            # enregistrement de ce cas dans le dict de bilan de synonymes
                                            dict_bilan_synonymes[
                                                row["numero_bracelet"]
                                            ] = {
                                                "nom_lieu_csv": df.at[
                                                    index, "save_lieu_dit"
                                                ],
                                                "correspondance": df_result.iloc[0][
                                                    "nom_lieu_tir_synonyme_origin"
                                                ],
                                                "id_correspondance": df_result.iloc[0][
                                                    "id_lieu_tir_synonyme"
                                                ],
                                                "type_correspondance": "EXACTE_ZC",
                                                "raison": "Nom exact retrouvé dans la ZC",
                                                "id_zone_indicative_realisee": id_zone_indicative_realisee,
                                                "id_zone_cynegetique_realisee": id_zone_cynegetique_realisee,
                                                "id_commune": row["commune_id_area"],
                                                "id_lieu_tir": df_result.iloc[0][
                                                    "id_lieu_tir"
                                                ],
                                                "nom_lieu_tir": df_result.iloc[0][
                                                    "nom_lieu_tir"
                                                ],
                                                "lattitude": row["latitude"],
                                                "longitude": row["longitude"],
                                            }

                                        else:
                                            # Pas de nom exact retrouvé dans la même zone cynégétique, on recherche avec rapidfuzz les lieu tir synonymes qui sont le plus similaires dans la même zone cynégétique
                                            liste_nom_lieu_tir_synonyme_in_zc = (
                                                df_lts.loc[
                                                    df_lts["id_zc_lieu_tir"]
                                                    == id_zone_cynegetique_realisee
                                                ]["nom_lieu_tir_synonyme"].tolist()
                                            )
                                            if liste_nom_lieu_tir_synonyme_in_zc:
                                                resultat = rpfz.process.extractOne(
                                                    nom_parc_lieu_dit,
                                                    liste_nom_lieu_tir_synonyme_in_zc,
                                                    scorer=rpfz.fuzz.ratio,
                                                )
                                                if (
                                                    resultat[1]
                                                    >= SCORE_MINIMUM_RAPIDFUZZ
                                                ):
                                                    # si un resultat a été trouvé avec un score de similarité suffisant, On le prend
                                                    meilleur_match = resultat[0]
                                                    id_new_lieu_tir_synonyme = df_lts.loc[
                                                        (
                                                            (
                                                                df_lts[
                                                                    "nom_lieu_tir_synonyme"
                                                                ]
                                                                == meilleur_match
                                                            )
                                                            & (
                                                                df_lts["id_zc_lieu_tir"]
                                                                == id_zone_cynegetique_realisee
                                                            )
                                                        ),
                                                        "id_lieu_tir_synonyme",
                                                    ].values[
                                                        0
                                                    ]
                                                    df.at[
                                                        index, "id_lieu_tir_synonyme"
                                                    ] = None  # trop de risque de se tromper.
                                                    df.at[
                                                        index, "nom_lieu_tir_synonyme"
                                                    ] = None  # trop de risque de se tromper, on laisse la valeur à None mais on indique dans le commentaire
                                                    df.at[
                                                        index, "commentaires_erreurs"
                                                    ] += f"Lieu tir {nom_save_lieu_dit} déclaré: Nom similaire trouvé dans la ZC: {meilleur_match}  mais pas dans la ZI."
                                                    # enregistrement de ce cas dans le dict de bilan de synonymes
                                                    dict_bilan_synonymes[
                                                        row["numero_bracelet"]
                                                    ] = {
                                                        "nom_lieu_csv": df.at[
                                                            index, "save_lieu_dit"
                                                        ],
                                                        "correspondance": df_lts.loc[
                                                            (
                                                                df_lts[
                                                                    "id_lieu_tir_synonyme"
                                                                ]
                                                                == id_new_lieu_tir_synonyme
                                                            ),
                                                            "nom_lieu_tir_synonyme_origin",
                                                        ].values[0],
                                                        "id_correspondance": id_new_lieu_tir_synonyme,
                                                        "type_correspondance": "SIMILAIRE_ZC",
                                                        "raison": "Nom similaire retrouvé dans la ZC",
                                                        "id_zone_indicative_realisee": id_zone_indicative_realisee,
                                                        "id_zone_cynegetique_realisee": id_zone_cynegetique_realisee,
                                                        "id_commune": row[
                                                            "commune_id_area"
                                                        ],
                                                        "id_lieu_tir": df_lts.loc[
                                                            (
                                                                df_lts[
                                                                    "id_lieu_tir_synonyme"
                                                                ]
                                                                == id_new_lieu_tir_synonyme
                                                            ),
                                                            "id_lieu_tir",
                                                        ].values[0],
                                                        "nom_lieu_tir": df_lts.loc[
                                                            (
                                                                df_lts[
                                                                    "id_lieu_tir_synonyme"
                                                                ]
                                                                == id_new_lieu_tir_synonyme
                                                            ),
                                                            "nom_lieu_tir",
                                                        ].values[0],
                                                        "lattitude": row["latitude"],
                                                        "longitude": row["longitude"],
                                                    }

                                                else:
                                                    # Aucune similarité suffisante n'a été trouvée même dans la même commune, on considère que le lieu de tir n'a pas été retrouvé et on ajoute un commentaire d'erreur pour indiquer qu'aucun lieu de tir synonyme n'a été trouvé pour ce lieu dit de tir saisi dans le csv. On enregistre aussi ce cas dans le dict de bilan des synonymes pour pouvoir ajouter ce lieu dit comme synonyme à l'avenir dans la base de données des lieux de tir synonymes en indiquant les zones et la commune associées pour faciliter le travail de l'équipe technique.
                                                    # C'est soit une erreur de saisie soit un lieu dit qui n'existe pas dans la base de données et qui pourrait être ajouté comme synonyme à l'avenir si c'est un lieu dit qui existe mais qui a été mal saisi.
                                                    df.at[
                                                        index, "commentaires_erreurs"
                                                    ] += f"Aucun lieu de tir synonyme trouvé pour le lieu dit {nom_save_lieu_dit} dans la ZI, ZC ou la commune. "
                                                    dict_bilan_synonymes[
                                                        row["numero_bracelet"]
                                                    ] = {
                                                        "nom_lieu_csv": df.at[
                                                            index, "save_lieu_dit"
                                                        ],
                                                        "correspondance": None,
                                                        "id_correspondance": None,
                                                        "type_correspondance": "AUCUNE",
                                                        "raison": "Aucun nom similaire retrouvé",
                                                        "id_zone_indicative_realisee": id_zone_indicative_realisee,
                                                        "id_zone_cynegetique_realisee": id_zone_cynegetique_realisee,
                                                        "id_commune": id_commune,
                                                        "id_lieu_tir": None,
                                                        "nom_lieu_tir": None,
                                                        "lattitude": row["latitude"],
                                                        "longitude": row["longitude"],
                                                    }

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
        for index, row in df.iterrows():
            if row["valide"] == True and pd.notna(row["commentaires_erreurs"]):
                commentaire = row["commentaire"] if pd.notna(row["commentaire"]) else ""
                df.at[index, "commentaire"] = (
                    f"{commentaire} \n {row['commentaires_erreurs']}"
                )
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
            df_update = df_update[COLUMNS_REALISATION].copy()
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


def etape__creation_dataframe_erreurs( df_original, df_insert_erreurs, df_update_erreurs, apiResponse):
    try:

        if df_update_erreurs.shape[0] > 0:
            # on ne garde que la colonne commentaires erreurs des dataframes d'erreurs d'insertion et de mise à jour
            df_erreurs = pd.concat(
                [df_insert_erreurs, df_update_erreurs], ignore_index=True
            )
        else:
            df_erreurs = df_insert_erreurs.copy()

        if df_erreurs.shape[0] > 0:  # si il existe des erreurs
            df_erreurs.set_index("id_geochasse", inplace=True)
            df_erreurs = df_erreurs["commentaires_erreurs"]

            # on sort le numéro de bracelet de l'index pour le remplacre par id_geochasse
            df_origin = df_original.copy()
            df_origin["numero"] = df_origin.index
            df_origin.set_index("id_geochasse", inplace=True)

            # on ajoute la colonne commentaires_erreurs au dataframe d'origine en ne gardant que les lignes en erreur.
            df_origin = df_origin.join(df_erreurs, how="inner")

            # creation d'un nom de fichier csv sous forme AAAA-MM-JJ_HH-MM-SS_erreurs_import_geochasse.csv
            nom_fichier = f"{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')}_erreurs_import_geochasse.csv"
            chemin_fichier = Path(DOSSIER_RAPPORTS) / nom_fichier
            df_origin.to_csv(chemin_fichier, index=False)

            # apiResponse.add_log(message=f"Un fichier d'erreur enregistré: {chemin_fichier}", type_log="INFO")
            # type_log FILE permettra d'indiquer au frontend que c'est le nom d'un fichier à télécharger
            if df_erreurs.shape[0] > 0:
                apiResponse.add_log(message=f"{nom_fichier}", type_log="FILE")

        return df_erreurs, apiResponse

    except Exception as e:
        user_message = f"Une erreur est survenue lors de la création du rapport CSV des erreurs. {e}"
        apiResponse.add_log(message=user_message, type_log="ERROR")
        apiResponse.add_error(system_error=str(e), user_message=user_message)
        return df_erreurs, apiResponse


def etape__creation_csv_a_verifier(df, df_original, apiResponse):
    try:
        df_verif = df.loc[df["a_verifier"] == True].copy()
        if df_verif.shape[0] > 0:  # si il existe des erreurs
            df_verif.set_index("id_geochasse", inplace=True)
            df_verif = df_verif["commentaires_erreurs"]

            # on sort le numéro de bracelet de l'index pour le remplacre par id_geochasse
            df_origin = df_original.copy()
            df_origin["numero"] = df_origin.index
            df_origin.set_index("id_geochasse", inplace=True)

            # on ajoute la colonne commentaires_erreurs au dataframe d'origine en ne gardant que les lignes en erreur.
            df_origin = df_origin.join(df_verif, how="inner")
            # creation d'un nom de fichier csv sous forme AAAA-MM-JJ_HH-MM-SS_a_verifier.csv
            nom_fichier = (
                f"{pd.Timestamp.now().strftime('%Y-%m-%d_%H-%M-%S')}_a_verifier.csv"
            )
            chemin_fichier = Path(DOSSIER_RAPPORTS) / nom_fichier
            df_origin.to_csv(chemin_fichier, index=False)
        # apiResponse.add_log(message=f"Un fichier d'erreur enregistré: {chemin_fichier}", type_log="INFO")
        # type_log FILE permettra d'indiquer au frontend que c'est le nom d'un fichier à télécharger
        if df_verif.shape[0] > 0:
            apiResponse.add_log(
                message=f"{df_verif.shape[0]} lignes avec des données aberrantes: à vérifier",
                type_log="WARNING",
            )
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


def traitement_import_realisation_chasse(path_csv, id_saison, update):
    """Fonction principale de traitement de l'import csv.
    Retourne un objet ApiResponse avec les messages, le journal de l'opération et les données à retourner à l'utilisateur.
    """
    if update == "true":
        update = True
    elif update == "false":
        update = False

    apiResponse = initialisation_apiResponse()
    if apiResponse.success == False:
        apiResponse.print_all()
        return apiResponse

    df, apiResponse = etape__récuperation_csv(apiResponse)
    if apiResponse.success == False:
        return apiResponse
    df, apiResponse = etape__clean_csv(df, apiResponse)
    df_original = (
        df.copy()
    )  # on garde une copie du dataframe original pour pouvoir faire des comparaisons à l'avenir si besoin et pour garder une trace de ce qui a été saisi dans le csv.
    if apiResponse.success == False:
        return apiResponse
    df, apiResponse = etape__recupération_attributions(
        df, id_saison, update, apiResponse
    )
    if apiResponse.success == False:
        return apiResponse
    df, apiResponse = etape__verification_donnees_geochasse(df, apiResponse)
    if apiResponse.success == False:
        return apiResponse
    df, apiResponse = etape__ajout_colonnes_vides_pour_bdd(df, apiResponse, update)
    if apiResponse.success == False:
        return apiResponse
    df, apiResponse = etape__integration_communes_dans_df(df, apiResponse)
    if apiResponse.success == False:
        return apiResponse
    df, apiResponse = etape__integration_zones_dans_df(df, apiResponse)
    if apiResponse.success == False:
        return apiResponse
    # dict_bilan_synonymes contiendra un bilan des correspondances trouvées entre les lieux dits saisis dans le csv et les lieux de tir synonymes de la bdd
    df, apiResponse, dict_bilan_synonymes = (
        etape__recherche_lieux_dits_de_tir_de_realisation(df, apiResponse)
    )
    if apiResponse.success == False:
        return apiResponse

    apiResponse = etape_save_bilan_synonymes_in_csv(dict_bilan_synonymes, apiResponse)

    df, apiResponse = etape__remplissage_commentaires(df, apiResponse)
    if apiResponse.success == False:
        return apiResponse

    # insertion puis mise à jour, on fait les 2 avant de vérifier si il y a des erreurs.
    apiResponse, df_erreurs_insert = etape__insert_new_realisations(df, apiResponse)
    if update == True:
        apiResponse, df_erreurs_update = etape__update_realisations(df, apiResponse)
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

    # apiResponse.print_all() # pour le débug
    # print (df)

    return apiResponse
