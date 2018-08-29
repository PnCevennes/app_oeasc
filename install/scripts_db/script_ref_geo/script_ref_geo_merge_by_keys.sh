
if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file



name=$1
table=table_${name}
keys=keys_${name}
table=${!table}
keys=${!keys}



cat << EOF

UPDATE ref_geo.${table}
    SET geom=a.geom FROM (
        SELECT CONCAT(${keys}) as ccod, ST_MULTI(ST_UNION(geom)) as geom
        FROM ref_geo.${table}
        GROUP BY ccod
        HAVING COUNT(*) > 1
        )a

    WHERE a.ccod=CONCAT(${keys});

DELETE FROM ref_geo.${table}
    WHERE id IN (SELECT id
        FROM (SELECT id,
            ROW_NUMBER() OVER (partition BY CONCAT(${keys}) ORDER BY id) AS rnum
            FROM ref_geo.${table}) t
                WHERE t.rnum > 1);

EOF
