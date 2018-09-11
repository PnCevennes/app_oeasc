

if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

echo ${0##/*/}

psql -b -d $db_name -h $db_host -U $user_pg <<EOF
-- -- SELECT pg_terminate_backend(pid), * FROM active_locks
EOF


# schema oeasc

file_SQL_OEASC=$ROOT_DIR/$sql_dir/SQL/oeasc.sql
echo create file : $file_SQL_OEASC
echo '-- oeasc' > $file_SQL_OEASC

# ajout de fonctions dans ref_geo et ref_nomenclature
$ROOT_DIR/$sql_dir/script_oeasc/script_add_functions_ext.sh >> $file_SQL_OEASC

# creer le schema oeasc et les elements pour l alerte
$ROOT_DIR/$sql_dir/script_oeasc/script_oeasc_schema.sh >> $file_SQL_OEASC

#creer les vue relative au données carte parcelle foret etc...
$ROOT_DIR/$sql_dir/script_oeasc/script_oeasc_views.sh >> $file_SQL_OEASC




