ALTER TABLE oeasc.t_declarations ADD COLUMN b_autorisation BOOLEAN;
ALTER TABLE oeasc.t_declarations ADD COLUMN peuplement_surface DOUBLE PRECISION;

UPDATE ref_nomenclatures.t_nomenclatures 
	SET (label_default, label_fr, definition_default, definition_fr) = 
	( SELECT a, a, a, a
			FROM ( SELECT 'Dégâts sur piste, clôture et/ou murets' AS a
			)b
		)
	WHERE cd_nomenclature = 'P/C';
