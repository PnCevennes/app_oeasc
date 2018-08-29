DROP TABLE ref_geo.parcellaire_foret_publique_pec_test;

CREATE TABLE ref_geo.parcellaire_foret_publique_pec_test AS TABLE ref_geo.parcellaire_foret_publique_pec;

SELECT ccod_tpde, ccod_frt, llib_ut, llib_prf,
       dept, ccod_pst, ccod_ut, llib_frt, agent_pst, ccod_prf, 
       concat
  FROM ref_geo.parcellaire_foret_publique_pec
  ORDER BY ccod_frt;

  SELECT COUNT(*), CONCAT(ccod_frt, ccod_ut, ccod_prf) as v
  FROM ref_geo.parcellaire_foret_publique_pec
GROUP BY v
HAVING COUNT(*) > 1  
ORDER BY v;


UPDATE ref_geo.parcellaire_foret_publique_pec_test SET ccod_prf = b FROM (SELECT ccod_prf as b FROM ref_geo.parcellaire_foret_publique_pec
)a
WHERE CONCAT(ccod_frt, ccod_ut, ccod_prf) = 
 (SELECT CONCAT(ccod_frt, ccod_ut, ccod_prf) as v
  FROM ref_geo.parcellaire_foret_publique_pec
GROUP BY v
HAVING COUNT(*) > 1  
ORDER BY v);

SELECT ccod_prf, id, ccod_tpde, ccod_frt, llib_ut, llib_prf,
       dept, ccod_pst, ccod_ut, llib_frt, agent_pst, ccod_prf, 
       concat FROM ref_geo.parcellaire_foret_publique_pec_test
WHERE ccod_pst = '87200407' AND ccod_frt = 'MALENE';

SELECT ccod_prf, id, ccod_tpde, ccod_frt, llib_ut, llib_prf,
       dept, ccod_pst, ccod_ut, llib_frt, agent_pst, ccod_prf, 
       concat FROM
 (SELECT COUNT(*), CONCAT(ccod_frt, ccod_ut, ccod_prf) as v
  FROM ref_geo.parcellaire_foret_publique_pec_test
GROUP BY v
HAVING COUNT(*) > 1  
ORDER BY v)a, ref_geo.parcellaire_foret_publique_pec
WHERE a.v = CONCAT(ccod_frt, ccod_ut, ccod_prf);


