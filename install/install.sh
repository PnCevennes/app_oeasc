#!/bin/bash
# Installation / mise à jour complète d'OEASC (idempotent : peut être relancé à tout moment).
#
# Étapes :
#   1. paquets système (apt)                           [sudo]
#   2. virtualenv Python + dépendances de requirements.txt (seulement celles qui manquent)
#   3. lecture de install/config_principal.yaml (variables db_*, URL_*, gun_*, APP_PORT, ...)
#   4. dépendances npm (seulement si package-lock.json a changé) + build du frontend
#   5. service systemd + logrotate + (re)démarrage     [sudo]
#
# Le mot de passe sudo est demandé une seule fois au début (sauf si root ou sudo sans mot de passe).
# La base de données n'est PAS touchée (migrations : `flask db upgrade <révision>`, voir install/docs/alembic.md).

set -eo pipefail

ROOT_DIR=$(readlink -e "$(dirname "${BASH_SOURCE[0]}")/..")
CONFIG_FILE=${OEASC_CONFIG:-$ROOT_DIR/install/config_principal.yaml}
NODE_MIN=24
SERVICE=oeasc

SKIP_APT=0; SKIP_NPM=0; SKIP_RESTART=0; FORCE_NPM=0; REMOVE_VENV=0; WITH_APACHE=0

usage() {
    cat <<USAGE
Usage : install/install.sh [options]
  --skip-apt        ne pas installer les paquets système
  --skip-npm        ne pas installer les paquets npm ni builder le frontend
  --skip-restart    ne pas configurer/redémarrer le service systemd
  --force-npm       réinstaller node_modules (npm ci) même si package-lock.json est inchangé
  --remove-venv     supprimer et recréer le virtualenv
  --with-apache     installer le vhost Apache (install/assets/apache2/oeasc.conf)
  -h, --help        cette aide
USAGE
}

for arg in "$@"; do
    case "$arg" in
        --skip-apt) SKIP_APT=1 ;;
        --skip-npm) SKIP_NPM=1 ;;
        --skip-restart) SKIP_RESTART=1 ;;
        --force-npm) FORCE_NPM=1 ;;
        --remove-venv) REMOVE_VENV=1 ;;
        --with-apache) WITH_APACHE=1 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "Option inconnue : $arg"; usage; exit 1 ;;
    esac
done

step() { echo; echo "==> $*"; }
die()  { echo "ERREUR : $*" >&2; exit 1; }

[ -f "$CONFIG_FILE" ] || die "$CONFIG_FILE absent : copier install/config_principal.yaml.sample et l'adapter"
cd "$ROOT_DIR"

########################################################################
# sudo : mot de passe demandé une fois, jamais affiché ni écrit sur disque
########################################################################
SUDO_PASS=""
NEED_SUDO=0
{ [ "$SKIP_APT" = 0 ] || [ "$SKIP_RESTART" = 0 ] || [ "$WITH_APACHE" = 1 ]; } && NEED_SUDO=1

if [ "$NEED_SUDO" = 1 ] && [ "$(id -u)" != 0 ]; then
    command -v sudo >/dev/null || die "sudo n'est pas installé"
    if ! sudo -n true 2>/dev/null; then
        sudo -k
        for essai in 1 2 3; do
            read -r -s -p "Mot de passe sudo pour $USER : " SUDO_PASS; echo
            if printf '%s\n' "$SUDO_PASS" | sudo -S -p '' -v 2>/dev/null; then break; fi
            SUDO_PASS=""
            echo "Mot de passe incorrect."
            [ "$essai" = 3 ] && die "authentification sudo impossible"
        done
    fi
fi

run_sudo() {
    if [ "$(id -u)" = 0 ]; then "$@"
    elif [ -n "$SUDO_PASS" ]; then printf '%s\n' "$SUDO_PASS" | sudo -S -p '' "$@"
    else sudo -n "$@"
    fi
}

TMP_DIR=$(mktemp -d)
trap 'rm -rf "$TMP_DIR"; SUDO_PASS=""' EXIT

########################################################################
# 1. paquets système
########################################################################
if [ "$SKIP_APT" = 0 ]; then
    step "Paquets système"
    PAQUETS="git curl build-essential python3 python3-venv python3-dev python3-pip libpq-dev libgeos-dev gettext-base"
    [ "$WITH_APACHE" = 1 ] && PAQUETS="$PAQUETS apache2"
    manquants=""
    for p in $PAQUETS; do
        dpkg -s "$p" >/dev/null 2>&1 || manquants="$manquants $p"
    done
    if [ -n "$manquants" ]; then
        echo "Installation :$manquants"
        run_sudo apt-get update
        run_sudo apt-get install -y --no-install-recommends $manquants
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
[ -x venv/bin/python ] || python3 -m venv venv
# shellcheck disable=SC1091
source venv/bin/activate
pip install --quiet --upgrade pip
# pip ne (ré)installe que ce qui manque ou ne respecte pas les versions de requirements.txt
pip install -r requirements.txt
pip check || echo "(avertissement : dépendances python incohérentes, voir ci-dessus)"

########################################################################
# 3. configuration
########################################################################
step "Lecture de la configuration ($CONFIG_FILE)"
. "$ROOT_DIR/install/load_config.sh" "$CONFIG_FILE"
echo "Backend : port $APP_PORT, gunicorn $gun_num_workers workers sur $gun_host"

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
# 5. systemd, logrotate, apache, redémarrage
########################################################################
if [ "$SKIP_RESTART" = 0 ]; then
    step "Service systemd '$SERVICE'"
    export USER_SERVICE=${USER:-$(id -un)} BASE_DIR=$ROOT_DIR
    export GUN_NUM_WORKERS=$gun_num_workers GUN_HOST=$gun_host GUN_PORT=$APP_PORT GUN_TIMEOUT=$gun_timeout

    run_sudo install -d -o "$USER_SERVICE" -g "$USER_SERVICE" -m 0750 /var/log/oeasc

    # les variables ${GUNICORN_*} propres à systemd ne sont pas substituées (liste explicite)
    envsubst '${USER_SERVICE} ${BASE_DIR} ${GUN_NUM_WORKERS} ${GUN_HOST} ${GUN_PORT} ${GUN_TIMEOUT}' \
        < install/assets/oeasc.service > "$TMP_DIR/oeasc.service"
    USER=$USER_SERVICE envsubst '${USER}' < install/assets/log_rotate > "$TMP_DIR/oeasc.logrotate"

    run_sudo install -m 644 "$TMP_DIR/oeasc.service" /etc/systemd/system/oeasc.service
    run_sudo install -m 644 "$TMP_DIR/oeasc.logrotate" /etc/logrotate.d/oeasc
    run_sudo systemctl daemon-reload
    run_sudo systemctl enable "$SERVICE.service"
    run_sudo systemctl restart "$SERVICE.service"
    sleep 2
    if run_sudo systemctl is-active --quiet "$SERVICE.service"; then
        echo "Service $SERVICE actif"
    else
        run_sudo systemctl status "$SERVICE.service" --no-pager || true
        die "le service $SERVICE n'a pas démarré (journalctl -u $SERVICE)"
    fi
fi

if [ "$WITH_APACHE" = 1 ]; then
    step "Apache"
    sed "s!/PATH/TO/app_oeasc!$ROOT_DIR!g; s!127.0.0.1:5005!127.0.0.1:$APP_PORT!g" \
        install/assets/apache2/oeasc.conf > "$TMP_DIR/oeasc.conf"
    run_sudo install -m 644 "$TMP_DIR/oeasc.conf" /etc/apache2/conf-available/oeasc.conf
    for m in proxy proxy_http rewrite; do run_sudo a2enmod "$m" >/dev/null; done
    run_sudo a2enconf oeasc
    run_sudo apache2ctl configtest
    run_sudo systemctl reload apache2
fi

echo
echo "Installation terminée."
