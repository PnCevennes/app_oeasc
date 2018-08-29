

if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

echo ${0##/*/}

psql -b -d $db_name -h $db_host -U $user_pg <<EOF
SELECT pg_terminate_backend(pid), * FROM active_locks
EOF


#nomenclature

file_SQL_NOMENCLATURE=$ROOT_DIR/$sql_dir/SQL/nomenclature.sql
echo create file : $file_SQL_NOMENCLATURE
echo '-- nomenclature' > $file_SQL_NOMENCLATURE

#remplir la nomenclature specifique à OEASC
$ROOT_DIR/$sql_dir/script_nomenclature/script_oeasc_nomenclature.sh >> $file_SQL_NOMENCLATURE
