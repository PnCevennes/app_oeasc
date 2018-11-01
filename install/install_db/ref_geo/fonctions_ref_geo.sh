function import_shp() {
    name=$1
    shp_file=$2
    file_coding=$3

    table=ref_geo.temp_${name}
    tmp_file=/tmp/oeasc_import_${name}.shp
    srid=2154

    echo "DROP TABLE IF EXISTS $table;" | $psqla >> $log_file

    #import shp
    shp2pgsql  -W ${file_coding} -s ${srid} -D -I ${shp_file} ${table} | grep -v "\[" | grep -v '^\s*$$' > $tmp_file

    #correction typo
    sed -i -e "s/Š/è/g" -e "s/‚/é/g" -e "s/“/ô/g" -e "s/č/ê/g" $tmp_file
    sed -i -e "s/cêze/cèse/g" -e "s/Cêze/Cèse/g" $tmp_file

    echo >> $log_file
    echo import table $table from file $shp_file >> $log_file
    cat $tmp_file | $psqla >> $log_file

    echo "ALTER TABLE ${table} RENAME COLUMN gid TO id;" | $psqla >> $log_file

    correct_geometry $name

    correct_ccod $name

}


function clear_all(){

    clear_geometry OEASC_CADASTRE
    clear_geometry OEASC_COMMUNE
    clear_geometry OEASC_DGD
    clear_geometry OEASC_SECTION
    clear_geometry OEASC_ONF_FRT
    clear_geometry OEASC_ONF_PRF
    clear_geometry OEASC_ONF_UG
    clear_geometry OEASC_PERIMETRE
    clear_geometry OEASC_SECTEUR
    clear_geometry ZC_PNC
    clear_geometry AA_PNC

    clear_cor_old_communes
    clear_cor_dgd_cadastre

}

function clean() {

    name=$1
    tmp_file=/tmp/oeasc_import_${name}.shp

    echo "DROP TABLE IF EXISTS $table;" | $psqla >> log_file
    rm -f $tmp_file

}


function get_id_type() {

    name=$1
    id_type=$(echo "SELECT ref_geo.get_id_type('"$name"');" | $psqla -t)
    id_type=$(echo $id_type)
    echo ${id_type}
}

function correct_geometry() {

    name=$1
    table=ref_geo.temp_${name}

    echo correct $name

    if [ "$name" = "OEASC_DGD" ]
    then

        cat <<EOF | $psqla >> $log_file

        WITH corrected_data AS (
            SELECT id, st_union(geom) as corrected_geom, st_geometrytype(st_union(geom))
                FROM (
                    SELECT (st_dump(st_makevalid(geom))).geom as geom, id
                    FROM ${table}
                    WHERE NOT st_isvalid(geom)
                )a
                WHERE NOT st_geometrytype(geom) = 'ST_LineString'
                GROUP BY id
        )
        UPDATE ${table} d SET geom = c.corrected_geom
            FROM corrected_data c
            WHERE d.id = c.id;
EOF

    fi

     cat <<EOF | $psqla >> $log_file
        UPDATE  ${table} SET geom = st_makevalid(geom)
            WHERE NOT ST_ISVALID(geom);
EOF

}

function correct_ccod() {

    name=$1
    table=ref_geo.temp_${name}

    if [ "${name}" == "OEASC_ONF_FRT" ] || [ "${name}" == "OEASC_ONF_PRF" ] || [ "${name}" == "OEASC_ONF_UG" ]
    then
        # changer les ccod_frt qui contiennent - pour _
        # correction - en _ pour ccod_frt


        cat <<EOF | $psqla >> $log_file

        UPDATE ${table}
            SET ccod_frt = REPLACE(ccod_frt,'-','_')
            WHERE ccod_frt LIKE '%-%';
EOF

    fi

}

function clear_geometry() {

    name=$1
    table=ref_geo.temp_${name}

    cat <<EOF  | $psqla >> $log_file

    DELETE FROM ref_geo.li_areas WHERE id_type=ref_geo.get_id_type('$name');
    DELETE FROM ref_geo.l_areas_simples WHERE id_type=ref_geo.get_id_type('$name');

    ALTER TABLE ref_geo.l_areas DISABLE TRIGGER ALL;
    DELETE FROM ref_geo.l_areas WHERE id_type=ref_geo.get_id_type('$name');
    ALTER TABLE ref_geo.l_areas ENABLE TRIGGER ALL;

    DELETE FROM ref_geo.bib_areas_types WHERE id_type=ref_geo.get_id_type('$name');

EOF
}

function select_inside_oeasc() {

    name=$1
    table=ref_geo.temp_${name}

    cat <<EOF | $psqla >> $log_file

        DELETE FROM ${table} t
            USING ref_geo.temp_oeasc_perimetre as p
            WHERE NOT ST_INTERSECTS(t.geom, p.geom);
EOF

}

function reinit_seq_l_areas() {

    echo "SELECT setval('ref_geo.l_areas_id_area_seq', COALESCE((SELECT MAX(id_area)+1 FROM ref_geo.l_areas), 1), false);"| $psqla >> $log_file
    echo "SELECT setval('ref_geo.l_areas_simples_id_area_seq', COALESCE((SELECT MAX(id_area_simple)+1 FROM ref_geo.l_areas_simples), 1), false);"| $psqla >> $log_file
    echo "SELECT setval('ref_geo.bib_areas_types_id_type_seq', COALESCE((SELECT MAX(id_type)+1 FROM ref_geo.bib_areas_types), 1), false);"| $psqla >> $log_file
    echo "SELECT setval('ref_geo.li_areas_id_info_seq', COALESCE((SELECT MAX(id_info)+1 FROM ref_geo.li_areas), 1), false);"| $psqla >> $log_file
}

function populate_li_areas() {

    name=$1
    table=ref_geo.temp_${name}
    keys_code=$2 # pour area_code
    keys_label=$3 # pour le label
    dept=$4
    surface_renseignee=$5

    cat <<EOF | $psqla >> $log_file

    DELETE FROM ref_geo.li_areas WHERE id_type=ref_geo.get_id_type('$name');

    INSERT INTO ref_geo.li_areas(id_area, id_type, area_name, area_code, source, label, dept, surface_renseignee, surface_calculee)
    SELECT l.id_area, l.id_type, l.area_name, l.area_code, 'OEASC', ${keys_label}, $dept, ROUND($surface_renseignee), ROUND(ST_AREA(l.geom)/10000)
        FROM ${table}, ref_geo.l_areas as l
        WHERE l.id_type = ref_geo.get_id_type('${name}')
            AND ${keys_code} = l.area_code;

EOF
}

function populate_l_areas() {

    type_code=$1
    type_name=$2
    type_desc=$3
    keys_name=$4 # pour area_name
    keys_code=$5 # pour area_code

    table=ref_geo.temp_${name}

    cat <<EOF | $psqla >> $log_file

    INSERT INTO ref_geo.bib_areas_types (type_name, type_code, type_desc, ref_name, ref_version, num_version)
        VALUES('$type_name', '$type_code', '$type_desc', 'OEASC', 2018, '');

    INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, geom_4326, source)
    SELECT ref_geo.get_id_type('${name}'), ${keys_name}, ${keys_code}, geom, ST_CENTROID(geom), ST_TRANSFORM(geom, 4326), 'OEASC'
    FROM ${table};

EOF


    if [ "${name}" == "OEASC_ONF_UG" ]
    then

        cat <<EOF | $psqla >> $log_file

UPDATE ref_geo.l_areas
    SET (area_name)=(SELECT ref_geo.clean_ug_name(area_name)
        FROM ref_geo.l_areas as l
            WHERE l.id_area=ref_geo.l_areas.id_area
        )
        WHERE id_type=ref_geo.get_id_type('OEASC_ONF_UG')

EOF

    fi
}

function merge_geom_by_code() {

    name=$1
    keys_code=$2

    table=ref_geo.temp_${name}



    cat << EOF  | $psqla >> $log_file

UPDATE ${table}
    SET geom=a.geom FROM (
        SELECT ${keys_code} as ccod, ST_MULTI(ST_UNION(geom)) as geom
        FROM ${table}
        GROUP BY ccod
        HAVING COUNT(*) > 1
        )a

    WHERE a.ccod=${keys_code};

DELETE FROM ${table}
    WHERE id IN (SELECT id
        FROM (SELECT id,
            ROW_NUMBER() OVER (partition BY ${keys_code} ORDER BY id) AS rnum
            FROM ${table}) t
                WHERE t.rnum > 1);

EOF

}

function index_geom_by_code() {

    name=$1
    keys_code=$2

    table=ref_geo.temp_${name}

    cat << EOF | $psqla >> $log_file

ALTER TABLE $table DROP COLUMN IF EXISTS suffix;
ALTER TABLE $table ADD COLUMN suffix integer;

UPDATE ${table} as c
    SET suffix=b.suffix_b
    FROM (
        SELECT id, ${keys_code} as ccod,
            row_number() OVER (
                PARTITION BY ${keys_code}
                    ORDER BY ${keys_code}, id) AS suffix_b
            FROM (
                SELECT COUNT(*) as c, ${keys_code} as ccod
                    FROM ${table} as b
                    GROUP BY ccod
                    HAVING COUNT(*) >1
                    ORDER BY ccod
            )a, ${table}
        WHERE a.ccod = ${keys_code}
        ORDER BY a.ccod
    )b
    WHERE b.ccod = ${keys_code} and b.id = c.id;
EOF

}

function label_propre() {

    name=$1
    file=$2

    cat << EOF | $psqla >> $log_file

DROP TABLE IF EXISTS temp;

CREATE TABLE temp (code text, name text);

\COPY temp FROM '$file' WITH DELIMITER ';' CSV QUOTE AS '''';

UPDATE ref_geo.li_areas
    SET (label)=
        (SELECT t.name
            FROM temp as t
            WHERE t.code=area_code)
    WHERE id_type = ref_geo.get_id_type('$name');

DROP TABLE IF EXISTS temp;

EOF

}


function process_geom() {

id_type=$(get_id_type $name)
if [ "$id_type" == "" ]
then
    modifs=1

    echo process $name

    echo id_type n''existe pas pour $name

    import_shp $name $shp_file $shp_coding

    [ "$select" == "1" ] && select_inside_oeasc $name

    [ "$merge" == "1" ] && merge_geom_by_code $name $keys_code
    [ "$index" == "1" ] && index_geom_by_code $name $keys_code

    reinit_seq_l_areas

    populate_l_areas "$name" "$type_name" "$type_desc" "$keys_name" "$keys_code"

    populate_li_areas "$name" "$keys_code" "$keys_label" "$keys_dept" "$keys_surf"

else
    echo id_type $id_type existe deja pour $name
fi

    [ -f "$label_file" ] && label_propre $name $label_file

}




function create_sections() {

reinit_seq_l_areas

name=OEASC_SECTION

dl=10

id_type=$(get_id_type $name)

if [ "$id_type" == "" ]
then

    modifs=1
    echo process $name

    cat << EOF | $psqla >> $log_file

-- SECTIONS CADASTRALES

INSERT INTO ref_geo.bib_areas_types (type_name, type_code, type_desc, ref_name, ref_version, num_version)
    VALUES('Sections cadastrales','OEASC_SECTION', 'Sections cadastrales', 'OEASC', 2018, '');

SELECT ref_geo.get_id_type('OEASC_SECTION');

DROP TABLE IF EXISTS temp;

CREATE TABLE temp(area_code character varying(256), area_name character varying(256), geom GEOMETRY);

INSERT INTO temp(area_code, area_name, geom)
SELECT CONCAT(insee_com, '-',section), CONCAT(nom_com, '-',section), ST_MULTI(ST_MAKEVALID(ST_BUFFER(ST_BUFFER(ST_UNION(geom),$dl),-$dl)))
  FROM ref_geo.temp_oeasc_cadastre
  GROUP BY insee_com, nom_com, section
  ORDER BY insee_com, nom_com, section;

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, geom_4326, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_SECTION'), t.area_name, t.area_code, t.geom, ST_TRANSFORM(t.geom, 4326), ST_CENTROID(t.geom), 'OEASC', '', true
    FROM temp as t;

DELETE FROM ref_geo.li_areas WHERE id_type=ref_geo.get_id_type('$name');

INSERT INTO ref_geo.li_areas(id_area, id_type, area_name, area_code, source, label, dept, surface_renseignee, surface_calculee)
    SELECT l.id_area, l.id_type, l.area_name, l.area_code, 'OEASC', l.area_name, SUBSTRING(l.area_code,1,2), ROUND(ST_AREA(l.geom)/10000), ROUND(ST_AREA(l.geom)/10000)
        FROM ref_geo.l_areas as l
        WHERE l.id_type = ref_geo.get_id_type('${name}');

DROP TABLE temp;

EOF

else

    echo id_type $id_type existe deja pour $name

fi

}

function test_simple() {

    name=$1

    test=$(echo "SELECT id_type FROM ref_geo.l_areas_simples WHERE id_type=ref_geo.get_id_type('$name') LIMIT 1" | $psqla -t)
    echo $test
}

function simplify_geom() {

name=$1
tolerance=$2

if [ "$(test_simple $name)" == "" ]
then
cat << EOF | $psqla # >> $log_file

DELETE FROM ref_geo.l_areas_simples WHERE id_type=ref_geo.get_id_type('$name');

INSERT INTO ref_geo.l_areas_simples(id_area, id_type, area_name, area_code, source, geom_4326, tolerance)
    SELECT l.id_area, l.id_type, l.area_name, l.area_code, 'OEASC', ST_TRANSFORM(ST_MULTI(ST_SIMPLIFY(l.geom, $tolerance)), 4326), $tolerance
        FROM ref_geo.l_areas as l
        WHERE l.id_type = ref_geo.get_id_type('${name}');

EOF
fi

}

function simplify_topology_geom() {

name=$1
tolerance=$2

if [ "$(test_simple $name)" == "" ]
then
cat << EOF | $psqla #>> $log_file

DELETE FROM ref_geo.l_areas_simples WHERE id_type=ref_geo.get_id_type('$name');

SELECt ref_geo.simplify_by_type_code('$name', $tolerance);

EOF
fi


}

function process_communes() {

name=OEASC_COMMUNE

if [ "$(get_id_type $name)" == "" ]
then
echo process $name

modifs=1

cat << EOF | $psqla >> $log_file

INSERT INTO ref_geo.bib_areas_types (type_name, type_code, type_desc, ref_name, ref_version, num_version)
    VALUES('Communes de l''OEASC','OEASC_COMMUNE', 'Communes de l''OEASC', 'OEASC', 2018, '');

DELETE FROM ref_geo.l_areas_simples WHERE id_type=ref_geo.get_id_type('$name');

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, geom_4326, centroid, source, comment, enable)
    SELECT id_type, CONCAT(SUBSTRING(area_code, 1, 2), '-', area_name), area_code, b.geom, ST_TRANSFORM(b.geom, 4326), centroid, 'OEASC', '', true FROM (
        SELECT ref_geo.get_id_type('$name') as id_type, a.area_name, a.area_code, a.geom, a.centroid, 'OEASC', '', true
            FROM (
                SELECT t.area_name, t.area_code, t.geom, t.centroid
                    FROM ref_geo.l_areas as t
                    WHERE id_type=ref_geo.get_id_type('COM') AND enable
                    )a, ref_geo.temp_oeasc_perimetre as p
            WHERE ST_INTERSECTS(a.geom, p.geom))b, ref_geo.temp_oeasc_perimetre as p
        WHERE ST_AREA(ST_INTERSECTION(b.geom, p.geom))*(1.0/ST_AREA(b.geom) + 1.0/ST_AREA(p.geom))/2 > 0.05;

DELETE FROM ref_geo.li_areas WHERE id_type=ref_geo.get_id_type('$name');

INSERT INTO ref_geo.li_areas(id_area, id_type, area_name, area_code, source, label, dept, surface_renseignee, surface_calculee)
    SELECT l.id_area, l.id_type, l.area_name, l.area_code, 'OEASC', CONCAT(SUBSTRING(l.area_code,1,2),'-',l.area_name), SUBSTRING(l.area_code,1,2), ROUND(ST_AREA(l.geom)/10000), ROUND(ST_AREA(l.geom)/10000)
        FROM ref_geo.l_areas as l
        WHERE l.id_type = ref_geo.get_id_type('${name}');


EOF

else

    echo id_type $id_type existe deja pour $name

fi

}


reinit_index() {
echo réinitialisation de l index
[ "$modifs" == "0" ] && echo modifs $modifs : pas de modifications a prendre en compte pour l index
[ "$modifs" == "1" ] && cat << EOF | $psqla # >> $log_file

-- l_areas
DROP INDEX ref_geo.idx_l_areas_type;

CREATE INDEX idx_l_areas_type
    ON ref_geo.l_areas
    USING btree
    (id_type);


DROP INDEX ref_geo.idx_l_areas_area_code;

CREATE INDEX idx_l_areas_area_code
    ON ref_geo.l_areas
    USING btree
    (area_code);


-- li_areas
DROP INDEX ref_geo.idx_li_areas_type;

CREATE INDEX idx_li_areas_type
    ON ref_geo.li_areas
    USING btree
    (id_type);


DROP INDEX ref_geo.idx_li_areas_area_code;

CREATE INDEX idx_li_areas_area_code
    ON ref_geo.li_areas
    USING btree
    (area_code);

-- l_areas_simples
DROP INDEX ref_geo.idx_l_areas_simples_type;

CREATE INDEX idx_l_areas_simples_type
    ON ref_geo.l_areas_simples
    USING btree
    (id_type);


DROP INDEX ref_geo.idx_l_areas_simples_area_code;

CREATE INDEX idx_l_areas_simples_area_code
    ON ref_geo.l_areas_simples
    USING btree
    (area_code);


EOF

}

function clear_cor_old_communes() {

echo "DROP TABLE IF EXISTS ref_geo.cor_old_communes;" | $psqla #>> $log_file

}

function clear_cor_dgd_cadastre() {

echo "DROP TABLE IF EXISTS ref_geo.cor_dgd_cadastre;" | $psqla #>> $log_file

}

function table_exists() {
schema=$1
table=$2
test=$(echo "SELECT table_exists('$schema', '$table')" | $psqla -t)
test=$(echo $test)
echo $test
}

function process_cor_old_communes() {

if [ "$(table_exists ref_geo cor_old_communes)" == "f" ]
then
echo process_cor_old_communes
cat << EOF | $psqla >> $log_file

DROP TABLE IF EXISTS temp;

CREATE TABLE temp(area_code character varying(256), area_name character varying(256), geom GEOMETRY);

INSERT INTO temp(area_code, geom)
    SELECT SUBSTR(area_code, 1,5) as code, ST_UNION(geom) as geom
        FROM ref_geo.l_areas
        WHERE id_type = ref_geo.get_id_type('OEASC_SECTION')
        GROUP BY code
        ORDER BY code;

DROP TABLE IF EXISTS ref_geo.cor_old_communes;

CREATE TABLE IF NOT EXISTS ref_geo.cor_old_communes(
    area_code character varying,
    old_area_codes character varying[],

    CONSTRAINT pk_cor_old_communes PRIMARY KEY (area_code)

);

INSERT INTO ref_geo.cor_old_communes
SELECT l.area_code, array_sort_unique(array_agg(t.area_code))
    FROM temp AS t, ref_geo.l_areas AS l
    WHERE l.id_type = ref_geo.get_id_type('OEASC_COMMUNE')
    AND ST_INTERSECTS(t.geom, l.geom)
    AND ST_AREA(ST_INTERSECTION(t.geom, l.geom)) * ( 1.0 / ST_AREA(t.geom) + 1.0 / ST_AREA(l.geom) ) > 0.5
    GROUP BY l.area_code
    ORDER BY l.area_code;

EOF
fi
}


function process_cor_dgd_cadastre() {

if [ "$(table_exists ref_geo cor_dgd_cadastre)" == "f" ] 
then
echo process_cor_dgd_cadastre
cat << EOF | $psqla >> $log_file

DROP TABLE IF EXISTS ref_geo.cor_dgd_cadastre;

CREATE TABLE ref_geo.cor_dgd_cadastre
(
    area_code_dgd CHARACTER VARYING,
    area_code_cadastre CHARACTER VARYING
);

INSERT INTO ref_geo.cor_dgd_cadastre
    SELECT a.area_code, l.area_code
        FROM ref_geo.l_areas as l, (SELECT area_code, ref_geo.intersect_rel_area(id_area, 'OEASC_CADASTRE', 0.1) as id_area_cadastre
            FROM ref_geo.l_areas
            WHERE id_type=ref_geo.get_id_type('OEASC_DGD'))a
        WHERE l.id_area = a.id_area_cadastre;


EOF
fi
}
