"""
Configuration de l'application OEASC.

Source unique : install/config_principal.yaml (copie de config_principal.yaml.sample).
Chemin surchargeable avec la variable d'environnement OEASC_CONFIG.

Les constantes en MAJUSCULES définies ici sont chargées dans app.config
via ``app.config.from_object(config)``.
"""

import os
from pathlib import Path
from urllib.parse import quote

import yaml

ROOT_DIR = Path(__file__).absolute().parent.parent
CONFIG_FILE = Path(
    os.environ.get("OEASC_CONFIG") or ROOT_DIR / "install" / "config_principal.yaml"
)


def _charger(path):
    if not path.is_file():
        raise FileNotFoundError(
            f"Fichier de configuration introuvable : {path}. "
            "Copier install/config_principal.yaml.sample en install/config_principal.yaml "
            "puis l'adapter."
        )
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


_cfg = _charger(CONFIG_FILE)
_db = _cfg["base_de_donnees"]
_urls = _cfg["urls"]
_app = _cfg["application"]
_admin = _cfg["administrateur"]
_mail = _cfg["mail"]
_tuiles = _cfg["tuiles"]


def _uri_base(db):
    """URI SQLAlchemy construite depuis la section base_de_donnees (identifiants échappés)."""
    return "postgresql://{user}:{pwd}@{host}:{port}/{nom}".format(
        user=quote(str(db["utilisateur"]), safe=""),
        pwd=quote(str(db["mot_de_passe"]), safe=""),
        host=db["host"],
        port=db["port"],
        nom=db["nom"],
    )


############################## BASE DE DONNÉES ##############################
SQLALCHEMY_DATABASE_URI = _uri_base(_db)
SQLALCHEMY_ECHO = _db["sqlalchemy_echo"]
SQLALCHEMY_ENGINE_OPTIONS = _db["sqlalchemy_engine_options"]

############################## URL ##############################
# normalisées : le code concatène URL_APPLICATION + "/api/..." et URL_FRONTEND + "login" / "#/..."
URL_APPLICATION = str(_urls["application"]).rstrip("/")
URL_FRONTEND = str(_urls["frontend"]).rstrip("/") + "/"
URL_USERSHUB = _urls["usershub"]
PORT = _urls["port"]
REDIRECT_ON_FORBIDDEN = _urls["redirect_on_forbidden"]

############################## APPLICATION ##############################
DEBUG = _app["debug"]
MODE_DEVELOPPEMENT = _app["mode_developpement"]
MODE_TEST = _app.get("mode_test", 0)
ID_APP = _app["id_app"]
CODE_APPLICATION = _app["code_application"]
SECRET_KEY = _app["secret_key"]
PASS_METHOD = _app["pass_method"]
COOKIE_EXPIRATION = _app["cookie_expiration"]
COOKIE_AUTORENEW = _app["cookie_autorenew"]
PROXY_FIX = _app["proxy_fix"]
AUTH_PROVIDER = _app["auth_provider"]
GOOGLE_VERIFICATION_FILE = _app.get("google_verification_file", "")
ENABLE_NOMENCLATURE_TAXONOMIC_FILTERS = _app["enable_nomenclature_taxonomic_filters"]

############################## ADMINISTRATEUR ##############################
ADMIN_APPLICATION_LOGIN = _admin["login"]
ADMIN_APPLICATION_PASSWORD = _admin["mot_de_passe"]
ADMIN_APPLICATION_MAIL = _admin["mail"]

############################## MAIL ##############################
ANIMATEUR_APPLICATION_MAIL = _mail["animateur_mail"]
MAIL_SERVER = _mail["server"]
MAIL_PORT = _mail["port"]
MAIL_USE_SSL = _mail["use_ssl"]
MAIL_USE_TLS = _mail["use_tls"]
MAIL_USERNAME = _mail["username"]
MAIL_PASSWORD = _mail["password"]
MAIL_DEBUG = _mail["debug"]
MAIL_ASCII_ATTACHMENTS = _mail["ascii_attachments"]
CODE_APPLICATION_MAIL = _mail["code_application_mail"]

############################## SENTRY ##############################
SENTRY_DSN = _cfg.get("sentry", {}).get("dsn", "")
SENTRY_TRACES_SAMPLE_RATE = _cfg.get("sentry", {}).get("traces_sample_rate", 1.0)

############################## TUILES (fond de carte) ##############################
TILE_UPSTREAM_URL = _tuiles["url"]
TILE_USER_AGENT = _tuiles["user_agent"]
TILE_CACHE_MAX_AGE = int(_tuiles["cache_jours"] * 24 * 3600)
TILE_TIMEOUT = _tuiles["timeout"]
TILE_CACHE_DIR_NAME = _tuiles["dossier_cache"]

############################## DÉCLARATIONS ##############################
# dict partagé : ne pas le modifier (voir oeasc/modules/oeasc/declaration/variables.py)
DECLARATION = _cfg["declaration"]
