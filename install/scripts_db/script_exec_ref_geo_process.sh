if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

echo ${0##/*/}

file_SQL_REF_GEO_PROCESS=$ROOT_DIR/$sql_dir/SQL/ref_geo_process.sql

echo process file $file_SQL_REF_GEO_PROCESS

cat $file_SQL_REF_GEO_PROCESS | psql -d $db_name -h $db_host -U $user_pg
