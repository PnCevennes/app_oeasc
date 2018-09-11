CREATE OR REPLACE FUNCTION array_sort_unique (ANYARRAY) RETURNS ANYARRAY
LANGUAGE SQL
AS $body$
  SELECT ARRAY(
    SELECT DISTINCT $1[s.i]
    FROM generate_series(array_lower($1,1), array_upper($1,1)) AS s(i)
    ORDER BY 1
  );
$body$;


DROP TABLE IF EXISTS temp;

CREATE TABLE IF NOT EXISTS temp(
area_code character varying, 
area_code2 character varying
);

INSERT INTO temp
SELECT l.area_code, a.area_code
--SELECT l.area_code, array_sort_unique(array_agg(a.area_code)) 
--, array_sort_unique(array_agg(a.area_name)), array_sort_unique(array_agg(a.area_code))
FROM ref_geo.l_areas as l, (SELECT id_area, area_name, area_code, geom
FROM ref_geo.l_areas
WHERE id_type = ref_geo.get_id_type('COMMUNES'))a
WHERE ST_AREA(ST_INTERSECTION(a.geom, l.geom)) * ( 1.0 / (ST_AREA(a.geom)) + 1.0 / (ST_AREA(l.geom)) ) > 0.05
AND l.id_type = ref_geo.get_id_type('OEASC_COMMUNE')
GROUP BY l.area_code, a.area_code
ORDER BY l.area_code;

SELECT *
FROM temp;

SELECT area_name
FROM ref_geo.l_areas
WHERE id_type = ref_geo.get_id_type('OEASC_CADASTRE')
LIMIT 10;

SELECT t.area_code, l.area_code, l.area_name
FROM ref_geo.l_areas as l, temp as t
WHERE l.area_name LIKE CONCAT(t.area_code2, '%')
AND t.area_code='48166'
AND l.id_type = ref_geo.get_id_type('OEASC_CADASTRE')
ORDER BY t.area_code2

