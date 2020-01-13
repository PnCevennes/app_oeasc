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
		ref_geo.get_area_names(ARRAY_AGG(l.id_area)) AS noms
		
		FROM oeasc.t_forets f
		JOIN oeasc.cor_areas_forets c
			ON c.id_foret = f.id_foret
		JOIN ref_geo.l_areas l
			ON l.id_type = ref_geo.get_id_type('OEASC_COMMUNE')
				AND l.id_area = c.id_area
		GROUP BY f.id_foret
	),
	
	parcelles AS ( SELECT 
		d.id_declaration,
		ref_geo.get_area_names(ARRAY_AGG(l.id_area)) AS noms
		
		FROM oeasc.t_declarations d
		JOIN oeasc.cor_areas_declarations c
			ON c.id_declaration = d.id_declaration
		JOIN ref_geo.l_areas l
			ON l.id_type IN (
				ref_geo.get_id_type('OEASC_ONF_UG'),
				ref_geo.get_id_type('OEASC_ONF_CADASTRE')
				)
				AND l.id_area = c.id_area
		GROUP BY d.id_declaration
	),

	secteurs AS ( SELECT 
		d.id_declaration,
		ref_geo.get_area_names(ARRAY_AGG(l.id_area)) AS noms,
		ARRAY_AGG(l.id_area) AS ids
		
		FROM oeasc.t_declarations d
		JOIN oeasc.cor_areas_declarations c
			ON c.id_declaration = d.id_declaration
		JOIN ref_geo.l_areas l
			ON l.id_type = ref_geo.get_id_type('OEASC_SECTEUR')
				AND l.id_area = c.id_area
				
		GROUP BY d.id_declaration
	),
	
	declarant AS ( SELECT
		r.id_role AS "id_declarant",
		CONCAT(UPPER(r.nom_role), ' ', r.prenom_role) AS "declarant",
		r.organisme
		FROM utilisateurs.t_roles r
	),
	
	peuplement AS ( SELECT
		id_declaration,
		
		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_type) AS peuplement_type_mnemo,
		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_origine) AS peuplement_origine_mnemo,
		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_essence_principale) AS peuplement_ess_1_mnemo,
		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_paturage_statut) AS peuplement_paturage_statut_mnemo,
		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_paturage_frequence) AS peuplement_paturage_frequence_mnemo,

		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_type) AS peuplement_type_label,
		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_origine) AS peuplement_origine_label,
		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_essence_principale) AS peuplement_ess_1_label,
		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_paturage_statut) AS peuplement_paturage_statut_label,
		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_paturage_frequence) AS peuplement_paturage_frequence_label
		
		FROM oeasc.t_declarations d
	),
	
	peuplement_nomenclatures AS ( SELECT
		d.id_declaration,

		ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT c_maturite.id_nomenclature)) AS peuplement_maturite_mnemo,
		ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT c_ess_2.id_nomenclature)) AS peuplement_ess_2_mnemo,
		ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT c_ess_3.id_nomenclature)) AS peuplement_ess_3_mnemo,
		ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT c_paturage_type.id_nomenclature)) AS peuplement_paturage_type_mnemo,
		ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT c_paturage_saison.id_nomenclature)) AS peuplement_paturage_saison_mnemo,
		ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT c_protection_type.id_nomenclature)) AS peuplement_protection_type_mnemo,
		ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT c_espece.id_nomenclature)) AS espece_mnemo,

		ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT c_maturite.id_nomenclature)) AS peuplement_maturite_label,
		ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT c_ess_2.id_nomenclature)) AS peuplement_ess_2_label,
		ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT c_ess_3.id_nomenclature)) AS peuplement_ess_3_label,
		ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT c_paturage_type.id_nomenclature)) AS peuplement_paturage_type_label,
		ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT c_paturage_saison.id_nomenclature)) AS peuplement_paturage_saison_label,
		ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT c_protection_type.id_nomenclature)) AS peuplement_protection_type_label,
		ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT c_espece.id_nomenclature)) AS espece_label
		
		FROM oeasc.t_declarations d
		JOIN oeasc.cor_nomenclature_declarations_essence_secondaire c_ess_2
			ON d.id_declaration = c_ess_2.id_declaration
		JOIN oeasc.cor_nomenclature_declarations_essence_complementaire c_ess_3
			ON d.id_declaration = c_ess_3.id_declaration
		JOIN oeasc.cor_nomenclature_declarations_maturite c_maturite
			ON d.id_declaration = c_maturite.id_declaration
		JOIN oeasc.cor_nomenclature_declarations_paturage_type c_paturage_type
			ON d.id_declaration = c_paturage_type.id_declaration
		JOIN oeasc.cor_nomenclature_declarations_paturage_saison c_paturage_saison
			ON d.id_declaration = c_paturage_saison.id_declaration
		JOIN oeasc.cor_nomenclature_declarations_protection_type c_protection_type
			ON d.id_declaration = c_protection_type.id_declaration
		JOIN oeasc.cor_nomenclature_declarations_espece AS c_espece
			ON d.id_declaration = c_espece.id_declaration

		GROUP BY d.id_declaration
	),

	degat_type AS ( SELECT
		deg.id_declaration,
		ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT deg.id_nomenclature_degat_type)) AS degat_type_mnemo,
		ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT deg.id_nomenclature_degat_type)) AS degat_type_label

		FROM oeasc.t_degats deg
		GROUP BY deg.id_declaration
	),

	centroid AS ( SELECT
		id_declaration,
		ST_X(center) AS x,
		ST_Y(center) AS y
		FROM ( SELECT 
			id_declaration,
			ST_CENTROID(ST_UNION(l.geom_4326)) AS center
			FROM oeasc.cor_areas_declarations c
			JOIN ref_geo.l_areas l
				ON l.id_area = c.id_area
					AND l.id_type IN (
						ref_geo.get_id_type('OEASC_CADASTRE'),
						ref_geo.get_id_type('OEASC_ONF_UG'))
			GROUP BY id_declaration				
		)a
	)

	
    SELECT
	d.id_declaration,
	TO_CHAR(d.meta_create_date, 'DD-MM-YYYY') AS "Date",

	u.id_declarant,
	u.declarant AS "Déclarant",
	u.organisme AS "Organisme",

	f.id_foret, 
        f.label_foret AS "Nom forêt",
        f.statut AS "Statut forêt",
        f.document AS "Documentée",
        
        c.noms AS "Commnune(s)",
	s.noms AS "Secteur",
	pa.noms AS "Parcelle(s)",

	p.peuplement_type_mnemo,
	p.peuplement_origine_mnemo,	
        pn.peuplement_maturite_mnemo,
        p.peuplement_ess_1_mnemo,
        pn.peuplement_ess_2_mnemo,
        pn.peuplement_ess_3_mnemo,
        p.peuplement_paturage_statut_mnemo,
        p.peuplement_paturage_frequence_mnemo,
	pn.peuplement_paturage_type_mnemo,
	pn.peuplement_paturage_saison_mnemo,
	pn.peuplement_protection_type_mnemo,
	pn.espece_mnemo,

	p.peuplement_type_label,
	p.peuplement_origine_label,	
        pn.peuplement_maturite_label,
        p.peuplement_ess_1_label,
        pn.peuplement_ess_2_label,
        pn.peuplement_ess_3_label,
        p.peuplement_paturage_statut_label,
        p.peuplement_paturage_frequence_label,
	pn.peuplement_paturage_type_label,
	pn.peuplement_paturage_saison_label,
	pn.peuplement_protection_type_label,
	pn.espece_label,

	deg.degat_type_mnemo,
	deg.degat_type_label,

	ARRAY[ce.y, ce.x] as centroid

        
        FROM oeasc.t_declarations d
	JOIN declarant u
		ON u.id_declarant = d.id_declarant
        JOIN foret f
		ON f.id_foret = d.id_foret
	JOIN communes c
		ON c.id_foret = f.id_foret
	JOIN parcelles pa
		ON pa.id_declaration = d.id_declaration
	JOIN secteurs s
		ON s.id_declaration = d.id_declaration
	JOIN peuplement p
		ON p.id_declaration = d.id_declaration
	LEFT JOIN peuplement_nomenclatures pn
		ON pn.id_declaration = d.id_declaration
	JOIN degat_type deg
		ON deg.id_declaration = d.id_declaration
	JOIN centroid ce
		ON ce.id_declaration = d.id_declaration

	
	ORDER BY d.id_declaration;

SELECT * FROM oeasc.v_declarations
