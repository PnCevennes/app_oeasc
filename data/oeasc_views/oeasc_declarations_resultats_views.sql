-- vues pour les resultats

-- time line declaration

DROP VIEW IF EXISTS oeasc_declarations.v_timeline_declaration ;
CREATE OR REPLACE VIEW oeasc_declarations.v_timeline_declaration  AS
SELECT 
	COUNT(*) AS value,
	TO_CHAR(meta_create_date, 'YYYY-MM') || '-01' AS date
	FROM oeasc_declarations.v_declarations
	GROUP BY "date"
	ORDER BY "date"
	;

DROP FUNCTION IF EXISTS oeasc_declarations.create_result_view;
CREATE OR REPLACE FUNCTION oeasc_declarations.create_result_view(field_name text)
  RETURNS text AS
$BODY$

    BEGIN
	EXECUTE format('
-- nb_declaration

DROP VIEW IF EXISTS oeasc_declarations.v_nb_declaration_' || $1 || ' ;
CREATE OR REPLACE VIEW oeasc_declarations.v_nb_declaration_' || $1 || ' AS
SELECT 
	COUNT(*) AS value,
	UNNEST(STRING_TO_ARRAY(' || $1 || ', '', '')) AS label
	FROM oeasc_declarations.v_declarations
	GROUP BY label
	ORDER BY value DESC;

-- time line declaration

DROP VIEW IF EXISTS oeasc_declarations.v_timeline_declaration_' || $1 || ' ;
CREATE OR REPLACE VIEW oeasc_declarations.v_timeline_declaration_' || $1 || '  AS
SELECT 
	COUNT(*) AS value,
	UNNEST(STRING_TO_ARRAY(' || $1 || ', '', '')) AS split,
	TO_CHAR(meta_create_date, ''YYYY-MM'') || ''-01'' AS date
	FROM oeasc_declarations.v_declarations
	GROUP BY "date", split
	ORDER BY "date"
	;	
	')
   USING field_name;
            return 'ok';
         END;
    $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;
ALTER FUNCTION oeasc_declarations.create_result_view(text)
  OWNER TO dbadmin;


SELECT oeasc_declarations.create_result_view(field_name) FROM 
	( SELECT UNNEST(ARRAY[
	'secteur',
	'organisme_group',
	'type_foret',
	'peuplement_ess_1_mnemo',
	'peuplement_ess_2_mnemo',
	'peuplement_type_mnemo',
    'peuplement_maturite_mnemo',
    'peuplement_paturage_type_mnemo',
    'degat_types_mnemo'
	]) AS field_name)a;
