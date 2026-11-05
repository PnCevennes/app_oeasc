-- Fonctions, vues et triggers du schéma oeasc_chasse.
-- Généré le 2026-11-05 depuis la base oeasc2 (référence : les modèles et la base de production,
-- les anciens fichiers install/data/chasse/*.sql sont périmés). Exécuté par `flask init-db`.

CREATE OR REPLACE FUNCTION oeasc_chasse.fct_calcul_ice_mc(id_espece_in integer, id_zone_cynegetique_in integer)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
		DECLARE
			j_out JSONB;
		BEGIN
			RAISE NOTICE 'calcul ice pour id_espece % id_zone_cynegetique %', id_espece_in, id_zone_cynegetique_in;
		    WITH
				-- 1 ere extraction (date + poids)
				pre_data_1 AS ( SELECT
					date_exacte,
					id_espece,
					id_zone_cynegetique_realisee,
					oeasc_chasse.fct_day_of_year(date_exacte, '06-01') AS doy,
					oeasc_chasse.fct_poid_vide(id_espece, poid_entier, poid_vide, poid_c_f_p) AS pv,
					ta.id_saison
				FROM oeasc_chasse.t_realisations tr
				JOIN oeasc_chasse.t_attributions ta ON ta.id_attribution = tr.id_attribution
				JOIN oeasc_chasse.t_type_bracelets ttb ON ta.id_type_bracelet = ttb.id_type_bracelet
				JOIN ref_nomenclatures.t_nomenclatures tn ON tn.id_nomenclature = id_nomenclature_classe_age
				WHERE 
					date_exacte IS NOT NULL
					AND COALESCE(poid_entier, poid_vide, poid_c_f_p) IS NOT NULL
					AND tn.cd_nomenclature = '3' -- juvenile
				)
				-- minimum des dates de chasse (apres le 06-01) tout confondu (pour rapporter à cette date)
				, min_doy AS ( SELECT 
					min(doy) AS min_doy
					FROM pre_data_1
				)
				-- x (date rapportée), y (poid vide), pour une espece et un massif
				, pre_data_2 AS ( SELECT
					id_saison,
					doy - md.min_doy + 1 AS x,
					pv AS y
					FROM pre_data_1 p1, min_doy md
					WHERE 
						p1.id_espece = id_espece_in
						AND p1.id_zone_cynegetique_realisee = id_zone_cynegetique_in
					ORDER BY doy - md.min_doy, y
				)
				-- mediane des jours de chasse
				, median AS ( SELECT
					percentile_disc(0.5) WITHIN GROUP (ORDER BY x) AS median
					FROM pre_data_2
				)
				-- regression linéaire
				, regr_1 AS ( SELECT
					r_lm_slope_j(ARRAY_AGG(y::FLOAT), ARRAY_AGG(x::FLOAT)) AS lm
					FROM pre_data_2
				)		
				-- poid rapporté au jour médian
				, p_corr AS ( SELECT
					id_saison,
					( pd2.x - m.median ) * (r1.lm->'slope')::float + y AS y_corr
					FROM pre_data_2 pd2, median m, regr_1 r1
				)
				-- poid moyen par saison
				, p_moy AS ( SELECT
					id_saison,
					y_corr,
					avg(y_corr) OVER (PARTITION BY id_saison) AS y_moy
					FROM p_corr
				)
				-- erreurs pour intervalles de confiance
				, erreurs AS ( SELECT 
					ts.id_saison,
					y_moy,
					CASE
						WHEN count(*) > 1 THEN 
							sqrt(
								sum( (y_corr - y_moy)^2 ) / ( (count(*) -1) * count(*) )
							) 
						ELSE NULL 
					END AS err,
					count(*) AS nb
					FROM p_moy
					JOIN oeasc_chasse.t_saisons ts ON ts.id_saison = p_moy.id_saison
					GROUP BY ts.id_saison, y_moy
					ORDER BY nom_saison
				)
				-- intervalle de confiance
				, inter_conf AS ( SELECT
					*,
					y_moy - err * tinv(0.05,(nb -1)::INT) AS limit_inf,
					y_moy + err * tinv(0.05,(nb -1)::INT) AS limit_sup
				FROM erreurs e
				)
				--json
				, inter_conf_json AS (
				SELECT
					row_to_json(a)::jsonb AS infsup
					FROM (
						SELECT 
							ARRAY_AGG(limit_inf) AS inf,
							ARRAY_AGG(limit_sup) AS sup 
						FROM inter_conf
					)a
				)
				-- regression
				, regr_2 AS ( SELECT
--					to_jsonb(ARRAY_AGG(y_moy::FLOAT)) AS lm
					r_lm_slope_j(ARRAY_AGG(y_moy::FLOAT), ARRAY_AGG(SPLIT_PART(nom_saison, '-', 1)::FLOAT)) || icj.infsup AS lm
					FROM inter_conf ic
					JOIN inter_conf_json icj ON TRUE
					JOIN oeasc_chasse.t_saisons ts ON ts.id_saison = ic.id_saison
					GROUP BY icj.infsup
					--ORDER BY nom_saison
				)
				SELECT INTO j_out
					row_to_json(a)::jsonb
					FROM ( SELECT
						r2.lm AS res_lm_moy,
						r1.lm AS res_lm_data,
						nom_zone_cynegetique,
						nom_espece
						FROM regr_1 r1, regr_2 r2
						JOIN oeasc_commons.t_especes te ON te.id_espece = id_espece_in
						JOIN oeasc_chasse.t_zone_cynegetiques tzc ON tzc.id_zone_cynegetique = id_zone_cynegetique_in
					)a;
			RETURN j_out;
		END;
		$function$;

CREATE OR REPLACE FUNCTION oeasc_chasse.fct_calcul_ice_mc(id_espece_in integer, id_zone_indicative_in integer[], id_zone_cynegetique_in integer[], id_secteur_in integer[], poids_ou_dagues_in boolean)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
		DECLARE
			j_out JSONB;
		BEGIN
			RAISE NOTICE 'calcul ice pour id_espece % id_zone_indicative %d id_zone_cynegetique % id_secteur % poids dagues %', id_espece_in, id_zone_indicative_in, id_zone_cynegetique_in, id_secteur_in, poids_ou_dagues_in;
		    WITH
				-- 1 ere extraction (date + poids)
				pre_data_1 AS ( SELECT
					date_exacte,
					id_espece,
					id_secteur,
					id_zone_cynegetique_realisee,
					id_zone_indicative_realisee,
					oeasc_chasse.fct_day_of_year(date_exacte, '06-01') AS doy,
					oeasc_chasse.fct_poid_vide(id_espece, poid_entier, poid_vide, poid_c_f_p) AS pv,
					CASE
						WHEN long_dagues_droite IS NOT NULL AND long_dagues_gauche IS NOT NULL
							THEN (long_dagues_droite + long_dagues_gauche) / 2
						ELSE COALESCE(long_dagues_droite, long_dagues_gauche)
 					END as long_dagues,
					ta.id_saison,
					ts.nom_saison
				FROM oeasc_chasse.t_realisations tr
				JOIN oeasc_chasse.t_attributions ta ON ta.id_attribution = tr.id_attribution
				JOIN oeasc_chasse.t_saisons ts ON ts.id_saison = ta.id_saison
				JOIN oeasc_chasse.t_type_bracelets ttb ON ta.id_type_bracelet = ttb.id_type_bracelet
				JOIN ref_nomenclatures.t_nomenclatures tn ON tn.id_nomenclature = id_nomenclature_classe_age
				JOIN oeasc_chasse.t_zone_cynegetiques tzc ON tzc.id_zone_cynegetique = tr.id_zone_cynegetique_realisee
				WHERE
					date_exacte IS NOT NULL
					AND (
						-- le poids n'est requis que pour le calcul sur la masse corporelle, pas pour les dagues
						poids_ou_dagues_in IS FALSE
						OR COALESCE(poid_entier, poid_vide, poid_c_f_p) IS NOT NULL
					)
					AND (
						-- si on veut les resultats sur les dagues alors on prend toutes les classes d'ages
						(poids_ou_dagues_in IS FALSE) AND (tn.cd_nomenclature IN ('3', '5')) --juvenile et subadulte
						OR
						-- si on veut les poids on ne prend que les juvenile
						( poids_ou_dagues_in IS TRUE) AND (tn.cd_nomenclature = '3') --juvenile
					)
				)
				-- minimum des dates de chasse (apres le 06-01) tout confondu (pour rapporter à cette date)
				, min_doy AS ( SELECT
					min(doy) AS min_doy
					FROM pre_data_1
				)
				-- x (date rapportée), y (poid vide), pour une espece et un massif
				, pre_data_2 AS ( SELECT
					id_saison,
					doy - md.min_doy + 1 AS x,
					CASE
						WHEN poids_ou_dagues_in THEN pv
						ELSE long_dagues
					END AS y
					FROM pre_data_1 p1, min_doy md
					WHERE
						p1.id_espece = id_espece_in
						AND ( poids_ou_dagues_in OR long_dagues IS NOT NULL )
						AND (
							array_length(id_zone_indicative_in, 1) IS NULL
							OR
							p1.id_zone_indicative_realisee =  ANY(id_zone_indicative_in)
						)
						AND (
							array_length(id_zone_cynegetique_in, 1) IS NULL
							OR
							p1.id_zone_cynegetique_realisee =  ANY(id_zone_cynegetique_in)
						)
						AND (
							array_length(id_secteur_in, 1) IS NULL
							OR
							p1.id_secteur = ANY(id_secteur_in)
						)
					ORDER BY doy - md.min_doy, y
				)
				-- mediane des jours de chasse
				, median AS ( SELECT
					percentile_disc(0.5) WITHIN GROUP (ORDER BY x) AS median
					FROM pre_data_2
				)
				-- regression linéaire
				, regr_1 AS ( SELECT
					r_lm_slope_j(ARRAY_AGG(y::FLOAT), ARRAY_AGG(x::FLOAT)) AS lm
					FROM pre_data_2
				)
				-- poid rapporté au jour médian
				, p_corr AS ( SELECT
					id_saison,
					( pd2.x - m.median ) * (r1.lm->'slope')::float + y AS y_corr
					FROM pre_data_2 pd2, median m, regr_1 r1
				)
				-- poid moyen par saison
				, p_moy AS ( SELECT
					id_saison,
					y_corr,
					avg(y_corr) OVER (PARTITION BY id_saison) AS y_moy
					FROM p_corr
				)
				-- erreurs pour intervalles de confiance
				, erreurs AS ( SELECT
					ts.id_saison,
					y_moy,
					CASE
						WHEN count(*) > 1 THEN
							sqrt(
								sum( (y_corr - y_moy)^2 ) / ( (count(*) -1) * count(*) )
							)
						ELSE NULL
					END AS err,
					count(*) AS nb
					FROM p_moy
					JOIN oeasc_chasse.t_saisons ts ON ts.id_saison = p_moy.id_saison
					GROUP BY ts.id_saison, y_moy
					ORDER BY nom_saison
				)
				-- intervalle de confiance
				, inter_conf AS ( SELECT
					*,
					y_moy - err * tinv(0.05,(nb -1)::INT) AS limit_inf,
					y_moy + err * tinv(0.05,(nb -1)::INT) AS limit_sup
				FROM erreurs e
				)
				--json
				, inter_conf_json AS (
				SELECT
					row_to_json(a)::jsonb AS infsup
					FROM (
						SELECT
							ARRAY_AGG(limit_inf) AS inf,
							ARRAY_AGG(limit_sup) AS sup
						FROM inter_conf
					)a
				)
				-- regression
				, regr_2 AS ( SELECT
--					to_jsonb(ARRAY_AGG(y_moy::FLOAT)) AS lm
					r_lm_slope_j(
						ARRAY_AGG(y_moy::FLOAT ORDER BY nom_saison),
						ARRAY_AGG(SPLIT_PART(nom_saison, '-', 1)::FLOAT ORDER BY nom_saison)
					) || icj.infsup AS lm
					FROM inter_conf ic
					JOIN inter_conf_json icj ON TRUE
					JOIN oeasc_chasse.t_saisons ts ON ts.id_saison = ic.id_saison
					GROUP BY icj.infsup
				)
				SELECT INTO j_out
					row_to_json(a)::jsonb
					FROM ( SELECT
						r2.lm AS res_lm_moy,
						r1.lm AS res_lm_data,
						(
							SELECT STRING_AGG(nom_zone_cynegetique, ', ' ORDER BY nom_zone_cynegetique)
								FROM oeasc_chasse.t_zone_cynegetiques tzc
								WHERE tzc.id_zone_cynegetique = ANY(id_zone_cynegetique_in)
						) as  nom_zone_cynegetique,
						(
							SELECT STRING_AGG(nom_zone_indicative, ', ' ORDER BY nom_zone_indicative)
								FROM oeasc_chasse.t_zone_indicatives tzi
								WHERE tzi.id_zone_indicative = ANY(id_zone_indicative_in)
						) as  nom_zone_indicative,
						(
							SELECT STRING_AGG(nom_secteur, ', ' ORDER BY nom_secteur)
								FROM oeasc_commons.t_secteurs ts
								WHERE ts.id_secteur = ANY(id_secteur_in)
						) as  nom_secteur,
						nom_espece,
						CASE WHEN poids_ou_dagues_in THEN 'poids' ELSE 'dagues' END AS data_type
						FROM regr_1 r1, regr_2 r2
						JOIN oeasc_commons.t_especes te ON te.id_espece = id_espece_in
					)a;
			RETURN j_out;
		END;
		$function$;

CREATE OR REPLACE FUNCTION oeasc_chasse.fct_custom_results_j(args jsonb)
 RETURNS jsonb
 LANGUAGE plpgsql
AS $function$
				BEGIN
					RAISE NOTICE 'ARG JSONB %s', args;
					RETURN json_agg(a)
						FROM oeasc_chasse.fct_custom_results_t(args::JSONB)a;
				END;
			$function$;

CREATE OR REPLACE FUNCTION oeasc_chasse.fct_custom_results_t(args jsonb)
 RETURNS TABLE(text character varying, count integer)
 LANGUAGE plpgsql
AS $function$
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
			$function$;

CREATE OR REPLACE FUNCTION oeasc_chasse.fct_day_of_year(date_exacte date, md_ref character varying)
 RETURNS integer
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
		DECLARE
			day_of_year INTEGER;
			ref_date DATE;
			ref_date_minus_one DATE;
		BEGIN
			SELECT INTO ref_date (TO_CHAR(date_exacte, 'YYYY')::INT || '-' || MD_ref)::DATE;
			SELECT INTO ref_date_minus_one (TO_CHAR(date_exacte, 'YYYY')::INT - 1 || '-' || MD_ref)::DATE;
			SELECT INTO day_of_year CASE
				WHEN date_exacte < ref_date THEN TO_CHAR(date_exacte, 'J')::INT - TO_CHAR(ref_date_minus_one, 'J')::INT
				ELSE TO_CHAR(date_exacte, 'J')::INT - TO_CHAR(ref_date, 'J')::INT
			END;
			RETURN day_of_year;
		END;
	$function$;

CREATE OR REPLACE FUNCTION oeasc_chasse.fct_poid_vide(id_espece_in integer, poids_entier_in double precision, poids_vide_in double precision, poids_c_f_p_in double precision)
 RETURNS integer
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
		DECLARE
			poids_vide_out INTEGER;
			CODE_ESPECE VARCHAR;
			pe_exp FLOAT;
			pe_puis FLOAT;
			pcfp_exp FLOAT;
			pcfp_puis FLOAT;
		BEGIN
			SELECT INTO code_espece te.code_espece FROM oeasc_commons.t_especes te WHERE te.id_espece = id_espece_in;
			IF code_espece = 'CF' THEN
				pe_exp := -0.3948 ;
				pe_puis := 1.0247 ;
				pcfp_exp := -0.1128 ;
				pcfp_puis := 1.0041 ;
			ELSIF code_espece = 'CH' THEN
				pe_exp := -0.3572 ;
				pe_puis := 1.023 ;
				pcfp_exp := -0.2868 ;
				pcfp_puis := 1.0614 ;
			END IF;
			SELECT INTO poids_vide_out CASE
				WHEN NOT poids_vide_in IS NULL THEN poids_vide_in
				WHEN NOT poids_entier_in IS NULL THEN EXP(pe_exp)* poids_entier_in^pe_puis
				WHEN NOT poids_c_f_p_in IS NULL THEN EXP(pcfp_exp)* poids_c_f_p_in^pcfp_puis
			END AS pv;
			RETURN poids_vide_out;
		END;
	$function$;

CREATE OR REPLACE FUNCTION oeasc_chasse.fct_trg_calculate_realisation_categorie()
 RETURNS trigger
 LANGUAGE plpgsql
AS $function$  
	DECLARE id_categorie int;
		BEGIN
					
		WITH d AS (
			SELECT ttb.id_espece, NEW.id_nomenclature_sexe, NEW.id_nomenclature_classe_age 
			FROM  oeasc_chasse.t_attributions ta 
			JOIN oeasc_chasse.t_type_bracelets ttb 
			ON ttb.id_type_bracelet = ta.id_type_bracelet
			WHERE ta.id_attribution = NEW.id_attribution
		)
		SELECT c.id_nomenclature_categorie INTO id_categorie
		FROM d
		LEFT JOIN oeasc_chasse.calculate_categorie_sp_age_sexe c
		ON  c.id_espece = d.id_espece
			AND (c.id_nomenclature_sexe= d.id_nomenclature_sexe OR c.id_nomenclature_sexe IS NULL )
			AND c.id_nomenclature_age=d.id_nomenclature_classe_age; 
		NEW.id_nomenclature_categorie := id_categorie;
        return NEW;
end;
$function$;

CREATE OR REPLACE FUNCTION oeasc_chasse.get_lieu_tir_synonyme_label(my_id_lieu_tir_synonyme integer)
 RETURNS character varying
 LANGUAGE plpgsql
 IMMUTABLE
AS $function$
        DECLARE lieu_tir_synonyme_label CHARACTER VARYING;
        BEGIN
        SELECT INTO lieu_tir_synonyme_label 
            CASE 
                WHEN tlts.nom_lieu_tir_synonyme = tlt.nom_lieu_tir  
                    THEN tlt.label_commune || ' - ' || tlt.nom_lieu_tir
                ELSE tlt.label_commune || ' - ' || tlts.nom_lieu_tir_synonyme || ' [' || tlt.nom_lieu_tir || ']'
            END
        FROM oeasc_chasse.t_lieu_tir_synonymes tlts
        JOIN oeasc_chasse.t_lieu_tirs tlt ON tlt.id_lieu_tir = tlts.id_lieu_tir
        WHERE tlts.id_lieu_tir_synonyme = my_id_lieu_tir_synonyme;
        RETURN lieu_tir_synonyme_label;
        END;
        $function$;

CREATE OR REPLACE VIEW oeasc_chasse.v_bilan AS
SELECT tbch.id_saison,
    tbch.id_espece,
    tzc.id_zone_cynegetique,
    sum(tbch.nb_affecte_min) AS nb_affecte_min,
    sum(tbch.nb_affecte_max) AS nb_affecte_max,
    sum(tbch.nb_realise) AS nb_realise,
    sum(tbch.nb_realise_avant_11) AS nb_realise_avant_11
   FROM ((oeasc_chasse.t_bilan_chasse_historique tbch
     JOIN oeasc_chasse.t_zone_indicatives tzi ON ((tzi.id_zone_indicative = tbch.id_zone_indicative)))
     JOIN oeasc_chasse.t_zone_cynegetiques tzc ON ((tzc.id_zone_cynegetique = tzi.id_zone_cynegetique)))
  GROUP BY tbch.id_saison, tbch.id_espece, tzc.id_zone_cynegetique
UNION
 SELECT ta.id_saison,
    ttb.id_espece,
    tr.id_zone_cynegetique_realisee AS id_zone_cynegetique,
    tam.nb_affecte_min,
    tam.nb_affecte_max,
    count(*) AS nb_realise,
    count(*) FILTER (WHERE (tr.date_exacte <= (concat(split_part((ts.nom_saison)::text, '-'::text, 1), '-11-30'))::date)) AS nb_realise_avant_11
   FROM ((((oeasc_chasse.t_realisations tr
     JOIN oeasc_chasse.t_attributions ta ON ((ta.id_attribution = tr.id_attribution)))
     JOIN oeasc_chasse.t_saisons ts ON ((ts.id_saison = ta.id_saison)))
     JOIN oeasc_chasse.t_type_bracelets ttb ON ((ttb.id_type_bracelet = ta.id_type_bracelet)))
     JOIN oeasc_chasse.t_attribution_massifs tam ON (((tam.id_saison = ta.id_saison) AND (tam.id_espece = ttb.id_espece) AND (tr.id_zone_cynegetique_realisee = tam.id_zone_cynegetique))))
  GROUP BY ttb.id_espece, tr.id_zone_cynegetique_realisee, ta.id_saison, tam.nb_affecte_min, tam.nb_affecte_max
  ORDER BY 1, 2, 3;

CREATE OR REPLACE VIEW oeasc_chasse.v_bilan_pretty AS
SELECT vb.id_saison,
    ts.nom_saison,
    vb.id_espece,
    te.nom_espece,
    te.code_espece,
    vb.id_zone_cynegetique,
    tzc.nom_zone_cynegetique,
    tzc.code_zone_cynegetique,
    vb.nb_affecte_min,
    vb.nb_affecte_max,
    vb.nb_realise,
    vb.nb_realise_avant_11
   FROM (((oeasc_chasse.v_bilan vb
     JOIN oeasc_chasse.t_saisons ts ON ((ts.id_saison = vb.id_saison)))
     JOIN oeasc_chasse.t_zone_cynegetiques tzc ON ((tzc.id_zone_cynegetique = vb.id_zone_cynegetique)))
     JOIN oeasc_commons.t_especes te ON ((te.id_espece = vb.id_espece)))
  ORDER BY ts.nom_saison;

CREATE OR REPLACE VIEW oeasc_chasse.v_custom_result_attribution AS
SELECT ta.id_attribution,
    tr.id_realisation,
    te.nom_espece,
    te.id_espece,
    tzc.id_zone_cynegetique,
    tzc.nom_zone_cynegetique,
    tzi.id_zone_indicative,
    tzi.nom_zone_indicative,
    ts.nom_saison,
    ts.id_saison,
    tsec.nom_secteur,
    tsec.id_secteur,
    ttb.code_type_bracelet AS bracelet,
        CASE
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '01'::text) THEN 'Jan.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '02'::text) THEN 'Fév.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '03'::text) THEN 'Mar.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '04'::text) THEN 'Avr.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '05'::text) THEN 'Mai'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '06'::text) THEN 'Juin'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '07'::text) THEN 'Juil.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '08'::text) THEN 'Aou.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '09'::text) THEN 'Sep.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '10'::text) THEN 'Oct.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '11'::text) THEN 'Nov.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '12'::text) THEN 'Déc.'::text
            ELSE to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text)
        END AS mois_txt,
        CASE
            WHEN (date_part('month'::text, tr.date_exacte) < (6)::double precision) THEN (date_part('month'::text, tr.date_exacte) + (12)::double precision)
            ELSE date_part('month'::text, tr.date_exacte)
        END AS mois_txt_sort,
        CASE
            WHEN (tr.id_zone_cynegetique_realisee IS NULL) THEN false
            WHEN (tr.id_zone_cynegetique_realisee = ta.id_zone_cynegetique_affectee) THEN false
            ELSE true
        END AS transfert_zc,
        CASE
            WHEN (tr.id_zone_indicative_realisee IS NULL) THEN false
            WHEN (tr.id_zone_indicative_realisee = ta.id_zone_indicative_affectee) THEN false
            ELSE true
        END AS transfert_zi
   FROM (((((((oeasc_chasse.t_attributions ta
     LEFT JOIN oeasc_chasse.t_realisations tr ON ((ta.id_attribution = tr.id_attribution)))
     JOIN oeasc_chasse.t_saisons ts ON ((ts.id_saison = ta.id_saison)))
     JOIN oeasc_chasse.t_type_bracelets ttb ON ((ttb.id_type_bracelet = ta.id_type_bracelet)))
     JOIN oeasc_commons.t_especes te ON ((te.id_espece = ttb.id_espece)))
     LEFT JOIN oeasc_chasse.t_zone_cynegetiques tzc ON ((tzc.id_zone_cynegetique = COALESCE(tr.id_zone_cynegetique_realisee, ta.id_zone_cynegetique_affectee))))
     LEFT JOIN oeasc_chasse.t_zone_indicatives tzi ON ((tzi.id_zone_indicative = COALESCE(tr.id_zone_indicative_realisee, ta.id_zone_indicative_affectee))))
     LEFT JOIN oeasc_commons.t_secteurs tsec ON ((tsec.id_secteur = tzc.id_secteur)));

CREATE OR REPLACE VIEW oeasc_chasse.v_custom_results AS
SELECT tr.id_nomenclature_mode_chasse,
    tnmc.label_fr AS label_mode_chasse,
    tns.label_fr AS label_sexe,
    tnca.label_fr AS label_classe_age,
    te.nom_espece,
    te.id_espece,
    tzc.id_zone_cynegetique,
    tzc.nom_zone_cynegetique,
    tzi.id_zone_indicative,
    tzi.nom_zone_indicative,
    ts.nom_saison,
    ts.id_saison,
    tsec.nom_secteur,
    tsec.id_secteur,
    ttb.code_type_bracelet AS bracelet,
        CASE
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '01'::text) THEN 'Jan.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '02'::text) THEN 'Fév.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '03'::text) THEN 'Mar.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '04'::text) THEN 'Avr.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '05'::text) THEN 'Mai'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '06'::text) THEN 'Juin'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '07'::text) THEN 'Juil.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '08'::text) THEN 'Aou.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '09'::text) THEN 'Sep.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '10'::text) THEN 'Oct.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '11'::text) THEN 'Nov.'::text
            WHEN (to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text) = '12'::text) THEN 'Déc.'::text
            ELSE to_char((tr.date_exacte)::timestamp with time zone, 'MM'::text)
        END AS mois_txt,
        CASE
            WHEN (date_part('month'::text, tr.date_exacte) < (6)::double precision) THEN (date_part('month'::text, tr.date_exacte) + (12)::double precision)
            ELSE date_part('month'::text, tr.date_exacte)
        END AS mois_txt_sort
   FROM ((((((((((oeasc_chasse.t_realisations tr
     LEFT JOIN ref_nomenclatures.t_nomenclatures tnmc ON ((tnmc.id_nomenclature = tr.id_nomenclature_mode_chasse)))
     LEFT JOIN ref_nomenclatures.t_nomenclatures tns ON ((tns.id_nomenclature = tr.id_nomenclature_sexe)))
     LEFT JOIN ref_nomenclatures.t_nomenclatures tnca ON ((tnca.id_nomenclature = tr.id_nomenclature_classe_age)))
     JOIN oeasc_chasse.t_attributions ta ON ((ta.id_attribution = tr.id_attribution)))
     JOIN oeasc_chasse.t_saisons ts ON ((ts.id_saison = ta.id_saison)))
     JOIN oeasc_chasse.t_type_bracelets ttb ON ((ttb.id_type_bracelet = ta.id_type_bracelet)))
     JOIN oeasc_commons.t_especes te ON ((te.id_espece = ttb.id_espece)))
     JOIN oeasc_chasse.t_zone_cynegetiques tzc ON ((tzc.id_zone_cynegetique = COALESCE(tr.id_zone_cynegetique_realisee, ta.id_zone_cynegetique_affectee))))
     LEFT JOIN oeasc_chasse.t_zone_indicatives tzi ON ((tzi.id_zone_indicative = COALESCE(tr.id_zone_indicative_realisee, ta.id_zone_indicative_affectee))))
     JOIN oeasc_commons.t_secteurs tsec ON ((tsec.id_secteur = tzc.id_secteur)));

CREATE OR REPLACE VIEW oeasc_chasse.v_plan_chasse_realisation_bilan AS
WITH d AS (
         SELECT ta.id_saison,
            ttb.id_espece,
            tr.id_zone_cynegetique_realisee,
            tr.id_zone_indicative_realisee,
            tr.id_realisation,
            tr.date_exacte
           FROM ((oeasc_chasse.t_realisations tr
             JOIN oeasc_chasse.t_attributions ta ON ((ta.id_attribution = tr.id_attribution)))
             JOIN oeasc_chasse.t_type_bracelets ttb ON ((ttb.id_type_bracelet = ta.id_type_bracelet)))
        )
 SELECT tbch.id_saison,
    tbch.id_espece,
    tbch.id_zone_indicative,
    tzi.id_zone_cynegetique,
    tzc.id_secteur,
    0 AS nb_affecte_min,
    tbch.nb_affecte_max,
    tbch.nb_realise AS nb_realisation,
    tbch.nb_realise_avant_11 AS nb_realisation_avant_11
   FROM ((oeasc_chasse.t_bilan_chasse_historique tbch
     JOIN oeasc_chasse.t_zone_indicatives tzi ON ((tzi.id_zone_indicative = tbch.id_zone_indicative)))
     JOIN oeasc_chasse.t_zone_cynegetiques tzc ON ((tzc.id_zone_cynegetique = tzi.id_zone_cynegetique)))
UNION
 SELECT ta.id_saison,
    ttb.id_espece,
    ta.id_zone_indicative_affectee AS id_zone_indicative,
    ta.id_zone_cynegetique_affectee AS id_zone_cynegetique,
    tzc.id_secteur,
    0 AS nb_affecte_min,
    count(DISTINCT ta.id_attribution) AS nb_affecte_max,
    count(DISTINCT tr.id_realisation) FILTER (WHERE (tr.id_realisation IS NOT NULL)) AS nb_realisation,
    count(DISTINCT tr.id_realisation) FILTER (WHERE ((tr.id_realisation IS NOT NULL) AND (tr.date_exacte IS NOT NULL) AND (tr.date_exacte <= (concat(split_part((ts.nom_saison)::text, '-'::text, 1), '-10-31'))::date))) AS nb_realisation_avant_11
   FROM ((((oeasc_chasse.t_attributions ta
     JOIN oeasc_chasse.t_saisons ts ON ((ts.id_saison = ta.id_saison)))
     JOIN oeasc_chasse.t_type_bracelets ttb ON ((ttb.id_type_bracelet = ta.id_type_bracelet)))
     JOIN oeasc_chasse.t_zone_cynegetiques tzc ON ((tzc.id_zone_cynegetique = ta.id_zone_cynegetique_affectee)))
     LEFT JOIN d tr ON (((tr.id_saison = ta.id_saison) AND (tr.id_espece = ttb.id_espece) AND (tr.id_zone_cynegetique_realisee = ta.id_zone_cynegetique_affectee) AND (tr.id_zone_indicative_realisee = ta.id_zone_indicative_affectee))))
  GROUP BY ta.id_saison, ttb.id_espece, ta.id_zone_indicative_affectee, ta.id_zone_cynegetique_affectee, tzc.id_secteur;

CREATE OR REPLACE VIEW oeasc_chasse.v_pre_bilan_histo AS
WITH affectations AS (
         SELECT tam_1.id_saison,
            tam_1.id_espece,
            tzc.id_secteur,
            tzc.id_zone_cynegetique,
            sum(tam_1.nb_affecte_min) OVER (PARTITION BY tam_1.id_saison, tam_1.id_espece) AS nb_attribution_min_espece,
            sum(tam_1.nb_affecte_max) OVER (PARTITION BY tam_1.id_saison, tam_1.id_espece) AS nb_attribution_max_espece,
            sum(tam_1.nb_affecte_min) OVER (PARTITION BY tam_1.id_saison, tam_1.id_espece, tzc.id_secteur) AS nb_attribution_min_secteur,
            sum(tam_1.nb_affecte_max) OVER (PARTITION BY tam_1.id_saison, tam_1.id_espece, tzc.id_secteur) AS nb_attribution_max_secteur,
            tam_1.nb_affecte_min AS nb_attribution_min_zc,
            tam_1.nb_affecte_max AS nb_attribution_max_zc
           FROM (oeasc_chasse.t_attribution_massifs tam_1
             JOIN oeasc_chasse.t_zone_cynegetiques tzc ON ((tzc.id_zone_cynegetique = tam_1.id_zone_cynegetique)))
        )
 SELECT tam.id_saison,
    tam.id_espece,
    tam.id_secteur,
    tzi.id_zone_cynegetique,
    tzi.id_zone_indicative,
    tam.nb_attribution_min_espece,
    tam.nb_attribution_max_espece,
    sum(tbch.nb_realise) OVER (PARTITION BY tam.id_saison, tam.id_espece) AS nb_realisation_espece,
    sum(tbch.nb_realise_avant_11) OVER (PARTITION BY tam.id_saison, tam.id_espece) AS nb_realisation_avant_11_espece,
    tam.nb_attribution_min_secteur,
    tam.nb_attribution_max_secteur,
    sum(tbch.nb_realise) OVER (PARTITION BY tam.id_saison, tam.id_espece, tam.id_secteur) AS nb_realisation_secteur,
    sum(tbch.nb_realise_avant_11) OVER (PARTITION BY tam.id_saison, tam.id_espece, tam.id_secteur) AS nb_realisation_avant_11_secteur,
    tam.nb_attribution_min_zc,
    tam.nb_attribution_max_zc,
    sum(tbch.nb_realise) OVER (PARTITION BY tam.id_saison, tam.id_espece, tzi.id_zone_cynegetique) AS nb_realisation_zc,
    sum(tbch.nb_realise_avant_11) OVER (PARTITION BY tam.id_saison, tam.id_espece, tzi.id_zone_cynegetique) AS nb_realisation_avant_11_zc,
    0 AS nb_attribution_min_zi,
    tbch.nb_affecte_max AS nb_attribution_max_zi,
    tbch.nb_realise AS nb_realisation_zi,
    tbch.nb_realise_avant_11 AS nb_realisation_avant_11_zi
   FROM ((oeasc_chasse.t_bilan_chasse_historique tbch
     JOIN oeasc_chasse.t_zone_indicatives tzi ON ((tzi.id_zone_indicative = tbch.id_zone_indicative)))
     JOIN affectations tam ON (((tam.id_espece = tbch.id_espece) AND (tam.id_zone_cynegetique = tzi.id_zone_cynegetique) AND (tam.id_saison = tbch.id_saison))));

CREATE OR REPLACE VIEW oeasc_chasse.v_pre_bilan_saisie AS
WITH realisations AS (
         SELECT ta.id_saison,
            ttb.id_espece,
            ta.id_zone_cynegetique_affectee AS id_zone_cynegetique,
            ta.id_zone_indicative_affectee AS id_zone_indicative,
            count(DISTINCT ta.id_attribution) AS nb_attribution_zi,
            count(*) FILTER (WHERE (tr.id_realisation IS NOT NULL)) AS nb_realise,
            count(*) FILTER (WHERE ((tr.id_realisation IS NOT NULL) AND (tr.date_exacte IS NOT NULL) AND (tr.date_exacte <= (concat(split_part((ts.nom_saison)::text, '-'::text, 1), '-10-31'))::date))) AS nb_realise_avant_11
           FROM (((oeasc_chasse.t_attributions ta
             LEFT JOIN oeasc_chasse.t_realisations tr ON ((ta.id_attribution = tr.id_attribution)))
             JOIN oeasc_chasse.t_saisons ts ON ((ts.id_saison = ta.id_saison)))
             JOIN oeasc_chasse.t_type_bracelets ttb ON ((ttb.id_type_bracelet = ta.id_type_bracelet)))
          GROUP BY ta.id_saison, ttb.id_espece, ta.id_zone_indicative_affectee, ta.id_zone_cynegetique_affectee
        ), affectations AS (
         SELECT tam.id_saison,
            tam.id_espece,
            tzc.id_secteur,
            tzc.id_zone_cynegetique,
            sum(tam.nb_affecte_min) OVER (PARTITION BY tam.id_saison, tam.id_espece) AS nb_attribution_min_espece,
            sum(tam.nb_affecte_max) OVER (PARTITION BY tam.id_saison, tam.id_espece) AS nb_attribution_max_espece,
            sum(tam.nb_affecte_min) OVER (PARTITION BY tam.id_saison, tam.id_espece, tzc.id_secteur) AS nb_attribution_min_secteur,
            sum(tam.nb_affecte_max) OVER (PARTITION BY tam.id_saison, tam.id_espece, tzc.id_secteur) AS nb_attribution_max_secteur,
            tam.nb_affecte_min AS nb_attribution_min_zc,
            tam.nb_affecte_max AS nb_attribution_max_zc
           FROM (oeasc_chasse.t_attribution_massifs tam
             JOIN oeasc_chasse.t_zone_cynegetiques tzc ON ((tzc.id_zone_cynegetique = tam.id_zone_cynegetique)))
        )
 SELECT a.id_saison,
    a.id_espece,
    a.id_secteur,
    a.id_zone_cynegetique,
    r.id_zone_indicative,
    a.nb_attribution_min_espece,
    a.nb_attribution_max_espece,
    sum(r.nb_realise) OVER (PARTITION BY a.id_saison, a.id_espece) AS nb_realisation_espece,
    sum(r.nb_realise_avant_11) OVER (PARTITION BY a.id_saison, a.id_espece) AS nb_realisation_avant_11_espece,
    a.nb_attribution_min_secteur,
    a.nb_attribution_max_secteur,
    sum(r.nb_realise) OVER (PARTITION BY a.id_saison, a.id_espece, a.id_secteur) AS nb_realisation_secteur,
    sum(r.nb_realise_avant_11) OVER (PARTITION BY a.id_saison, a.id_espece, a.id_secteur) AS nb_realisation_avant_11_secteur,
    a.nb_attribution_min_zc,
    a.nb_attribution_max_zc,
    sum(r.nb_realise) OVER (PARTITION BY a.id_saison, a.id_espece, a.id_zone_cynegetique) AS nb_realisation_zc,
    sum(r.nb_realise_avant_11) OVER (PARTITION BY a.id_saison, a.id_espece, a.id_zone_cynegetique) AS nb_realisation_avant_11_zc,
    0 AS nb_attribution_min_zi,
    r.nb_attribution_zi AS nb_attribution_max_zi,
    r.nb_realise AS nb_realisation_zi,
    r.nb_realise_avant_11 AS nb_realisation_avant_11_zi
   FROM (realisations r
     JOIN affectations a ON (((r.id_zone_cynegetique = a.id_zone_cynegetique) AND (r.id_espece = a.id_espece) AND (r.id_saison = a.id_saison))));

CREATE OR REPLACE VIEW oeasc_chasse.v_pre_bilan AS
SELECT v_pre_bilan_histo.id_saison,
    v_pre_bilan_histo.id_espece,
    v_pre_bilan_histo.id_secteur,
    v_pre_bilan_histo.id_zone_cynegetique,
    v_pre_bilan_histo.id_zone_indicative,
    v_pre_bilan_histo.nb_attribution_min_espece,
    v_pre_bilan_histo.nb_attribution_max_espece,
    v_pre_bilan_histo.nb_realisation_espece,
    v_pre_bilan_histo.nb_realisation_avant_11_espece,
    v_pre_bilan_histo.nb_attribution_min_secteur,
    v_pre_bilan_histo.nb_attribution_max_secteur,
    v_pre_bilan_histo.nb_realisation_secteur,
    v_pre_bilan_histo.nb_realisation_avant_11_secteur,
    v_pre_bilan_histo.nb_attribution_min_zc,
    v_pre_bilan_histo.nb_attribution_max_zc,
    v_pre_bilan_histo.nb_realisation_zc,
    v_pre_bilan_histo.nb_realisation_avant_11_zc,
    v_pre_bilan_histo.nb_attribution_min_zi,
    v_pre_bilan_histo.nb_attribution_max_zi,
    v_pre_bilan_histo.nb_realisation_zi,
    v_pre_bilan_histo.nb_realisation_avant_11_zi
   FROM oeasc_chasse.v_pre_bilan_histo
UNION
 SELECT v_pre_bilan_saisie.id_saison,
    v_pre_bilan_saisie.id_espece,
    v_pre_bilan_saisie.id_secteur,
    v_pre_bilan_saisie.id_zone_cynegetique,
    v_pre_bilan_saisie.id_zone_indicative,
    v_pre_bilan_saisie.nb_attribution_min_espece,
    v_pre_bilan_saisie.nb_attribution_max_espece,
    v_pre_bilan_saisie.nb_realisation_espece,
    v_pre_bilan_saisie.nb_realisation_avant_11_espece,
    v_pre_bilan_saisie.nb_attribution_min_secteur,
    v_pre_bilan_saisie.nb_attribution_max_secteur,
    v_pre_bilan_saisie.nb_realisation_secteur,
    v_pre_bilan_saisie.nb_realisation_avant_11_secteur,
    v_pre_bilan_saisie.nb_attribution_min_zc,
    v_pre_bilan_saisie.nb_attribution_max_zc,
    v_pre_bilan_saisie.nb_realisation_zc,
    v_pre_bilan_saisie.nb_realisation_avant_11_zc,
    v_pre_bilan_saisie.nb_attribution_min_zi,
    v_pre_bilan_saisie.nb_attribution_max_zi,
    v_pre_bilan_saisie.nb_realisation_zi,
    v_pre_bilan_saisie.nb_realisation_avant_11_zi
   FROM oeasc_chasse.v_pre_bilan_saisie;

CREATE OR REPLACE VIEW oeasc_chasse.v_pre_bilan_pretty AS
SELECT vb.id_saison,
    ts.nom_saison,
    vb.id_espece,
    te.nom_espece,
    te.code_espece,
    vb.id_secteur,
    tsec.nom_secteur,
    tsec.code_secteur,
    vb.id_zone_cynegetique,
    tzc.nom_zone_cynegetique,
    tzc.code_zone_cynegetique,
    vb.id_zone_indicative,
    tzi.nom_zone_indicative,
    tzi.code_zone_indicative,
    vb.nb_attribution_min_espece,
    vb.nb_attribution_max_espece,
    vb.nb_realisation_espece,
    vb.nb_realisation_avant_11_espece,
    vb.nb_attribution_min_secteur,
    vb.nb_attribution_max_secteur,
    vb.nb_realisation_secteur,
    vb.nb_realisation_avant_11_secteur,
    vb.nb_attribution_min_zi,
    vb.nb_attribution_max_zi,
    vb.nb_realisation_zi,
    vb.nb_realisation_avant_11_zi,
    vb.nb_attribution_min_zc,
    vb.nb_attribution_max_zc,
    vb.nb_realisation_zc,
    vb.nb_realisation_avant_11_zc
   FROM (((((oeasc_chasse.v_pre_bilan vb
     JOIN oeasc_chasse.t_saisons ts ON ((ts.id_saison = vb.id_saison)))
     JOIN oeasc_chasse.t_zone_cynegetiques tzc ON ((tzc.id_zone_cynegetique = vb.id_zone_cynegetique)))
     JOIN oeasc_chasse.t_zone_indicatives tzi ON ((tzi.id_zone_indicative = vb.id_zone_indicative)))
     JOIN oeasc_commons.t_secteurs tsec ON ((tsec.id_secteur = vb.id_secteur)))
     JOIN oeasc_commons.t_especes te ON ((te.id_espece = vb.id_espece)));

DROP TRIGGER IF EXISTS tri_calculate_realisation_categorie_t_realisations ON oeasc_chasse.t_realisations;
CREATE TRIGGER tri_calculate_realisation_categorie_t_realisations BEFORE INSERT OR UPDATE ON oeasc_chasse.t_realisations FOR EACH ROW EXECUTE FUNCTION oeasc_chasse.fct_trg_calculate_realisation_categorie();

DROP TRIGGER IF EXISTS tri_meta_dates_change_t_attributions ON oeasc_chasse.t_attributions;
CREATE TRIGGER tri_meta_dates_change_t_attributions BEFORE INSERT OR UPDATE ON oeasc_chasse.t_attributions FOR EACH ROW EXECUTE FUNCTION fct_trg_meta_dates_change();

DROP TRIGGER IF EXISTS tri_meta_dates_change_t_realisations ON oeasc_chasse.t_realisations;
CREATE TRIGGER tri_meta_dates_change_t_realisations BEFORE INSERT OR UPDATE ON oeasc_chasse.t_realisations FOR EACH ROW EXECUTE FUNCTION fct_trg_meta_dates_change();
