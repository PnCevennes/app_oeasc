if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

echo ${0##/*/}

# schema ref_geo

file_SQL_REF_GEO_IMPORT=$ROOT_DIR/$sql_dir/SQL/ref_geo_import.sql
echo create file : $file_SQL_REF_GEO_IMPORT
echo '-- ref_geo import' > $file_SQL_REF_GEO_IMPORT


#importer le perimetre OEASC
$ROOT_DIR/$sql_dir/script_ref_geo/script_ref_geo_import_oeasc.sh >> $file_SQL_REF_GEO_IMPORT # perimetre

#importer depuis les .shp et corrige les geometries fausse
$ROOT_DIR/$sql_dir/script_ref_geo/script_ref_geo_import_shp.sh >> $file_SQL_REF_GEO_IMPORT # geometries ONF DGD CADASTRE COMMUNE
