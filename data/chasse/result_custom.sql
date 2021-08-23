DROP VIEW IF EXISTS oeasc_chasse.v_custom_results;
CREATE OR REPLACE VIEW oeasc_chasse.v_custom_results AS
SELECT 
	id_nomenclature_mode_chasse,
	tnmc.label_fr AS label_mode_chasse,
	tns.label_fr AS label_sexe,
	tnca.label_fr AS label_classe_age,
	te.nom_espece,
	tzc.nom_zone_cynegetique,
	tzi.nom_zone_indicative,
	'a'
	FROM oeasc_chasse.t_realisations tr
	LEFT JOIN ref_nomenclatures.t_nomenclatures tnmc ON tnmc.id_nomenclature = id_nomenclature_mode_chasse
	LEFT JOIN ref_nomenclatures.t_nomenclatures tns ON tns.id_nomenclature = id_nomenclature_sexe
	LEFT JOIN ref_nomenclatures.t_nomenclatures tnca ON tnca.id_nomenclature = id_nomenclature_classe_age
	JOIN oeasc_chasse.t_attributions ta ON ta.id_attribution = tr.id_attribution 
	JOIN oeasc_chasse.t_type_bracelets ttb ON ttb.id_type_bracelet = ta.id_type_bracelet 
	JOIN oeasc_commons.t_especes te  ON te.id_espece = ttb.id_espece
	JOIN oeasc_chasse.t_zone_cynegetiques tzc ON tzc.id_zone_cynegetique = id_zone_cynegetique_realisee 
	JOIN oeasc_chasse.t_zone_indicatives tzi ON tzi.id_zone_indicative = id_zone_indicative_realisee 
;

DROP FUNCTION IF EXISTS oeasc_chasse.fct_custom_results_t(IN VARCHAR);
CREATE OR REPLACE FUNCTION oeasc_chasse.fct_custom_results_t(IN field_name VARCHAR)
	RETURNS TABLE (
		text CHARACTER VARYING,
		count INTEGER	
	) AS
		$BODY$
			BEGIN
			RETURN QUERY
				EXECUTE FORMAT(
					'SELECT
						%I,
						count(*)::INTEGER
						FROM oeasc_chasse.v_custom_results
						GROUP BY %I
						ORDER BY count(*) DESC',
   					field_name,
   					field_name
   				);	
			END;
		$BODY$
	LANGUAGE plpgsql VOLATILE;

DROP FUNCTION IF EXISTS oeasc_chasse.fct_custom_results_j(IN VARCHAR);
CREATE OR REPLACE FUNCTION oeasc_chasse.fct_custom_results_j(IN field_name VARCHAR)
	RETURNS JSONB AS 
		$BODY$
			BEGIN
				RETURN json_agg(a)
					FROM oeasc_chasse.fct_custom_results_t(field_name)a;
			END;
		$BODY$
	LANGUAGE plpgsql VOLATILE;
	
SELECT * FROM oeasc_chasse.fct_custom_results_t('nom_espece')

