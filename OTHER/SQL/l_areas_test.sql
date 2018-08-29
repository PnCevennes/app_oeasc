DROP TABLE IF EXISTS ref_geo.l_areas_test;

CREATE TABLE ref_geo.l_areas_test AS TABLE ref_geo.l_areas;


-- insert ONF forets

INSERT INTO ref_geo.l_areas_test(id_type, area_name, area_code, geom, centroid, source, comment, enable)
SELECT 301, CONCAT(llib_ut, '_',llib_frt), CONCAT(ccod_frt, ccod_ut), geom, ST_CENTROID(geom), 'ONF', '', true
FROM ref_geo.forets_gestion_onf_pec;


-- insert ONF parcelles

INSERT INTO ref_geo.l_areas_test(id_type, area_name, area_code, geom, centroid, source, comment, enable)
SELECT 302, CONCAT(llib_ut, '_', llib_frt, '_', llib_prf), CONCAT(ccod_frt, ccod_ut, ccod_prf), geom, ST_CENTROID(geom), 'ONF', '', true
FROM ref_geo.parcellaire_foret_publique_pec;


-- insert ONF unites gestion

INSERT INTO ref_geo.l_areas_test(id_type, area_name, area_code, geom, centroid, source, comment, enable)
SELECT 303, CONCAT(llib_ut, '_', llib_frt, '_', llib_prf, '_', ccod_ug), CONCAT(ccod_frt, ccod_ut, ccod_prf, ccod_ug), geom, ST_CENTROID(geom), 'ONF', '', true
FROM ref_geo.unites_gestion_foret_publique_pec;


