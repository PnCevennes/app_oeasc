ALTER TABLE oeasc_declarations.t_declarations ADD centroid float[];

UPDATE oeasc_declarations.t_declarations e SET geom=d.geom, geom_4326=d.geom_4326, centroid=d.centroid
FROM (SELECT id_declaration, geom, geom_4326, ARRAY[ST_Y(centroid), ST_X(centroid)] AS centroid
FROM (SELECT id_declaration, geom, geom_4326, ST_CENTROID(geom_4326) AS centroid
FROM (SELECT id_declaration, geom, ST_TRANSFORM(geom, 4326) AS geom_4326
FROM (SELECT id_declaration, ST_MULTI(ST_UNION(l.geom)) AS geom
FROM oeasc_declarations.cor_areas_declarations c
JOIN ref_geo.l_areas l ON c.id_area = l.id_area AND l.id_type IN (ref_geo.get_id_type('OEASC_ONF_UG'), ref_geo.get_id_type('OEASC_CADASTRE'))
GROUP BY id_declaration)a)b)c)d
WHERE d.id_declaration = e.id_declaration;
