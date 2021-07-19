	 CREATE EXTENSION if not exists plr;
	
	drop function if exists oeasc_chasse.get_day_of_year(in date_exacte date,in MD_ref character varying);
	create or replace function oeasc_chasse.get_day_of_year(in date_exacte date,in MD_ref character varying)
	RETURNS INTEGER AS
	$BODY$
	DECLARE 
		day_of_year INTEGER;
		ref_date DATE;
		ref_date_minus_one DATE;
	begin
	select into ref_date (to_char(date_exacte, 'YYYY')::int || '-' || MD_ref)::date;
	select into ref_date_minus_one (to_char(date_exacte, 'YYYY')::int - 1 || '-' || MD_ref)::date;
	SELECT INTO day_of_year 
	case when date_exacte < ref_date
	then to_char(date_exacte, 'J')::int - to_char(ref_date_minus_one, 'J')::int
	else to_char(date_exacte, 'J')::int - to_char(ref_date, 'J')::int
	end;
	RETURN day_of_year;
	END;
	$BODY$
	LANGUAGE plpgsql IMMUTABLE
	COST 100;
	
	drop function if exists oeasc_chasse.get_poid_vide(in id_espece_in integer,in poids_entier_in integer, in poids_vide_in integer, in poids_c_f_p_in integer);
	create or replace function oeasc_chasse.get_poid_vide(in id_espece_in integer,in poids_entier_in integer, in poids_vide_in integer, in poids_c_f_p_in integer)
	RETURNS INTEGER as
	$BODY$
	DECLARE 
		poids_vide_out INTEGER;
		CODE_ESPECE varchar;
		pe_exp float;
		pe_puis float;
		pcfp_exp FLOAT;
		pcfp_puis FLOAT;
	BEGIN 
		select into code_espece te.code_espece from oeasc_commons.t_especes te where te.id_espece = id_espece_in;
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
	SELECT INTO poids_vide_out
		CASE
			WHEN NOT poids_vide_in IS NULL THEN poids_vide_in
			WHEN NOT poids_entier_in IS NULL THEN exp(pe_exp)*poids_entier_in^pe_puis
			WHEN NOT poids_c_f_p_in IS NULL THEN  exp(pcfp_exp)*poids_c_f_p_in^pcfp_puis
			END as pv;
	RETURN poids_vide_out;
	END;
	$BODY$
	LANGUAGE plpgsql IMMUTABLE
	COST 100;
		
	drop function if exists r_lm_slope(float[], float[]);
	CREATE OR REPLACE FUNCTION r_lm_slope(float[], float[])
	RETURNS float[] as
	$BODY$
	    res <- lm(arg1 ~ arg2)
	    summary(res)
	    coefs <- res$coefficients
	    r <- summary(res)$r.squared
	    outa <- array(0, 5)
	    outa[1] <- res$coefficients[1]
	    outa[2] <- res$coefficients[2]
	    outa[3] <- summary(res)$coefficients[1,4]
	    outa[4] <- summary(res)$coefficients[2,4]
	    outa[5] <- summary(res)$r.squared	
	    return (outa)
	$BODY$ 
	LANGUAGE plr;	

	drop function if exists tinv(in p_value_in float, in df_in integer);
	CREATE OR REPLACE FUNCTION tinv(in p_value_in float, in df_in integer)
	 RETURNS float
	AS $$	
	    return (abs(qt(p_value_in, df=df_in)))
	$$
    LANGUAGE plr
	;	

	select tinv(0.05, 10)
	
--CREATE OR REPLACE FUNCTION import_chasse.fct_calcul_ice_mc(isp character varying)
-- RETURNS TABLE(nom_saison character varying, massif_aggrege character varying, pmc double precision, lim_sup double precision, lim_inf double precision, nb_d integer)	with 
		-- input : pour la fonction
		input as (
			select 
				1 as id_espece,
				1 as id_zone_cynegetique
		)
		-- 1 ere extraction (date + poids)
		, pre_data_1 as (
			select
				date_exacte,
				poid_entier,  poid_vide, poid_c_f_p,
				id_espece, id_zone_cynegetique_realisee,
				oeasc_chasse.get_day_of_year(date_exacte, '06-01') as doy,
				oeasc_chasse.get_poid_vide(id_espece, poid_entier, poid_vide, poid_c_f_p) as pv,
				ts.nom_saison
			from oeasc_chasse.t_realisations tr
			join oeasc_chasse.t_attributions ta on ta.id_attribution = tr.id_attribution 
			join oeasc_chasse.t_saisons ts on ts.id_saison = ta.id_saison 
			join oeasc_chasse.t_type_bracelets ttb on ta.id_type_bracelet = ttb.id_type_bracelet
			join ref_nomenclatures.t_nomenclatures tn on tn.id_nomenclature = id_nomenclature_classe_age 
			where 
				date_exacte is not null
				and coalesce(poid_entier,  poid_vide, poid_c_f_p) is not null
				and tn.cd_nomenclature = '3' -- juvenile
		)
		-- minimum des dates de chasse (apres le 06-01) tout confondu (pour rapporter à cette date)
		, min_doy as (
	    	select 
	    		min(doy) as min_doy
	    	from pre_data_1
		)
		-- x (date rapportée), y (poid vide), pour une espece et un massif
		-- ajouter autres input ??? (age, sexe) ???
		, pre_data_2 as (
			select
				date_exacte, 
				nom_saison,
				doy - md.min_doy + 1 as x,
				pv as y
			from input as i
			join min_doy as md on true 
			join pre_data_1 as pd1 on pd1.id_espece = i.id_espece and pd1.id_zone_cynegetique_realisee = i.id_zone_cynegetique
		)
		-- mediane des jours de chasse
		, median as (
			select 
				percentile_disc(0.5) within group (order by x) as median
			from pre_data_2
		)
		-- regression linéaire
		, regr as (
			select
				lm[1] as y_intersect,
				lm[2] as slope,
				lm[3] as p_value_intersect,
				lm[4] as p_value_slope,
				lm[5] as r2
				from (
					select r_lm_slope(array_agg(y::float), array_agg(x::float))as lm
			from pre_data_2 pd2)a
		)
		-- poid rapporté au jour médian
		, p_corr as (
			select
				nom_saison,
				(pd2.x - m.median) * r.slope + y as y_corr
			from pre_data_2 pd2, median m, regr r
		)
		-- poid moyen par saison
		, p_moy as (
			select
				nom_saison,
				y_corr,
				avg(y_corr) over (partition by nom_saison) as y_moy
			from p_corr
		)
		, erreurs as (
			select 
				nom_saison,
				y_moy,
				sqrt(
					sum( (y_corr - y_moy)^2 ) / ( (count(*) -1) * count(*) )
				)  as err,
				count(*) as nb
			from p_moy
			group by nom_saison, y_moy
		)
		-- intervalle de confiance
		, interval as (
			select
				*,
				y_moy - err * tinv(0.05,  (nb -1)::int) as lim_inf,
				y_moy + err * tinv(0.05,  (nb -1)::int) as lim_sup
			from erreurs e
			order by nom_saison
		)
		-- regression
		, regr2 as (
			select
				lm[1] as y_intersect,
				lm[2] as slope,
				lm[3] as p_value_intersect,
				lm[4] as p_value_slope,
				lm[5] as r2
				from (
					select r_lm_slope(array_agg(y_moy::float), array_agg(split_part(nom_saison, '-', 1)::float - 2013))as lm
					from interval
				)a
		)
		select
			p.nom_saison,
			x,
			y,
			y_moy,
			lim_inf,
			lim_sup,
			regr.p_value_slope as pval1,
			regr.slope as slope1,
			regr2.p_value_slope as pval2,
			regr2.slope as slope2
		from regr, regr2, interval i 
		join pre_data_2 p on p.nom_saison = i.nom_saison