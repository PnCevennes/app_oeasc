-- ICE

CREATE EXTENSION IF NOT EXISTS plr;

-- fonction qui renvoie le jour dans l'année, modulo une date pivot (mois -jour : 'MM-DD')
DROP FUNCTION IF EXISTS oeasc_chasse.fct_day_of_year(IN date_exacte DATE, IN MD_ref CHARACTER VARYING);
CREATE OR REPLACE FUNCTION oeasc_chasse.fct_day_of_year(IN date_exacte DATE, IN MD_ref CHARACTER VARYING)
	RETURNS INTEGER AS
	$BODY$
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
	$BODY$
	LANGUAGE plpgsql IMMUTABLE
	COST 100;

-- function qui calcule le poid vide en fonction des valeurs de (poid_entier, poid_vide, poid_c_f_p)
DROP FUNCTION IF EXISTS oeasc_chasse.fct_poid_vide(IN id_espece_in INTEGER, IN poids_entier_in FLOAT, IN poids_vide_in FLOAT, IN poids_c_f_p_in FLOAT);
CREATE OR REPLACE FUNCTION oeasc_chasse.fct_poid_vide(IN id_espece_in INTEGER, IN poids_entier_in FLOAT, IN poids_vide_in FLOAT, IN poids_c_f_p_in FLOAT)
	RETURNS INTEGER AS
	$BODY$
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
	$BODY$
	LANGUAGE plpgsql IMMUTABLE
	COST 100;

-- fonction qui calcule les paramètre de regression lineaire avec R
-- r_lm_slope_a(y, x)
-- out : array :
--  - 1: intercept
-- 	- 2: slope
--  - 3: p_value_intercept
--  - 4: p_value_slope
--  - 5: r2
DROP FUNCTION IF EXISTS r_lm_slope_a(FLOAT[], FLOAT[]);
CREATE OR REPLACE FUNCTION r_lm_slope_a(FLOAT[], FLOAT[])
	RETURNS FLOAT[] AS
	$BODY$
	    res <- lm(arg1 ~ arg2)
	    summary(res)
	    coefs <- res$coefficients
	    r <- summary(res)$r.squared
	    outa <- array(0, 5)
	    outa[1] <- res$coefficients[1]
	    outa[2] <- res$coefficients[2]
	    outa[3] <- summary(res)$coefficients[1, 4]
	    outa[4] <- summary(res)$coefficients[2, 4]
	    outa[5] <- summary(res)$r.squared
	    return (outa)
	$BODY$
	LANGUAGE plr;

-- regression lineaire avec sortie sous forme de table
DROP FUNCTION IF EXISTS r_lm_slope_t(FLOAT[], FLOAT[]);
CREATE OR REPLACE FUNCTION r_lm_slope_t(y_in FLOAT[], x_in FLOAT[])
	RETURNS TABLE(
		intercept FLOAT,
		slope FLOAT,
		p_value_intercept FLOAT,
		p_value_slope FLOAT,
		r2 FLOAT,
		x FLOAT[],
		y FLOAT[],
		nb INTEGER
	) AS
	$BODY$
		DECLARE
			lm_res FLOAT[];
		BEGIN
			SELECT INTO lm_res r_lm_slope_a(y_in, x_in);
			RETURN QUERY
				SELECT
					lm_res[1] AS intercept,
					lm_res[2] AS slope,
					lm_res[3] AS p_value_interept,
					lm_res[4] AS p_value_slope,
					lm_res[5] AS r2,
					x_in,
					y_in,
					array_length(x, 1) AS nb;
		END;
	$BODY$
	LANGUAGE plpgsql;

-- regression lineaire avec sortie sous forme de jsonb
DROP FUNCTION IF EXISTS r_lm_slope_j(FLOAT[], FLOAT[]);
CREATE OR REPLACE FUNCTION r_lm_slope_j(y FLOAT[], x FLOAT[])
	RETURNS JSONB AS
	$BODY$
		BEGIN
			RETURN row_to_json(lm) FROM r_lm_slope_t(y, x) lm;
		END
	$BODY$
	LANGUAGE plpgsql;



-- Distribution de student inverse( intervalle, ddl)
DROP FUNCTION IF EXISTS tinv(IN p_value_in FLOAT, IN df_in INTEGER);
CREATE OR REPLACE FUNCTION tinv(IN p_value_in FLOAT, IN df_in INTEGER)
	 RETURNS FLOAT AS
	 $BODY$
	    return (abs(qt(p_value_in, df = df_in)));
	$BODY$
    LANGUAGE plr;

-- Calcul ice
DROP FUNCTION IF EXISTS oeasc_chasse.fct_calcul_ice_mc(id_espece_in INTEGER, ids_zone_indicative_in INTEGER[], ids_zone_cynegetique_in INTEGER[], ids_secteur_in INTEGER[]);
CREATE OR REPLACE FUNCTION oeasc_chasse.fct_calcul_ice_mc(id_espece_in INTEGER, ids_zone_indicative_in INTEGER[], ids_zone_cynegetique_in INTEGER[], ids_secteur_in INTEGER[])
		RETURNS JSONB AS
		$BODY$
		DECLARE
			j_out JSONB;
		BEGIN
			RAISE NOTICE 'calcul ice pour id_espece % ids_zone_indicative %d ids_zone_cynegetique % ids_secteur %', id_espece_in, ids_zone_indicative_in, ids_zone_cynegetique_in, ids_secteur_in;
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
					ta.id_saison
				FROM oeasc_chasse.t_realisations tr
				JOIN oeasc_chasse.t_attributions ta ON ta.id_attribution = tr.id_attribution
				JOIN oeasc_chasse.t_saisons ts ON ts.id_saison = ta.id_saison
				JOIN oeasc_chasse.t_type_bracelets ttb ON ta.id_type_bracelet = ttb.id_type_bracelet
				JOIN ref_nomenclatures.t_nomenclatures tn ON tn.id_nomenclature = id_nomenclature_classe_age
				JOIN oeasc_chasse.t_zone_cynegetiques tzc ON tzc.id_zone_cynegetique = tr.id_zone_cynegetique_realisee
				WHERE
					date_exacte IS NOT NULL
					AND COALESCE(poid_entier, poid_vide, poid_c_f_p) IS NOT NULL
					AND tn.cd_nomenclature = '3' -- juvenile
				ORDER BY nom_saison
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
						AND (
							array_length(ids_zone_indicative_in, 1) IS NULL
							OR
							p1.id_zone_indicative_realisee =  ANY(ids_zone_indicative_in)
						)
						AND (
							array_length(ids_zone_cynegetique_in, 1) IS NULL
							OR
							p1.id_zone_cynegetique_realisee =  ANY(ids_zone_cynegetique_in)
						)
						AND (
							array_length(ids_secteur_in, 1) IS NULL
							OR
							p1.id_secteur = ANY(ids_secteur_in)
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
						(
							SELECT STRING_AGG(nom_zone_cynegetique, ', ' ORDER BY nom_zone_cynegetique)
								FROM oeasc_chasse.t_zone_cynegetiques tzc
								WHERE tzc.id_zone_cynegetique = ANY(ids_zone_cynegetique_in)
						) as  nom_zone_cynegetique,
						(
							SELECT STRING_AGG(nom_zone_indicative, ', ' ORDER BY nom_zone_indicative)
								FROM oeasc_chasse.t_zone_indicatives tzi
								WHERE tzi.id_zone_indicative = ANY(ids_zone_indicative_in)
						) as  nom_zone_indicative,
						(
							SELECT STRING_AGG(nom_secteur, ', ' ORDER BY nom_secteur)
								FROM oeasc_commons.t_secteurs ts
								WHERE ts.id_secteur = ANY(ids_secteur_in)
						) as  nom_secteur,
						nom_espece
						FROM regr_1 r1, regr_2 r2
						JOIN oeasc_commons.t_especes te ON te.id_espece = id_espece_in
					)a;
			RETURN j_out;
		END;
		$BODY$
		LANGUAGE plpgsql;