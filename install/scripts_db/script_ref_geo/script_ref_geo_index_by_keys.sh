
if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

name=$1
table=table_$name
keys=keys_$name
table=${!table}
keys=${!keys}


cat <<EOF

ALTER TABLE ref_geo.$table DROP COLUMN IF EXISTS suffix;
ALTER TABLE ref_geo.$table ADD COLUMN suffix integer;

UPDATE ref_geo.${table} as c
    SET suffix=b.suffix_b
    FROM (
        SELECT id, CONCAT(${keys}) as ccod,
            row_number() OVER (
                PARTITION BY CONCAT(${keys})
                    ORDER BY CONCAT(${keys}), id) AS suffix_b
            FROM (
                SELECT COUNT(*) as c, CONCAT(${keys}) as ccod
                    FROM ref_geo.${table} as b
                    GROUP BY ccod
                    HAVING COUNT(*) >1
                    ORDER BY ccod
            )a, ref_geo.${table}
        WHERE a.ccod = CONCAT(${keys})
        ORDER BY a.ccod
    )b
    WHERE b.ccod = CONCAT(${keys}) and b.id = c.id;

EOF
