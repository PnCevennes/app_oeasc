CREATE OR REPLACE FUNCTION array_sort_unique (ANYARRAY) RETURNS ANYARRAY
LANGUAGE SQL
AS $body$
  SELECT ARRAY(
    SELECT DISTINCT $1[s.i]
    FROM generate_series(array_lower($1,1), array_upper($1,1)) AS s(i)
    ORDER BY 1
  );
$body$;


DROP TABLE IF EXISTS ref_geo.cor_old_communes;

CREATE TABLE IF NOT EXISTS ref_geo.cor_old_communes(
area_code character varying, 
area_code2 character varying
);

INSERT INTO ref_geo.cor_old_communes
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

CREATE OR REPLACE FUNCTION ref_geo.get_old_communes(
    IN myarea_code character varying)

  RETURNS TABLE(area_code character varying) AS
$BODY$
        BEGIN
            RETURN QUERY

                SELECT t.area_code2
			FROM ref_geo.cor_old_communes as t
			WHERE t.area_code=myarea_code
			ORDER BY t.area_code2;

          END;
    $BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100
  ROWS 1000;

SELECT ref_geo.get_old_communes('48116');
SELECT * FROM temp ORDER BY area_code;