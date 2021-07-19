set -x
EXEC_DIR=$(readlink -e "${0%/*}")
OEASC_DIR=${EXEC_DIR}/../..
source ${OEASC_DIR}/config/settings.ini


export PGPASSWORD=$user_pg_pass;

psql -h $db_host -U $user_pg -d $db_name -c 'DROP SCHEMA IF EXISTS oeasc_chasse CASCADE'
psql -h $db_host -U $user_pg -d $db_name -c 'CREATE SCHEMA oeasc_chasse'
psql -h $db_host -U $user_pg -d $db_name -f ${OEASC_DIR}/data/chasse/schema_chasse.sql

# import export schema
if [ ! -f /tmp/import_chasse.dump ]; then
    export PGPASSWORD=$chasse_user_pg_pass;
    pg_dump -h $chasse_db_host -U $chasse_user_pg -d $chasse_db_name -n chasse --no-owner --no-acl -Fc > /tmp/import_chasse.dump
fi 
 export PGPASSWORD=$user_pg_pass;
 psql -h $db_host -U $user_pg -d $db_name -c 'DROP SCHEMA IF EXISTS import_chasse CASCADE'
 psql -h $db_host -U $user_pg -d $db_name -c 'DROP SCHEMA IF EXISTS chasse CASCADE'
 psql -h $db_host -U $user_pg -d $db_name -c 'CREATE SCHEMA chasse'
 pg_restore -h $db_host -U $user_pg -d $db_name -n chasse --no-owner --no-acl /tmp/import_chasse.dump
 psql -h $db_host -U $user_pg -d $db_name -c 'ALTER SCHEMA chasse RENAME TO import_chasse'

psql -h $db_host -U $user_pg -d $db_name -f ${OEASC_DIR}/data/chasse/functions_chasse.sql
psql -h $db_host -U $user_pg -d $db_name -f ${OEASC_DIR}/data/chasse/ice.sql
psql -h $db_host -U $user_pg -d $db_name -f ${OEASC_DIR}/data/chasse/views_chasse.sql
psql -h $db_host -U $user_pg -d $db_name -f ${OEASC_DIR}/data/oeasc_schema/ref_geo.sql

psql -h $db_host -U $user_pg -d $db_name -f ${OEASC_DIR}/data/chasse/insert_data_chasse.sql

