DROP VIEW IF EXISTS oeasc_chasse.v_custom_results;
CREATE OR REPLACE VIEW oeasc_chasse.v_custom_results AS
SELECT 
	id_nomenclature_mode_chasse,
	tnmc.label_fr AS label_mode_chasse,
	tns.label_fr AS label_sexe,
	tnca.label_fr AS label_classe_age,
	te.nom_espece,
	tzc.id_zone_cynegetique,	
	tzc.nom_zone_cynegetique,
	tzi.id_zone_indicative,
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

DROP FUNCTION IF EXISTS oeasc_chasse.fct_custom_results_t(IN args JSONB);
CREATE OR REPLACE FUNCTION oeasc_chasse.fct_custom_results_t(IN args JSONB)
	RETURNS TABLE (
		text CHARACTER VARYING,
		count INTEGER	
	) AS
		$BODY$
			DECLARE field_name VARCHAR;
			DECLARE q VARCHAR;
			DECLARE _key VARCHAR;
			DECLARE _value VARCHAR;
			DECLARE _t_filter VARCHAR;
			BEGIN
			SELECT INTO q FORMAT('SELECT %I, count(*)::INTEGER
	FROM %s', args->>'field_name', args->>'view');
			FOR _key, _value IN
       			SELECT * FROM jsonb_each(args->'filters')
    		LOOP
    			RAISE NOTICE '% : %', _key, _value;
    			IF _t_filter IS NULL THEN
					SELECT INTO q FORMAT(' %s
	WHERE', q);
				ELSE
					SELECT INTO q FORMAT('%s
		AND', q);
				END IF;
			SELECT INTO _t_filter '(''' || STRING_AGG(a, ''', ''') || ''')' FROM jsonb_array_elements_text(_value::JSONB) AS a;
			SELECT INTO q FORMAT('%s %I::varchar IN %s', q,  _key, _t_filter);
    		END LOOP;
    		SELECT INTO q FORMAT('%s
	GROUP BY %I
	ORDER BY count(*) DESC ', q, args->>'field_name');
       			RAISE NOTICE '%', q  ;

			RETURN QUERY
				EXECUTE q;
			END;
		$BODY$
	LANGUAGE plpgsql VOLATILE;

DROP FUNCTION IF EXISTS oeasc_chasse.fct_custom_results_j(IN VARCHAR);
DROP FUNCTION IF EXISTS oeasc_chasse.fct_custom_results_j(IN VARCHAR, IN VARCHAR);
DROP FUNCTION IF EXISTS oeasc_chasse.fct_custom_results_j(IN VARCHAR, IN JSONB);
CREATE OR REPLACE FUNCTION oeasc_chasse.fct_custom_results_j(IN field_name VARCHAR, filters JSONB)
	RETURNS JSONB AS 
		$BODY$
			BEGIN
				RETURN json_agg(a)
					FROM oeasc_chasse.fct_custom_results_t(field_name, filters)a;
			END;
		$BODY$
	LANGUAGE plpgsql VOLATILE;

