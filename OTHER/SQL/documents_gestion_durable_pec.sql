SELECT id, geom, forid, fornom, forsur, forinsee, dgdtype, proid, proref, 
       prosur, progen, proetat, proexp, prodecdat, prop, perlig1, perlig2, 
       perlig3, perlig4, percp, perbur, x, y, surface
  FROM ref_geo.documents_gestion_durable_pec
  WHERE NOT st_isvalid(geom);


-- Vérification de la correction automatique

CREATE TABLE ref_geo.documents_gestion_durable_pec_valid AS
SELECT st_makevalid(geom), id
FROM ref_geo.documents_gestion_durable_pec
  WHERE NOT st_isvalid(geom);

CREATE VIEW ref_geo.v_temp_valid AS
SELECT *, row_number() over()
FROM (
	SELECT (st_dump(st_makevalid)).geom as geom, st_geometrytype((st_dump(st_makevalid)).geom),id
	FROM ref_geo.documents_gestion_durable_pec_valid  
)a

DROP VIEW ref_geo.v_temp_valid;
DROP TABLE ref_geo.documents_gestion_durable_pec_valid;

--Correction des données de géometrie en excluant les linestring générées par st_makevalid
-- Après vérification visuelle
WITH corrected_data AS (
	SELECT id, st_union(geom) as corrected_geom, st_geometrytype(st_union(geom))
	FROM (
		SELECT (st_dump(st_makevalid(geom))).geom as geom, id
		FROM ref_geo.documents_gestion_durable_pec  
		WHERE NOT st_isvalid(geom)
	)a
	WHERE NOT st_geometrytype(geom) = 'ST_LineString'
	GROUP BY id
)
UPDATE ref_geo.documents_gestion_durable_pec d SET geom = c.corrected_geom
FROM corrected_data c
WHERE d.id = c.id;