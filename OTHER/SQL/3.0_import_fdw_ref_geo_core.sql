DROP SCHEMA IF EXISTS import_ref_geo CASCADE;
CREATE SCHEMA IF NOT EXISTS import_ref_geo;

IMPORT FOREIGN SCHEMA ref_geo  
    FROM SERVER referentiels_server INTO import_ref_geo;

-- Clean table 
TRUNCATE TABLE ref_geo.bib_areas_types CASCADE;
TRUNCATE TABLE ref_geo.dem_vector CASCADE;

INSERT INTO ref_geo.bib_areas_types
SELECT * 
FROM import_ref_geo.bib_areas_types;

INSERT INTO ref_geo.l_areas
SELECT * 
FROM import_ref_geo.l_areas;

/*
-- Non pris en compte car tables potentiellement spécifiques
INSERT INTO ref_geo.li_grids
SELECT * 
FROM import_ref_geo.li_grids;

INSERT INTO ref_geo.li_municipalities
SELECT * 
FROM import_ref_geo.li_municipalities;
*/

/*
INSERT INTO ref_geo.dem_vector
SELECT * 
FROM import_ref_geo.dem_vector;
*/