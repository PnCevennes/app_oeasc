if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

echo ${0##/*/}

psql -b -d $db_name -h $db_host -U $user_pg <<EOF
DROP SCHEMA IF EXISTS oeasc CASCADE;
EOF

file_SQL_ADD_FUNCTION_EXT=$ROOT_DIR/$sql_dir/SQL/add_functions_ext.sql
cat $file_SQL_ADD_FUNCTION_EXT | psql -b -d $db_name -h $db_host -U $user_pg

${ROOT_DIR}/install/scripts_db/script_exec_ref_geo_import.sh
${ROOT_DIR}/install/scripts_db/script_exec_ref_geo_process.sh
${ROOT_DIR}/install/scripts_db/script_exec_nomenclature.sh
${ROOT_DIR}/install/scripts_db/script_exec_oeasc.sh
