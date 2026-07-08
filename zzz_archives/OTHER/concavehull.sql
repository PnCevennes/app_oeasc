--DROP TABLE IF EXISTS temp;
--CREATE TABLE temp(area_code character varying(256), area_name character varying(256), geom GEOMETRY);

--INSERT INTO temp(area_code, area_name, geom)
--SELECT CONCAT(insee_com, '-',section), CONCAT(nom_com, '-',section), ST_MULTI(ST_UNION(geom))
--  FROM ref_geo.l_oeasc_cadastre
--  GROUP BY insee_com, nom_com, section
-- ORDER BY insee_com, nom_com, section;


DROP TABLE IF EXISTS temp2;
CREATE TABLE temp2(area_code character varying(256), area_name character varying(256), geom GEOMETRY);

INSERT INTO temp2 
SELECT area_code, area_name, ST_MULTI(ST_CONCAVEHULL(geom, 0.7, true))
FROM temp;

--INSERT INTO temp2
--SELECT area_code, area_name,
--ST_MULTI(ST_CONVEXHULL(ST_UNION((ST_CONVEXHULL(f.geom))))) as geom
--		FROM (SELECT area_code, area_name, (ST_DUMP(geom)).geom as geom
--			FROM temp
--		WHERE area_code LIKE '48155-%'
--		)f
--		GROUP BY area_code, area_name;

		
UPDATE temp2 SET (geom) = 
	(SELECT ST_INTERSECTION(t.geom, c.geom) 
		FROM temp2 as t, ref_geo.l_areas as c 
		WHERE temp2.area_code=t.area_code 
		AND 
		c.id_type = ref_geo.get_id_type('OEASC_COMMUNE')
		AND SUBSTR(t.area_code, 1, 5) IN ( SELECT ref_geo.get_old_communes(c.area_code))
		);

DROP TABLE IF EXISTS temp3;
CREATE TABLE temp3(area_code character varying(256), area_name character varying(256), geom GEOMETRY);

INSERT INTO temp3
SELECT t2.area_code, t2.area_name, ST_MULTI(ST_DIFFERENCE(t2.geom, a.geom))
FROM temp2 as t2, 
(SELECT t2.area_code, ST_UNION((ST_INTERSECTION(t.geom, t2.geom))) as geom
FROM temp2 as t2, temp as t
WHERE t2.area_code != t.area_code
AND SUBSTR(t.area_code, 1, 5) LIKE SUBSTR(t2.area_code, 1, 5)
AND ST_INTERSECTS(t.geom, t2.geom)
GROUP BY t2.area_code
ORDER BY t2.area_code)a
WHERE t2.area_code = a.area_code;

--DROP TABLE IF EXISTS temp3;
--CREATE TABLE temp3(area_code character varying(256), area_name character varying(256), geom GEOMETRY);

--INSERT INTO temp3
--SELECT area_code, area_name, ST_MULTI(geom) FROM temp2;

ALTER TABLE ref_geo.l_areas DISABLE TRIGGER ALL;
DELETE FROM ref_geo.l_areas
WHERE id_type=ref_geo.get_id_type('OEASC_SECTION');
ALTER TABLE ref_geo.l_areas ENABLE TRIGGER ALL;

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, geom_4326, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_SECTION'), t.area_name, t.area_code, t.geom, ST_TRANSFORM(t.geom, 4326), ST_CENTROID(t.geom), 'OEASC', '', true
    FROM temp3 as t;
