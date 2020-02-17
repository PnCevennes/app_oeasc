-- vues pour les resultats


-- nb_declaration_secteur

DROP VIEW IF EXISTS oeasc_declarations.nb_declaration_secteur ;
CREATE OR REPLACE VIEW oeasc_declarations.nb_declaration_secteur AS
SELECT 
	COUNT(*) AS value,
	secteurs AS label
	FROM oeasc_declarations.v_declarations
	GROUP BY secteurs
	ORDER BY value DESC;


-- nb_declaration_organismes

DROP VIEW IF EXISTS oeasc_declarations.nb_declaration_organisme ;
CREATE OR REPLACE VIEW oeasc_declarations.nb_declaration_organisme AS
SELECT 
	COUNT(*) AS value,
	organisme AS label
	FROM oeasc_declarations.v_declarations
	GROUP BY organisme
	ORDER BY value DESC;


-- time line declaration

DROP VIEW IF EXISTS oeasc_declarations.timeline_declaration ;
CREATE OR REPLACE VIEW oeasc_declarations.timeline_declaration  AS
SELECT 
	COUNT(*) AS value,
	TO_CHAR(meta_create_date, 'YYYY-MM') || '-01' AS date
	FROM oeasc_declarations.v_declarations
	GROUP BY "date"
	ORDER BY "date"
	;

SELECT * FROM oeasc_declarations.timeline_declaration;


-- time line declaration secteur

DROP VIEW IF EXISTS oeasc_declarations.timeline_declaration_secteur ;
CREATE OR REPLACE VIEW oeasc_declarations.timeline_declaration_secteur  AS
SELECT 
	COUNT(*) AS value,
	secteurs,
	TO_CHAR(meta_create_date, 'YYYY-MM') || '-01' AS date
	FROM oeasc_declarations.v_declarations
	GROUP BY "date", secteurs
	ORDER BY "date"
	;

SELECT * FROM oeasc_declarations.timeline_declaration_secteur;
