# install_ref_geo.sh

function import_shp() {
    name=$1
    shp_file=$2
    file_coding=$3

    table=ref_geo.temp_${name}
    tmp_file=/tmp/oeasc_import_${name}.shp
    srid=2154

    echo "DROP TABLE IF EXISTS $table;" | $psqla >> $log_file

    #import shp
    shp2pgsql  -W ${file_coding} -s ${srid} -D -I ${dir_data}/donnees_gestion_foret/${shp_file} ${table} | grep -v "\[" | grep -v '^\s*$$' > $tmp_file

    #correction typo
    sed -i -e "s/Š/è/g" -e "s/‚/é/g" -e "s/“/ô/g" -e "s/č/ê/g" $tmp_file
    sed -i -e "s/cêze/cèse/g" -e "s/Cêze/Cèse/g" $tmp_file

    echo >> $log_file
    echo import table $table from file $shp_file >> $log_file
    cat $tmp_file | $psqla >> $log_file

    # correct_geometry $name

    correct_ccod $name

    select_inside_oeasc $name

    reinit_seq_l_areas

}


function clean() {

    name=$1
    tmp_file=/tmp/oeasc_import_${name}.shp

    echo "DROP TABLE IF EXISTS $table;" | $psqla >> log_file
    rm $tmp_file

}


function get_id_type() {

    name=$1
    id_type=$(echo "SELECT ref_geo.get_id_type('"$name"');" | $psqla -t)
    id_type=$(echo $id_type)
    echo ${id_type}
    if [ "$id_type" != "" ]
    then
        return 1
    else
        return 0
    fi

}

function correct_geometry() {

    name=$1
    table=ref_geo.temp_${name}

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

        ALTER TABLE ${table} RENAME COLUMN gid TO id;

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

    DELETE FROM ref_geo.l_areas WHERE id_type=ref_geo.get_id_type('$name');

    ALTER TABLE ref_geo.l_areas DISABLE TRIGGER ALL;
    DELETE FROM ref_geo.bib_areas_types WHERE id_type=ref_geo.get_id_type('$name');
    ALTER TABLE ref_geo.l_areas ENABLE TRIGGER ALL;

EOF
}

function select_inside_oeasc() {

    name=$1
    table=ref_geo.temp_${name}

    cat <<EOF | $psqla >> $log_file

        DELETE FROM ${table} t
            USING ref_geo.perimetre_OEASC as p
            WHERE NOT ST_INTERSECTS(t.geom, p.geom);
EOF

}

function reinit_seq_l_areas() {

    echo "SELECT setval('ref_geo.l_areas_id_area_seq', (SELECT max(id_area)  FROM ref_geo.l_areas), true)" | $psqla >> $log_file;
    echo "SELECT setval('ref_geo.bib_areas_types_id_type_seq', (SELECT max(id_type)  FROM ref_geo.bib_areas_types), true)" | $psqla >> $log_file;

}

function populate_l_areas() {

    type_code=$1
    type_name=$2
    ref_name=$3
    keys_label=$4 # pour area_name
    keys=$5 # pour area_code

    cat <<EOF | $psqla #>> $log_file

    ALTER TABLE ref_geo.l_areas ADD COLUMN IF NOT EXISTS geom_4326 geometry(MultiPolygon,4326);

    INSERT INTO ref_geo.bib_areas_types (type_name, type_code, type_desc, ref_name, ref_version, num_version)
        VALUES('$type_name', '$type_code', '$ref_name', 'OEASC', 2018, '');

    SELECT ref_geo.get_id_type('${name}'), CONCAT(${keys_label}), CONCAT(${keys})
    FROM ${table};

    INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, geom_4326, source, comment, enable)
    SELECT ref_geo.get_id_type('${name}'), CONCAT(${keys_label}), CONCAT(${keys}), geom, ST_CENTROID(geom), ST_TRANSFORM(geom, 4326), 'OEASC', '', true
    FROM ${table};

EOF


    if [ "${name}" == "OEASC_ONF_PRF" ] || [ "${name}" == "OEASC_ONF_UG" ]
    then

        cat <<EOF | $psqla >> $log_file

    ALTER TABLE ref_geo.l_areas DISABLE TRIGGER ALL;

    UPDATE ref_geo.l_areas SET area_name = regexp_replace(area_name, '-_', '_', 'g') WHERE id_type = ref_geo.get_id_type('$name');
    UPDATE ref_geo.l_areas SET area_name = regexp_replace(area_name, '-$', '', 'g') WHERE id_type = ref_geo.get_id_type('$name');
    UPDATE ref_geo.l_areas SET area_name = regexp_replace(area_name, '_$', '', 'g') WHERE id_type = ref_geo.get_id_type('$name');

    ALTER TABLE ref_geo.l_areas ENABLE TRIGGER ALL;

EOF

    fi
}

# OEASC_ONF_FRT   forets_gestion_onf_pec              CP1250          "dept,'-',ccod_frt"                                     "dept,'-',llib_frt"
# OEASC_ONF_PRF   parcellaire_foret_publique_pec      CP1250          "dept,'-',ccod_frt,'-',ccod_prf"                        "ccod_prf"
# OEASC_ONF_UG    unites_gestion_foret_publique_pec   latin1          "dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix" "ccod_prf,'-',ccod_ug,'_',suffix"
# OEASC_DGD       documents_gestion_durable_pec       ISO-8859-1      "forid,'-',proref"                                      "forinsee,'-',fornom"
# OEASC_CADASTRE  cadastre_pec                        windows-1250    "insee_com,'-',section,'-',num_parc"                    "insee_com,'-',section,'-',num_parc"

# ONF FRT

clear_geometry OEASC_ONF_FRT

echo process geometries

name=OEASC_ONF_FRT

echo process $name

if [ "$(get_id_type $name)" == "" ]
then

    echo id_type n''existe pas pour $name

    import_shp $name forets_gestion_onf_pec CP1250
    populate_l_areas $name 'ONF Forêts' 'Forêts ONF' "llib_frt" "dept,'-',ccod_frt"
    clean $name


else
    echo id_type $id_type existe deja pour $name
fi


