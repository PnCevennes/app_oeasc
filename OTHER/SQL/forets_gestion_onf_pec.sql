SELECT id, geom, ccod_frt, ccod_tpde, ccod_ut, llib_frt, llib_ut, qsret_frt, 
       dept, date_maj, geom_4326
  FROM ref_geo.forets_gestion_onf_pec
  WHERE NOT st_isvalid(geom);

UPDATE  ref_geo.forets_gestion_onf_pec SET geom = st_makevalid(geom)
  WHERE NOT st_isvalid(geom);

SELECT llib_frt
FROM ref_geo.forets_gestion_onf_pec
WHERE llib_frt LIKE CONCAT('%Š%');

SELECT llib_frt
FROM ref_geo.forets_gestion_onf_pec
WHERE llib_frt LIKE CONCAT('%‚%');

SELECT llib_frt
FROM ref_geo.forets_gestion_onf_pec
WHERE llib_frt LIKE CONCAT('%“%');

UPDATE  ref_geo.forets_gestion_onf_pec
SET llib_frt = REPLACE(llib_frt, 'Š', 'è')
WHERE llib_frt LIKE '%Š%';

UPDATE  ref_geo.forets_gestion_onf_pec 
SET llib_frt = REPLACE(llib_frt, '‚', 'é')
WHERE llib_frt LIKE '%‚%';

UPDATE  ref_geo.forets_gestion_onf_pec 
SET llib_frt = REPLACE(llib_frt, '“', 'ô')
WHERE llib_frt LIKE '%“%';

UPDATE  ref_geo.forets_gestion_onf_pec 
SET llib_frt = REPLACE(llib_frt, 'département et hépitaux', 'département et hôpitaux')
WHERE llib_frt LIKE '%département et hépitaux%';

ALTER TABLE ref_geo.forets_gestion_onf_pec RENAME COLUMN id TO unique_id; 

ALTER TABLE ref_geo.forets_gestion_onf_pec ADD COLUMN geom_4326 geometry(MultiPolygon,4326);   
UPDATE  ref_geo.forets_gestion_onf_pec SET geom_4326 = st_transform(geom, 4326);