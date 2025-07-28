#!/usr/bin/env bash


set -eo pipefail

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
export BASE_DIR=$(dirname "${SCRIPT_DIR}")

echo "Création du fichier de logs…"
sudo install -d -o ${USER} -g ${USER} -m 0750 /var/log/oeasc

echo "Installation des fichiers de service systemd…"
envsubst '${USER} ${BASE_DIR}' < "${BASE_DIR}/install/assets/oeasc.service" | sudo tee /etc/systemd/system/oeasc.service

echo "Installation de la configuration logrotate…"
envsubst '${USER}' < "${BASE_DIR}/install/assets/log_rotate" | sudo tee /etc/logrotate.d/oeasc

echo "Activation de oeasc au démarrage…"
sudo systemctl enable oeasc.service
echo "Vous pouvez maintenant démarrer OEASC avec la commande : sudo systemctl start oeasc"