-- l_areas INSER geom pour l''oeasc

ALTER TABLE ref_geo.l_areas DISABLE TRIGGER ALL;

DELETE FROM ref_geo.l_areas
    WHERE id_type >= 300 and id_type <= 400;

ALTER TABLE ref_geo.l_areas ENABLE TRIGGER ALL;

DROP TABLE IF EXISTS temp;

CREATE TABLE temp
(
  id_type integer NOT NULL,
  area_name character varying(250),
  area_code character varying(25),
  geom geometry(MultiPolygon,2154),
  centroid geometry(Point,2154),
  source character varying(250),
  comment text,
  enable boolean NOT NULL DEFAULT true,
  geom_4326 geometry(MultiPolygon,4326)

);

COPY temp FROM '/tmp/l_areas_oeasc.csv';

SELECT setval('ref_geo.l_areas_id_area_seq', (SELECT max(id_area)  FROM ref_geo.l_areas), true);

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source,
       comment, enable, geom_4326)
       SELECT * FROM temp;


-- relations entre anciennes et nouvelles communes par area_code

DROP TABLE IF EXISTS ref_geo.cor_old_communes;

CREATE TABLE IF NOT EXISTS ref_geo.cor_old_communes(
    area_code character varying,
    old_area_codes character varying[],

    CONSTRAINT pk_cor_old_communes PRIMARY KEY (area_code)

);

COPY ref_geo.cor_old_communes FROM '/tmp/cor_old_communes_oeasc.csv';


-- relations dgd cadastre par area_code

DROP TABLE IF EXISTS ref_geo.cor_dgd_cadastre;

CREATE TABLE ref_geo.cor_dgd_cadastre
(
    area_code_dgd CHARACTER VARYING, 
    area_code_cadastre CHARACTER VARYING

);

COPY ref_geo.cor_dgd_cadastre FROM '/tmp/cor_dgd_cadastre_oeasc.csv';
