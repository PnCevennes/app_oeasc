SELECT id, geom, surf_ha, nom_com, code_insee, statut, coeur, aire_adhes, 
       pec, massif, depart, region, nom_ccom, natur_ccom, pop_2014
  FROM ref_geo.communes
WHERE NOT st_isvalid(geom);

ALTER TABLE ref_geo.communes ADD COLUMN geom_4326 geometry(MultiPolygon,4326);   
UPDATE  ref_geo.communes SET geom_4326 = st_transform(geom, 4326);