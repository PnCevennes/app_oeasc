DROP VIEW IF EXISTS oeasc.v_declarations CASCADE;
CREATE OR REPLACE VIEW oeasc.v_declarations AS

    WITH
	foret AS ( SELECT 
		f.id_foret,
		label_foret,
		CASE WHEN b_statut_public THEN 'Public' ELSE 'Privé' END AS statut,
		CASE WHEN b_document THEN 'Oui' ELSE 'non' END AS document
		
		FROM oeasc.t_forets f
	),
	
	communes AS ( SELECT 
		f.id_foret,
		ref_geo.get_area_names(ARRAY_AGG(areas_communes.id_area)) AS noms_communes
		
		FROM oeasc.t_forets f
		JOIN oeasc.cor_areas_forets c
			ON c.id_foret = f.id_foret
		JOIN ref_geo.l_areas areas_communes
			ON areas_communes.id_type = ref_geo.get_id_type('OEASC_COMMUNE')
		GROUP BY f.id_foret
	),
	
	declarant AS ( SELECT
		r.id_role AS "id_declarant",
		CONCAT(UPPER(r.nom_role), ' ', r.prenom_role) AS "declarant",
		r.organisme AS "Organisme"
		
		FROM utilisateurs.t_roles r
	),
	
	peuplement AS ( SELECT
		id_declaration,
		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_essence_principale) AS essence_1_mnemo,
		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_essence_principale) AS essence_1_label

		FROM oeasc.t_declarations d
	),
	
	peuplement_essence_2 AS ( SELECT
		d.id_declaration,
		ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(c.id_nomenclature)) AS mnemo,
		ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(c.id_nomenclature)) AS label
		
		FROM oeasc.t_declarations d
		JOIN oeasc.cor_nomenclature_declarations_essence_secondaire c
			ON d.id_declaration = c.id_declaration
		GROUP BY d.id_declaration
	),

	peuplement_essence_3 AS ( SELECT
		d.id_declaration,
		ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(c.id_nomenclature)) AS mnemo,
		ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(c.id_nomenclature)) AS label
		
		FROM oeasc.t_declarations d
		JOIN oeasc.cor_nomenclature_declarations_essence_complementaire c
			ON d.id_declaration = c.id_declaration
		GROUP BY d.id_declaration
	),

    SELECT
	d.id_declaration,
	TO_CHAR(d.meta_create_date, 'YYYY-MM-DD') AS "Date (A M J)",

	declarant.id_declarant,
	declarant.declarant AS "Déclarant",

	
        foret.label_foret AS "Nom forêt",
        foret.statut AS "Statut forêt",
        foret.document AS "Documentée",
        
        communes.noms_communes AS "Commnune(s)",

        peuplement.essence_1_mnemo,
        peuplement.essence_1_label,
        
        peuplement_essence_2.label AS "peuplement_essence_2_label",
        peuplement_essence_2.mnemo AS "peuplement_essence_2_mnemo",

        peuplement_essence_3.label AS "peuplement_essence_3_label",
        peuplement_essence_3.mnemo AS "peuplement_essence_3_mnemo"
	
        
        FROM oeasc.t_declarations d
	JOIN declarant
		ON declarant.id_declarant = d.id_declarant
        JOIN foret 
		ON foret.id_foret = d.id_foret
	JOIN communes
		ON communes.id_foret = foret.id_foret
	JOIN peuplement
		ON peuplement.id_declaration = d.id_declaration
	JOIN peuplement_essence_2
		ON peuplement_essence_2.id_declaration = d.id_declaration
	JOIN peuplement_essence_3
		ON peuplement_essence_3.id_declaration = d.id_declaration
	
	ORDER BY d.id_declaration;

SELECT * FROM oeasc.v_declarations
