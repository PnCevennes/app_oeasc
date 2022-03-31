--
-- fonctions et vues pour les rendus génériques
--
-- TODO
--  - à déplacer dans un cadre plus général
--  - à commenter quand le code est arrêté
--

--
-- vue pour les rendus génériques chasse
--
-- TODO
--  - compléter les champs quand le chaînage est ok
--
	DROP VIEW IF EXISTS oeasc_chasse.v_custom_results;
	CREATE OR REPLACE VIEW oeasc_chasse.v_custom_results AS
	SELECT
		id_nomenclature_mode_chasse,
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
			WHEN to_char(tr.date_exacte, 'MM')::text = '01' THEN 'Jan.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '02' THEN 'Fev.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '03' THEN 'Mar.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '04' THEN 'Avr.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '05' THEN 'Mai'
			WHEN to_char(tr.date_exacte, 'MM')::text = '06' THEN 'Juin'
			WHEN to_char(tr.date_exacte, 'MM')::text = '07' THEN 'Juil.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '08' THEN 'Aou.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '09' THEN 'Sep.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '10' THEN 'Oct.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '11' THEN 'Nov.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '12' THEN 'Déc.'
			ELSE to_char(tr.date_exacte, 'MM')::text
		END AS mois_txt,
		CASE
			WHEN date_part('month', tr.date_exacte) < 6 THEN date_part('month', tr.date_exacte) + 12
			ELSE date_part('month', tr.date_exacte)
		END AS mois_txt_sort

		FROM oeasc_chasse.t_realisations tr
		LEFT JOIN ref_nomenclatures.t_nomenclatures tnmc ON tnmc.id_nomenclature = id_nomenclature_mode_chasse
		LEFT JOIN ref_nomenclatures.t_nomenclatures tns ON tns.id_nomenclature = id_nomenclature_sexe
		LEFT JOIN ref_nomenclatures.t_nomenclatures tnca ON tnca.id_nomenclature = id_nomenclature_classe_age
		JOIN oeasc_chasse.t_attributions ta ON ta.id_attribution = tr.id_attribution
		JOIN oeasc_chasse.t_saisons ts ON ts.id_saison = ta.id_saison
		JOIN oeasc_chasse.t_type_bracelets ttb ON ttb.id_type_bracelet = ta.id_type_bracelet
		JOIN oeasc_commons.t_especes te  ON te.id_espece = ttb.id_espece
		JOIN oeasc_chasse.t_zone_cynegetiques tzc ON tzc.id_zone_cynegetique = ta.id_zone_cynegetique_affectee
		JOIN oeasc_chasse.t_zone_indicatives tzi ON tzi.id_zone_indicative = ta.id_zone_indicative_affectee
		JOIN oeasc_commons.t_secteurs tsec ON tsec.id_secteur = tzc.id_secteur
	;



	DROP VIEW IF EXISTS oeasc_chasse.v_custom_result_attribution;
	CREATE OR REPLACE VIEW oeasc_chasse.v_custom_result_attribution AS
	SELECT
		-- id_nomenclature_mode_chasse,
		-- tnmc.label_fr AS label_mode_chasse,
		-- tns.label_fr AS label_sexe,
		-- tnca.label_fr AS label_classe_age,
		ta.id_attribution,
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
			WHEN to_char(tr.date_exacte, 'MM')::text = '01' THEN 'Jan.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '02' THEN 'Fev.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '03' THEN 'Mar.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '04' THEN 'Avr.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '05' THEN 'Mai'
			WHEN to_char(tr.date_exacte, 'MM')::text = '06' THEN 'Juin'
			WHEN to_char(tr.date_exacte, 'MM')::text = '07' THEN 'Juil.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '08' THEN 'Aou.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '09' THEN 'Sep.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '10' THEN 'Oct.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '11' THEN 'Nov.'
			WHEN to_char(tr.date_exacte, 'MM')::text = '12' THEN 'Déc.'
			ELSE to_char(tr.date_exacte, 'MM')::text
		END AS mois_txt,
		CASE
			WHEN date_part('month', tr.date_exacte) < 6 THEN date_part('month', tr.date_exacte) + 12
			ELSE date_part('month', tr.date_exacte)
		END AS mois_txt_sort
		FROM oeasc_chasse.t_attributions ta
		-- LEFT JOIN ref_nomenclatures.t_nomenclatures tnmc ON tnmc.id_nomenclature = id_nomenclature_mode_chasse
		-- LEFT JOIN ref_nomenclatures.t_nomenclatures tns ON tns.id_nomenclature = id_nomenclature_sexe
		-- LEFT JOIN ref_nomenclatures.t_nomenclatures tnca ON tnca.id_nomenclature = id_nomenclature_classe_age
		LEFT JOIN oeasc_chasse.t_realisations tr ON ta.id_attribution = tr.id_attribution
		JOIN oeasc_chasse.t_saisons ts ON ts.id_saison = ta.id_saison
		JOIN oeasc_chasse.t_type_bracelets ttb ON ttb.id_type_bracelet = ta.id_type_bracelet
		JOIN oeasc_commons.t_especes te  ON te.id_espece = ttb.id_espece
		LEFT JOIN oeasc_chasse.t_zone_cynegetiques tzc ON tzc.id_zone_cynegetique = ta.id_zone_cynegetique_affectee
		LEFT JOIN oeasc_chasse.t_zone_indicatives tzi ON tzi.id_zone_indicative = ta.id_zone_indicative_affectee
		LEFT JOIN oeasc_commons.t_secteurs tsec ON tsec.id_secteur = tzc.id_secteur
	;


