

if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

echo ${0##/*/}



psql -b -d $db_name -h $db_host -U $user_pg <<EOF

DROP TABLE IF EXISTS ref_geo.l_oeasc_onf_frt CASCADE;
DROP TABLE IF EXISTS ref_geo.l_oeasc_onf_prf CASCADE;
DROP TABLE IF EXISTS ref_geo.l_oeasc_onf_ug CASCADE;
DROP TABLE IF EXISTS ref_geo.l_oeasc_dgd CASCADE;
DROP TABLE IF EXISTS ref_geo.l_oeasc_cadastre CASCADE;

EOF
