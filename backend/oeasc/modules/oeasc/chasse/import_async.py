"""
Traitement asynchrone de l'import CSV Geochasse.

La route HTTP se contente d'enregistrer le fichier + créer un fichier de suivi
JSON, puis délègue le traitement long à un thread de fond. Le frontend suit
l'avancement en interrogeant `import/status/<id_import>`.

Le suivi est un simple fichier `<id_import>.json` dans `static/imports_chasse/`,
lisible par n'importe quel worker gunicorn. Pas d'historique conservé : les
fichiers de plus d'un an (JSON de suivi + CSV importés) sont purgés à chaque
nouvel import.
"""

import json
import os
import re
import secrets
import threading
import time
from datetime import datetime
from pathlib import Path

from flask import current_app

from .importation_csv import traitement_import_realisation_chasse

config = current_app.config

DOSSIER_SUIVI = Path(config["ROOT_DIR"]) / "static/imports_chasse"
DOSSIER_SUIVI.mkdir(parents=True, exist_ok=True)

# format d'un id_import : AAAAMMJJ-HHMMSS-xxxx (xxxx = 4 hexa aléatoires)
RE_ID_IMPORT = re.compile(r"^\d{8}-\d{6}-[0-9a-f]{4}$")

# au-delà de ce délai sans fin, un import resté "EN_COURS" est considéré comme
# interrompu (worker gunicorn recyclé pendant le traitement, etc.)
DELAI_IMPORT_BLOQUE_MIN = 30

# rétention des fichiers de suivi + CSV importés
RETENTION_JOURS = 365


def purger_vieux_suivis(jours=RETENTION_JOURS):
    """Supprime les fichiers de suivi JSON et les CSV importés de plus de `jours`
    jours. Best effort : toute erreur est ignorée."""
    limite = time.time() - jours * 86400
    try:
        for f in DOSSIER_SUIVI.iterdir():
            if f.suffix.lower() not in (".json", ".csv"):
                continue
            try:
                if f.stat().st_mtime < limite:
                    f.unlink(missing_ok=True)
            except OSError:
                pass
    except OSError:
        pass


def _chemin_suivi(id_import):
    """Chemin du fichier de suivi, après validation stricte de l'id (anti path traversal)."""
    if not RE_ID_IMPORT.match(id_import or ""):
        return None
    chemin = (DOSSIER_SUIVI / f"{id_import}.json").resolve()
    if chemin.parent != DOSSIER_SUIVI.resolve():
        return None
    return chemin


def _ecrire_suivi(id_import, **champs):
    """Met à jour le fichier de suivi (lecture -> fusion -> écriture atomique).

    Un seul writer par fichier (le thread de l'import) : pas de verrou nécessaire,
    l'écriture atomique protège juste le lecteur (polling) d'un fichier tronqué.
    """
    chemin = _chemin_suivi(id_import)
    if chemin is None:
        return
    data = {}
    if chemin.is_file():
        try:
            data = json.loads(chemin.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
    data.update(champs)
    data["id_import"] = id_import
    tmp = chemin.with_suffix(".json.tmp")
    tmp.write_text(
        json.dumps(data, default=str, ensure_ascii=False), encoding="utf-8"
    )
    os.replace(tmp, chemin)


def creer_suivi(
    id_saison, do_update, nom_fichier, chemin_fichier, id_role, nom_complet
):
    """Crée le fichier de suivi (statut EN_ATTENTE) et renvoie son id_import."""
    purger_vieux_suivis()
    id_import = "{}-{}".format(
        datetime.now().strftime("%Y%m%d-%H%M%S"), secrets.token_hex(2)
    )
    _ecrire_suivi(
        id_import,
        statut="EN_ATTENTE",
        id_saison=id_saison,
        do_update=bool(do_update),
        nom_fichier=nom_fichier,
        chemin_fichier=str(chemin_fichier),
        id_role=id_role,
        nom_complet=nom_complet,
        journal=[],
        success=None,
        message=None,
        meta_create_date=datetime.now().isoformat(),
        date_fin=None,
    )
    return id_import


def lire_suivi(id_import):
    """Renvoie l'état courant d'un import (dict) ou None si inconnu."""
    chemin = _chemin_suivi(id_import)
    if chemin is None or not chemin.is_file():
        return None
    try:
        data = json.loads(chemin.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None

    # import resté "EN_COURS" trop longtemps => probablement interrompu
    if data.get("statut") == "EN_COURS":
        debut = data.get("meta_create_date")
        try:
            age_min = (
                datetime.now() - datetime.fromisoformat(debut)
            ).total_seconds() / 60
        except (TypeError, ValueError):
            age_min = 0
        if age_min > DELAI_IMPORT_BLOQUE_MIN:
            data["statut"] = "ERREUR"
            data["message"] = (
                "Le traitement semble interrompu (délai dépassé). Relancez l'import."
            )

    data["journal"] = data.get("journal") or []
    return data


def _traiter(app, id_import, chemin_fichier, id_saison, do_update, id_role, nom_complet):
    with app.app_context():
        try:
            _ecrire_suivi(id_import, statut="EN_COURS")

            def progress(api, label="", num=0, total=0):
                champs = {"journal": list(api.journal)}
                if label:
                    champs["message"] = (
                        f"Étape {num}/{total} : {label}" if total else label
                    )
                _ecrire_suivi(id_import, **champs)

            api = traitement_import_realisation_chasse(
                chemin_fichier,
                id_saison,
                "true" if do_update else "false",
                id_role=id_role,
                nom_complet=nom_complet,
                progress_callback=progress,
            )
            _ecrire_suivi(
                id_import,
                journal=list(api.journal),
                success=bool(api.success),
                message=(api.message or None),
                statut="TERMINE" if api.success else "ERREUR",
                date_fin=datetime.now().isoformat(),
            )
        except Exception as e:  # noqa: BLE001 - on veut journaliser toute erreur
            current_app.logger.exception("Import chasse %s : échec", id_import)
            try:
                _ecrire_suivi(
                    id_import,
                    statut="ERREUR",
                    message=str(e),
                    date_fin=datetime.now().isoformat(),
                )
            except Exception:
                pass
        finally:
            try:
                config["DB"].session.remove()
            except Exception:
                pass


def lancer_import_async(
    id_import, chemin_fichier, id_saison, do_update, id_role, nom_complet
):
    """Démarre le traitement dans un thread de fond (daemon)."""
    app = current_app._get_current_object()
    thread = threading.Thread(
        target=_traiter,
        args=(
            app,
            id_import,
            chemin_fichier,
            id_saison,
            do_update,
            id_role,
            nom_complet,
        ),
        name=f"import-chasse-{id_import}",
        daemon=True,
    )
    thread.start()
