-- Function: ref_geo.get_id_type(character varying)

DROP FUNCTION IF EXISTS ref_geo.get_id_type(character varying) CASCADE;

CREATE OR REPLACE FUNCTION ref_geo.get_id_type(mytypecode CHARACTER VARYING)
    RETURNS INTEGER AS
    $BODY$
    --
    -- Returns the id_type from the type code of bib_areas_type
    --
        DECLARE thetypecode INTEGER;
        BEGIN
            SELECT INTO thetypecode id_type FROM ref_geo.bib_areas_types WHERE type_code = mytypecode;
            return thetypecode;
        END;
    $BODY$

    LANGUAGE plpgsql IMMUTABLE
    COST 100;


-- Function: ref_geo.intersect(INTEGER, CHARACTER VARYING)

DROP FUNCTION IF EXISTS ref_geo.intersect(INTEGER, CHARACTER VARYING) CASCADE;

CREATE OR REPLACE FUNCTION ref_geo.intersect(
    myidarea INTEGER,
    mytypecode CHARACTER VARYING)
    RETURNS TABLE (id_area INT, area_code VARCHAR) AS
    --
    -- Returns the id_area(s) of the areas of type code intersecting with area id_area
    --
    $$
        BEGIN
            RETURN QUERY
                WITH test AS (SELECT l.geom as geom
                    FROM ref_geo.l_areas as l
                    WHERE L.id_area=myidarea)
                SELECT l.id_area, l.area_name
                    FROM ref_geo.l_areas as l, test
                    WHERE l.id_type = ref_geo.get_id_type(mytypecode) AND ST_INTERSECTS(l.geom, test.geom);
        END;
    $$

    LANGUAGE plpgsql IMMUTABLE
    COST 100;


-- retourne les id de ref_geo.l_areas de type mytypecode 
-- qui intersectent avec la geometry mygeom 
-- avec une tolerance sur l'aire d'intersection relative (valeur conseillée 0.05)
DROP FUNCTION IF EXISTS ref_geo.intersect_geom_type_tol(geometry, character varying, double precision);

CREATE OR REPLACE FUNCTION ref_geo.intersect_geom_type_tol(
    IN mygeom geometry,
    IN mytypecode character varying,
    IN tolerance double precision)
  RETURNS TABLE(id_area integer) AS
$BODY$
        BEGIN
            RETURN QUERY

	WITH 

	test AS (SELECT
		mygeom as geom, ST_AREA(mygeom) AS area
	),

	preselected AS ( SELECT
		l.id_area, l.geom
		FROM ref_geo.l_areas AS l
		JOIN test t ON TRUE
		WHERE l.id_type = ref_geo.get_id_type(mytypecode)
			AND ST_INTERSECTS(l.geom, t.geom)
	)

	SELECT (p.id_area)
		FROM preselected AS p
		JOIN test AS t ON TRUE
		WHERE ST_AREA(ST_INTERSECTION(p.geom, t.geom))*(1.0/ST_AREA(t.geom) + 1.0/t.area)/2 > tolerance
	;
          END;
    $BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100
  ROWS 1000;

-- Function: ref_geo.intersect_id_area_type_tol(integer, character varying, double precision)
-- retourne les id de ref_geo.l_areas de type mytypecode 
-- qui intersecten

	DROP FUNCTION IF EXISTS ref_geo.intersect_id_area_type_tol(integer, character varying, double precision);

CREATE OR REPLACE FUNCTION ref_geo.intersect_id_area_type_tol(
    IN myidarea integer,
    IN mytypecode character varying,
    IN tolerance double precision)
  RETURNS TABLE(id_area integer) AS
$BODY$
        BEGIN
            RETURN QUERY

	WITH 
  test AS (
    SELECT l.geom, ST_AREA(l.geom) AS area
      FROM ref_geo.l_areas l
      WHERE l.id_area = myidarea
  ),

  preselected AS ( SELECT l.id_area, l.geom
		FROM ref_geo.l_areas AS l
		JOIN test t ON TRUE
		WHERE l.id_type = ref_geo.get_id_type(mytypecode)
			AND ST_INTERSECTS(l.geom, t.geom)
	)

	SELECT (p.id_area)
		FROM preselected AS p
		JOIN test AS t
		ON TRUE
		WHERE ST_AREA(ST_INTERSECTION(p.geom, t.geom))*(1.0/ST_AREA(p.geom) + 1.0/t.area)/2 > tolerance
	;
          END;
    $BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100
  ROWS 1000;


DROP FUNCTION IF EXISTS ref_geo.clean_ug_name(text) CASCADE;

CREATE OR REPLACE FUNCTION ref_geo.clean_ug_name(
    name text)

    RETURNS text AS
    --
    -- Returns the id_area(s) of the areas of type code intersecting with area id_area
    --
    $BODY$
            DECLARE name_out TEXT;
    BEGIN
            SELECT INTO name_out regexp_replace(b.name, '-$', '', 'g')
                FROM (SELECT regexp_replace(a.name, '_$', '', 'g') as name
                    FROM (SELECT regexp_replace(name, '-_', '_', 'g') as name)a
                    )b;
            return name_out;
         END;
    $BODY$

    LANGUAGE plpgsql IMMUTABLE
    COST 100;


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


  CREATE OR REPLACE FUNCTION table_exists(schema_name character varying, table_name character varying)
   RETURNS boolean AS
$BODY$
BEGIN
   IF EXISTS(
       SELECT *
       FROM pg_class as tbl
       INNER JOIN pg_namespace as schm on tbl.relnamespace = schm.oid
       WHERE schm.nspname = '' || schema_name || ''
       AND tbl.relname = '' || table_name || ''
   ) THEN
       RETURN true;
   ELSE
       RETURN false;
   END IF;
END;
$BODY$
LANGUAGE 'plpgsql' VOLATILE;


DROP FUNCTION IF EXISTS ref_geo.get_massif(integer []);

CREATE OR REPLACE FUNCTION ref_geo.get_massif(
    IN myidareas integer[])
  
  RETURNS integer AS
$BODY$
    DECLARE id_area_out INTEGER;
        BEGIN
        
                WITH centroid AS (SELECT ST_CENTROID(ST_UNION(l.geom)) as geom
                    FROM ref_geo.l_areas as l
                    WHERE l.id_area = ANY(myidareas))

        SELECT into id_area_out l.id_area
            FROM ref_geo.l_areas as l, centroid
            WHERE l.id_type = ref_geo.get_id_type('OEASC_SECTEUR') AND
            ST_INTERSECTS(l.geom, centroid.geom);
            
        RETURN id_area_out;
          END;
    $BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;


DROP FUNCTION IF EXISTS array_sort_unique (ANYARRAY);


CREATE OR REPLACE FUNCTION array_sort_unique (ANYARRAY) RETURNS ANYARRAY
LANGUAGE SQL
AS $body$
  SELECT ARRAY(
    SELECT DISTINCT $1[s.i]
    FROM generate_series(array_lower($1,1), array_upper($1,1)) AS s(i)
    ORDER BY 1
  );
$body$;


CREATE OR REPLACE FUNCTION ref_geo.get_area_name(myidarea integer DEFAULT NULL::integer)
  RETURNS character varying AS
$BODY$
--Function which return the label from the id_nomenclature
DECLARE
	theareaname character varying;
  BEGIN
  SELECT INTO theareaname area_name
  FROM ref_geo.l_areas n
  WHERE id_area = myidarea;
return theareaname;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;
ALTER FUNCTION ref_geo.get_area_name(integer)
  OWNER TO dbadmin;


  CREATE OR REPLACE FUNCTION ref_geo.get_area_names(myidareas integer[])
  RETURNS character varying AS
$BODY$
--Function which return the label from the id_nomenclature
DECLARE
	theareanames character varying;
  BEGIN
  SELECT INTO theareanames STRING_AGG(DISTINCT areaname, ', ')
  FROM (SELECT ref_geo.get_area_name(UNNEST(myidareas)) AS areaname)a;
return theareanames;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;
ALTER FUNCTION ref_geo.get_area_names(integer[])
  OWNER TO dbadmin;



CREATE OR REPLACE FUNCTION ref_geo.get_area_code(myidarea integer DEFAULT NULL::integer)
  RETURNS character varying AS
$BODY$
--Function which return the label from the id_nomenclature
DECLARE
	theareacode character varying;
  BEGIN
  SELECT INTO theareacode area_code
  FROM ref_geo.l_areas n
  WHERE id_area = myidarea;
return theareacode;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;
ALTER FUNCTION ref_geo.get_area_code(integer)
  OWNER TO dbadmin;


  CREATE OR REPLACE FUNCTION ref_geo.get_area_codes(myidareas integer[])
  RETURNS character varying AS
$BODY$
--Function which return the label from the id_nomenclature
DECLARE
	theareacodes character varying;
  BEGIN
  SELECT INTO theareacodes STRING_AGG(DISTINCT areacode, ', ')
  FROM (SELECT ref_geo.get_area_code(UNNEST(myidareas)) AS areacode)a;
return theareacodes;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;
ALTER FUNCTION ref_geo.get_area_codes(integer[])
  OWNER TO dbadmin;

