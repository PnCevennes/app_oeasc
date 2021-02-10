EXEC_DIR=$(readlink -e "${0%/*}")
OEASC_DIR=${EXEC_DIR}/../..
source ${OEASC_DIR}/config/settings.ini
    
export PGPASSWORD=$user_pg_pass;

psql -h $db_host -U $user_pg -d $db_name -f ${OEASC_DIR}/data/chasse/schema_chasse.sql
psql -h $db_host -U $user_pg -d $db_name -f ${OEASC_DIR}/data/chasse/fdw_chasse.sql \
-v chasse_db_host=${chasse_db_host} \
-v chasse_db_name=${chasse_db_name} \
-v chasse_db_port=${chasse_db_port} \
-v chasse_user_pg=${chasse_user_pg} \
-v user_pg=${user_pg} \
-v chasse_user_pg_pass=${chasse_user_pg_pass}
psql -h $db_host -U $user_pg -d $db_name -f ${OEASC_DIR}/data/chasse/insert_data_chasse.sql

