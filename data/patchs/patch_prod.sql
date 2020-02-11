-- patch prod
DROP TRIGGER IF EXISTS trg_cor_areas_forets ON oeasc_forets.t_forets;

-- sections
INSERT INTO oeasc_forets.cor_areas_forets(id_foret, id_area)
SELECT 
	f.id_foret,
	ref_geo.intersect_geom_type_tol(d.geom, 'OEASC_SECTION', 0.01) as id_area

FROM oeasc_forets.t_forets f
LEFT JOIN ( SELECT id_foret 
	FROM oeasc_forets.cor_areas_forets cf
	JOIN ref_geo.l_areas lf ON lf.id_area = cf.id_area AND lf.id_type = ref_geo.get_id_type('OEASC_SECTION')
	GROUP BY id_foret
)a ON a.id_foret = f.id_foret
JOIN oeasc_declarations.v_declarations d ON d.id_foret = f.id_foret 
WHERE a.id_foret IS NULL AND NOT f.b_document
ORDER BY f.id_foret

-- communes
INSERT INTO oeasc_forets.cor_areas_forets(id_foret, id_area)
SELECT 
	f.id_foret,
	ref_geo.intersect_geom_type_tol(d.geom, 'OEASC_COMMUNE', 0.01) as id_area

FROM oeasc_forets.t_forets f
LEFT JOIN ( SELECT id_foret 
	FROM oeasc_forets.cor_areas_forets cf
	JOIN ref_geo.l_areas lf ON lf.id_area = cf.id_area AND lf.id_type = ref_geo.get_id_type('OEASC_COMMUNE')
	GROUP BY id_foret
)a ON a.id_foret = f.id_foret
JOIN oeasc_declarations.v_declarations d ON d.id_foret = f.id_foret 
WHERE a.id_foret IS NULL AND NOT f.b_document
ORDER BY f.id_foret
