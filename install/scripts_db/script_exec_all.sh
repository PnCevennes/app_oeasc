if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

echo ${0##/*/}

psql -b -d $db_name -h $db_host -U $user_pg <<EOF

SELECT pg_terminate_backend(pid), * FROM active_locks;
DROP SCHEMA IF EXISTS oeasc CASCADE;

EOF


${ROOT_DIR}/install/scripts_db/script_add_functions_ext.sh

if [[ -f ${ROOT_DIR}/install/scripts_db/script_ref_geo/l_areas_oeasc.csv ]]; then

    # si on a un fichier de sauvegarde des aires qui concernent l'oeasc on fait la copie
    cp ${ROOT_DIR}/install/scripts_db/script_ref_geo/*_oeasc.csv /tmp/.

    echo copy ref_geo data
    cat ${ROOT_DIR}/install/scripts_db/SQL/get_areas_from_csv.sql | psql -b -d $db_name -h $db_host -U $user_pg

    rm -f /tmp/*_oeasc.csv

else

    # sinon on reproce à l'export et au traitement des géométries
    echo import from shapefiles
    ${ROOT_DIR}/install/scripts_db/script_exec_ref_geo_import.sh

    echo process ref_geo data
    ${ROOT_DIR}/install/scripts_db/script_exec_ref_geo_process.sh

    cp /tmp/*_oeasc.csv ${ROOT_DIR}/install/scripts_db/script_ref_geo/.

fi

${ROOT_DIR}/install/scripts_db/script_exec_nomenclature.sh
${ROOT_DIR}/install/scripts_db/script_exec_oeasc.sh
