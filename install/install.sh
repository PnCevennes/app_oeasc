#!/bin/bash
# Installation / mise à jour d'OEASC sur un serveur de PRODUCTION (idempotent : peut être relancé à tout moment).
# En développement, ne pas utiliser ce script : `flask run` (backend) et `npm run serve` (frontend).
#
# Étapes :
#   1. paquets système (apt)                           [sudo]
#   2. virtualenv Python + dépendances de requirements.txt (seulement celles qui manquent)
#   3. lecture et vérification de install/config_principal.yaml (secrets, debug...)
#   4. dépendances npm (seulement si package-lock.json a changé) + build du frontend
#   5. service systemd + logrotate + (re)démarrage + vérification HTTP   [sudo]
#   6. (--with-apache) configuration Apache, restaurée si `configtest` échoue   [sudo]
#   7. état des migrations Alembic (information seulement)
#
# À lancer en utilisateur normal (pas en root) : c'est cet utilisateur qui fait tourner le service.
# Le mot de passe sudo est demandé une seule fois au début.
# La base de données n'est PAS modifiée (migrations : `flask db upgrade <révision>`, voir install/docs/alembic.md).

set -eo pipefail

ROOT_DIR=$(readlink -e "$(dirname "${BASH_SOURCE[0]}")/..")
CONFIG_FILE=${OEASC_CONFIG:-$ROOT_DIR/install/config_principal.yaml}
NODE_MIN=24
SERVICE=oeasc

SKIP_APT=0; SKIP_NPM=0; SKIP_RESTART=0; FORCE_NPM=0; REMOVE_VENV=0; WITH_APACHE=0; MODE_ENV=0

step() { echo; echo "==> $*"; }
warn() { echo "ATTENTION : $*" >&2; }
die()  { echo "ERREUR : $*" >&2; exit 1; }

########################################################################
# Lecture de config_principal.yaml -> variables bash
# Utilisable par les autres scripts : eval "$(install/install.sh --env [fichier.yaml])"
# (db_host, db_port, db_name, user_pg, user_pg_pass, URL_*, APP_PORT, gun_*, ...)
########################################################################
exporter_config() {
    local python=python3
    [ -x "$ROOT_DIR/venv/bin/python" ] && python="$ROOT_DIR/venv/bin/python"
    "$python" - "$1" <<'PYEOF2' || die "lecture de la configuration impossible (PyYAML installé ?)"
import shlex
import sys

import yaml

with open(sys.argv[1], encoding="utf-8") as f:
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
    "DEBUG": app.get("debug", False), "MODE_DEVELOPPEMENT": app.get("mode_developpement", False),
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
PYEOF2
}

usage() {
    cat <<USAGE
Usage : install/install.sh [options]      (serveur de production uniquement)
  --skip-apt        ne pas installer les paquets système
  --skip-npm        ne pas installer les paquets npm ni builder le frontend
  --skip-restart    ne pas configurer/redémarrer le service systemd
  --force-npm       réinstaller node_modules (npm ci) même si package-lock.json est inchangé
  --remove-venv     supprimer et recréer le virtualenv
  --with-apache     installer la configuration Apache (install/assets/apache2/oeasc.conf)
  --env [fichier]   affiche la configuration en \`export VAR=valeur\` pour \`eval\`, et quitte
  -h, --help        cette aide
USAGE
}

while [ $# -gt 0 ]; do
    case "$1" in
        --skip-apt) SKIP_APT=1 ;;
        --skip-npm) SKIP_NPM=1 ;;
        --skip-restart) SKIP_RESTART=1 ;;
        --force-npm) FORCE_NPM=1 ;;
        --remove-venv) REMOVE_VENV=1 ;;
        --with-apache) WITH_APACHE=1 ;;
        --env)
            MODE_ENV=1
            if [ -n "$2" ] && [ "${2#--}" = "$2" ]; then CONFIG_FILE=$2; shift; fi
            ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Option inconnue : $1" >&2; usage >&2; exit 1 ;;
    esac
    shift
done

# mode lecture de config pour les autres scripts : install.sh --env [fichier.yaml]
if [ "$MODE_ENV" = 1 ]; then
    [ -f "$CONFIG_FILE" ] || die "$CONFIG_FILE absent"
    exporter_config "$CONFIG_FILE"
    exit 0
fi

[ -f "$CONFIG_FILE" ] || die "$CONFIG_FILE absent : copier install/config_principal.yaml.sample et l'adapter"
# chemin absolu : il est écrit dans le service systemd
CONFIG_FILE=$(readlink -e "$CONFIG_FILE")

if [ "$(id -u)" = 0 ]; then
    die "ne pas lancer install.sh en root (ni avec sudo) : venv, node_modules et dist appartiendraient
à root et le service tournerait en root. Le lancer avec l'utilisateur qui fera tourner le service :
les étapes qui en ont besoin appellent sudo elles-mêmes."
fi
SERVICE_USER=$(id -un)

cd "$ROOT_DIR"

########################################################################
# sudo : authentification une fois au début, maintenue pendant le script
# (le mot de passe n'est ni stocké ni envoyé aux commandes)
########################################################################
NEED_SUDO=0
{ [ "$SKIP_APT" = 0 ] || [ "$SKIP_RESTART" = 0 ] || [ "$WITH_APACHE" = 1 ]; } && NEED_SUDO=1

TMP_DIR=$(mktemp -d)
SUDO_KEEPALIVE=""
nettoyage() {
    rm -rf "$TMP_DIR"
    [ -n "$SUDO_KEEPALIVE" ] && kill "$SUDO_KEEPALIVE" 2>/dev/null || true
}
trap nettoyage EXIT

if [ "$NEED_SUDO" = 1 ]; then
    command -v sudo >/dev/null || die "sudo n'est pas installé"
    echo "Droits administrateur nécessaires (paquets, service systemd, apache)."
    sudo -v || die "authentification sudo impossible"
    # renouvelle le ticket sudo tant que le script tourne
    ( while kill -0 "$$" 2>/dev/null; do sudo -n true 2>/dev/null; sleep 50; done ) &
    SUDO_KEEPALIVE=$!
fi

########################################################################
# 1. paquets système
########################################################################
if [ "$SKIP_APT" = 0 ]; then
    step "Paquets système"
    command -v apt-get >/dev/null || die "apt-get introuvable : installer les paquets à la main puis relancer avec --skip-apt"
    PAQUETS="git curl build-essential python3 python3-venv python3-dev python3-pip libpq-dev libgeos-dev gettext-base"
    [ "$WITH_APACHE" = 1 ] && PAQUETS="$PAQUETS apache2"
    manquants=""
    for p in $PAQUETS; do
        dpkg-query -W -f='${Status}' "$p" 2>/dev/null | grep -q "install ok installed" || manquants="$manquants $p"
    done
    if [ -n "$manquants" ]; then
        echo "Installation :$manquants"
        sudo apt-get update
        sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends $manquants
        hash -r
    else
        echo "Tous les paquets système sont déjà présents"
    fi
fi

########################################################################
# 2. virtualenv + dépendances python
########################################################################
step "Environnement Python"
if [ "$REMOVE_VENV" = 1 ] && [ -d venv ]; then
    echo "Suppression du virtualenv existant"
    rm -rf venv
fi
if [ -d venv ] && [ ! -O venv ]; then
    die "venv/ n'appartient pas à $SERVICE_USER (reliquat d'une installation en root ?) : sudo rm -rf $ROOT_DIR/venv puis relancer"
fi
[ -x venv/bin/pip ] || python3 -m venv venv
[ -x venv/bin/pip ] || die "virtualenv créé sans pip (paquet python3-venv manquant ?)"
# shellcheck disable=SC1091
source venv/bin/activate
pip install --quiet --upgrade pip
# l'ancien paquet "oeasc" (install/setup.py) n'existe plus : les migrations sont référencées dans backend/app.py.
# Désinstallé AVANT requirements.txt : ses versions épinglées provoqueraient de faux conflits pip.
pip uninstall -y oeasc >/dev/null 2>&1 || true
# pip ne (ré)installe que ce qui manque ou ne respecte pas les versions de requirements.txt
pip install -r requirements.txt
pip check || warn "dépendances python incohérentes, voir ci-dessus"

########################################################################
# 3. configuration : lecture et vérifications de production
########################################################################
step "Lecture de la configuration ($CONFIG_FILE)"
eval "$(exporter_config "$CONFIG_FILE")"
echo "Backend : port $APP_PORT, gunicorn $gun_num_workers workers sur $gun_host"

erreurs=()
[ "$DEBUG" = true ] && erreurs+=("application.debug doit valoir false en production")
[ "$MODE_DEVELOPPEMENT" = true ] && erreurs+=("application.mode_developpement doit valoir false en production")
case "$SECRET_KEY" in
    ""|changer-cette-cle) erreurs+=("application.secret_key n'est pas renseignée (valeur d'exemple)") ;;
esac
[ "${#SECRET_KEY}" -ge 16 ] || erreurs+=("application.secret_key trop courte (16 caractères minimum)")
[ "$user_pg_pass" = mot_de_passe_complexe ] && erreurs+=("base_de_donnees.mot_de_passe est la valeur d'exemple")
[ "$ADMIN_APPLICATION_PASSWORD" = un_mot_de_passe_complexe ] && erreurs+=("administrateur.mot_de_passe est la valeur d'exemple")
if [ ${#erreurs[@]} -gt 0 ]; then
    printf '  - %s\n' "${erreurs[@]}" >&2
    die "configuration non adaptée à la production ($CONFIG_FILE)"
fi
[ "$gun_host" = 0.0.0.0 ] && warn "gunicorn.host = 0.0.0.0 : le backend est joignable directement sur le port $APP_PORT
  sans passer par Apache. Mettre 127.0.0.1 si Apache est sur ce serveur."
case "$MAIL_SERVER $MAIL_USERNAME" in
    *domaine.fr*) warn "section mail : valeurs d'exemple (domaine.fr), les mails ne partiront pas" ;;
esac

# Connexion à la base : sans elle toutes les routes API répondent 500
# (la vérification HTTP de fin d'installation ne le verrait pas : `/` ne touche pas la base)
echo "Connexion à la base $db_name sur $db_host:$db_port (utilisateur $user_pg)"
if ! erreur_pg=$(PGHOST=$db_host PGPORT=$db_port PGDATABASE=$db_name PGUSER=$user_pg PGPASSWORD=$user_pg_pass \
        PGCONNECT_TIMEOUT=10 python -c 'import psycopg2; psycopg2.connect("").close()' 2>&1); then
    echo "$erreur_pg" | grep -v '^Traceback\|^  ' >&2
    die "base de données injoignable. Selon le message ci-dessus :
  - 'No route to host' / 'timeout' : serveur éteint, mauvaise IP ou pare-feu (ping $db_host ; nc -zv $db_host $db_port)
  - 'Connection refused' : PostgreSQL n'écoute pas sur cette adresse (listen_addresses dans postgresql.conf)
  - 'no pg_hba.conf entry' / 'password authentication failed' : pg_hba.conf ou base_de_donnees.mot_de_passe"
fi

########################################################################
# 4. npm + build
########################################################################
if [ "$SKIP_NPM" = 0 ]; then
    step "Node ($NODE_MIN+) et paquets npm"
    node_ok() { command -v node >/dev/null && [ "$(node -p 'process.versions.node.split(".")[0]')" -ge "$NODE_MIN" ]; }
    if ! node_ok; then
        export NVM_DIR="${NVM_DIR:-$HOME/.nvm}"
        if [ ! -s "$NVM_DIR/nvm.sh" ]; then
            echo "Installation de nvm"
            curl -fsSL https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash
        fi
        # shellcheck disable=SC1091
        . "$NVM_DIR/nvm.sh"
        nvm install "$NODE_MIN"
        nvm use "$NODE_MIN"
    fi
    node_ok || die "node >= $NODE_MIN introuvable"
    echo "node $(node -v), npm $(npm -v)"

    export OEASC_CONFIG="$CONFIG_FILE"
    cd "$ROOT_DIR/frontend"
    STAMP=node_modules/.package-lock.sha256
    LOCK_HASH=$(sha256sum package-lock.json package.json | sha256sum | cut -d' ' -f1)
    if [ "$FORCE_NPM" = 1 ] || [ ! -d node_modules ] || [ "$(cat "$STAMP" 2>/dev/null)" != "$LOCK_HASH" ]; then
        echo "Installation des paquets npm"
        npm ci
        echo "$LOCK_HASH" > "$STAMP"
    else
        echo "node_modules à jour (package.json / package-lock.json inchangés)"
    fi
    step "Build du frontend (config lue dans $CONFIG_FILE)"
    npm run build
    cd "$ROOT_DIR"
fi

########################################################################
# 5. systemd, logrotate, redémarrage
########################################################################
port_ecoute() { ss -tln 2>/dev/null | awk '{print $4}' | grep -qE "[.:]$1\$"; }

if [ "$SKIP_RESTART" = 0 ]; then
    step "Service systemd '$SERVICE' (utilisateur $SERVICE_USER)"
    if ! systemctl is-active --quiet "$SERVICE.service" 2>/dev/null && port_ecoute "$APP_PORT"; then
        warn "le port $APP_PORT est déjà occupé (flask run / gunicorn lancé à la main ?) : le service ne pourra pas démarrer.
  Voir : ss -tlnp | grep :$APP_PORT"
    fi

    export USER_SERVICE=$SERVICE_USER BASE_DIR=$ROOT_DIR OEASC_CONFIG_FILE=$CONFIG_FILE
    export GUN_NUM_WORKERS=$gun_num_workers GUN_HOST=$gun_host GUN_PORT=$APP_PORT GUN_TIMEOUT=$gun_timeout

    sudo install -d -o "$USER_SERVICE" -g "$USER_SERVICE" -m 0750 /var/log/oeasc

    # les variables ${GUNICORN_*} propres à systemd ne sont pas substituées (liste explicite)
    envsubst '${USER_SERVICE} ${BASE_DIR} ${OEASC_CONFIG_FILE} ${GUN_NUM_WORKERS} ${GUN_HOST} ${GUN_PORT} ${GUN_TIMEOUT}' \
        < install/assets/oeasc.service > "$TMP_DIR/oeasc.service"
    USER=$USER_SERVICE envsubst '${USER}' < install/assets/log_rotate > "$TMP_DIR/oeasc.logrotate"

    sudo install -m 644 "$TMP_DIR/oeasc.service" /etc/systemd/system/oeasc.service
    sudo install -m 644 "$TMP_DIR/oeasc.logrotate" /etc/logrotate.d/oeasc
    sudo systemctl daemon-reload
    sudo systemctl enable "$SERVICE.service"
    sudo systemctl restart "$SERVICE.service"

    # Type=simple : "actif" dès le lancement, même si gunicorn plante ensuite ->
    # on attend une vraie réponse HTTP (n'importe quel code, 404 compris)
    case "$gun_host" in 0.0.0.0|localhost|127.0.0.1) hote_test=127.0.0.1 ;; *) hote_test=$gun_host ;; esac
    echo -n "Attente de la réponse de gunicorn sur $hote_test:$APP_PORT "
    demarre=0
    for _ in $(seq 1 30); do
        if ! systemctl is-active --quiet "$SERVICE.service"; then break; fi
        if curl -s -o /dev/null --max-time 5 "http://$hote_test:$APP_PORT/"; then demarre=1; break; fi
        echo -n "."; sleep 1
    done
    echo
    if [ "$demarre" = 1 ]; then
        echo "Service $SERVICE actif et répond"
    else
        sudo systemctl status "$SERVICE.service" --no-pager || true
        die "le service $SERVICE ne répond pas (journalctl -u $SERVICE -n 50 ; /var/log/oeasc/oeasc.log)"
    fi
fi

########################################################################
# 6. Apache
########################################################################
if [ "$WITH_APACHE" = 1 ]; then
    step "Apache"
    [ -d /etc/apache2/conf-available ] || die "/etc/apache2/conf-available absent (apache2 non installé ?)"
    APACHE_CONF=/etc/apache2/conf-available/oeasc.conf
    sed "s!/PATH/TO/app_oeasc!$ROOT_DIR!g; s!127.0.0.1:5005!127.0.0.1:$APP_PORT!g" \
        install/assets/apache2/oeasc.conf > "$TMP_DIR/oeasc.conf"

    # sauvegarde de l'ancienne configuration : remise en place si la nouvelle est refusée,
    # pour ne pas laisser Apache incapable de recharger (ce qui toucherait les autres sites du serveur)
    etait_active=0
    [ -e /etc/apache2/conf-enabled/oeasc.conf ] && etait_active=1
    if [ -f "$APACHE_CONF" ]; then cp "$APACHE_CONF" "$TMP_DIR/oeasc.conf.ancien"; fi

    sudo install -m 644 "$TMP_DIR/oeasc.conf" "$APACHE_CONF"
    for m in proxy proxy_http rewrite; do sudo a2enmod -q "$m" >/dev/null; done
    sudo a2enconf -q oeasc >/dev/null
    if ! sudo apache2ctl configtest; then
        if [ -f "$TMP_DIR/oeasc.conf.ancien" ]; then
            sudo install -m 644 "$TMP_DIR/oeasc.conf.ancien" "$APACHE_CONF"
            echo "Ancienne configuration Apache remise en place." >&2
        fi
        [ "$etait_active" = 0 ] && sudo a2disconf -q oeasc >/dev/null
        die "configuration Apache refusée (voir ci-dessus), Apache n'a pas été rechargé"
    fi
    sudo systemctl reload apache2

    # www-data doit pouvoir traverser tous les dossiers jusqu'à frontend/dist
    # (un home en 750, par défaut sous Debian, donne un 403 sans message clair)
    if [ -d "$ROOT_DIR/frontend/dist" ] && ! sudo -u www-data test -r "$ROOT_DIR/frontend/dist/index.html"; then
        warn "Apache (www-data) ne peut pas lire $ROOT_DIR/frontend/dist. Donner le droit de traverser aux dossiers parents :"
        p="$ROOT_DIR/frontend/dist"
        while [ "$p" != / ]; do
            sudo -u www-data test -x "$p" || echo "  chmod o+x $p" >&2
            p=$(dirname "$p")
        done
    fi
fi

########################################################################
# 7. migrations (information seulement : plusieurs branches Alembic, cible explicite obligatoire)
########################################################################
step "État des migrations Alembic (aucune migration n'est appliquée par ce script)"
(
    cd "$ROOT_DIR/backend"
    export OEASC_CONFIG="$CONFIG_FILE"
    if courantes=$(flask db current 2>/dev/null | grep -E '^[0-9a-f]{12}'); then
        en_retard=$(echo "$courantes" | grep -v '(head)' || true)
        if [ -n "$en_retard" ]; then
            echo "Branches dont la révision courante n'est pas la tête (migrations peut-être en attente) :"
            echo "$en_retard" | sed 's/^/  /'
            echo "Voir install/docs/alembic.md, puis : cd backend && flask db upgrade <révision>"
        else
            echo "Toutes les branches sont à leur tête."
        fi
    else
        warn "impossible de lire l'état des migrations (base injoignable ou vide ? voir flask init-db)"
    fi
)

echo
echo "Installation terminée."
