DROP TABLE  IF EXISTS ref_geo.forets_gestion_onf_pec_merge ;

SELECT COUNT(*), CONCAT(ccod_frt, ccod_ut) as ccod, ST_MULTI(ST_UNION(geom)) as single_geom
  FROM ref_geo.forets_gestion_onf_pec_merge
  GROUP BY ccod
  ORDER BY ccod
  HAVING COUNT(*) > 1;


CREATE TABLE ref_geo.forets_gestion_onf_pec_merge AS
SELECT id , a.single_geom AS geom, ccod_frt, ccod_tpde, ccod_ut, llib_frt, llib_ut, qsret_frt, 
       dept, date_maj, ST_TRANSFORM(a.single_geom, 4326) AS geom_4326
       FROM
(SELECT COUNT(*), CONCAT(ccod_frt, ccod_ut) as ccod, ST_MULTI(ST_UNION(geom)) as single_geom
  FROM ref_geo.forets_gestion_onf_pec
  GROUP BY ccod
HAVING COUNT(*) > 1
  )a, ref_geo.forets_gestion_onf_pec
  WHERE CONCAT(ccod_frt, ccod_ut) = ccod;

DELETE FROM ref_geo.forets_gestion_onf_pec
WHERE id IN (SELECT id
              FROM (SELECT id,
                             ROW_NUMBER() OVER (partition BY CONCAT(ccod_frt, ccod_ut) ORDER BY id) AS rnum
                     FROM ref_geo.forets_gestion_onf_pec) t
              WHERE t.rnum >= 1);


INSERT INTO ref_geo.forets_gestion_onf_pec(geom, ccod_frt, ccod_tpde, ccod_ut, llib_frt, llib_ut, qsret_frt, 
       dept, date_maj, geom_4326) (SELECT geom, ccod_frt, ccod_tpde, ccod_ut, llib_frt, llib_ut, qsret_frt, 
       dept, date_maj, geom_4326 FROM ref_geo.forets_gestion_onf_pec_merge);

DELETE FROM ref_geo.forets_gestion_onf_pec
WHERE id IN (SELECT id
              FROM (SELECT id,
                             ROW_NUMBER() OVER (partition BY CONCAT(ccod_frt, ccod_ut) ORDER BY id) AS rnum
                     FROM ref_geo.forets_gestion_onf_pec) t
              WHERE t.rnum > 1);


SELECT COUNT(*), CONCAT(ccod_frt, ccod_ut) as ccod, ST_MULTI(ST_UNION(geom)) as single_geom
  FROM ref_geo.forets_gestion_onf_pec_merge
  GROUP BY ccod
  HAVING COUNT(*) > 1;

DROP TABLE  IF EXISTS ref_geo.forets_gestion_onf_pec_merge ;

-- DELETE FROM ref_geo.test_forets_gestion_onf_pec AS t1, ref_geo.test_forets_gestion_onf_pec AS t2
-- WHERE t1.id > t2.id
-- AND CONCAT(t1.ccod_frt, t1.ccod_ut) = CONCAT(t2.ccod_frt, t2.ccod_ut)

  