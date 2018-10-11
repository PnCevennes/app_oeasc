
if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file



tmp_file=/tmp/tmp_shsql

echo "-- import perimetre OEASC" > $tmp_file

db_schema=ref_geo

# import oeasc
codage=ISO-8859-1
db_schema=ref_geo
shp=Perimetre_OEASC
table=${shp}

shp2pgsql  -W ${codage} -s 2154 -d -D -I ${dir_data}/Zonage_OEASC/${shp}.shp ${db_schema}.${table} >> $tmp_file


shp2pgsql  -W ${codage} -s 2154 -d -D -I ${dir_data}/limites_pnc/zone_coeur.shp ref_geo.zc_pnc >> $tmp_file
shp2pgsql  -W ${codage} -s 2154 -d -D -I ${dir_data}/limites_pnc/aire_adhesion.shp ref_geo.zc_pnc >> $tmp_file



cat $tmp_file
