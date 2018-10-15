-- ref_geo process

UPDATE ref_geo.l_OEASC_ONF_FRT
    SET geom=a.geom FROM (
        SELECT CONCAT(dept,'-',ccod_frt) as ccod, ST_MULTI(ST_UNION(geom)) as geom
        FROM ref_geo.l_OEASC_ONF_FRT
        GROUP BY ccod
        HAVING COUNT(*) > 1
        )a

    WHERE a.ccod=CONCAT(dept,'-',ccod_frt);

DELETE FROM ref_geo.l_OEASC_ONF_FRT
    WHERE id IN (SELECT id
        FROM (SELECT id,
            ROW_NUMBER() OVER (partition BY CONCAT(dept,'-',ccod_frt) ORDER BY id) AS rnum
            FROM ref_geo.l_OEASC_ONF_FRT) t
                WHERE t.rnum > 1);


UPDATE ref_geo.l_OEASC_ONF_PRF
    SET geom=a.geom FROM (
        SELECT CONCAT(dept,'-',ccod_frt,'-',ccod_prf) as ccod, ST_MULTI(ST_UNION(geom)) as geom
        FROM ref_geo.l_OEASC_ONF_PRF
        GROUP BY ccod
        HAVING COUNT(*) > 1
        )a

    WHERE a.ccod=CONCAT(dept,'-',ccod_frt,'-',ccod_prf);

DELETE FROM ref_geo.l_OEASC_ONF_PRF
    WHERE id IN (SELECT id
        FROM (SELECT id,
            ROW_NUMBER() OVER (partition BY CONCAT(dept,'-',ccod_frt,'-',ccod_prf) ORDER BY id) AS rnum
            FROM ref_geo.l_OEASC_ONF_PRF) t
                WHERE t.rnum > 1);


ALTER TABLE ref_geo.l_OEASC_ONF_UG DROP COLUMN IF EXISTS suffix;
ALTER TABLE ref_geo.l_OEASC_ONF_UG ADD COLUMN suffix integer;

UPDATE ref_geo.l_OEASC_ONF_UG as c
    SET suffix=b.suffix_b
    FROM (
        SELECT id, CONCAT(dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix) as ccod,
            row_number() OVER (
                PARTITION BY CONCAT(dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix)
                    ORDER BY CONCAT(dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix), id) AS suffix_b
            FROM (
                SELECT COUNT(*) as c, CONCAT(dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix) as ccod
                    FROM ref_geo.l_OEASC_ONF_UG as b
                    GROUP BY ccod
                    HAVING COUNT(*) >1
                    ORDER BY ccod
            )a, ref_geo.l_OEASC_ONF_UG
        WHERE a.ccod = CONCAT(dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix)
        ORDER BY a.ccod
    )b
    WHERE b.ccod = CONCAT(dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix) and b.id = c.id;

-- l_areas

-- -- SELECT pg_terminate_backend(pid), * FROM active_locks;

-- ajouter id_type dans bib_areas_type

DROP TABLE IF EXISTS oeasc.cor_areas_declaration CASCADE;


DROP SCHEMA IF EXISTS oeasc CASCADE;


DROP TABLE IF EXISTS ref_geo.li_OEASC_ONF_FRT CASCADE;


DROP TABLE IF EXISTS ref_geo.li_OEASC_ONF_PRF CASCADE;


DROP TABLE IF EXISTS ref_geo.li_OEASC_ONF_UG CASCADE;


DROP TABLE IF EXISTS ref_geo.li_OEASC_DGD CASCADE;


DROP TABLE IF EXISTS ref_geo.li_OEASC_CADASTRE CASCADE;


DROP TABLE IF EXISTS ref_geo.li_oeasc_cadastre CASCADE;


-- bib_areas_type

ALTER TABLE ref_geo.l_areas DISABLE TRIGGER ALL;

DELETE FROM ref_geo.l_areas
    WHERE id_type >= 300 and id_type <= 400;

ALTER TABLE ref_geo.l_areas ENABLE TRIGGER ALL;

SELECT setval('ref_geo.l_areas_id_area_seq', (SELECT max(id_area)  FROM ref_geo.l_areas), true);

DELETE FROM ref_geo.bib_areas_types CASCADE
    WHERE id_type >= 300 and id_type <= 400;

-- UPDATE ref_geo.bib_areas_types
--    SET type_code='COM'
--    WHERE id_type=101;

-- UPDATE ref_geo.bib_areas_types
--    SET type_code='DEPARTEMENTS'
--    WHERE id_type=102;


INSERT INTO ref_geo.bib_areas_types (
    id_type, type_name, type_code, type_desc, ref_name, ref_version, num_version)

    VALUES(301, 'ONF Forêts', 'OEASC_ONF_FRT', 'Forêts ONF', 'ONF', 2018, ''),
        (302, 'ONF Parcelles', 'OEASC_ONF_PRF', 'Parcelles ONF', 'ONF', 2018, ''),
        (303, 'ONF UG', 'OEASC_ONF_UG', 'Unités de gestion ONF', 'ONF', 2018, ''),
        (304, 'DGD', 'OEASC_DGD', 'Document de gestion durable', 'ONF', 2018, ''),
        (305, 'CADASTRE', 'OEASC_CADASTRE', 'Cadastre pour l''oeasc', 'OEASC', 2018, ''),
        (306, 'COMMUNES OEASC', 'OEASC_COMMUNE', 'Communes de l''oeasc', 'OEASC', 2018, ''),
        (307, 'DEPARTEMENTS OEASC', 'OEASC_DEPARTEMENT', 'Départements de l''oeasc', 'OEASC', 2018, ''),
        (308, 'Section cadastrale simplifiées', 'OEASC_SECTION', 'Section cadastrale', 'OEASC', 2018, ''),
        (320, 'OEASC Périmètre', 'OEASC_PERIMETRE', 'Périmetre de l''OEASC', 'OEASC', 2018, ''),
        (321, 'ZC_PNC', 'ZC_PERIMETRE', 'Zone Coeur du PNC', 'OEASC', 2018, ''),
        (322, 'AA_PNC', 'AA_PERIMETRE', 'Aire d''adhésion du PNC', 'OEASC', 2018, ''),
        (338, 'Section cadastrale completes', 'OEASC_SECTION_RAW', 'Section cadastrale completes', 'OEASC', 2018, '');

SELECT setval('ref_geo.l_areas_id_area_seq', COALESCE((SELECT MAX(id_area)+1 FROM ref_geo.l_areas), 1), false);

-- communes oeasc

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT id_type, CONCAT(SUBSTRING(area_code, 1, 2), '-', area_name), area_code, b.geom, centroid, 'OEASC', '', true FROM (
        SELECT ref_geo.get_id_type('OEASC_COMMUNE') as id_type, a.area_name, a.area_code, a.geom, a.centroid, 'OEASC', '', true
            FROM (
                SELECT t.area_name, t.area_code, t.geom, t.centroid
                    FROM ref_geo.l_areas as t
                    WHERE id_type=ref_geo.get_id_type('COM') AND enable
                    )a, ref_geo.perimetre_OEASC as p
            WHERE ST_INTERSECTS(a.geom, p.geom))b, ref_geo.perimetre_OEASC as p
        WHERE ST_AREA(ST_INTERSECTION(b.geom, p.geom))*(1.0/ST_AREA(b.geom) + 1.0/ST_AREA(p.geom))/2 > 0.05;


-- departements oeasc

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_DEPARTEMENT'), a.area_name, a.area_code, a.geom, a.centroid, 'OEASC', '', true
        FROM (
            SELECT t.area_name, t.area_code, t.geom, t.centroid
                FROM ref_geo.l_areas as t
                    WHERE id_type=ref_geo.get_id_type('DEP') AND enable
                    )a, ref_geo.perimetre_OEASC as p
       WHERE ST_INTERSECTS(a.geom, p.geom);

-- AA et ZC

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('ZC_PERIMETRE'), 'Zone coeur du parc des cévennes', 'ZC_PNC', geom, ST_CENTROID(geom), 'OEASC', '', true
    FROM ref_geo.zc_pnc;

 INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('AA_PERIMETRE'), 'Aire adhésion parc des cévenness', 'AA_PNC', geom, ST_CENTROID(geom), 'OEASC', '', true
    FROM ref_geo.aa_pnc;

-- perimetre oeasc

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_PERIMETRE'), 'Perimetre OEASC', 'OEASC_PERIMETRE', geom, ST_CENTROID(geom), 'OEASC', '', true
    FROM ref_geo.perimetre_oeasc;


-- placer dans l_areas et faire les tables d attributs

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_ONF_FRT'), CONCAT(dept,'-',llib_frt), CONCAT(dept,'-',ccod_frt), geom, ST_CENTROID(geom), 'OEASC', '', true
    FROM ref_geo.l_OEASC_ONF_FRT;


INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_ONF_PRF'), CONCAT(ccod_prf), CONCAT(dept,'-',ccod_frt,'-',ccod_prf), geom, ST_CENTROID(geom), 'OEASC', '', true
    FROM ref_geo.l_OEASC_ONF_PRF;


INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_ONF_UG'), CONCAT(ccod_prf,'-',ccod_ug,'_',suffix), CONCAT(dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix), geom, ST_CENTROID(geom), 'OEASC', '', true
    FROM ref_geo.l_OEASC_ONF_UG;


INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_DGD'), CONCAT(forinsee,'-',fornom), CONCAT(forid,'-',proref), geom, ST_CENTROID(geom), 'OEASC', '', true
    FROM ref_geo.l_OEASC_DGD;


INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_CADASTRE'), CONCAT(insee_com,'-',section,'-',num_parc), CONCAT(insee_com,'-',section,'-',num_parc), geom, ST_CENTROID(geom), 'OEASC', '', true
    FROM ref_geo.l_OEASC_CADASTRE;


-- correct nom ONF UG et ONF PRF

ALTER TABLE ref_geo.l_areas DISABLE TRIGGER ALL;

UPDATE ref_geo.l_areas SET area_name = regexp_replace(area_name, '-_', '_', 'g') WHERE id_type = ref_geo.get_id_type('OEASC_ONF_PRF') OR id_type = ref_geo.get_id_type('OEASC_ONF_UG');
UPDATE ref_geo.l_areas SET area_name = regexp_replace(area_name, '-$', '', 'g') WHERE id_type = ref_geo.get_id_type('OEASC_ONF_PRF') OR id_type = ref_geo.get_id_type('OEASC_ONF_UG');
UPDATE ref_geo.l_areas SET area_name = regexp_replace(area_name, '_$', '', 'g') WHERE id_type = ref_geo.get_id_type('OEASC_ONF_PRF') OR id_type = ref_geo.get_id_type('OEASC_ONF_UG');

ALTER TABLE ref_geo.l_areas ENABLE TRIGGER ALL;

-- add column geom_4326

ALTER TABLE ref_geo.l_areas ADD COLUMN geom_4326 geometry(MultiPolygon,4326);


-- add column geom_4326

ALTER TABLE ref_geo.l_areas ADD COLUMN geom_4326 geometry(MultiPolygon,4326);


UPDATE ref_geo.l_areas SET geom_4326 = st_transform(geom, 4326);


-- SECTIONS CADASTRALES RAW

 DROP TABLE IF EXISTS temp;

CREATE TABLE temp(area_code character varying(256), area_name character varying(256), geom GEOMETRY);

INSERT INTO temp(area_code, area_name, geom)
    SELECT CONCAT(insee_com, '-',section), CONCAT(nom_com, '-',section), ST_MULTI(ST_UNION(geom))
        FROM ref_geo.l_oeasc_cadastre
        GROUP BY insee_com, nom_com, section
        ORDER BY insee_com, nom_com, section;

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, geom_4326, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_SECTION_RAW'), t.area_name, t.area_code, t.geom, ST_TRANSFORM(t.geom, 4326), ST_CENTROID(t.geom), 'OEASC', '', true
    FROM temp as t;

-- SECTIONS CADASTRALES SIMPLE

DROP TABLE IF EXISTS temp;

CREATE TABLE temp(area_code character varying(256), area_name character varying(256), geom GEOMETRY);

INSERT INTO temp(area_code, area_name, geom)
SELECT CONCAT(insee_com, '-',section), CONCAT(nom_com, '-',section), ST_UNION(ST_BUFFER(geom,20))
  FROM ref_geo.l_oeasc_cadastre
  GROUP BY insee_com, nom_com, section
  ORDER BY insee_com, nom_com, section;


DROP TABLE IF EXISTS temp2;

CREATE TABLE temp2(area_code character varying(256), area_name character varying(256), geom GEOMETRY);

SELECT 'aa';

INSERT INTO temp2(area_code, area_name, geom)
    SELECT area_code, area_name, ST_MULTI(ST_SIMPLIFY(geom, 50, true))
    FROM temp;

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, geom_4326, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_SECTION'), t.area_name, t.area_code, t.geom, ST_TRANSFORM(t.geom, 4326), ST_CENTROID(t.geom), 'OEASC', '', true
    FROM temp2 as t;


-- bidouille pour ne pas avoir deux fois le nom 48-bougès pff

UPDATE ref_geo.l_areas
    SET area_name='48-bougès_sj'
    WHERE area_code LIKE '%BOUGESSJ';


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


-- cor vielles communes

DROP TABLE IF EXISTS temp;

CREATE TABLE temp(area_code character varying(256), area_name character varying(256), geom GEOMETRY);

INSERT INTO temp(area_code, geom)
    SELECT SUBSTR(area_code, 1,5) as code, ST_UNION(geom) as geom
        FROM ref_geo.l_areas
        WHERE id_type = ref_geo.get_id_type('OEASC_SECTION_RAW')
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


CREATE OR REPLACE FUNCTION ref_geo.get_old_communes(
    IN myarea_code character varying)

  RETURNS TABLE(old_area_code character varying) AS
$BODY$
        BEGIN
            RETURN QUERY

        SELECT UNNEST(old_area_codes)
        FROM ref_geo.cor_old_communes
        WHERE area_code = myarea_code;
          END;
    $BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100
  ROWS 1000;


DROP TABLE IF EXISTS ref_geo.cor_dgd_cadastre;

CREATE TABLE ref_geo.cor_dgd_cadastre
(
    area_code_dgd CHARACTER VARYING,
    area_code_cadastre CHARACTER VARYING
);

INSERT INTO ref_geo.cor_dgd_cadastre
SELECT a.area_code, l.area_code
    FROM ref_geo.l_areas as l, (SELECT area_code, ref_geo.intersect_rel_area(id_area, 'OEASC_CADASTRE', 0.05) as id_area_cadastre
        FROM ref_geo.l_areas
        WHERE id_type=ref_geo.get_id_type('OEASC_DGD'))a
    WHERE l.id_area = a.id_area_cadastre;


-- sauvegarde des données pour ne pas tout recalculer par la suite

COPY
(SELECT id_type, area_name, area_code, geom, centroid, source,
       comment, enable, geom_4326
    FROM ref_geo.l_areas
    WHERE id_type >= 300 AND id_type < 400)
    TO '/tmp/l_areas_oeasc.csv';

COPY ref_geo.cor_old_communes TO '/tmp/cor_old_communes_oeasc.csv';
COPY ref_geo.cor_dgd_cadastre TO '/tmp/cor_dgd_cadastre_oeasc.csv';

