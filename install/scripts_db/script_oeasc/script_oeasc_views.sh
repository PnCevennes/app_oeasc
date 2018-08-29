
if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file


table_l_areas=l_areas

for name in $list_name
do
    table=table_$name
    table=${!table}
    keys=keys_$name
    keys=${!keys}
    echo '-- create ref_geo.vl_${name}'

    cat << EOF

    CREATE OR REPLACE VIEW ref_geo.vl_${name} AS
        SELECT li.*, la.geom_4326
            FROM ref_geo.li_${name} as li, ref_geo.l_areas as la,
            (SELECT geom_4326 
                FROM ref_geo.l_areas
                WHERE id_type=ref_geo.get_id_type('OEASC_PERIMETRE')
            )a
        WHERE la.area_code = li.area_code AND ST_INTERSECTS(la.geom_4326, a.geom_4326);

EOF

done
