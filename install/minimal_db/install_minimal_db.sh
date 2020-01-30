usershub_release=2.1.0
nomenclature_release=1.3.0
geonature_realease=2.3.0
srid_local=4326

ROOT_DIR=$(readlink -e "${0%/*}")/../../
log_file=${ROOT_DIR}var/log/install_db.log

MINIMAL_INSTALL_DIR=${ROOT_DIR}/install/install_db/minimal_db
. ${ROOT_DIR}/config/settings.ini


echo "Installation de la base minimale pour l'OEASC"


echo "Schema utilisateur"
sql_file=${MINIMAL_INSTALL_DIR}/userhub.sql
url=https://raw.githubusercontent.com/PnEcrins/UsersHub/$usershub_release/data/usershub.sql
if [ ! -f $sql_file ]; then
    wget --no-cache --no-cookies $url -P $sql_file
fi
echo "export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file"


echo "Schema nomenclature"
sql_file=${MINIMAL_INSTALL_DIR}/nomenclature.sql
url=https://raw.githubusercontent.com/PnX-SI/Nomenclature-api-module/$nomenclature_release/data/nomenclatures.sql
if [ ! -f $sql_file ]; then
    wget --no-cache --no-cookies $url -P $sql_file
fi
echo "export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file"


echo "Schema ref_geo"
sql_file=${MINIMAL_INSTALL_DIR}/ref_geo.sql
url=https://raw.githubusercontent.com/PnX-SI/GeoNature/$geonature_realease/data/core/ref_geo.sql
if [ ! -f $sql_file ]; then
    wget --no-cache --no-cookies $url -P $sql_file
    sudo sed -i "s/MYLOCALSRID/$srid_local/g" tmp/geonature/ref_geo.sql
fi
echo "export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file"
sql_file=${ROOT_DIR}/data/oeasc_schemas/ref_geo.sql
echo "export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file"



echo "Schema oeasc_commons"
sql_file=${ROOT_DIR}/data/oeasc_schemas/oeasc_commons.sql
echo "export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file"


echo "Schema oeasc_declarations"
sql_file=${ROOT_DIR}/data/oeasc_declarations.sql

echo "Schema oeasc_declarations views"
echo "export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file"
sql_file=${ROOT_DIR}/data/oeasc_declarations_views.sql


echo "Fonctions"

echo "fonctions nomenclatures" 
sql_file=${ROOT_DIR}/data/functions/nomenclatures.sql
echo "export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file"

echo "fonctions ref_geo" 
sql_file=${ROOT_DIR}/data/functions/ref_geo.sql
echo "export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file"



#echo "Schema oeasc_in"
#sql_file=${ROOT_DIR}/data/oeasc_in.sql
#echo "export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file"


