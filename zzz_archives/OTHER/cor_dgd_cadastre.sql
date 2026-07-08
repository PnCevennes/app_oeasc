DROP TABLE IF EXISTS oeasc_forets.cor_dgd_cadastre;

CREATE TABLE oeasc_forets.cor_dgd_cadastre
(
    id_area_dgd integer NOT NULL,
    id_area_cadastre integer NOT NULL,

    CONSTRAINT pk_cor_areas_declaration PRIMARY KEY (id_area_dgd, id_area_cadastre),

    CONSTRAINT fk_cor_dgd_cadastre_id_area_dgd FOREIGN KEY (id_area_dgd)
        REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,

    CONSTRAINT fk_cor_dgd_cadastre_id_area_cadastre FOREIGN KEY (id_area_cadastre)
        REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,

     CONSTRAINT check_cor_dgd_cadastre_dgd CHECK (ref_geo.check_area_type_code(id_area_dgd, 'OEASC_DGD'::character varying)),
     
     CONSTRAINT check_cor_dgd_cadastre_cadastre CHECK (ref_geo.check_area_type_code(id_area_cadastre, 'OEASC_CADASTRE'::character varying))

);

SELECT id_area, ref_geo.intersect_id_area_type_tol(id_area, 'OEASC_CADASTRE', 0.05)
	FROM ref_geo.l_areas
	WHERE id_type=ref_geo.get_id_type('OEASC_DGD');
