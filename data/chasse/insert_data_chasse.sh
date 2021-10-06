set -x
EXEC_DIR=$(readlink -e "${0%/*}")
OEASC_DIR=${EXEC_DIR}/../..
source ${OEASC_DIR}/config/settings.ini


export PGPASSWORD=$user_pg_pass;

psql -h $db_host -U $user_pg -d $db_name -c 'DROP SCHEMA IF EXISTS oeasc_chasse CASCADE'
psql -h $db_host -U $user_pg -d $db_name -c 'CREATE SCHEMA oeasc_chasse'
psql -h $db_host -U $user_pg -d $db_name -f ${OEASC_DIR}/data/chasse/schema_chasse.sql

# import export schema
if [ ! -f data/import_chasse.dump ]; then
    export PGPASSWORD=$chasse_user_pg_pass;
    pg_dump -h $chasse_db_host -U $chasse_user_pg -d $chasse_db_name -n chasse --no-owner --no-acl -Fc > data/import_chasse.dump
fi

export PGPASSWORD=$user_pg_pass;
psql -h $db_host -U $user_pg -d $db_name -c 'DROP SCHEMA IF EXISTS import_chasse CASCADE'
psql -h $db_host -U $user_pg -d $db_name -c 'DROP SCHEMA IF EXISTS chasse CASCADE'
psql -h $db_host -U $user_pg -d $db_name -c 'CREATE SCHEMA chasse'
pg_restore -h $db_host -U $user_pg -d $db_name -n chasse --no-owner --no-acl data/import_chasse.dump
psql -h $db_host -U $user_pg -d $db_name -c 'ALTER SCHEMA chasse RENAME TO import_chasse'

# import des données zi zc
shp2pgsql -s 2154 -I shp/ZI_chasse_v2clean.shp oeasc_chasse.t_import_zi | psql -h $db_host -U $user_pg -d $db_name

psql -v ON_ERROR_STOP=1 -h $db_host -U $user_pg -d $db_name -f ${OEASC_DIR}/data/chasse/functions_chasse.sql
psql -v ON_ERROR_STOP=1 -h $db_host -U $user_pg -d $db_name -f ${OEASC_DIR}/data/chasse/result_ice.sql
psql -v ON_ERROR_STOP=1 -h $db_host -U $user_pg -d $db_name -f ${OEASC_DIR}/data/chasse/result_custom.sql
psql -v ON_ERROR_STOP=1 -h $db_host -U $user_pg -d $db_name -f ${OEASC_DIR}/data/chasse/views_chasse.sql
psql -h $db_host -U $user_pg -d $db_name -f ${OEASC_DIR}/data/oeasc_schemas/ref_geo.sql
psql -v ON_ERROR_STOP=1 -h $db_host -U $user_pg -d $db_name -f ${OEASC_DIR}/data/chasse/insert_data_chasse.sql

