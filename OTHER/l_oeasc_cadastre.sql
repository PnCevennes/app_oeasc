DROP TABLE IF EXISTS temp;

CREATE TABLE temp(area_code character varying(256), area_name character varying(256), geom GEOMETRY);

INSERT INTO temp(area_code, area_name, geom)
SELECT CONCAT(insee_com, '-',section), CONCAT(nom_com, '-',section), ST_MULTI(ST_UNION(geom))
  FROM ref_geo.l_oeasc_cadastre
  GROUP BY insee_com, nom_com, section
  ORDER BY insee_com, nom_com, section;


SELECT * FROM temp;

DELETE FROM ref_geo.bib_areas_type WHERE id_type = 308

INSERT INTO ref_geo.bib_areas_types (
    id_type, type_name, type_code, type_desc, ref_name, ref_version, num_version)

    VALUES
        (308, 'Section cadastrale', 'OEASC_SECTION', 'Section cadastrale', 'OEASC', 2018, '');

DELETE FROM  ref_geo.l_areas WHERE id_type = ref_geo.get_id_type('OEASC_SECTION');

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, geom_4326, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_SECTION'), t.area_name, t.area_code, geom, ST_TRANSFORM(geom, 4326), ST_CENTROID(geom), 'OEASC', '', true
    FROM temp as t;