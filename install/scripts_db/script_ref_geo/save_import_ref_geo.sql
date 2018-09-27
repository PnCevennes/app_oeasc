COPY (SELECT id_type, area_name, area_code, geom, centroid, source, enable, geom_4326 FROM ref_geo.l_areas WHERE id_type >=300 and id_type <=400) to '/tmp/l_areas_oeasc.tsv';

DROP TABLE IF EXISTS temp;

CREATE TABLE temp
(
  id_type integer NOT NULL,
  area_name character varying(250),
  area_code character varying(25),
  geom geometry(MultiPolygon,2154),
  centroid geometry(Point,2154),
  source character varying(250),
  enable boolean NOT NULL DEFAULT true,
  geom_4326 geometry(MultiPolygon,4326)
);

COPY temp FROM '/tmp/l_areas_oeasc.tsv'; 

DELETE FROM ref_geo.l_areas
WHERE id_type >=300 and id_type <=400;


INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom , centroid, source, enable, geom_4326)
SELECT id_type, area_name, area_code, geom , centroid, source, enable, geom_4326
FROM temp