DROP VIEW IF EXISTS oeasc.v_declarations CASCADE;
CREATE OR REPLACE VIEW oeasc.v_declarations AS
    SELECT
        d.id_declaration,
        d.id_declarant,
        CONCAT(UPPER(r.nom_role), ' ', r.prenom_role) as declarant,
        r.organisme,
        f.label_foret,
        f.b_statut_public,
        f.b_document,
        d.meta_create_date as date,
        (SELECT ARRAY_AGG(c.id_area)
            FROM oeasc.cor_areas_forets c
            JOIN ref_geo.l_areas l
		ON c.id_area = l.id_area
	    WHERE c.id_foret = d.id_foret
            AND l.id_type in (
                    ref_geo.get_id_type('OEASC_COMMUNE')))
            AS areas_communes,
        (SELECT ARRAY_AGG(c.id_area)
            FROM oeasc.cor_areas_declarations c
            JOIN ref_geo.l_areas l
		ON c.id_area = l.id_area
            WHERE c.id_declaration = d.id_declaration
		AND l.id_type in (
                    ref_geo.get_id_type('OEASC_ONF_UG'),
                    ref_geo.get_id_type('OEASC_ONF_PRF'),
                    ref_geo.get_id_type('OEASC_CADASTRE')
                    )) as areas_localisation,
        (SELECT ARRAY_AGG(c.id_area)
            FROM oeasc.cor_areas_declarations c
            JOIN ref_geo.l_areas l
		ON c.id_area = l.id_area
            WHERE c.id_declaration = d.id_declaration
		AND l.id_type in (
                    ref_geo.get_id_type('OEASC_SECTEUR')
                    )) as areas_secteur,
        d.id_nomenclature_peuplement_type,
        d.id_nomenclature_peuplement_origine,
        (SELECT ARRAY_AGG(id_nomenclature)
            FROM oeasc.cor_nomenclature_declarations_maturite c
            WHERE c.id_declaration = d.id_declaration) as nomenclatures_peuplement_maturite,

        d.id_nomenclature_peuplement_essence_principale,
        (SELECT ARRAY_AGG(id_nomenclature)
            FROM oeasc.cor_nomenclature_declarations_essence_secondaire c
            WHERE c.id_declaration = d.id_declaration) as nomenclatures_peuplement_essence_secondaire,
        (SELECT ARRAY_AGG(id_nomenclature)
            FROM oeasc.cor_nomenclature_declarations_essence_complementaire c
            WHERE c.id_declaration = d.id_declaration) as nomenclatures_peuplement_essence_complementaire,

        d.id_nomenclature_peuplement_paturage_statut,
        d.id_nomenclature_peuplement_paturage_frequence,
        (SELECT ARRAY_AGG(id_nomenclature)
            FROM oeasc.cor_nomenclature_declarations_paturage_type c
            WHERE c.id_declaration = d.id_declaration) as nomenclatures_peuplement_paturage_type,
        (SELECT ARRAY_AGG(id_nomenclature)
            FROM oeasc.cor_nomenclature_declarations_paturage_saison c
            WHERE c.id_declaration = d.id_declaration) as nomenclatures_peuplement_paturage_saison,

        (SELECT ARRAY_AGG(id_nomenclature)
            FROM oeasc.cor_nomenclature_declarations_protection_type c
            WHERE c.id_declaration = d.id_declaration) as nomenclatures_peuplement_protection_type,
        d.autre_protection,

        (SELECT ARRAY_AGG(id_nomenclature)
            FROM oeasc.cor_nomenclature_declarations_espece c
            WHERE c.id_declaration = d.id_declaration) as nomenclatures_peuplement_espece,
        id_nomenclature_peuplement_acces,


        (SELECT ARRAY_AGG(id_nomenclature_degat_type)
            FROM oeasc.t_degats deg
            WHERE deg.id_declaration = d.id_declaration) as nomenclatures_degat_type,
        (SELECT ARRAY[ST_Y(center), ST_X(center)] 
            FROM (SELECT ST_CENTROID(ST_UNION(l.geom_4326)) as center
                FROM oeasc.cor_areas_declarations c
                JOIN ref_geo.l_areas l ON c.id_area = l.id_area AND l.id_type != ref_geo.get_id_type('OEASC_SECTEUR')
                WHERE c.id_declaration=d.id_declaration
        )a) AS centroid
        FROM oeasc.t_declarations AS d
        JOIN utilisateurs.t_roles AS r ON r.id_role = d.id_declarant
        JOIN oeasc.t_forets AS f ON d.id_foret = f.id_foret;

SELECT * FROM oeasc.v_declarations






-- DROP FUNCTION ref_nomenclatures.get_nomenclature_mnemonique(integer);

DROP VIEW IF EXISTS oeasc.vpretty_declarations CASCADE;
CREATE OR REPLACE VIEW oeasc.vpretty_declarations AS
	SELECT 
		id_declaration AS id,
		declarant AS "Nom declarant",
		organisme AS "Orgnaisme",
		date AS "Date",
		label_foret AS "Nom forêt",
		CASE WHEN b_statut_public THEN 'Public' ELSE 'Privé' END as "Statut forêt",
		CASE WHEN b_document THEN 'Oui' ELSE 'non' END as "Documentée",
		ref_geo.get_area_names(areas_secteur) AS "Secteur",
		ref_geo.get_area_names(areas_communes) AS "Commnune(s)",
		ref_geo.get_area_names(areas_localisation) AS "Parcelle(s)",
		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_essence_principale) AS "Ess. 1",
		ref_nomenclatures.get_nomenclature_mnemoniques(nomenclatures_peuplement_essence_secondaire) AS "Ess. 2",
		ref_nomenclatures.get_nomenclature_mnemoniques(nomenclatures_peuplement_essence_complementaire) AS "Ess. 3",
		

		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_type) AS "Type de peuplement",
		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_origine) AS "Origine du peuplement",
		ref_nomenclatures.get_nomenclature_mnemoniques(nomenclatures_peuplement_maturite) AS "Maturité du peuplement",
	
		ref_nomenclatures.get_nomenclature_mnemoniques(nomenclatures_peuplement_paturage_type) AS "Type de pâturage",
		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_paturage_statut) AS "Statut du pâturage",
		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_paturage_frequence) AS "Fréquence du pâturage",
		ref_nomenclatures.get_nomenclature_mnemoniques(nomenclatures_peuplement_paturage_saison) AS "Saisonalité du pâturage",
		ref_nomenclatures.get_nomenclature_mnemoniques(nomenclatures_peuplement_protection_type) AS "Type de protection",
		autre_protection AS "Autre protection",
		ref_nomenclatures.get_nomenclature_mnemoniques(nomenclatures_peuplement_espece) AS "Espèces avéreés",
		ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_acces) AS "Acces",
		'a'
		
	FROM oeasc.v_declarations;
	

SELECT * FROM oeasc.vpretty_declarations;

DROP VIEW IF EXISTS oeasc.vl_declarations;
CREATE OR REPLACE VIEW oeasc.vl_declarations AS
    SELECT
        v.*,
        ( SELECT ST_UNION(l.geom)
            FROM oeasc.cor_areas_declarations c
            JOIN ref_geo.l_areas l
                ON l.id_area = c.id_area
            WHERE c.id_declaration = d.id_declaration
                AND l.id_type in (
                    ref_geo.get_id_type('OEASC_ONF_UG'),
                    ref_geo.get_id_type('OEASC_CADASTRE')
                    )
        ) AS geom
    FROM oeasc.t_declarations AS d
    JOIN oeasc.v_declarations AS v
        ON d.id_declaration = v.id_declaration;

SELECT * FROM oeasc.vl_declarations
