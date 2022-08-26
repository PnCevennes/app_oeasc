-- oeasc_chasse.v_plan_chasse_realisation_bilan source
DROP VIEW IF EXISTS oeasc_chasse.v_plan_chasse_realisation_bilan;
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
