#!/bin/bash

# Génère la configuration du frontend (frontend/src/config/config.js) à partir de
# install/config_principal.yaml. Le backend lit directement ce fichier (backend/config.py).
# Usage : init_config.sh [install/config_principal.yaml]

if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/..
fi

config_file=${1:-$ROOT_DIR/install/config_principal.yaml}

if [ ! -f "$config_file" ]
then
    echo "Fichier de configuration $config_file absent : copier install/config_principal.yaml.sample et l'adapter"
    exit 1
fi

# charge db_host, URL_APPLICATION, URL_FRONTEND, ... depuis le yaml
. "$ROOT_DIR/install/load_config.sh" "$config_file"

# front
cp "$ROOT_DIR/frontend/src/config/config.js.sample" "$ROOT_DIR/frontend/src/config/config.js"
sed -i -e s!'URL_APPLICATION.*'!"URL_APPLICATION: '"$URL_APPLICATION"',"! "$ROOT_DIR/frontend/src/config/config.js"
sed -i -e s!'URL_FRONTEND.*'!"URL_FRONTEND: '"$URL_FRONTEND"',"! "$ROOT_DIR/frontend/src/config/config.js"

cat "$ROOT_DIR/frontend/src/config/config.js"
