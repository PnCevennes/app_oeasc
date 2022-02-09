DROP VIEW IF EXISTS oeasc_chasse.v_pre_bilan_saisie CASCADE;
CREATE VIEW oeasc_chasse.v_pre_bilan_saisie AS
WITH pre_bilan AS (
	select
	ta.id_saison,
	ttb.id_espece,
	tr.id_zone_cynegetique_realisee as id_zone_cynegetique,
	tr.id_zone_indicative_realisee as id_zone_indicative,
	tam.nb_affecte_min AS nb_attribution_min_zc,
	tam.nb_affecte_max  AS nb_attribution_max_zc,
	COUNT(*) as nb_realisation_zi,
	COUNT(*) filter (where date_exacte <= (CONCAT(SPLIT_PART(ts.nom_saison, '-', 1), '-10-31'))::date) nb_realisation_avant_11_zi
	from oeasc_chasse.t_realisations tr
	join oeasc_chasse.t_attributions ta on ta.id_attribution = tr.id_attribution
	join oeasc_chasse.t_saisons ts on ts.id_saison = ta.id_saison
	join oeasc_chasse.t_type_bracelets ttb on ttb.id_type_bracelet = ta.id_type_bracelet
	join oeasc_chasse.t_attribution_massifs tam on tam.id_saison = ta.id_saison and tam.id_espece = ttb.id_espece and tr.id_zone_cynegetique_realisee = tam.id_zone_cynegetique
	GROUP BY
		ta.id_saison,
		ttb.id_espece,
		tr.id_zone_indicative_realisee,
		tr.id_zone_cynegetique_realisee,
		nb_affecte_min,
		nb_affecte_max
),
attributions AS (
	SELECT
		ttb.id_espece,
		ta.id_saison,
		ta.id_zone_cynegetique_affectee AS id_zone_cynegetique,
		ta.id_zone_indicative_affectee AS id_zone_indicative
	FROM oeasc_chasse.t_attributions ta
	JOIN oeasc_chasse.t_type_bracelets ttb ON ttb.id_type_bracelet = ta.id_type_bracelet
), count_attribution_zi AS (
	SELECT
		COUNT(*) AS nb_attribution_zi,
		id_espece,
		id_saison,
		id_zone_indicative
		FROM attributions
		GROUP BY
			id_espece,
			id_saison,
			id_zone_indicative
)
, count_zc AS (
	SELECT
		SUM(nb_realisation_zi) AS nb_realisation_zc,
		SUM(nb_realisation_avant_11_zi) AS nb_realisation_avant_11_zc,
		nb_attribution_min_zc,
		nb_attribution_max_zc,
		id_espece,
		id_saison,
		id_zone_cynegetique
		FROM pre_bilan
		GROUP BY
			id_espece,
			id_saison,
			id_zone_cynegetique,
			nb_attribution_min_zc,
			nb_attribution_max_zc
)
, count_espece AS (
	SELECT
		SUM(nb_attribution_min_zc) AS nb_attribution_min_espece,
		SUM(nb_attribution_max_zc) AS nb_attribution_max_espece,
		SUM(nb_realisation_zc) AS nb_realisation_espece,
		SUM(nb_realisation_avant_11_zc) AS nb_realisation_avant_11_espece,
		id_espece,
		id_saison
		FROM count_zc
		GROUP BY
			id_espece,
			id_saison
)
SELECT
	pb.id_saison,
	pb.id_espece,
	ce.nb_attribution_min_espece,
	ce.nb_attribution_max_espece,
	ce.nb_realisation_espece,
	ce.nb_realisation_avant_11_espece,
	pb.id_zone_cynegetique,
	pb.id_zone_indicative,
	pb.nb_attribution_min_zc,
	pb.nb_attribution_max_zc,
	czc.nb_realisation_zc,
	czc.nb_realisation_avant_11_zc,
	0 * cazi.nb_attribution_zi  AS nb_attribution_min_zi,
	cazi.nb_attribution_zi AS nb_attribution_max_zi,
	pb.nb_realisation_zi,
	pb.nb_realisation_avant_11_zi
	FROM pre_bilan pb
	JOIN count_attribution_zi cazi ON cazi.id_saison = pb.id_saison AND cazi.id_espece = pb.id_espece AND cazi.id_zone_indicative = pb.id_zone_indicative
	JOIN count_zc czc ON czc.id_saison = pb.id_saison AND czc.id_espece = pb.id_espece AND czc.id_zone_cynegetique = pb.id_zone_cynegetique
	JOIN count_espece ce ON ce.id_saison = pb.id_saison AND ce.id_espece = pb.id_espece
;

DROP VIEW IF EXISTS oeasc_chasse.v_pre_bilan_histo CASCADE;
CREATE VIEW oeasc_chasse.v_pre_bilan_histo AS
WITH pre_bilan AS (
	SELECT
		id_saison,
		id_espece,
		tzc.id_zone_cynegetique,
		tzi.id_zone_indicative,
		nb_affecte_min AS nb_attribution_min_zi,
		nb_affecte_max AS nb_attribution_max_zi,
		nb_realise AS nb_realisation_zi,
		nb_realise_avant_11 AS nb_realisation_avant_11_zi
		from oeasc_chasse.t_bilan_chasse_historique tbch
		join oeasc_chasse.t_zone_indicatives tzi on tzi.id_zone_indicative = tbch.id_zone_indicative
		join oeasc_chasse.t_zone_cynegetiques tzc on tzc.id_zone_cynegetique = tzi.id_zone_cynegetique
), count_zc AS (
	SELECT
		SUM(nb_realisation_zi) AS nb_realisation_zc,
		SUM(nb_realisation_avant_11_zi) AS nb_realisation_avant_11_zc,
		SUM(nb_attribution_min_zi) AS nb_attribution_min_zc,
		SUM(nb_attribution_max_zi) AS nb_attribution_max_zc,
		id_espece,
		id_saison,
		id_zone_cynegetique
		FROM pre_bilan
		GROUP BY
			id_espece,
			id_saison,
			id_zone_cynegetique
), count_espece AS (
	SELECT
		SUM(nb_attribution_min_zi) AS nb_attribution_min_espece,
		SUM(nb_attribution_max_zi) AS nb_attribution_max_espece,
		SUM(nb_realisation_zi) AS nb_realisation_espece,
		SUM(nb_realisation_avant_11_zi) AS nb_realisation_avant_11_espece,
		id_espece,
		id_saison
		FROM pre_bilan
		GROUP BY
			id_espece,
			id_saison
)
SELECT
	pb.id_saison,
	pb.id_espece,
	ce.nb_attribution_min_espece,
	ce.nb_attribution_max_espece,
	ce.nb_realisation_espece,
	ce.nb_realisation_avant_11_espece,
	pb.id_zone_cynegetique,
	pb.id_zone_indicative,
	czc.nb_attribution_min_zc,
	czc.nb_attribution_max_zc,
	czc.nb_realisation_zc,
	czc.nb_realisation_avant_11_zc,
	pb.nb_attribution_min_zi,
	pb.nb_attribution_max_zi,
	pb.nb_realisation_zi,
	pb.nb_realisation_avant_11_zi
	FROM pre_bilan pb
	JOIN count_zc czc ON czc.id_saison = pb.id_saison AND czc.id_espece = pb.id_espece AND czc.id_zone_cynegetique = pb.id_zone_cynegetique
	JOIN count_espece ce ON ce.id_saison = pb.id_saison AND ce.id_espece = pb.id_espece;

DROP VIEW IF EXISTS oeasc_chasse.v_pre_bilan CASCADE;
CREATE VIEW oeasc_chasse.v_pre_bilan AS
SELECT * FROM oeasc_chasse.v_pre_bilan_histo
UNION
SELECT * FROM oeasc_chasse.v_pre_bilan_saisie;

DROP VIEW IF EXISTS oeasc_chasse.v_pre_bilan_pretty CASCADE;
CREATE VIEW oeasc_chasse.v_pre_bilan_pretty AS
SELECT
	vb.id_saison,
	nom_saison,
	vb.id_espece,
	nom_espece,
	code_espece,
	vb.id_zone_cynegetique,
	nom_zone_cynegetique,
	code_zone_cynegetique,
	vb.id_zone_indicative,
	nom_zone_indicative,
	code_zone_indicative,
	nom_secteur,
	code_secteur,
	nb_attribution_min_zi,
	nb_attribution_max_zi,
	nb_realisation_zi,
	nb_realisation_avant_11_zi,
	nb_attribution_min_zc,
	nb_attribution_max_zc,
	nb_realisation_zc,
	nb_realisation_avant_11_zc,
	nb_attribution_min_espece,
	nb_attribution_max_espece,
	nb_realisation_espece,
	nb_realisation_avant_11_espece
	FROM oeasc_chasse.v_pre_bilan vb
	join oeasc_chasse.t_saisons ts on ts.id_saison =vb.id_saison
	join oeasc_chasse.t_zone_cynegetiques tzc on tzc.id_zone_cynegetique = vb.id_zone_cynegetique
	join oeasc_chasse.t_zone_indicatives tzi on tzi.id_zone_indicative = vb.id_zone_indicative
	join oeasc_commons.t_secteurs tsec on tsec.id_secteur = tzc.id_secteur
	join oeasc_commons.t_especes te on te.id_espece = vb.id_espece;
