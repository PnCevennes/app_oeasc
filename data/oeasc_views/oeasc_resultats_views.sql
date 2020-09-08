-- vues pour les resultats

-- time line declaration
DROP SCHEMA IF EXISTS oeasc_resultats CASCADE;
CREATE SCHEMA oeasc_resultats;


DROP VIEW IF EXISTS oeasc_resultats.v_timeline_declaration ;
CREATE OR REPLACE VIEW oeasc_resultats.v_timeline_declaration  AS
SELECT 
	COUNT(*) AS value,
	TO_CHAR(meta_create_date, 'YYYY-MM') || '-01' AS date
	FROM oeasc_declarations.v_declarations
	GROUP BY "date"
	ORDER BY "date"
	;

DROP FUNCTION IF EXISTS oeasc_resultats.create_declaration_view;
CREATE OR REPLACE FUNCTION oeasc_resultats.create_declaration_view(field_name text)
  RETURNS text AS
$BODY$

    BEGIN
	EXECUTE format('
-- nb_declaration

DROP VIEW IF EXISTS oeasc_resultats.v_nb_declaration_' || $1 || ' ;
CREATE OR REPLACE VIEW oeasc_resultats.v_nb_declaration_' || $1 || ' AS
SELECT 
	COUNT(*) AS value,
	UNNEST(STRING_TO_ARRAY(' || $1 || ', '', '')) AS label
	FROM oeasc_declarations.v_declarations
	GROUP BY label
	ORDER BY value DESC;

-- time line declaration

DROP VIEW IF EXISTS oeasc_resultats.v_timeline_declaration_' || $1 || ' ;
CREATE OR REPLACE VIEW oeasc_resultats.v_timeline_declaration_' || $1 || '  AS
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





DROP VIEW IF EXISTS oeasc_resultats.v_nb_essence;
CREATE OR REPLACE VIEW oeasc_resultats.v_nb_essence AS
(SELECT
	COUNT(*) AS value,
	peuplement_ess_1_mnemo AS label,
	'Essence objectif principale' AS split
FROM oeasc_declarations.v_declarations
GROUP BY label
ORDER BY VALUE DESC)

UNION ALL

(SELECT
	COUNT(*) AS value,
	UNNEST(STRING_TO_ARRAY(peuplement_ess_2_mnemo, ', ')) AS label,
	'Essence objectif secondaire' AS split
FROM oeasc_declarations.v_declarations
GROUP BY label
ORDER BY VALUE DESC);




DROP FUNCTION IF EXISTS oeasc_resultats.create_degat_view;
CREATE OR REPLACE FUNCTION oeasc_resultats.create_degat_view(field_name text)
  RETURNS text AS
$BODY$

    BEGIN
	EXECUTE format('

-- nb_degat

DROP VIEW IF EXISTS oeasc_resultats.v_nb_' || $1 || ' ;
CREATE OR REPLACE VIEW oeasc_resultats.v_nb_' || $1 || ' AS
SELECT 
	COUNT(*) AS value,
	' || $1 || ' AS label
	FROM oeasc_declarations.v_degats
    WHERE ' || $1 || ' IS NOT NULL
	GROUP BY label
	ORDER BY value DESC;
	
	')
   USING field_name;
            return 'ok';
         END;
    $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

DROP VIEW IF EXISTS oeasc_resultats.v_nb_degat_type_mnemo;
CREATE VIEW oeasc_resultats.v_nb_degat_type_mnemo AS
SELECT
	COUNT(*) AS value,
	degat_type_mnemo AS label
	FROM oeasc_declarations.v_degats 
	GROUP BY label
	ORDER BY value DESC
	;


SELECT oeasc_resultats.create_declaration_view(field_name) FROM 
	( SELECT UNNEST(ARRAY[
	'secteur',
	'organisme_group',
	'type_foret',
	'peuplement_ess_1_mnemo',
	'peuplement_ess_2_mnemo',
	'peuplement_type_mnemo',
    'peuplement_maturite_mnemo',
    'peuplement_paturage_type_mnemo',
    'degat_type_mnemos'
	]) AS field_name)a;

SELECT oeasc_resultats.create_degat_view(field_name) FROM 
	( SELECT UNNEST(ARRAY[
    'degat_type_mnemo',
    'degat_essence_mnemo',
    'degat_gravite_mnemo',
    'degat_etendue_mnemo',
    'degat_anteriorite_mnemo'
	]) AS field_name)a;


SELECT * FROM oeasc_declarations.v_declaration_degats;

DROP FUNCTION IF EXISTS oeasc_resultats.create_view_2;
CREATE OR REPLACE FUNCTION oeasc_resultats.create_view_2(field_name_1 text, field_name_2 text)
  RETURNS text AS
$BODY$

    BEGIN
	EXECUTE format('

DROP VIEW IF EXISTS oeasc_resultats.v_nb_' || $1 || '_' || $2 || ' ;
CREATE OR REPLACE VIEW oeasc_resultats.v_nb_' || $1 || '_' || $2 || '  AS
SELECT 
	COUNT(*) AS value,
	' || $2 || ' AS label,
	' || $1 || ' AS split
	
	FROM oeasc_declarations.v_declaration_degats
    WHERE ' || $1 || ' IS NOT NULL AND  ' || $2 || ' IS NOT NULL
	GROUP BY label, split
	ORDER BY value DESC;
	')
	
   USING field_name_1, field_name_2;
            return 'ok';
         END;
    $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

SELECT oeasc_resultats.create_view_2('degat_type_mnemo', 'degat_essence_mnemo');
SELECT oeasc_resultats.create_view_2('degat_gravite_mnemo', 'degat_essence_mnemo');
SELECT oeasc_resultats.create_view_2('degat_gravite_mnemo', 'peuplement_type_mnemo');
