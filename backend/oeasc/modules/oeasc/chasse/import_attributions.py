"""
Traitement des imports liés au plan de chasse annuel (« attributions de chasse »).

Trois imports CSV séquentiels, chacun conditionné par le précédent (cf.
`get_etat_import_attributions`) :

1. `traitement_import_saison_dates`        -> oeasc_chasse.t_saison_dates
2. `traitement_import_attribution_massifs` -> oeasc_chasse.t_attribution_massifs
3. `traitement_import_attributions`        -> oeasc_chasse.t_attributions

Ces fonctions remplacent les scripts SQL manuels historiques
(`1_import_saison_chasse.sql`, `2_import_plan_chasse.sql`).

Elles sont appelées :
  - en tâche de fond par `import_async._traiter` (thread + suivi JSON + polling),
    avec la même signature que `traitement_import_realisation_chasse`
    `(path_csv, id_saison, update, id_role=, nom_complet=, progress_callback=)` ;
    `id_saison` et `update` sont ignorés : la saison courante fait foi.
  - directement dans un script de vérification (sous `with app.app_context()`).

Elles retournent toujours un objet `ApiResponse` (`.success`, `.message`,
`.journal` — tags `[INFO]/[ERROR]/[WARNING]`).

NB : ne pas importer `import_async` ici (import circulaire).
"""

import csv
import re
import unicodedata
from contextlib import nullcontext
from datetime import datetime

import pandas as pd
from flask import current_app, has_app_context
from sqlalchemy import select, delete

from app import app

from oeasc.utils.apiResponse import ApiResponse
from oeasc.modules.oeasc.chasse.models import (
    TSaisons,
    TSaisonDates,
    TAttributionMassifs,
    TAttributions,
    TTypeBracelets,
    TZoneIndicatives,
    TZoneCynegetiques,
)
from oeasc.modules.oeasc.commons.models import TEspeces, TNomenclaturesOeasc

config = current_app.config
DB = config["DB"]

# mnémonique du type de nomenclature « mode de chasse » (label_default : Affut / Approche / Battue / Individuel)
MNEMONIQUE_MODE_CHASSE = "OEASC_MOD_CHASSE"

# nombre maximum d'erreurs listées dans le message utilisateur
MAX_ERREURS_MESSAGE = 20


def _app_context():
    """Contexte applicatif seulement si aucun n'est déjà actif (thread d'import
    async, route Flask et scripts fournissent déjà le leur — on réutilise alors
    la même session)."""
    return nullcontext() if has_app_context() else app.app_context()


# ---------------------------------------------------------------------------
#  Helpers
# ---------------------------------------------------------------------------


def _normalize(valeur):
    """Minuscule, sans accent, sans espaces de bord. Sert au matching insensible
    à la casse/aux accents des entêtes de colonnes et des valeurs."""
    if valeur is None:
        return ""
    s = unicodedata.normalize("NFKD", str(valeur))
    s = s.encode("ascii", "ignore").decode("ascii")
    return s.strip().lower()


def _normalize_saison(valeur):
    """« 2026/2027 », « 2026 - 2027 » -> « 2026-2027 » pour comparer à nom_saison."""
    return re.sub(r"\s+", "", str(valeur or "")).replace("/", "-")


def _detect_sep(path):
    """Détection du séparateur (`;` ou `,`) : même heuristique que
    `importation_csv.etape__récuperation_csv` (comptage sur un échantillon)."""
    with open(path, "rb") as f:
        sample = f.read(4096).decode("utf-8-sig", errors="replace")
    return ";" if sample.count(";") > sample.count(",") else ","


def lire_csv_auto(path):
    """Lit le CSV en autodétectant le séparateur ; force les entêtes en
    minuscules. Tout est lu en texte pour maîtriser le parsing nous-mêmes.

    Répare les lignes « sur-quotées » par certains exports Excel : quand un champ
    contient le séparateur, la ligne entière se retrouve entre guillemets et donc
    dans la seule première colonne — on la redécoupe alors nous-mêmes."""
    sep = _detect_sep(path)
    df = pd.read_csv(
        path, sep=sep, encoding="utf-8-sig", dtype=str, keep_default_na=False
    )
    df.columns = [str(c).strip().lower() for c in df.columns]

    if len(df.columns) >= 2:
        premiere = df.columns[0]
        autres = list(df.columns[1:])
        a_reparer = df.index[
            df[autres].eq("").all(axis=1)
            & df[premiere].str.contains(re.escape(sep), regex=True)
        ]
        for idx in a_reparer:
            parts = next(csv.reader([df.at[idx, premiere]], delimiter=sep))
            for col, val in zip(df.columns, parts):
                df.at[idx, col] = val.strip()

    return df, sep


def _resoudre_colonnes(df, alias_map):
    """alias_map : {nom_canonique: [variantes...]}. Compare via `_normalize`.
    Retourne (mapping {canonique: nom_colonne_reel}, [canoniques manquants])."""
    cols_norm = {_normalize(c): c for c in df.columns}
    mapping = {}
    manquantes = []
    for canon, variantes in alias_map.items():
        trouve = None
        for candidat in [canon, *variantes]:
            reel = cols_norm.get(_normalize(candidat))
            if reel is not None:
                trouve = reel
                break
        if trouve is None:
            manquantes.append(canon)
        else:
            mapping[canon] = trouve
    return mapping, manquantes


def _parse_date_fr(valeur):
    s = str(valeur or "").strip()
    if not s:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _parse_int(valeur):
    s = str(valeur or "").strip()
    if s == "" or s.lower() in ("nan", "none"):
        return None
    try:
        return int(float(s.replace(",", ".")))
    except (ValueError, TypeError):
        return None


def _split_modes(valeur):
    """« Approche, Affut » -> ['Approche', 'Affut'] (séparateur `,` ou `;`)."""
    s = str(valeur or "").strip()
    if not s:
        return []
    return [p.strip() for p in re.split(r"\s*[,;]\s*", s) if p.strip()]


def _init_api(id_role, nom_complet):
    api = ApiResponse(log_file="import_attributions.log")
    api.id_role = id_role
    api.nom_complet = nom_complet or "Utilisateur"
    api.return_journal = True
    api.add_log(
        f"Import plan de chasse lancé par {api.nom_complet} "
        f"(id_role: {id_role}) le "
        f"{pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}.",
        with_timestamp=True,
    )
    return api


def _make_progress(progress_callback, total):
    compteur = {"n": 0}

    def _progress(api, label=""):
        compteur["n"] += 1
        if progress_callback is not None:
            try:
                progress_callback(api, label, compteur["n"], total)
            except (
                Exception
            ):  # noqa: BLE001 - la progression ne doit jamais casser l'import
                pass

    return _progress


def _abandon_erreurs(api, erreurs, prefixe="Import annulé"):
    """Journalise chaque erreur puis marque l'ApiResponse en échec avec un
    message utilisateur récapitulatif."""
    for e in erreurs:
        api.add_log(e, type_log="ERROR")
    apercu = " | ".join(erreurs[:MAX_ERREURS_MESSAGE])
    if len(erreurs) > MAX_ERREURS_MESSAGE:
        apercu += f" … (+{len(erreurs) - MAX_ERREURS_MESSAGE} autres)"
    message = f"{prefixe} ({len(erreurs)} erreur(s)) : {apercu}"
    # system_error concis : le détail complet est déjà dans les lignes [ERROR]
    api.add_error(system_error=message, user_message=message)
    return api


def _saison_courante():
    return (
        DB.session.execute(select(TSaisons).where(TSaisons.current.is_(True)))
        .scalars()
        .first()
    )


def _lookup_especes():
    """{nom_espece normalisé: id_espece}."""
    return {
        _normalize(nom): id_e
        for id_e, nom in DB.session.execute(
            select(TEspeces.id_espece, TEspeces.nom_espece)
        ).all()
    }


def _match_espece(valeur, especes):
    """Gère « Cerf », « Cerf élaphe », « Chevreuil européen »…"""
    n = _normalize(valeur)
    if not n:
        return None
    for nom_norm, id_e in especes.items():
        if n == nom_norm or n.startswith(nom_norm):
            return id_e
    return None


# ---------------------------------------------------------------------------
#  1. Dates de saison par mode de chasse -> t_saison_dates
# ---------------------------------------------------------------------------


def traitement_import_saison_dates(
    path_csv,
    id_saison=None,
    update="false",
    id_role=None,
    nom_complet=None,
    progress_callback=None,
):
    api = _init_api(id_role, nom_complet)
    _progress = _make_progress(progress_callback, 4)
    try:
        with _app_context():
            saison = _saison_courante()
            if saison is None:
                api.add_error(
                    system_error="Aucune saison courante (current=true).",
                    user_message="Aucune saison en cours. Créez la nouvelle saison "
                    "dans Données chasse → onglet Saisons.",
                )
                return api
            id_saison = saison.id_saison

            try:
                df, _sep = lire_csv_auto(path_csv)
            except Exception as e:  # noqa: BLE001
                api.add_error(
                    system_error=f"Lecture CSV : {e}",
                    user_message="Impossible de lire le fichier CSV.",
                )
                return api
            _progress(api, "Lecture du fichier CSV")

            cols, manquantes = _resoudre_colonnes(
                df,
                {
                    "espece": ["espèce", "nom_espece", "nom_vern"],
                    "date_debut": ["date debut", "date_debut"],
                    "date_fin": ["date fin", "date_fin"],
                    "type_chasse": ["type chasse", "mode_chasse", "mode chasse"],
                },
            )
            if manquantes:
                api.add_error(
                    system_error=f"Colonnes manquantes : {manquantes}",
                    user_message="Colonnes manquantes dans le fichier : "
                    + ", ".join(manquantes),
                )
                return api

            especes = _lookup_especes()
            modes = {
                _normalize(label): id_n
                for id_n, label in DB.session.execute(
                    select(
                        TNomenclaturesOeasc.id_nomenclature,
                        TNomenclaturesOeasc.label_default,
                    ).where(TNomenclaturesOeasc.type == MNEMONIQUE_MODE_CHASSE)
                ).all()
            }

            lignes = []
            erreurs = []
            for i, row in df.iterrows():
                num = i + 2  # +1 entête, +1 pour un index humain
                esp_val = row[cols["espece"]]
                id_espece = _match_espece(esp_val, especes)
                if id_espece is None:
                    erreurs.append(f"ligne {num} : espèce inconnue « {esp_val} »")
                    continue
                d_deb = _parse_date_fr(row[cols["date_debut"]])
                d_fin = _parse_date_fr(row[cols["date_fin"]])
                if d_deb is None or d_fin is None:
                    erreurs.append(
                        f"ligne {num} : date invalide "
                        f"(« {row[cols['date_debut']]} » / « {row[cols['date_fin']]} »)"
                    )
                    continue
                modes_ligne = _split_modes(row[cols["type_chasse"]])
                if not modes_ligne:
                    erreurs.append(f"ligne {num} : aucun mode de chasse renseigné")
                    continue
                for mode in modes_ligne:
                    id_nom = modes.get(_normalize(mode))
                    if id_nom is None:
                        erreurs.append(
                            f"ligne {num} : mode de chasse inconnu « {mode} »"
                        )
                        continue
                    lignes.append(
                        dict(
                            id_saison=id_saison,
                            id_espece=id_espece,
                            date_debut=d_deb,
                            date_fin=d_fin,
                            id_nomenclature_type_chasse=id_nom,
                        )
                    )
            _progress(api, "Validation des données")

            if erreurs:
                return _abandon_erreurs(api, erreurs)
            if not lignes:
                api.add_error(
                    system_error="Aucune ligne exploitable.",
                    user_message="Aucune donnée exploitable dans le fichier.",
                )
                return api

            nb_suppr = (
                DB.session.execute(
                    delete(TSaisonDates).where(TSaisonDates.id_saison == id_saison)
                ).rowcount
                or 0
            )
            DB.session.add_all([TSaisonDates(**ligne) for ligne in lignes])
            DB.session.commit()
            _progress(api, "Enregistrement")

            api.add_log(
                f"Saison {saison.nom_saison} : {nb_suppr} ligne(s) supprimée(s), "
                f"{len(lignes)} ligne(s) insérée(s) dans t_saison_dates.",
                type_log="INFO",
            )
            api.success = True
            api.message = f"Import des dates de saison terminé : {len(lignes)} lignes."
            return api
    except Exception as e:  # noqa: BLE001
        DB.session.rollback()
        current_app.logger.exception("import saison_dates")
        api.add_error(system_error=str(e), user_message=f"Erreur inattendue : {e}")
        return api


# ---------------------------------------------------------------------------
#  2. Attributions par massif -> t_attribution_massifs
# ---------------------------------------------------------------------------


def traitement_import_attribution_massifs(
    path_csv,
    id_saison=None,
    update="false",
    id_role=None,
    nom_complet=None,
    progress_callback=None,
):
    api = _init_api(id_role, nom_complet)
    _progress = _make_progress(progress_callback, 4)
    try:
        with _app_context():
            saison = _saison_courante()
            if saison is None:
                api.add_error(
                    system_error="Aucune saison courante.",
                    user_message="Aucune saison en cours.",
                )
                return api
            id_saison = saison.id_saison

            try:
                df, _sep = lire_csv_auto(path_csv)
            except Exception as e:  # noqa: BLE001
                api.add_error(
                    system_error=f"Lecture CSV : {e}",
                    user_message="Impossible de lire le fichier CSV.",
                )
                return api
            _progress(api, "Lecture du fichier CSV")

            cols, manquantes = _resoudre_colonnes(
                df,
                {
                    "nom_vern": ["nom vern", "espèce", "espece", "nom_espece"],
                    "massif": ["massif", "zone_cynegetique", "nom_zone_cynegetique"],
                    "saison": ["saison", "annee", "année"],
                    "nb_affecte_max": ["nb affecte max", "nb_affecte_max", "max"],
                },
            )
            if manquantes:
                api.add_error(
                    system_error=f"Colonnes manquantes : {manquantes}",
                    user_message="Colonnes manquantes dans le fichier : "
                    + ", ".join(manquantes),
                )
                return api
            cols_min, _ = _resoudre_colonnes(
                df, {"nb_affecte_min": ["nb affecte min", "nb_affecte_min", "min"]}
            )
            col_min = cols_min.get("nb_affecte_min")

            especes = _lookup_especes()
            zc_lookup = {
                _normalize(nom): id_zc
                for id_zc, nom in DB.session.execute(
                    select(
                        TZoneCynegetiques.id_zone_cynegetique,
                        TZoneCynegetiques.nom_zone_cynegetique,
                    )
                ).all()
            }

            nom_saison_norm = _normalize_saison(saison.nom_saison)
            lignes = []
            erreurs = []
            for i, row in df.iterrows():
                num = i + 2
                sais_val = row[cols["saison"]]
                if _normalize_saison(sais_val) != nom_saison_norm:
                    erreurs.append(
                        f"ligne {num} : année « {sais_val} » ≠ saison en cours "
                        f"« {saison.nom_saison} »"
                    )
                    continue
                nv = row[cols["nom_vern"]]
                id_espece = _match_espece(nv, especes)
                if id_espece is None:
                    erreurs.append(f"ligne {num} : espèce inconnue « {nv} »")
                    continue
                mv = str(row[cols["massif"]]).strip()
                id_zc = zc_lookup.get(_normalize(mv.rstrip(" ,")))
                if id_zc is None:
                    erreurs.append(f"ligne {num} : massif inconnu « {mv} »")
                    continue
                nb_max = _parse_int(row[cols["nb_affecte_max"]])
                if nb_max is None:
                    erreurs.append(
                        f"ligne {num} : nb_affecte_max invalide "
                        f"« {row[cols['nb_affecte_max']]} »"
                    )
                    continue
                nb_min = 0
                if col_min:
                    raw = str(row[col_min]).strip()
                    if raw:
                        nb_min = _parse_int(raw)
                        if nb_min is None:
                            erreurs.append(
                                f"ligne {num} : nb_affecte_min invalide « {raw} »"
                            )
                            continue
                lignes.append(
                    dict(
                        id_saison=id_saison,
                        id_espece=id_espece,
                        id_zone_cynegetique=id_zc,
                        nb_affecte_min=nb_min,
                        nb_affecte_max=nb_max,
                    )
                )
            _progress(api, "Validation des données")

            if erreurs:
                return _abandon_erreurs(api, erreurs)
            if not lignes:
                api.add_error(
                    system_error="Aucune ligne exploitable.",
                    user_message="Aucune donnée exploitable dans le fichier.",
                )
                return api

            nb_suppr = (
                DB.session.execute(
                    delete(TAttributionMassifs).where(
                        TAttributionMassifs.id_saison == id_saison
                    )
                ).rowcount
                or 0
            )
            DB.session.add_all([TAttributionMassifs(**ligne) for ligne in lignes])
            DB.session.commit()
            _progress(api, "Enregistrement")

            api.add_log(
                f"Saison {saison.nom_saison} : {nb_suppr} ligne(s) supprimée(s), "
                f"{len(lignes)} ligne(s) insérée(s) dans t_attribution_massifs.",
                type_log="INFO",
            )
            api.success = True
            api.message = (
                f"Import des attributions par massif terminé : {len(lignes)} lignes."
            )
            return api
    except Exception as e:  # noqa: BLE001
        DB.session.rollback()
        current_app.logger.exception("import attribution_massifs")
        api.add_error(system_error=str(e), user_message=f"Erreur inattendue : {e}")
        return api


# ---------------------------------------------------------------------------
#  3. Attributions de bracelets -> t_attributions (synchronisation incrémentale)
# ---------------------------------------------------------------------------

_RE_TERRITOIRE = re.compile(r"^\s*(\d+)\s*:\s*(.+)$")


def traitement_import_attributions(
    path_csv,
    id_saison=None,
    update="false",
    id_role=None,
    nom_complet=None,
    progress_callback=None,
):
    api = _init_api(id_role, nom_complet)
    _progress = _make_progress(progress_callback, 5)
    try:
        with _app_context():
            saison = _saison_courante()
            if saison is None:
                api.add_error(
                    system_error="Aucune saison courante.",
                    user_message="Aucune saison en cours.",
                )
                return api
            id_saison = saison.id_saison

            try:
                df, _sep = lire_csv_auto(path_csv)
            except Exception as e:  # noqa: BLE001
                api.add_error(
                    system_error=f"Lecture CSV : {e}",
                    user_message="Impossible de lire le fichier CSV.",
                )
                return api
            _progress(api, "Lecture du fichier CSV")

            cols, manquantes = _resoudre_colonnes(
                df,
                {
                    "espece": ["espèce", "espece", "type_bracelet", "bracelet"],
                    "quantite": ["quantité", "quantite", "qte"],
                    "n_debut": [
                        "n° debut",
                        "n°debut",
                        "n_debut",
                        "n debut",
                        "numero debut",
                        "no debut",
                        "n° début",
                        "debut",
                    ],
                    "n_fin": [
                        "n° fin",
                        "n°fin",
                        "n_fin",
                        "n fin",
                        "numero fin",
                        "no fin",
                        "fin",
                    ],
                    "annee": ["annee", "année", "an"],
                },
            )
            if manquantes:
                api.add_error(
                    system_error=f"Colonnes manquantes : {manquantes}",
                    user_message="Colonnes manquantes dans le fichier : "
                    + ", ".join(manquantes),
                )
                return api

            zi_col_map, _ = _resoudre_colonnes(
                df, {"zi": ["zi", "id_zi", "code_zi", "num_zi", "zone_indicative"]}
            )
            terr_col_map, _ = _resoudre_colonnes(
                df, {"territoire": ["territoire", "territ"]}
            )
            col_zi = zi_col_map.get("zi")
            col_terr = terr_col_map.get("territoire")
            if not col_zi and not col_terr:
                api.add_error(
                    system_error="Ni colonne 'zi' ni colonne 'territoire'.",
                    user_message="Le fichier doit contenir une colonne « zi » ou "
                    "une colonne « TERRITOIRE » de la forme « id_zi: nom_zi ».",
                )
                return api

            # {code_zone_indicative -> (id_zone_indicative, id_zone_cynegetique)}
            zi_lookup = {}
            for code, id_zi, id_zc in DB.session.execute(
                select(
                    TZoneIndicatives.code_zone_indicative,
                    TZoneIndicatives.id_zone_indicative,
                    TZoneIndicatives.id_zone_cynegetique,
                )
            ).all():
                zi_lookup[str(code).strip()] = (id_zi, id_zc)

            tb_lookup = {
                _normalize(code): (id_tb, code)
                for id_tb, code in DB.session.execute(
                    select(
                        TTypeBracelets.id_type_bracelet,
                        TTypeBracelets.code_type_bracelet,
                    )
                ).all()
            }

            nom_saison_norm = _normalize_saison(saison.nom_saison)
            # numero_bracelet -> dict(id_type_bracelet, id_zone_indicative_affectee, id_zone_cynegetique_affectee)
            cible = {}
            erreurs = []
            for i, row in df.iterrows():
                num = i + 2

                an = row[cols["annee"]]
                if _normalize_saison(an) != nom_saison_norm:
                    erreurs.append(
                        f"ligne {num} : année « {an} » ≠ saison en cours "
                        f"« {saison.nom_saison} »"
                    )
                    continue

                code_zi = str(row[col_zi]).strip() if col_zi else ""
                if not code_zi and col_terr:
                    m = _RE_TERRITOIRE.match(str(row[col_terr]))
                    if m:
                        code_zi = m.group(1).strip()
                if not code_zi:
                    erreurs.append(
                        f"ligne {num} : zone indicative (zi) introuvable "
                        "(colonne zi vide et TERRITOIRE non conforme)"
                    )
                    continue
                zi_hit = zi_lookup.get(code_zi)
                if zi_hit is None and code_zi.isdigit():
                    zi_hit = zi_lookup.get(str(int(code_zi)))
                if zi_hit is None:
                    erreurs.append(f"ligne {num} : zi « {code_zi} » inconnue")
                    continue
                id_zi, id_zc = zi_hit

                esp = str(row[cols["espece"]]).strip()
                tb = tb_lookup.get(_normalize(esp))
                if tb is None:
                    erreurs.append(
                        f"ligne {num} : type de bracelet / espèce « {esp} » inconnu"
                    )
                    continue
                id_tb, code_tb = tb

                n_deb = _parse_int(row[cols["n_debut"]])
                n_fin = _parse_int(row[cols["n_fin"]])
                qte = _parse_int(row[cols["quantite"]])
                if n_deb is None or n_fin is None or qte is None:
                    erreurs.append(
                        f"ligne {num} : N° debut / N° fin / Quantité invalides"
                    )
                    continue
                if n_fin < n_deb:
                    erreurs.append(
                        f"ligne {num} : N° fin ({n_fin}) < N° debut ({n_deb})"
                    )
                    continue
                if qte != (n_fin - n_deb + 1):
                    erreurs.append(
                        f"ligne {num} : Quantité {qte} ≠ {n_fin - n_deb + 1} "
                        f"(N° fin - N° debut + 1) pour zi {code_zi} / {esp}"
                    )
                    continue

                for n in range(n_deb, n_fin + 1):
                    numero = f"{code_tb}00{n}"
                    cible[numero] = dict(
                        id_type_bracelet=id_tb,
                        id_zone_indicative_affectee=id_zi,
                        id_zone_cynegetique_affectee=id_zc,
                    )
            _progress(api, "Validation des données")

            if erreurs:
                return _abandon_erreurs(api, erreurs)
            if not cible:
                api.add_error(
                    system_error="Aucune attribution exploitable.",
                    user_message="Aucune attribution exploitable dans le fichier.",
                )
                return api

            existant = {
                a.numero_bracelet: a
                for a in DB.session.execute(
                    select(TAttributions).where(TAttributions.id_saison == id_saison)
                )
                .scalars()
                .all()
            }
            _progress(api, "Comparaison avec l'existant")

            a_inserer = [k for k in cible if k not in existant]
            a_supprimer = [k for k in existant if k not in cible]
            a_maj = []
            for k, c in cible.items():
                a = existant.get(k)
                if a is None:
                    continue
                if (
                    a.id_type_bracelet != c["id_type_bracelet"]
                    or a.id_zone_indicative_affectee != c["id_zone_indicative_affectee"]
                    or a.id_zone_cynegetique_affectee
                    != c["id_zone_cynegetique_affectee"]
                ):
                    a_maj.append((a, c))

            now = datetime.now()
            for k in a_inserer:
                c = cible[k]
                DB.session.add(
                    TAttributions(
                        id_saison=id_saison,
                        numero_bracelet=k,
                        id_type_bracelet=c["id_type_bracelet"],
                        id_zone_indicative_affectee=c["id_zone_indicative_affectee"],
                        id_zone_cynegetique_affectee=c["id_zone_cynegetique_affectee"],
                        meta_create_date=now,
                        meta_update_date=now,
                    )
                )
            for a, c in a_maj:
                a.id_type_bracelet = c["id_type_bracelet"]
                a.id_zone_indicative_affectee = c["id_zone_indicative_affectee"]
                a.id_zone_cynegetique_affectee = c["id_zone_cynegetique_affectee"]
                a.meta_update_date = now

            protegees = []
            nb_supprimees = 0
            for k in a_supprimer:
                a = existant[k]
                if a.id_realisation is not None:
                    protegees.append(k)
                else:
                    DB.session.delete(a)
                    nb_supprimees += 1

            DB.session.commit()
            _progress(api, "Synchronisation")

            api.add_log(
                f"Saison {saison.nom_saison} : {len(a_inserer)} attribution(s) "
                f"ajoutée(s), {len(a_maj)} mise(s) à jour, "
                f"{nb_supprimees} supprimée(s).",
                type_log="INFO",
            )
            if protegees:
                api.add_log(
                    f"{len(protegees)} attribution(s) absente(s) du fichier mais "
                    "conservée(s) car une réalisation y est rattachée : "
                    + ", ".join(protegees[:50])
                    + (" …" if len(protegees) > 50 else ""),
                    type_log="WARNING",
                )
            api.success = True
            api.message = (
                f"Import des attributions terminé : +{len(a_inserer)} / "
                f"~{len(a_maj)} / -{nb_supprimees}."
            )
            return api
    except Exception as e:  # noqa: BLE001
        DB.session.rollback()
        current_app.logger.exception("import attributions")
        api.add_error(system_error=str(e), user_message=f"Erreur inattendue : {e}")
        return api


# ---------------------------------------------------------------------------
#  État d'avancement (pilote le déverrouillage des étapes côté frontend)
# ---------------------------------------------------------------------------


def get_etat_import_attributions():
    """Renvoie l'état des 4 étapes pour la saison courante."""
    with _app_context():
        saison = _saison_courante()
        if saison is None:
            return {
                "saison_courante": None,
                "saison_ok": False,
                "saison_dates_ok": False,
                "attribution_massifs_ok": False,
                "attributions_ok": False,
            }

        aujourdhui = datetime.now().date()
        saison_ok = saison.date_fin is None or aujourdhui <= saison.date_fin

        def _existe(model):
            return (
                DB.session.execute(
                    select(model.id_saison)
                    .where(model.id_saison == saison.id_saison)
                    .limit(1)
                ).first()
                is not None
            )

        return {
            "saison_courante": {
                "id_saison": saison.id_saison,
                "nom_saison": saison.nom_saison,
                "date_debut": (
                    saison.date_debut.isoformat() if saison.date_debut else None
                ),
                "date_fin": saison.date_fin.isoformat() if saison.date_fin else None,
            },
            "saison_ok": bool(saison_ok),
            "saison_dates_ok": _existe(TSaisonDates),
            "attribution_massifs_ok": _existe(TAttributionMassifs),
            "attributions_ok": _existe(TAttributions),
        }
