usershub_release=2.1.0
nomenclature_release=1.3.0
geonature_realease=2.3.0
srid_local=2154

ROOT_DIR=$(readlink -e "${0%/*}")/../..
log_file=${ROOT_DIR}/var/log/install_db.log

MINIMAL_INSTALL_DIR=${ROOT_DIR}/install/minimal_db
. ${ROOT_DIR}/config/settings.ini


echo "Installation de la base minimale pour l'OEASC" > $log_file

echo "delete_all" >> $log_file
sql_file=${MINIMAL_INSTALL_DIR}/delete_schemas.sql
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file

echo "minimal_install" >> $log_file
sql_file=${MINIMAL_INSTALL_DIR}/minimal_install.sql
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file


echo "Schema utilisateur" >> $log_file
sql_file=${MINIMAL_INSTALL_DIR}/usershub.sql
url=https://raw.githubusercontent.com/PnEcrins/UsersHub/$usershub_release/data/usershub.sql
if [ ! -f $sql_file ]; then
    wget --no-cache --no-cookies $url -O $sql_file
fi
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file


echo "Schema nomenclature" >> $log_file
sql_file=${MINIMAL_INSTALL_DIR}/nomenclature.sql
url=https://raw.githubusercontent.com/PnX-SI/Nomenclature-api-module/$nomenclature_release/data/nomenclatures.sql
if [ ! -f $sql_file ]; then
    wget --no-cache --no-cookies $url -O $sql_file
fi
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file

echo "fonctions nomenclatures" >> $log_file
sql_file=${ROOT_DIR}/data/functions/nomenclatures.sql
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file


echo "Schema ref_geo" >> $log_file
sql_file=${MINIMAL_INSTALL_DIR}/ref_geo.sql
url=https://raw.githubusercontent.com/PnX-SI/GeoNature/$geonature_realease/data/core/ref_geo.sql
if [ ! -f $sql_file ]; then
    wget --no-cache --no-cookies $url -O $sql_file
    sed -i "s/MYLOCALSRID/$srid_local/g" $sql_file
fi
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file

echo "complements ref_geo" >> $log_file
sql_file=${ROOT_DIR}/data/oeasc_schemas/ref_geo.sql
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file

echo "fonctions ref_geo" >> $log_file
sql_file=${ROOT_DIR}/data/functions/ref_geo.sql
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file


echo "fonctions generiques" >> $log_file
sql_file=${ROOT_DIR}/data/functions/generic.sql
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file

echo "Schema oeasc_commons" >> $log_file
sql_file=${ROOT_DIR}/data/oeasc_schemas/oeasc_commons.sql
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file

echo "Schema oeasc_forets" >> $log_file
sql_file=${ROOT_DIR}/data/oeasc_schemas/oeasc_forets.sql
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file


echo "Schema oeasc_declarations" >> $log_file
sql_file=${ROOT_DIR}/data/oeasc_schemas/oeasc_declarations.sql
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file

echo "Schema oeasc_declarations views" >> $log_file
sql_file=${ROOT_DIR}/data/oeasc_schemas/oeasc_declarations_views.sql
export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file

#echo "Schema oeasc_in"
#sql_file=${ROOT_DIR}/data/oeasc_in.sql
#echo export PGPASSWORD=$user_pg_pass;psql -h $db_host -U $user_pg -d $db_name -f $sql_file  &>> $log_file

cat $log_file | grep ERROR
