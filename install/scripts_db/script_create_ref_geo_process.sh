

if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

echo ${0##/*/}

# schema ref_geo

file_SQL_REF_GEO_PROCESS=$ROOT_DIR/$sql_dir/SQL/ref_geo_process.sql
echo create file : $file_SQL_REF_GEO_PROCESS
echo '-- ref_geo process' > $file_SQL_REF_GEO_PROCESS


#merger les geom de memes identifiants ou les indexe en rajoutant suffix (pour les UG)
$ROOT_DIR/$sql_dir/script_ref_geo/script_ref_geo_merge_or_index.sh >> $file_SQL_REF_GEO_PROCESS

#remplr l_areas avec les elts de geometrie
# + ref_geo.bib_areas_types
$ROOT_DIR/$sql_dir/script_ref_geo/script_ref_geo_l_areas.sh >> $file_SQL_REF_GEO_PROCESS

#remplir li_{nom de la table} pour les données attributs
$ROOT_DIR/$sql_dir/script_ref_geo/script_ref_geo_li_attributes.sh >> $file_SQL_REF_GEO_PROCESS
