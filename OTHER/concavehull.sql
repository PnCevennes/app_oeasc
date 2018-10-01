ALTER TABLE ref_geo.l_areas DISABLE TRIGGER ALL;
DELETE FROM ref_geo.l_areas
WHERE id_type=ref_geo.get_id_type('OEASC_SECTION');
ALTER TABLE ref_geo.l_areas ENABLE TRIGGER ALL;

DROP TABLE IF EXISTS temp;

CREATE TABLE temp(area_code character varying(256), area_name character varying(256), geom GEOMETRY);

INSERT INTO temp(area_code, area_name, geom)
SELECT CONCAT(insee_com, '-',section), CONCAT(nom_com, '-',section), ST_MULTI(ST_CONCAVEHULL(ST_UNION(geom), 0.7))
  FROM ref_geo.l_oeasc_cadastre
  GROUP BY insee_com, nom_com, section
  ORDER BY insee_com, nom_com, section;

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, geom_4326, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_SECTION'), t.area_name, t.area_code, t.geom, ST_TRANSFORM(t.geom, 4326), ST_CENTROID(t.geom), 'OEASC', '', true
    FROM temp as t;




ALTER TABLE ref_geo.l_areas DISABLE TRIGGER ALL;
DELETE FROM ref_geo.l_areas
WHERE id_type=309;
ALTER TABLE ref_geo.l_areas ENABLE TRIGGER ALL;

DELETE FROM ref_geo.bib_areas_types CASCADE
    WHERE id_type =309;

INSERT INTO ref_geo.bib_areas_types (
    id_type, type_name, type_code, type_desc, ref_name, ref_version, num_version)

    VALUES
        (309, 'Section cadastrale simplifiée', 'OEASC_SECTION_SAVE', 'Section cadastrale simplifiée', 'OEASC', 2018, '');

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, geom_4326, centroid, source, comment, enable)
SELECT ref_geo.get_id_type('OEASC_SECTION_SAVE'), area_name, area_code, geom,
 geom_4326, centroid, source, comment, enable
FROM ref_geo.l_areas
WHERE id_type=ref_geo.get_id_type('OEASC_SECTION');


ALTER TABLE ref_geo.l_areas DISABLE TRIGGER ALL;
DELETE FROM ref_geo.l_areas
WHERE id_type=ref_geo.get_id_type('OEASC_SECTION');
ALTER TABLE ref_geo.l_areas ENABLE TRIGGER ALL;

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, geom_4326, centroid, source, comment, enable)
SELECT ref_geo.get_id_type('OEASC_SECTION'), l.area_name, l.area_code, l.geom , ST_TRANSFORM(a.geom, 4326), ST_CENTROID(a.geom), 'OEASC', '', true 
FROM ref_geo.l_areas as l, 
(SELECT area_code, 
ST_MULTI(ST_CONCAVEHULL(ST_UNION(f.geom), 0.5)) as geom
 --ST_MULTI(ST_COLLECT(ST_POLYGON(ST_ExteriorRing(f.geom)))) as geom
		FROM (SELECT area_code, (ST_DUMP(geom)).geom as geom
			FROM ref_geo.l_areas
		WHERE id_type=ref_geo.get_id_type('OEASC_SECTION_SAVE')
		)f
		GROUP BY area_code)a
WHERE id_type=ref_geo.get_id_type('OEASC_SECTION_SAVE') and a.area_code=l.area_code;


--ALTER TABLE ref_geo.l_areas DISABLE TRIGGER ALL;
--DELETE FROM ref_geo.l_areas
--WHERE id_type=ref_geo.get_id_type('OEASC_SECTION');
--ALTER TABLE ref_geo.l_areas ENABLE TRIGGER ALL;


--UPDATE ref_geo.l_areas SET (geom)=
--(SELECT geom FROM
--	(SELECT area_code, id_type, ST_MULTI(ST_COLLECT(ST_SIMPLIFY(f.geom, 1))) as geom
--		FROM (SELECT area_code, (ST_DUMP(geom)).geom as geom
--			FROM ref_geo.l_areas
--			WHERE id_type=ref_geo.get_id_type('OEASC_SECTION_SIMPLE')
--		)f
--		GROUP BY area_code, id_type)c
--	WHERE c.area_code = area_code
--	AND c.id_type=ref_geo.get_id_type('OEASC_SECTION_SIMPLE')
--	AND id_type=ref_geo.get_id_type('OEASC_SECTION'))
	


--INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, geom_4326, centroid, source, comment, enable)
--SELECT ref_geo.get_id_type('OEASC_SECTION'), area_name, area_code, geom,
-- ST_MULTI(ST_PERIMETER(geom_4326)), centroid, source, comment, enable
--FROM ref_geo.l_areas
--WHERE id_type=ref_geo.get_id_type('OEASC_SECTION_SIMPLE')



