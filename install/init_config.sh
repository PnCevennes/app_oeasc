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

sed -i -e s!'^URL_APPLICATION.*'!"URL_APPLICATION = \""$URL_APPLICATION"\""! config/config.py
sed -i -e s!'^URL_USERSHUB.*'!"URL_USERSHUB = \""$URL_USERSHUB"\""! config/config.py
sed -i -e s/'^SQLALCHEMY_DATABASE_URI.*'/"SQLALCHEMY_DATABASE_URI = \""$DB_URI\"/ config/config.py #> config/config.py

for var in "MAIL_ANIMATEUR" "DEFAULT_MAIL_SENDER" \
"MAIL_SERVER" "MAIL_PORT" "MAIL_PASSWORD" "MAIL_USERNAME" \
"MAIL_ANIMATEUR" "MAIL_USE_SSL" "ADMIN_APPLICATION_PASSWORD" \
"ADMIN_APPLICATION_MAIL" "ADMIN_APPLICATION_LOGIN" "SECRET_KEY" \
"ANIMATEUR_APPLICATION_MAIL"
do    
    replace_str $var
done

for var in "ID_APP" "MAIL_USE_TLS" "MAIL_USE_SSL" "MODE_TEST" "MAIL_USE_TLS"
do
    replace_num $var
done

cat config/config.py


# front
if [ ! -f "static/src/js/config/config.js" ];
then 
cp static/src/js/config/config.js.sample static/src/js/config/config.js
exit 1
fi

if [ ! -f "static/src/js/config/config-map.js" ];
then 
cp static/src/js/config/config-map.js.sample static/src/js/config/config-map.js
exit 1
fi

sed -i -e s!'URL_APPLICATION.*'!"URL_APPLICATION: '"$URL_APPLICATION"',"! static/src/js/config/config.js
# sed -i -e s!'INIT_VIEW.*'!"INIT_VIEW: "$INIT_VIEW! static/src/js/config.js
cat static/src/js/config/config.js

exit 0
