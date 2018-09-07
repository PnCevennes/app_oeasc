if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

echo ${0##/*/}

file_SQL_OEASC=$ROOT_DIR/$sql_dir/SQL/oeasc.sql

echo process file $file_SQL_OEASC

cat $ROOT_DIR/$sql_dir/SQL/functions.sql | psql -d $db_name -h $db_host -U $user_pg
cat $ROOT_DIR/$sql_dir/SQL/oeasc_create_schema.sql | psql -d $db_name -h $db_host -U $user_pg
cat $ROOT_DIR/$sql_dir/SQL/oeasc_populate_organismes.sql | psql -d $db_name -h $db_host -U $user_pg
cat $ROOT_DIR/$sql_dir/SQL/oeasc_populate_frt.sql | psql -d $db_name -h $db_host -U $user_pg

${ROOT_DIR}/install/scripts_db/script_init_users.sh
