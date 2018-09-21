

if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

echo ${0##/*/}

psql -b -d $db_name -h $db_host -U $user_pg <<EOF
-- -- SELECT pg_terminate_backend(pid), * FROM active_locks
EOF

$ROOT_DIR/$sql_dir/script_create_ref_geo_import.sh
$ROOT_DIR/$sql_dir/script_create_ref_geo_process.sh
$ROOT_DIR/$sql_dir/script_create_nomenclature.sh




