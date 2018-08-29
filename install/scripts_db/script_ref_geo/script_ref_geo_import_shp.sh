
if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file



tmp_file_i=/tmp/tmp_shsql_i

echo "-- import ref_geo shp"

db_schema=ref_geo

for name in $list_name
do
    table=table_${name}
    shp=shp_${name}
    codage=codage_${name}
    table=${!table}
    shp=${!shp}
    codage=${!codage}

    # echo
    # echo "#######################################################################"
    # echo "#######################################################################"
    # echo
    # echo import de $name $dir_datas $codage
    # echo
    # echo "#######################################################################"
    # echo "#######################################################################"
    # echo


#     DROP TABLE IF EXISTS ref_geo.${table} CASCADE;
# EOF
    echo '-- import table ${table}' > $tmp_file_i

    cat <<EOF >> $tmp_file_i
    DROP TABLE IF EXISTS ref_geo.${table} CASCADE;
EOF


    shp2pgsql  -W ${codage} -s 2154 -D -I ${dir_data}/donnees_gestion_foret/${shp}.shp ${db_schema}.${table} | grep -v "\[" | grep -v '^\s*$$' >> $tmp_file_i


    # echo correction éàô
    sed -i -e "s/Š/è/g" -e "s/‚/é/g" -e "s/“/ô/g" -e "s/č/ê/g" $tmp_file_i
    sed -i -e "s/cêze/cèse/g" -e "s/Cêze/Cèse/g" $tmp_file_i



    echo "ALTER TABLE ref_geo.${table} RENAME COLUMN gid TO id;" >> $tmp_file_i


    if [ "${table}" = "l_OEASC_DGD" ]
    then

        echo '-- correction geom pour $table'

        cat <<EOF >> $tmp_file_i

        WITH corrected_data AS (
            SELECT id, st_union(geom) as corrected_geom, st_geometrytype(st_union(geom))
                FROM (
                    SELECT (st_dump(st_makevalid(geom))).geom as geom, id
                    FROM ref_geo.${table}
                    WHERE NOT st_isvalid(geom)
                )a
                WHERE NOT st_geometrytype(geom) = 'ST_LineString'
                GROUP BY id
        )
        UPDATE ref_geo.${table} d SET geom = c.corrected_geom
            FROM corrected_data c
            WHERE d.id = c.id;

EOF

    else if [ ${table} != "l_OEASC_CADASTRE" ]
        then
            # echo changer les ccod_frt qui contiennent - pour _
            # echo correction - en _ pour ccod_frt


            cat <<EOF >> $tmp_file_i

            UPDATE ref_geo.${table}
                SET ccod_frt = REPLACE(ccod_frt,'-','_')
                WHERE ccod_frt LIKE '%-%';

EOF

        fi
    fi

        echo '-- corrections geom invalides'

        cat <<EOF >> $tmp_file_i

        UPDATE  ref_geo.${table} SET geom = st_makevalid(geom)
            WHERE NOT ST_ISVALID(geom);
EOF

        echo '-- delete element outside OEASC'

        cat <<EOF >> $tmp_file_i


        DELETE FROM ref_geo.${table} t
        USING ref_geo.perimetre_OEASC as p
            WHERE NOT ST_INTERSECTS(t.geom, p.geom);
EOF

    cat $tmp_file_i

done


