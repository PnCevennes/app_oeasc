#!/bin/bash

echo "config settings"

if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/..
fi

config_file=$1

echo aa $config_file
. $config_file


echo "Creation de config/config.py"
cp config/config.py.sample config/config.py

DB_URI="postgresql:\/\/$user_pg:$user_pg_pass@$db_host:$db_port\/$db_name"

echo $DB_URI

sed -i -e s/'^SQLALCHEMY_DATABASE_URI.*'/"SQLALCHEMY_DATABASE_URI = \""$DB_URI\"/ config/config.py #> config/config.py
sed -i -e s/'^URL_APPLICATION.*'/"URL_APPLICATION = \"http:\/\/"$URL_APPLICATION\"/ config/config.py
sed -i -e s/'^URL_USERHUB.*'/"URL_USERHUB = \"http:\/\/"$URL_USERHUB\"/ config/config.py
sed -i -e s/'^ID_APP.*'/"ID_APP = "$ID_APP/ config/config.py

cat config/config.py
