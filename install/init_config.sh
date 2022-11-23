#!/bin/bash

# echo "config settings"

if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/..
fi

config_file=$1

# echo aa $config_file
. $config_file



rm config/oeasc_config.toml
if [ -f config/oeasc_config.toml ]; then
    echo "Utilisation du fichier de configuration exisant"
else
    echo "Création du fichier de configuration..."
    cp config/oeasc_config.toml.sample config/oeasc_config.toml
    echo "Préparation du fichier de configuration..."

    DB_URI="postgresql:\/\/$user_pg:$user_pg_pass@$db_host:$db_port\/$db_name"
    sed -i -e s!'^URL_APPLICATION.*'!"URL_APPLICATION = \""$URL_APPLICATION"\""! config/oeasc_config.toml
    sed -i -e s!'^URL_FRONTEND.*'!"URL_FRONTEND = \""$URL_FRONTEND"\""! config/oeasc_config.toml
    sed -i -e s!'^URL_USERSHUB.*'!"URL_USERSHUB = \""$URL_USERSHUB"\""! config/oeasc_config.toml
    sed -i -e s/'^SQLALCHEMY_DATABASE_URI.*'/"SQLALCHEMY_DATABASE_URI = \""$DB_URI\"/ config/oeasc_config.toml
    sed -i "s|^SECRET_KEY = .*$|SECRET_KEY = '`openssl rand -hex 32`'|" config/oeasc_config.toml

fi



# front
if [ -f config/oeasc_config.toml ]; then
    echo "Utilisation du fichier de configuration exisant"
else
    cp frontend/src/config/config.js.sample frontend/src/config/config.js
    sed -i -e s!'URL_APPLICATION.*'!"URL_APPLICATION: '"$URL_APPLICATION"',"! frontend/src/config/config.js
    sed -i -e s!'URL_FRONTEND.*'!"URL_FRONTEND: '"$URL_FRONTEND"',"! frontend/src/config/config.js
fi