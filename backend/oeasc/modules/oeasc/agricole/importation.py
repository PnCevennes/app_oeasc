"""
Import des dégâts agricoles (tableur des indemnisations) -> schéma oeasc_agricole.

Fichier attendu (csv, xls ou ods), une ligne par déclaration :
    Campagnes comptables, Date de création, N° dossier, Date document, Secteur,
    Code insee, Commune du dossier, Culture, Surface détruite (ha),
    Volume détruit (qtx), Unité de la quantité détruite expertisé, Pourcentage,
    Espèce, Montant payé PR (€), Surface RESSEMIS (ha),
    Montant payé RESSEMIS (€), Montant total payé (€)

`traitement_import_degats_agricoles` est appelée en tâche de fond par
`chasse.import_async._traiter` (thread + suivi JSON + polling), avec la signature
commune aux imports `(path, id_saison, update, id_role=, nom_complet=,
progress_callback=)` ; `id_saison` est ignoré : la saison vient de la colonne
« Campagnes comptables ».

Elle retourne toujours un objet `ApiResponse` (`.success`, `.message`,
`.journal` — tags `[INFO]/[ERROR]/[WARNING]`).

NB : ne pas importer `import_async` ici (import circulaire).
"""

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from pathlib import Path

import pandas as pd
from flask import current_app
from rapidfuzz import fuzz
from sqlalchemy import select, delete, insert, text, update as sql_update

from oeasc.utils.apiResponse import ApiResponse
from oeasc.modules.oeasc.chasse.import_attributions import (
    _app_context,
    _normalize,
    _parse_date_fr,
    _make_progress,
    _abandon_erreurs,
    _lookup_especes,
    _match_espece,
    lire_csv_auto,
)
from oeasc.ref_geo_oeasc.models import TCommunesArea
from .models import TSaisonAgricole, TTypeCulture, TDeclarationAgricole

config = current_app.config
DB = config["DB"]

EXTENSIONS_ACCEPTEES = (".csv", ".xls", ".ods")

# {nom canonique: [entêtes acceptées]} — comparées après `_normalize_entete`
# (casse, accents et ponctuation ignorés).
ALIAS_COLONNES = {
    "saison": ["campagnes comptables", "campagne comptable", "campagne", "saison"],
    "date_creation": ["date de creation", "date creation"],
    "numero_dossier": ["n dossier", "no dossier", "numero dossier", "num dossier"],
    "date_document": ["date document", "date du document"],
    "code_insee": ["code insee", "insee", "code insee commune"],
    "culture": ["culture", "type de culture"],
    "surface_detruite": ["surface detruite ha", "surface detruite"],
    # « volumedetruit » : le lecteur ods supprime le retour à la ligne de l'entête
    "volume_detruit": ["volume detruit qtx", "volume detruit", "volumedetruit qtx"],
    "unit_quantite_detruite": [
        "unite de la quantite detruite expertise",
        "unite de la quantite detruite",
        "unite quantite detruite",
    ],
    "pourcentage": ["pourcentage"],
    "espece": ["espece"],
    "montant_paye": ["montant paye pr", "montant paye"],
    "surface_ressemis": ["surface ressemis ha", "surface ressemis"],
    "montant_paye_ressemis": ["montant paye ressemis"],
    "montant_total_paye": ["montant total paye", "montant total"],
}

# score RapidFuzz (0-100) minimal pour rapprocher une entête d'un nom attendu
SEUIL_FUZZY = 85
# écart minimal avec le 2e meilleur candidat : en dessous, le rapprochement est
# jugé ambigu et refusé (ex. « Montant payé » face à deux colonnes de montants)
ECART_FUZZY = 3

# valeurs de la colonne Espèce absentes de oeasc_commons.t_especes
ALIAS_ESPECES = {"cervide": "cerf", "cervides": "cerf"}

COLONNES_NUMERIQUES = (
    "surface_detruite",
    "volume_detruit",
    "pourcentage",
    "montant_paye",
    "surface_ressemis",
    "montant_paye_ressemis",
    "montant_total_paye",
)

RE_SAISON = re.compile(r"^(\d{4})\s*[-/]\s*(\d{4})$")


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------


def _normalize_entete(valeur):
    """`_normalize` + ponctuation, retours à la ligne et espaces multiples
    réduits à un espace.
    Ex. : "Surface \\ndétruite (ha)" -> "surface detruite ha", "N° dossier" -> "n dossier".
    """
    return re.sub(r"[^a-z0-9]+", " ", _normalize(valeur)).strip()


def resoudre_colonnes(colonnes, alias_map=ALIAS_COLONNES):
    """Fait correspondre les colonnes du fichier aux noms canoniques attendus.

    1. correspondance exacte (après normalisation) sur les alias ;
    2. pour ce qui reste, rapprochement approximatif RapidFuzz (`fuzz.ratio`),
       un-pour-un par score décroissant : nécessaire car plusieurs entêtes sont
       proches entre elles (« Montant payé PR », « Montant payé RESSEMIS »,
       « Montant total payé »).

    Retourne (mapping {canon: colonne réelle}, approximations [(canon, colonne,
    score)], manquantes [canon]).
    """
    cols_norm = {}
    for c in colonnes:
        cols_norm.setdefault(_normalize_entete(c), c)

    mapping = {}
    for canon, variantes in alias_map.items():
        for candidat in variantes:
            reel = cols_norm.get(candidat)
            if reel is not None and reel not in mapping.values():
                mapping[canon] = reel
                break

    restantes = {n: c for n, c in cols_norm.items() if c not in mapping.values() and n}
    candidats = []
    for canon, variantes in alias_map.items():
        if canon in mapping:
            continue
        scores = sorted(
            (
                (max(fuzz.ratio(v, n) for v in variantes), c)
                for n, c in restantes.items()
            ),
            reverse=True,
        )
        if not scores or scores[0][0] < SEUIL_FUZZY:
            continue
        if len(scores) > 1 and scores[0][0] - scores[1][0] < ECART_FUZZY:
            continue
        candidats.append((scores[0][0], canon, scores[0][1]))

    approximations = []
    for score, canon, reel in sorted(candidats, reverse=True):
        if reel in mapping.values():
            continue
        mapping[canon] = reel
        approximations.append((canon, reel, round(score)))

    manquantes = [canon for canon in alias_map if canon not in mapping]
    return mapping, approximations, manquantes


def lire_fichier(path):
    """Lit le fichier (csv, xls ou ods) et renvoie un DataFrame.

    - csv : `lire_csv_auto` (séparateur autodétecté, tout en texte). Les exports
      Excel sont parfois en Windows-1252 : on retente alors après conversion.
    - xls / ods : première feuille, types natifs (dates, nombres) conservés.
    Les lignes entièrement vides sont retirées.
    """
    path = Path(path)
    ext = path.suffix.lower()
    if ext == ".csv":
        try:
            df, _sep = lire_csv_auto(str(path))
        except UnicodeDecodeError:
            path_utf8 = path.with_name(path.stem + "_utf8.csv")
            path_utf8.write_text(path.read_text(encoding="cp1252"), encoding="utf-8")
            df, _sep = lire_csv_auto(str(path_utf8))
    elif ext == ".xls":
        df = pd.read_excel(path, engine="xlrd")
    elif ext == ".ods":
        df = pd.read_excel(path, engine="odf")
    else:
        raise ValueError(f"extension non gérée : {ext}")

    df.columns = [str(c) for c in df.columns]
    vide = df.apply(lambda col: col.map(lambda v: _texte(v) == "")).all(axis=1)
    return df[~vide].reset_index(drop=True)


def _texte(valeur):
    """Cellule -> texte nettoyé ("" si vide). Un nombre entier lu comme flottant
    par le tableur redevient un entier : 1799.0 -> "1799"."""
    if valeur is None:
        return ""
    if isinstance(valeur, float):
        if pd.isna(valeur):
            return ""
        if valeur.is_integer():
            return str(int(valeur))
    try:
        if pd.isna(valeur):
            return ""
    except (TypeError, ValueError):
        pass
    return str(valeur).strip()


def _parse_date(valeur):
    """Cellule -> (ok, date|None). Vide = (True, None) ; illisible = (False, None)."""
    if isinstance(valeur, datetime):  # couvre pd.Timestamp
        return (True, None) if pd.isna(valeur) else (True, valeur.date())
    if isinstance(valeur, date):
        return True, valeur
    s = _texte(valeur)
    if not s:
        return True, None
    # « 2016-07-11 00:00:00 » : on ne garde que la partie date
    d = _parse_date_fr(s) or _parse_date_fr(s.split()[0])
    return (d is not None), d


def _parse_decimal(valeur):
    """Cellule -> (ok, Decimal|None). Accepte la virgule décimale, les espaces
    de milliers et les symboles « € » / « % »."""
    s = _texte(valeur)
    if not s:
        return True, None
    s = re.sub(r"[\s  €%]", "", s).replace(",", ".")
    try:
        d = Decimal(s)
    except InvalidOperation:
        return False, None
    return d.is_finite(), d if d.is_finite() else None


def _parse_saison(valeur):
    """« 2016-2017 » -> ("2016-2017", date(2016, 7, 1), date(2017, 6, 30)), ou None."""
    m = RE_SAISON.match(_texte(valeur))
    if not m:
        return None
    an1, an2 = int(m.group(1)), int(m.group(2))
    if an2 != an1 + 1:
        return None
    return f"{an1}-{an2}", date(an1, 7, 1), date(an2, 6, 30)


def _init_api(id_role, nom_complet):
    api = ApiResponse(log_file="import_degats_agricoles.log")
    api.id_role = id_role
    api.nom_complet = nom_complet or "Utilisateur"
    api.return_journal = True
    api.add_log(
        f"Import dégâts agricoles lancé par {api.nom_complet} "
        f"(id_role: {id_role}) le "
        f"{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}.",
        with_timestamp=True,
    )
    return api


def actualiser_saison_courante():
    """`current = true` sur la saison la plus récente, `false` sur les autres."""
    id_recente = DB.session.execute(
        select(TSaisonAgricole.id_saison)
        .order_by(
            TSaisonAgricole.date_debut.desc().nullslast(),
            TSaisonAgricole.nom_saison.desc(),
        )
        .limit(1)
    ).scalar_one_or_none()
    if id_recente is not None:
        DB.session.execute(
            sql_update(TSaisonAgricole).values(
                current=(TSaisonAgricole.id_saison == id_recente)
            )
        )
    return id_recente


def recaler_sequence_declarations():
    """Fait repartir `id_declaration` juste après le plus grand id présent.

    Sans cela, chaque import avec mise à jour (suppression puis réinsertion des
    dossiers) continue la numérotation après les id supprimés, et les id
    grimpent de plusieurs milliers à chaque fois.

    La table est verrouillée en écriture jusqu'à la fin de la transaction, pour
    qu'aucune insertion concurrente ne prenne un id entre le recalage et
    l'insertion (les lectures restent possibles).
    """
    DB.session.execute(
        text("LOCK TABLE oeasc_agricole.t_declaration_agricole IN EXCLUSIVE MODE")
    )
    DB.session.execute(text("""
            SELECT setval(
                pg_get_serial_sequence(
                    'oeasc_agricole.t_declaration_agricole', 'id_declaration'
                ),
                COALESCE(
                    (SELECT MAX(id_declaration)
                     FROM oeasc_agricole.t_declaration_agricole),
                    0
                ) + 1,
                false
            )
            """))


# ---------------------------------------------------------------------------
#  Traitement
# ---------------------------------------------------------------------------


def traitement_import_degats_agricoles(
    path,
    id_saison=None,  # ignoré : la saison vient du fichier (signature commune aux imports)
    update="false",
    id_role=None,
    nom_complet=None,
    progress_callback=None,
):
    """Importe un fichier de dégâts agricoles.

    - Saisons et types de culture absents de la base : créés.
    - Un dossier est identifié par son numéro et regroupe plusieurs déclarations.
      `update` faux : les dossiers déjà en base sont ignorés ; `update` vrai :
      toutes les déclarations des numéros de dossier présents dans le fichier
      sont supprimées, puis remplacées par celles du fichier. Les dossiers
      absents du fichier ne sont jamais touchés.
    - La moindre valeur invalide annule tout l'import (aucune écriture).
    """
    do_update = str(update).lower() == "true"
    api = _init_api(id_role, nom_complet)
    _progress = _make_progress(progress_callback, 5)
    try:
        with _app_context():
            # --- 1. lecture ----------------------------------------------------
            ext = Path(path).suffix.lower()
            if ext not in EXTENSIONS_ACCEPTEES:
                api.add_error(
                    system_error=f"Extension refusée : {ext}",
                    user_message="Format de fichier non pris en charge "
                    f"(« {ext or 'sans extension'} »). Formats acceptés : "
                    + ", ".join(EXTENSIONS_ACCEPTEES),
                )
                return api
            try:
                df = lire_fichier(path)
            except Exception as e:  # noqa: BLE001
                api.add_error(
                    system_error=f"Lecture du fichier : {e}",
                    user_message="Impossible de lire le fichier.",
                )
                return api
            if df.empty:
                api.add_error(
                    system_error="Fichier vide.",
                    user_message="Le fichier ne contient aucune ligne de données.",
                )
                return api
            _progress(api, "Lecture du fichier")

            # --- 2. colonnes ---------------------------------------------------
            cols, approximations, manquantes = resoudre_colonnes(df.columns)
            for canon, reel, score in approximations:
                api.add_log(
                    f"Colonne « {' '.join(reel.split())} » interprétée comme "
                    f"« {ALIAS_COLONNES[canon][0]} » (ressemblance {score} %).",
                    type_log="WARNING",
                )
            if manquantes:
                api.add_error(
                    system_error=f"Colonnes manquantes : {manquantes}",
                    user_message="Colonnes introuvables dans le fichier : "
                    + ", ".join(ALIAS_COLONNES[c][0] for c in manquantes),
                )
                return api
            _progress(api, "Reconnaissance des colonnes")

            # --- 3. validation ligne par ligne, sans rien écrire --------------
            especes = _lookup_especes()  # {nom normalisé -> id_espece}
            communes = dict(
                DB.session.execute(
                    select(TCommunesArea.insee_com, TCommunesArea.id)
                ).all()
            )

            lignes = []  # dicts de valeurs + nom_saison / nom_culture à résoudre
            saisons_fichier = {}  # {nom_saison: (date_debut, date_fin)}
            erreurs = []
            for i, row in df.iterrows():
                num = i + 2  # n° de ligne dans le fichier (+1 entête, +1 index 1-based)
                err = []

                saison = _parse_saison(row[cols["saison"]])
                if saison is None:
                    err.append(
                        f"saison invalide « {_texte(row[cols['saison']])} » "
                        "(attendu : AAAA-AAAA)"
                    )

                numero_dossier = _texte(row[cols["numero_dossier"]])
                if not numero_dossier:
                    err.append("n° de dossier vide")

                insee = _texte(row[cols["code_insee"]]).upper()
                if insee.isdigit():
                    insee = insee.zfill(5)
                id_commune = communes.get(insee)
                if id_commune is None:
                    err.append(f"code INSEE inconnu « {insee} »")

                esp_val = _texte(row[cols["espece"]])
                esp_norm = _normalize(esp_val)
                id_espece = _match_espece(
                    ALIAS_ESPECES.get(esp_norm, esp_norm), especes
                )
                if id_espece is None:
                    err.append(f"espèce inconnue « {esp_val} »")

                valeurs = {}
                for champ in ("date_creation", "date_document"):
                    ok, valeurs[champ] = _parse_date(row[cols[champ]])
                    if not ok:
                        err.append(
                            f"date invalide « {_texte(row[cols[champ]])} » "
                            f"({ALIAS_COLONNES[champ][0]})"
                        )
                for champ in COLONNES_NUMERIQUES:
                    ok, valeurs[champ] = _parse_decimal(row[cols[champ]])
                    if not ok:
                        err.append(
                            f"nombre invalide « {_texte(row[cols[champ]])} » "
                            f"({ALIAS_COLONNES[champ][0]})"
                        )

                if err:
                    erreurs.append(f"ligne {num} : " + " ; ".join(err))
                    continue

                saisons_fichier[saison[0]] = saison[1:]
                lignes.append(
                    dict(
                        valeurs,
                        nom_saison=saison[0],
                        numero_dossier=numero_dossier,
                        id_commune=id_commune,
                        id_espece=id_espece,
                        nom_culture=" ".join(_texte(row[cols["culture"]]).split()),
                        unit_quantite_detruite=_texte(
                            row[cols["unit_quantite_detruite"]]
                        )
                        or None,
                    )
                )
            _progress(api, "Validation des données")

            # abandon si la moindre erreur (aucune écriture faite)
            if erreurs:
                return _abandon_erreurs(api, erreurs)

            # --- 4. saisons et types de culture --------------------------------
            saisons = {
                s.nom_saison: s.id_saison
                for s in DB.session.execute(select(TSaisonAgricole)).scalars()
            }
            saisons_creees = sorted(set(saisons_fichier) - set(saisons))
            for nom in saisons_creees:
                debut, fin = saisons_fichier[nom]
                s = TSaisonAgricole(
                    nom_saison=nom, date_debut=debut, date_fin=fin, current=False
                )
                DB.session.add(s)
                DB.session.flush()
                saisons[nom] = s.id_saison
            actualiser_saison_courante()

            cultures = {
                _normalize_entete(c.nom_culture): c.id_culture
                for c in DB.session.execute(select(TTypeCulture)).scalars()
            }
            cultures_creees = []
            nb_sans_culture = 0
            for ligne in lignes:
                ligne["id_saison"] = saisons[ligne.pop("nom_saison")]
                nom = ligne.pop("nom_culture")
                if not nom:
                    ligne["id_culture"] = None
                    nb_sans_culture += 1
                    continue
                cle = _normalize_entete(nom)
                if cle not in cultures:
                    c = TTypeCulture(nom_culture=nom)
                    DB.session.add(c)
                    DB.session.flush()
                    cultures[cle] = c.id_culture
                    cultures_creees.append(nom)
                ligne["id_culture"] = cultures[cle]
            _progress(api, "Saisons et types de culture")

            # --- 5. déclarations ----------------------------------------------
            # un dossier est identifié par son seul numéro, quelle que soit la saison
            dossiers_fichier = {l["numero_dossier"] for l in lignes}
            dossiers_existants = set(
                DB.session.execute(
                    select(TDeclarationAgricole.numero_dossier)
                    .where(TDeclarationAgricole.numero_dossier.in_(dossiers_fichier))
                    .distinct()
                ).scalars()
            )

            nb_suppr = 0
            if do_update:
                # toutes les déclarations de ces dossiers sont supprimées : après
                # l'import, ils ne contiennent plus que les lignes du fichier
                if dossiers_existants:
                    nb_suppr = (
                        DB.session.execute(
                            delete(TDeclarationAgricole).where(
                                TDeclarationAgricole.numero_dossier.in_(
                                    dossiers_existants
                                )
                            )
                        ).rowcount
                        or 0
                    )
                a_inserer = lignes
            else:
                a_inserer = [
                    l for l in lignes if l["numero_dossier"] not in dossiers_existants
                ]

            if a_inserer:
                recaler_sequence_declarations()
                DB.session.execute(insert(TDeclarationAgricole), a_inserer)
            DB.session.commit()
            _progress(api, "Enregistrement")

            # --- bilan ----------------------------------------------------------
            if saisons_creees:
                api.add_log(
                    f"{len(saisons_creees)} saison(s) créée(s) : "
                    + ", ".join(saisons_creees),
                    type_log="INFO",
                )
            if cultures_creees:
                api.add_log(
                    f"{len(cultures_creees)} type(s) de culture créé(s) : "
                    + ", ".join(cultures_creees),
                    type_log="INFO",
                )
            if nb_sans_culture:
                api.add_log(
                    f"{nb_sans_culture} ligne(s) sans culture renseignée.",
                    type_log="WARNING",
                )
            nb_nouveaux = len(dossiers_fichier - dossiers_existants)
            if do_update:
                api.add_log(
                    f"{len(dossiers_existants)} dossier(s) déjà en base remplacé(s) "
                    f"({nb_suppr} déclaration(s) supprimée(s)).",
                    type_log="INFO",
                )
            elif dossiers_existants:
                api.add_log(
                    f"{len(dossiers_existants)} dossier(s) déjà en base ignoré(s) "
                    f"({len(lignes) - len(a_inserer)} ligne(s)). Cochez « Mettre à "
                    "jour les données existantes » pour les remplacer.",
                    type_log="WARNING",
                )
            api.add_log(
                f"{len(a_inserer)} déclaration(s) insérée(s), dont "
                f"{nb_nouveaux} nouveau(x) dossier(s).",
                type_log="INFO",
            )
            api.success = True
            api.message = (
                f"Import des dégâts agricoles terminé : {len(a_inserer)} "
                "déclaration(s) insérée(s)."
            )
            return api
    except Exception as e:  # noqa: BLE001
        DB.session.rollback()
        current_app.logger.exception("import degats agricoles")
        api.add_error(system_error=str(e), user_message=f"Erreur inattendue : {e}")
        return api
