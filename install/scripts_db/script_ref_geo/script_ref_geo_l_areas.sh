if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file


echo '-- l_areas'


cat << EOF

-- -- SELECT pg_terminate_backend(pid), * FROM active_locks;

EOF


echo '-- ajouter id_type dans bib_areas_type'


cat << EOF

DROP TABLE IF EXISTS oeasc.cor_areas_declaration CASCADE;

EOF

cat << EOF

DROP SCHEMA IF EXISTS oeasc CASCADE;

EOF



for name in $list_name
do
    table=table_${name}
    keys=keys_${name}

    table=${!table}
    keys=${!keys}

cat << EOF

DROP TABLE IF EXISTS ref_geo.li_${name} CASCADE;

EOF

done


cat << EOF

DROP TABLE IF EXISTS ref_geo.li_oeasc_cadastre CASCADE;

EOF



cat << EOF

-- bib_areas_type

DELETE FROM ref_geo.l_areas
    WHERE id_type >= 300 and id_type <= 400;

SELECT setval('ref_geo.l_areas_id_area_seq', (SELECT max(id_area)  FROM ref_geo.l_areas), true);

DELETE FROM ref_geo.bib_areas_types CASCADE
    WHERE id_type >= 300 and id_type <= 400;

UPDATE ref_geo.bib_areas_types
    SET type_code='COMMUNES'
    WHERE id_type=101;

UPDATE ref_geo.bib_areas_types
    SET type_code='DEPARTEMENTS'
    WHERE id_type=102;


INSERT INTO ref_geo.bib_areas_types (
    id_type, type_name, type_code, type_desc, ref_name, ref_version, num_version)

    VALUES(301, 'ONF Forêts', 'OEASC_ONF_FRT', 'Forêts ONF', 'ONF', 2018, ''),
        (302, 'ONF Parcelles', 'OEASC_ONF_PRF', 'Parcelles ONF', 'ONF', 2018, ''),
        (303, 'ONF UG', 'OEASC_ONF_UG', 'Unités de gestion ONF', 'ONF', 2018, ''),
        (304, 'DGD', 'OEASC_DGD', 'Document de gestion durable', 'ONF', 2018, ''),
        (305, 'CADASTRE', 'OEASC_CADASTRE', 'Cadastre pour l''oeasc', 'OEASC', 2018, ''),
        (306, 'COMMUNES OEASC', 'OEASC_COMMUNE', 'Communes de l''oeasc', 'OEASC', 2018, ''),
        (307, 'DEPARTEMENTS OEASC', 'OEASC_DEPARTEMENT', 'Départements de l''oeasc', 'OEASC', 2018, ''),
        (320, 'OEASC Périmètre', 'OEASC_PERIMETRE', 'Périmetre de l''OEASC', 'OEASC', 2018, '');


EOF

echo "SELECT setval('ref_geo.l_areas_id_area_seq', COALESCE((SELECT MAX(id_area)+1 FROM ref_geo.l_areas), 1), false);"

cat << EOF

-- communes oeasc

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT id_type, CONCAT(SUBSTRING(area_code, 1, 2), '-', area_name), area_code, b.geom, centroid, 'OEASC', '', true FROM (
        SELECT ref_geo.get_id_type('OEASC_COMMUNE') as id_type, a.area_name, a.area_code, a.geom, a.centroid, 'OEASC', '', true
            FROM (
                SELECT t.area_name, t.area_code, t.geom, t.centroid
                    FROM ref_geo.l_areas as t
                    WHERE id_type=ref_geo.get_id_type('COMMUNES') AND enable
                    )a, ref_geo.perimetre_OEASC as p
            WHERE ST_INTERSECTS(a.geom, p.geom))b, ref_geo.perimetre_OEASC as p
        WHERE ST_AREA(ST_INTERSECTION(b.geom, p.geom))*(1.0/ST_AREA(b.geom) + 1.0/ST_AREA(p.geom))/2 > 0.05;

-- INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
--   SELECT ref_geo.get_id_type('OEASC_COMMUNE'), a.area_name, a.area_code, a.geom, a.centroid, 'OEASC', '', true
--        FROM (
--           SELECT t.area_name, t.area_code, t.geom, t.centroid
--                FROM ref_geo.l_areas as t
--                    WHERE id_type=ref_geo.get_id_type('COMMUNES') AND enable
--                    )a, ref_geo.perimetre_OEASC as p
--       WHERE ST_INTERSECTS(a.geom, p.geom);
EOF


cat << EOF

-- departements oeasc

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_DEPARTEMENT'), a.area_name, a.area_code, a.geom, a.centroid, 'OEASC', '', true
        FROM (
            SELECT t.area_name, t.area_code, t.geom, t.centroid
                FROM ref_geo.l_areas as t
                    WHERE id_type=ref_geo.get_id_type('DEPARTEMENTS') AND enable
                    )a, ref_geo.perimetre_OEASC as p
       WHERE ST_INTERSECTS(a.geom, p.geom);
EOF


cat << EOF


-- insert OEASC Périmetre

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_PERIMETRE'), 'Périmètre OEASC', 'OEASC_PERIMETRE', geom, ST_CENTROID(geom), 'OEASC', '', true
    FROM ref_geo.perimetre_oeasc;

EOF

echo '-- placer dans l_areas et faire les tables d attributs'

for name in $list_name
do
    table=table_${name}
    keys=keys_${name}
    keys_label=keys_label_${name}
    table=${!table}
    keys=${!keys}
    keys_label=${!keys_label}


cat << EOF

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('${name}'), CONCAT(${keys_label}), CONCAT(${keys}), geom, ST_CENTROID(geom), 'OEASC', '', true
    FROM ref_geo.${table};

EOF

done



cat << EOF

-- add column geom_4326

ALTER TABLE ref_geo.l_areas ADD COLUMN geom_4326 geometry(MultiPolygon,4326);

EOF


cat << EOF

UPDATE ref_geo.l_areas SET geom_4326 = st_transform(geom, 4326);

EOF


cat << EOF

-- bidouille pour ne pas avoir deux fois le nom 48-bougès pff

UPDATE ref_geo.l_areas
    SET area_name='48-bougès_sj'
    WHERE area_code LIKE '%BOUGESSJ';

EOF

cat << EOF

-- index

DROP INDEX ref_geo.idx_l_areas_type_code_area;

CREATE INDEX idx_l_areas_type_code_area
    ON ref_geo.l_areas
    USING btree
    (id_type, area_code);


DROP INDEX ref_geo.idx_l_areas_type;

CREATE INDEX idx_l_areas_type
    ON ref_geo.l_areas
    USING btree
    (id_type);


DROP INDEX ref_geo.idx_l_areas_code_area;

CREATE INDEX idx_l_areas_code_area
    ON ref_geo.l_areas
    USING btree
    (area_code);

EOF
