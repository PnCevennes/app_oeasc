--------------------
--PUBLIC FUNCTIONS--
--------------------
CREATE OR REPLACE FUNCTION public.fct_trg_meta_dates_change()
  RETURNS trigger AS
$BODY$
begin
        if(TG_OP = 'INSERT') THEN
                NEW.meta_create_date = NOW();
        ELSIF(TG_OP = 'UPDATE') THEN
                NEW.meta_update_date = NOW();
                if(NEW.meta_create_date IS NULL) THEN
                        NEW.meta_create_date = NOW();
                END IF;
        end IF;
        return NEW;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

-- fn cor_areas_declarations
DROP FUNCTION IF EXISTS oeasc_declarations.fct_cor_areas_declarations(myid_declaration INTEGER);
 CREATE OR REPLACE FUNCTION oeasc_declarations.fct_cor_areas_declarations(myid_declaration INTEGER)
   RETURNS int AS
 $BODY$
 BEGIN

    DELETE FROM oeasc_declarations.cor_areas_declarations c
	USING ref_geo.l_areas l
	WHERE l.id_area=c.id_area AND l.id_type in (
	ref_geo.get_id_type('OEASC_SECTEUR'),
	ref_geo.get_id_type('OEASC_COMMUNE'),
	ref_geo.get_id_type('OEASC_SECTION'),
	ref_geo.get_id_type('OEASC_ONF_FRT'),
	ref_geo.get_id_type('OEASC_DGD')
	)
	AND c.id_declaration = myid_declaration
    ;

    INSERT INTO oeasc_declarations.cor_areas_declarations

    WITH geom AS ( SELECT 	
        c.id_declaration,
        ST_MULTI(ST_UNION(l.geom)) AS geom
        FROM oeasc_declarations.cor_areas_declarations c
        JOIN ref_geo.l_areas l
            ON l.id_area = c.id_area
            AND l.id_type IN (
                ref_geo.get_id_type('OEASC_ONF_UG'),
                ref_geo.get_id_type('OEASC_CADASTRE')
            )
        GROUP BY c.id_declaration
    ),
    selected_types AS (SELECT UNNEST(ARRAY [          
             'OEASC_SECTEUR',
             'OEASC_COMMUNE',
             'OEASC_SECTION',
             'OEASC_ONF_FRT',
--             'OEASC_ONF_PRF',
--             'OEASC_ONF_UG',
--             'OEASC_CADASTRE',
             'OEASC_DGD'
         ]) AS id_type)
        
         SELECT 
             myid_declaration,
             ref_geo.intersect_geom_type_tol(geom.geom, selected_types.id_type, 0.05) as id_area
             FROM selected_types
             JOIN geom ON geom.id_declaration = myid_declaration;

   RETURN 0;
 END;
$BODY$
   LANGUAGE plpgsql VOLATILE
   COST 100;


CREATE OR REPLACE FUNCTION oeasc_declarations.get_area_names(myiddeclaration integer, myareatype character varying)
  RETURNS character varying AS
$BODY$
--Function which return the label from the id_nomenclature
DECLARE
	theareanames character varying;
  BEGIN
  SELECT INTO theareanames STRING_AGG(DISTINCT l.area_name, ', ')
  FROM oeasc_declarations.cor_areas_declarations c
  LEFT JOIN ref_geo.l_areas l
    ON c.id_area = l.id_area
        AND l.id_type = ref_geo.get_id_type(myareatype)
    WHERE id_declaration = myiddeclaration
    ;

return theareanames;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;


CREATE OR REPLACE FUNCTION oeasc_declarations.get_area_codes(myiddeclaration integer, myareatype character varying)
  RETURNS character varying AS
$BODY$
--Function which return the label from the id_nomenclature
DECLARE
	theareacodes character varying;
  BEGIN
  SELECT INTO theareacodes STRING_AGG(DISTINCT l.area_code, ', ')
  FROM oeasc_declarations.cor_areas_declarations c
  LEFT JOIN ref_geo.l_areas l
    ON c.id_area = l.id_area
        AND l.id_type = ref_geo.get_id_type(myareatype)
    WHERE id_declaration = myiddeclaration
    ;

return theareacodes;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;



CREATE OR REPLACE FUNCTION oeasc_declarations.get_id_areas(myiddeclaration integer, myareatype character varying)
  RETURNS integer[] AS
$BODY$
--Function which return the label from the id_nomenclature
DECLARE
	theidareas character varying;
  BEGIN
  SELECT INTO theidareas ARRAY_AGG(DISTINCT l.id_area)
  FROM oeasc_declarations.cor_areas_declarations c
  LEFT JOIN ref_geo.l_areas l
    ON c.id_area = l.id_area
        AND l.id_type = ref_geo.get_id_type(myareatype) OR myareatype = '*'
    WHERE id_declaration = myiddeclaration
    AND l.id_area IS NOT NULL
    ;

return theidareas;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;
