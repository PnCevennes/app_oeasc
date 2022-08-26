--
-- Vues chasse pour les bilans
--

DROP VIEW IF EXISTS oeasc_chasse.v_pre_bilan_pretty;
DROP VIEW IF EXISTS oeasc_chasse.v_pre_bilan;
DROP VIEW IF EXISTS oeasc_chasse.v_pre_bilan_saisie;
DROP VIEW IF EXISTS oeasc_chasse.v_pre_bilan_histo;
DROP VIEW IF EXISTS oeasc_chasse.v_plan_chasse_realisation_bilan;



CREATE OR REPLACE VIEW oeasc_chasse.v_pre_bilan_saisie AS
  WITH realisations AS (
    SELECT
        ta.id_saison,
        ttb.id_espece,
        ta.id_zone_cynegetique_affectee as id_zone_cynegetique,
        ta.id_zone_indicative_affectee as id_zone_indicative,
        COUNT(DISTINCT ta.id_attribution) AS nb_attribution_zi,
        COUNT(*) filter (WHERE tr.id_realisation IS NOT NULL) AS nb_realise,
        COUNT(*) filter (
            WHERE tr.id_realisation IS NOT NULL
                AND tr.date_exacte IS NOT NULL
                AND tr.date_exacte <= (CONCAT(SPLIT_PART(ts.nom_saison, '-', 1), '-10-31'))::date
        ) AS nb_realise_avant_11
    from oeasc_chasse.t_attributions ta
    left join oeasc_chasse.t_realisations tr on ta.id_attribution = tr.id_attribution
    join oeasc_chasse.t_saisons ts on ts.id_saison = ta.id_saison
    join oeasc_chasse.t_type_bracelets ttb on ttb.id_type_bracelet = ta.id_type_bracelet
    GROUP BY
        ta.id_saison,
        ttb .id_espece,
        ta.id_zone_indicative_affectee,
        ta.id_zone_cynegetique_affectee
  ),affectations AS (
    SELECT tam.id_saison,
            tam.id_espece,
            tzc.id_secteur,
            tzc.id_zone_cynegetique,
            sum(tam.nb_affecte_min) OVER (PARTITION BY tam.id_saison, tam.id_espece) AS nb_attribution_min_espece,
            sum(tam.nb_affecte_max) OVER (PARTITION BY tam.id_saison, tam.id_espece) AS nb_attribution_max_espece,
            sum(tam.nb_affecte_min) OVER (PARTITION BY tam.id_saison, tam.id_espece, tzc.id_secteur) AS nb_attribution_min_secteur,
            sum(tam.nb_affecte_max) OVER (PARTITION BY tam.id_saison, tam.id_espece, tzc.id_secteur) AS nb_attribution_max_secteur,
            tam.nb_affecte_min nb_attribution_min_zc,
            tam.nb_affecte_max nb_attribution_max_zc
    FROM oeasc_chasse.t_attribution_massifs tam
    JOIN oeasc_chasse.t_zone_cynegetiques tzc
        ON tzc.id_zone_cynegetique = tam.id_zone_cynegetique
)
SELECT
    a.id_saison,
    a.id_espece,
    a.id_secteur,
    a.id_zone_cynegetique,
    r.id_zone_indicative,
    a.nb_attribution_min_espece,
    a.nb_attribution_max_espece,
    sum(r.nb_realise) OVER (PARTITION BY a.id_saison, a.id_espece)  AS nb_realisation_espece,
    sum(r.nb_realise_avant_11) OVER (PARTITION BY a.id_saison, a.id_espece)  AS nb_realisation_avant_11_espece,
    a.nb_attribution_min_secteur,
    a.nb_attribution_max_secteur,
    sum(r.nb_realise) OVER (PARTITION BY a.id_saison, a.id_espece, a.id_secteur)  AS nb_realisation_secteur,
    sum(r.nb_realise_avant_11) OVER (PARTITION BY a.id_saison, a.id_espece, a.id_secteur)  AS nb_realisation_avant_11_secteur,
    a.nb_attribution_min_zc,
    a.nb_attribution_max_zc,
    sum(r.nb_realise) OVER (PARTITION BY a.id_saison, a.id_espece, a.id_zone_cynegetique)  AS nb_realisation_zc,
    sum(r.nb_realise_avant_11) OVER (PARTITION BY a.id_saison, a.id_espece, a.id_zone_cynegetique)  AS nb_realisation_avant_11_zc,
    0 AS nb_attribution_min_zi, -- la valeur n'existe pas à l'echelle de la zi
    r.nb_attribution_zi AS nb_attribution_max_zi,
    r.nb_realise AS nb_realisation_zi,
    r.nb_realise_avant_11 AS nb_realisation_avant_11_zi
FROM realisations r
JOIN affectations a
ON r.id_zone_cynegetique = a.id_zone_cynegetique
    AND r.id_espece = a.id_espece
    AND r.id_saison = a.id_saison;

CREATE OR REPLACE VIEW oeasc_chasse.v_pre_bilan_histo AS
WITH affectations AS (
    SELECT tam.id_saison,
            tam.id_espece,
            tzc.id_secteur,
            tzc.id_zone_cynegetique,
            sum(tam.nb_affecte_min) OVER (PARTITION BY tam.id_saison, tam.id_espece) AS nb_attribution_min_espece,
            sum(tam.nb_affecte_max) OVER (PARTITION BY tam.id_saison, tam.id_espece) AS nb_attribution_max_espece,
            sum(tam.nb_affecte_min) OVER (PARTITION BY tam.id_saison, tam.id_espece, tzc.id_secteur) AS nb_attribution_min_secteur,
            sum(tam.nb_affecte_max) OVER (PARTITION BY tam.id_saison, tam.id_espece, tzc.id_secteur) AS nb_attribution_max_secteur,
            tam.nb_affecte_min nb_attribution_min_zc,
            tam.nb_affecte_max nb_attribution_max_zc
    FROM oeasc_chasse.t_attribution_massifs tam
    JOIN oeasc_chasse.t_zone_cynegetiques tzc
        ON tzc.id_zone_cynegetique = tam.id_zone_cynegetique
)
SELECT
        tam.id_saison,
        tam.id_espece,
        tam.id_secteur,
        tzi.id_zone_cynegetique,
        tzi.id_zone_indicative,
        tam.nb_attribution_min_espece,
        tam.nb_attribution_max_espece,
        sum(tbch.nb_realise) OVER (PARTITION BY tam.id_saison, tam.id_espece)  AS nb_realisation_espece,
        sum(tbch.nb_realise_avant_11) OVER (PARTITION BY tam.id_saison, tam.id_espece)  AS nb_realisation_avant_11_espece,
        tam.nb_attribution_min_secteur,
        tam.nb_attribution_max_secteur,
        sum(tbch.nb_realise) OVER (PARTITION BY tam.id_saison, tam.id_espece, tam.id_secteur)  AS nb_realisation_secteur,
        sum(tbch.nb_realise_avant_11) OVER (PARTITION BY tam.id_saison, tam.id_espece, tam.id_secteur)  AS nb_realisation_avant_11_secteur,
        tam.nb_attribution_min_zc,
        tam.nb_attribution_max_zc,
        sum(tbch.nb_realise) OVER (PARTITION BY tam.id_saison, tam.id_espece, tzi.id_zone_cynegetique)  AS nb_realisation_zc,
        sum(tbch.nb_realise_avant_11) OVER (PARTITION BY tam.id_saison, tam.id_espece, tzi.id_zone_cynegetique)  AS nb_realisation_avant_11_zc,
        0 AS nb_attribution_min_zi, -- la valeur n'existe pas à l'echelle de la zi
        tbch.nb_affecte_max AS nb_attribution_max_zi,
        tbch.nb_realise AS nb_realisation_zi,
        tbch.nb_realise_avant_11 AS nb_realisation_avant_11_zi
from oeasc_chasse.t_bilan_chasse_historique tbch
join oeasc_chasse.t_zone_indicatives tzi on tzi.id_zone_indicative = tbch.id_zone_indicative
join affectations tam
 on tam.id_espece = tbch.id_espece
    and tam.id_zone_cynegetique = tzi.id_zone_cynegetique
    AND tam.id_saison = tbch.id_saison;


CREATE VIEW oeasc_chasse.v_pre_bilan AS
	SELECT * FROM oeasc_chasse.v_pre_bilan_histo
	UNION
	SELECT * FROM oeasc_chasse.v_pre_bilan_saisie
;

CREATE VIEW oeasc_chasse.v_pre_bilan_pretty AS
SELECT
	vb.id_saison,
	nom_saison,
	vb.id_espece,
	nom_espece,
	code_espece,
	vb.id_secteur,
	nom_secteur,
	code_secteur,
	vb.id_zone_cynegetique,
	nom_zone_cynegetique,
	code_zone_cynegetique,
	vb.id_zone_indicative,
	nom_zone_indicative,
	code_zone_indicative,
	nb_attribution_min_espece,
	nb_attribution_max_espece,
	nb_realisation_espece,
	nb_realisation_avant_11_espece,
	nb_attribution_min_secteur,
	nb_attribution_max_secteur,
	nb_realisation_secteur,
	nb_realisation_avant_11_secteur,
	nb_attribution_min_zi,
	nb_attribution_max_zi,
	nb_realisation_zi,
	nb_realisation_avant_11_zi,
	nb_attribution_min_zc,
	nb_attribution_max_zc,
	nb_realisation_zc,
	nb_realisation_avant_11_zc
    -- ,
    -- min  (code_zone_indicative::int) OVER (PARTITION BY vb.id_saison, vb.id_espece, vb.id_secteur, vb.id_zone_cynegetique) AS min_zc_code_zi
    	FROM oeasc_chasse.v_pre_bilan vb
	join oeasc_chasse.t_saisons ts on ts.id_saison =vb.id_saison
	join oeasc_chasse.t_zone_cynegetiques tzc on tzc.id_zone_cynegetique = vb.id_zone_cynegetique
	join oeasc_chasse.t_zone_indicatives tzi on tzi.id_zone_indicative = vb.id_zone_indicative
	join oeasc_commons.t_secteurs tsec on tsec.id_secteur = vb.id_secteur
	join oeasc_commons.t_especes te on te.id_espece = vb.id_espece;


CREATE OR REPLACE VIEW oeasc_chasse.v_plan_chasse_realisation_bilan
AS SELECT tbch.id_saison,
    tbch.id_espece,
    tbch.id_zone_indicative,
    tzi.id_zone_cynegetique,
    tzc.id_secteur,
    0 AS nb_affecte_min,
    tbch.nb_affecte_max,
    tbch.nb_realise AS nb_realisation,
    tbch.nb_realise_avant_11 AS nb_realisation_avant_11
   FROM oeasc_chasse.t_bilan_chasse_historique tbch
     JOIN oeasc_chasse.t_zone_indicatives tzi ON tzi.id_zone_indicative = tbch.id_zone_indicative
     JOIN oeasc_chasse.t_zone_cynegetiques tzc ON tzc.id_zone_cynegetique = tzi.id_zone_cynegetique
UNION
 SELECT ta.id_saison,
    ttb.id_espece,
    ta.id_zone_indicative_affectee AS id_zone_indicative,
    ta.id_zone_cynegetique_affectee AS id_zone_cynegetique,
    tzc.id_secteur,
    0 AS nb_affecte_min,
    count(DISTINCT ta.id_attribution) AS nb_affecte_max,
    count(*) FILTER (WHERE tr.id_realisation IS NOT NULL) AS nb_realisation,
    count(*) FILTER (WHERE tr.id_realisation IS NOT NULL AND tr.date_exacte IS NOT NULL AND tr.date_exacte <= concat(split_part(ts.nom_saison::text, '-'::text, 1), '-10-31')::date) AS nb_realisation_avant_11
   FROM oeasc_chasse.t_attributions ta
     LEFT JOIN oeasc_chasse.t_realisations tr ON ta.id_attribution = tr.id_attribution
     JOIN oeasc_chasse.t_saisons ts ON ts.id_saison = ta.id_saison
     JOIN oeasc_chasse.t_type_bracelets ttb ON ttb.id_type_bracelet = ta.id_type_bracelet
     JOIN oeasc_chasse.t_zone_cynegetiques tzc ON tzc.id_zone_cynegetique = ta.id_zone_cynegetique_affectee

  GROUP BY ta.id_saison, ttb.id_espece, ta.id_zone_indicative_affectee, ta.id_zone_cynegetique_affectee, id_secteur;
