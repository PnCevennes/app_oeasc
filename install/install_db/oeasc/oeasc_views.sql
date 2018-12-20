DROP VIEW IF EXISTS oeasc.v_declarations;
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
        (SELECT ARRAY_AGG(id_area)
            FROM oeasc.cor_areas_forets c
            WHERE c.id_foret = d.id_foret) AS areas_foret,
        (SELECT ARRAY_AGG(id_area)
            FROM oeasc.cor_areas_declarations c
            WHERE c.id_declaration = d.id_declaration) as areas_localisation,
        d.id_nomenclature_peuplement_type,
        d.id_nomenclature_peuplement_origine,
        d.id_nomenclature_peuplement_essence_principale,
        (SELECT ARRAY_AGG(id_nomenclature)
            FROM oeasc.cor_nomenclature_declarations_essence_secondaire c
            WHERE c.id_declaration = d.id_declaration) as nomenclatures_peuplement_essence_secondaire,
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
        JOIN oeasc.t_forets AS f ON d.id_foret = f.id_foret
;
