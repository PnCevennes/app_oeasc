
if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file

name=$1
table=table_$name
keys_label=keys_label_$name
table=${!table}
keys_label=${!keys_label}


cat <<EOF

ALTER TABLE ref_geo.$table DROP COLUMN IF EXISTS suffix;
ALTER TABLE ref_geo.$table ADD COLUMN suffix integer;

UPDATE ref_geo.${table} as c
    SET suffix=b.suffix_b
    FROM (
        SELECT id, CONCAT(${keys_label}) as ccod,
            row_number() OVER (
                PARTITION BY CONCAT(${keys_label})
                    ORDER BY CONCAT(${keys_label}), id) AS suffix_b
            FROM (
                SELECT COUNT(*) as c, CONCAT(${keys_label}) as ccod
                    FROM ref_geo.${table} as b
                    GROUP BY ccod
                    HAVING COUNT(*) >1
                    ORDER BY ccod
            )a, ref_geo.${table}
        WHERE a.ccod = CONCAT(${keys_label})
        ORDER BY a.ccod
    )b
    WHERE b.ccod = CONCAT(${keys_label}) and b.id = c.id;

EOF
