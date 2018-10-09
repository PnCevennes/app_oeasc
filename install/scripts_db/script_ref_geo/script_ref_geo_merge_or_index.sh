
if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file


name='OEASC_ONF_FRT'
$ROOT_DIR/$sql_dir/script_ref_geo/script_ref_geo_merge_by_keys.sh $name

name='OEASC_ONF_PRF'
$ROOT_DIR/$sql_dir/script_ref_geo/script_ref_geo_merge_by_keys.sh $name

name='OEASC_ONF_UG'
$ROOT_DIR/$sql_dir/script_ref_geo/script_ref_geo_index_by_keys.sh $name

