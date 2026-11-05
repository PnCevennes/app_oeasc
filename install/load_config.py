#!/usr/bin/env python3
"""
Lit install/config_principal.yaml et affiche des `export VAR=valeur` à évaluer par bash.
Utilisé par install/load_config.sh (remplace l'ancien config/settings.ini).
Dépendance : PyYAML.
"""

import os
import shlex
import sys
from pathlib import Path

import yaml


def main():
    racine = Path(__file__).resolve().parent
    fichier = Path(
        sys.argv[1] if len(sys.argv) > 1 else os.environ.get("OEASC_CONFIG") or racine / "config_principal.yaml"
    )
    if not fichier.is_file():
        sys.exit(f"Fichier de configuration introuvable : {fichier}")
    with open(fichier, encoding="utf-8") as f:
        c = yaml.safe_load(f)

    db, urls, app, adm, gun, mail = (
        c["base_de_donnees"], c["urls"], c["application"], c["administrateur"], c["gunicorn"], c["mail"],
    )
    variables = {
        "db_host": db["host"], "db_port": db["port"], "db_name": db["nom"],
        "user_pg": db["utilisateur"], "user_pg_pass": db["mot_de_passe"],
        "user_install": db.get("utilisateur_install", ""), "user_install_pass": db.get("mot_de_passe_install", ""),
        "reset_geom": db.get("reset_geom", False),
        "MODE_TEST": app.get("mode_test", 0), "ID_APP": app["id_app"],
        "APP_PORT": urls.get("port", 5005),
        "URL_FRONTEND": urls["frontend"], "URL_APPLICATION": urls["application"], "URL_USERSHUB": urls["usershub"],
        "ADMIN_APPLICATION_LOGIN": adm["login"], "ADMIN_APPLICATION_PASSWORD": adm["mot_de_passe"],
        "ADMIN_APPLICATION_MAIL": adm["mail"],
        "gun_num_workers": gun["num_workers"], "gun_host": gun["host"], "gun_timeout": gun.get("timeout", 30),
        "ANIMATEUR_APPLICATION_MAIL": mail["animateur_mail"],
        "MAIL_SERVER": mail["server"], "MAIL_PORT": mail["port"],
        "MAIL_USERNAME": mail["username"], "MAIL_PASSWORD": mail["password"],
        "SECRET_KEY": app["secret_key"],
    }
    for nom, valeur in variables.items():
        if isinstance(valeur, bool):
            valeur = "true" if valeur else "false"
        print(f"export {nom}={shlex.quote(str(valeur))}")


main()
