

CREATE OR REPLACE VIEW public.active_locks AS 
 SELECT t.schemaname,
    t.relname,
    l.locktype,
    l.page,
    l.virtualtransaction,
    l.pid,
    l.mode,
    l.granted
   FROM pg_locks l
   JOIN pg_stat_all_tables t ON l.relation = t.relid
  WHERE t.schemaname <> 'pg_toast'::name AND t.schemaname <> 'pg_catalog'::name
  ORDER BY t.schemaname, t.relname;


CREATE OR REPLACE FUNCTION array_sort_unique (ANYARRAY) RETURNS ANYARRAY
LANGUAGE SQL
AS $BODY$
  SELECT ARRAY(
    SELECT DISTINCT $1[s.i]
    FROM generate_series(array_lower($1,1), array_upper($1,1)) AS s(i)
    ORDER BY 1
  );
$BODY$;

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


DROP FUNCTION IF EXISTS ref_geo.intersect_rel_area(INTEGER, CHARACTER VARYING, DOUBLE PRECISION) CASCADE;

CREATE OR REPLACE FUNCTION ref_geo.intersect_rel_area(
    myidarea INTEGER,
    mytypecode CHARACTER VARYING,
    seuil DOUBLE PRECISION)

    RETURNS TABLE (id_area INT) AS
    --
    -- Returns the id_area(s) of the areas of type code intersecting with area id_area
    --
    $$
        BEGIN
            RETURN QUERY

                WITH test AS (SELECT l.geom as geom
                    FROM ref_geo.l_areas as l
                    WHERE L.id_area=myidarea)

                SELECT(c.id_area)
                    FROM (
                        SELECT a.id_area
                            FROM (
                                SELECT l.id_area, l.geom
                                    FROM ref_geo.l_areas as l, test
                                    WHERE l.id_type = ref_geo.get_id_type(mytypecode) AND
                                    ST_INTERSECTS(l.geom, test.geom)
                                )a, test
                            WHERE ST_AREA(ST_INTERSECTION(a.geom, test.geom))*(1.0/ST_AREA(a.geom) + 1.0/ST_AREA(test.geom))/2 > seuil
                    )c;
          END;
    $$

    LANGUAGE plpgsql IMMUTABLE
    COST 100;


DROP FUNCTION IF EXISTS ref_geo.get_id_area_from_area_code(CHARACTER VARYING, CHARACTER VARYING) CASCADE;

CREATE OR REPLACE FUNCTION ref_geo.get_id_area_from_area_code(
    myareacode CHARACTER VARYING,
    mytypecode CHARACTER VARYING)

    RETURNS INTEGER AS
    $BODY$
    --
    -- Returns the id_area from area_code and id_type
    --
        DECLARE theidarea INTEGER;
        BEGIN
            SELECT INTO theidarea id_area FROM ref_geo.l_areas WHERE area_code = myareacode AND id_type = ref_geo.get_id_type(mytypecode);
            return theidarea;
        END;
    $BODY$

    LANGUAGE plpgsql IMMUTABLE
    COST 100;


-- Function: ref_nomenclatures.get_nomenclature_id_from_label(character varying, character varying)

DROP FUNCTION IF EXISTS ref_nomenclatures.get_nomenclature_id_from_label(character varying, character varying) CASCADE;

CREATE OR REPLACE FUNCTION ref_nomenclatures.get_nomenclature_id_from_label(
    mylabel CHARACTER VARYING,
    mytype_mnemonique CHARACTER VARYING)

    RETURNS INTEGER AS
    $BODY$
    --
    -- Returns id_nomenclature from the label and the type_code
    --
        DECLARE theidnomenclature INTEGER;
        BEGIN
            EXECUTE format( ' SELECT  n.id_nomenclature
                FROM ref_nomenclatures.t_nomenclatures n
                WHERE id_type = %s AND label_fr = ''%s'' ', ref_nomenclatures.get_id_nomenclature_type(mytype_mnemonique), mylabel)INTO theidnomenclature;
                return theidnomenclature;
        END;
    $BODY$
    LANGUAGE plpgsql IMMUTABLE
    COST 100;
