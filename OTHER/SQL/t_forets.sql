DROP TABLE IF EXISTS temp;


SELECT * FROM ref_geo.intersect_rel_area(2243189, 'OEASC_COMMUNE', 0.01);

CREATE TABLE temp (dept text, ccod_frt text, nom_proprietaire text);

COPY temp
    FROM '/home/joel/Info/PNC/OEASC/app_oeasc/install/scripts_db/script_oeasc/liens_proprietaires_publics_forets.csv'
    WITH DELIMITER ';' CSV QUOTE AS '''';


SELECT * FROM temp;


SELECT b.area_name, b.idp, b.idf, c.id_area, c.area_name
	FROM
	(SELECT oeasc.get_id_proprietaire_from_name(t.nom_proprietaire) as idp, ref_geo.get_id_area_from_area_code(a.area_code,'OEASC_ONF_FRT') as idf, geom, a.area_name
		FROM temp as t, (SELECT area_code, geom, area_name
			FROM ref_geo.l_areas
			WHERE id_type = ref_geo.get_id_type('OEASC_ONF_FRT'))a
		WHERE CONCAT(t.dept, '-', t.ccod_frt) = a.area_code)b, 
	(SELECT geom, id_area, area_name
		FROM ref_geo.l_areas
		WHERE id_type = ref_geo.get_id_type('OEASC_COMMUNE'))c

	WHERE ST_INTERSECTS(c.geom, b.geom)
	;

SELECT b.area_name, b.idp, b.idf, c.id_area, c.area_name, ST_AREA(ST_INTERSECTION(c.geom,b.geom))/ST_AREA(b.geom)
	FROM
	(SELECT oeasc.get_id_proprietaire_from_name(t.nom_proprietaire) as idp, ref_geo.get_id_area_from_area_code(a.area_code,'OEASC_ONF_FRT') as idf, geom, a.area_name
		FROM temp as t, (SELECT area_code, geom, area_name
			FROM ref_geo.l_areas
			WHERE id_type = ref_geo.get_id_type('OEASC_ONF_FRT'))a
		WHERE CONCAT(t.dept, '-', t.ccod_frt) = a.area_code)b, 
	(SELECT geom, id_area, area_name
		FROM ref_geo.l_areas
		WHERE id_type = ref_geo.get_id_type('OEASC_DEPARTEMENT'))c

	WHERE ST_INTERSECTS(c.geom, b.geom) and ST_AREA(ST_INTERSECTION(c.geom,b.geom))/ST_AREA(b.geom) > 0.025
	;
 