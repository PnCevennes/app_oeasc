#!/bin/bash

# echo "config settings"

if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/..
fi

config_file=$1

# echo aa $config_file
. $config_file


# echo "Creation de config/config.py"
cp config/config.py.sample config/config.py

DB_URI="postgresql:\/\/$user_pg:$user_pg_pass@$db_host:$db_port\/$db_name"

# echo $DB_URI

replace_str() {

    var=$1
    value=${!var}
    if [ "$value" != "" ]
    then
        sed -i -e s/"^${var}.*"/"${var} = \"${value}\""/ config/config.py

    fi

}

replace_num() {

    var=$1
    value=${!var}
    cote=$2
    if [ "$value" != "" ]
    then

        sed -i -e s/"^${var}.*"/"${var} = ${value}"/ config/config.py

    fi

}


sed -i -e s/'^URL_APPLICATION.*'/"URL_APPLICATION = \"http:\/\/"$URL_APPLICATION\"/ config/config.py
sed -i -e s/'^URL_USERHUB.*'/"URL_USERHUB = \"http:\/\/"$URL_USERHUB\"/ config/config.py
sed -i -e s/'^SQLALCHEMY_DATABASE_URI.*'/"SQLALCHEMY_DATABASE_URI = \""$DB_URI\"/ config/config.py #> config/config.py


for var in "MAIL_ANIMATEUR" "DEFAULT_MAIL_SENDER" "MAIL_SERVER" "MAIL_PORT" "MAIL_PASSWORD" "MAIL_USERNAME" "MAIL_ANIMATEUR" "MAIL_USE_SSL" "ADMIN_OEASC_PASSWORD" "ADMIN_OEASC_MAIL" "ADMIN_OEASC_LOGIN"
do
    replace_str $var
done

for var in "ID_APP" "MAIL_USE_TLS" "MAIL_USE_SSL"
do
    replace_num $var
done


# sed -i -e s/'^ID_APP.*'/"ID_APP = "$ID_APP/ config/config.py

# sed -i -e s/'^MAIL_ANIMATEUR.*'/"MAIL_ANIMATEUR = '"$MAIL_ANIMATEUR"'"/ config/config.py
# sed -i -e s/'^DEFAULT_MAIL_SENDER.*'/"DEFAULT_MAIL_SENDER = '"$DEFAULT_MAIL_SENDER"'"/ config/config.py
# sed -i -e s/'^MAIL_SERVER.*'/"MAIL_SERVER = '"$MAIL_SERVER"'"/ config/config.py
# sed -i -e s/'^MAIL_PORT.*'/"MAIL_PORT = "$MAIL_PORT/ config/config.py
# sed -i -e s/'^MAIL_USERNAME.*'/"MAIL_USERNAME = '"$MAIL_USERNAME"'"/ config/config.py
# sed -i -e s/'^MAIL_PASSWORD.*'/"MAIL_PASSWORD = '"$MAIL_PASSWORD"'"/ config/config.py
# sed -i -e s/'^MAIL_USE_TLS.*'/"MAIL_USE_TLS = "$MAIL_USE_TLS/ config/config.py
# sed -i -e s/'^MAIL_USE_SSL.*'/"MAIL_USE_SSL = "$MAIL_USE_SSL/ config/config.py

cat config/config.py
