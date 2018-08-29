SELECT   concat_ug
  FROM ref_geo.unites_gestion_foret_publique_pec
-- GROUP BY concat_ug
-- HAVING   COUNT(*) > 1
ORDER BY concat_ug;

SELECT SUM(a.nbr_doublon)
FROM (
SELECT   COUNT(*) AS nbr_doublon,  concat_ug
  FROM ref_geo.unites_gestion_foret_publique_pec
 GROUP BY concat_ug
 HAVING   COUNT(*) > 1
ORDER BY COUNT(*) DESC
)a

SELECT   *
  FROM ref_geo.unites_gestion_foret_publique_pec
WHERE concat_ug = 'BOUGES-188-n'