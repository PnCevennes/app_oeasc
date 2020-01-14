-- vue pour tableau et base pour les reste
DROP VIEW IF EXISTS oeasc.v_declarations CASCADE;
CREATE OR REPLACE VIEW oeasc.v_declarations AS

    WITH

    foret AS ( SELECT 
        f.id_foret,
        label_foret,
        b_document,
        b_statut_public,
        CASE WHEN b_statut_public THEN 'Public' ELSE 'Privé' END AS statut_public,
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
        LEFT JOIN ref_geo.l_areas l
            ON l.id_type IN (
                ref_geo.get_id_type('OEASC_ONF_UG'),
                ref_geo.get_id_type('OEASC_ONF_PRF'),
                ref_geo.get_id_type('OEASC_CADASTRE')
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
        
        peuplement_surface,

        ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_type) AS peuplement_type_mnemo,
        ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_origine) AS peuplement_origine_mnemo,
        ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_essence_principale) AS peuplement_ess_1_mnemo,
        ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_paturage_statut) AS peuplement_paturage_statut_mnemo,
        ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_paturage_frequence) AS peuplement_paturage_frequence_mnemo,
        ref_nomenclatures.get_nomenclature_mnemonique(id_nomenclature_peuplement_acces) AS peuplement_acces_mnemo,

        ref_nomenclatures.get_nomenclature_label(id_nomenclature_peuplement_type) AS peuplement_type_label,
        ref_nomenclatures.get_nomenclature_label(id_nomenclature_peuplement_origine) AS peuplement_origine_label,
        ref_nomenclatures.get_nomenclature_label(id_nomenclature_peuplement_essence_principale) AS peuplement_ess_1_label,
        ref_nomenclatures.get_nomenclature_label(id_nomenclature_peuplement_paturage_statut) AS peuplement_paturage_statut_label,
        ref_nomenclatures.get_nomenclature_label(id_nomenclature_peuplement_paturage_frequence) AS peuplement_paturage_frequence_label,
        ref_nomenclatures.get_nomenclature_label(id_nomenclature_peuplement_acces) AS peuplement_acces_label
        
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
        LEFT JOIN oeasc.cor_nomenclature_declarations_essence_secondaire c_ess_2
            ON d.id_declaration = c_ess_2.id_declaration
        LEFT JOIN oeasc.cor_nomenclature_declarations_essence_complementaire c_ess_3
            ON d.id_declaration = c_ess_3.id_declaration
        LEFT JOIN oeasc.cor_nomenclature_declarations_maturite c_maturite
            ON d.id_declaration = c_maturite.id_declaration
        LEFT JOIN oeasc.cor_nomenclature_declarations_paturage_type c_paturage_type
            ON d.id_declaration = c_paturage_type.id_declaration
        LEFT JOIN oeasc.cor_nomenclature_declarations_paturage_saison c_paturage_saison
            ON d.id_declaration = c_paturage_saison.id_declaration
        LEFT JOIN oeasc.cor_nomenclature_declarations_protection_type c_protection_type
            ON d.id_declaration = c_protection_type.id_declaration
        LEFT JOIN oeasc.cor_nomenclature_declarations_espece AS c_espece
            ON d.id_declaration = c_espece.id_declaration

        GROUP BY d.id_declaration
    ),

    degat_type AS ( SELECT
        deg.id_declaration,
        ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT deg.id_nomenclature_degat_type)) AS degat_types_mnemo,
        ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT deg.id_nomenclature_degat_type)) AS degat_types_label

        FROM oeasc.t_degats deg
        GROUP BY deg.id_declaration
    ),

    centroid AS ( SELECT
        id_declaration,
        ARRAY[ST_Y(center), ST_X(center)] AS centroid        
        FROM ( SELECT 
            id_declaration,
            ST_CENTROID(ST_UNION(l.geom_4326)) AS center
            FROM oeasc.cor_areas_declarations c
            JOIN ref_geo.l_areas l
                ON l.id_area = c.id_area
                    AND l.id_type IN (
                        ref_geo.get_id_type('OEASC_CADASTRE'),
                        ref_geo.get_id_type('OEASC_ONF_UG'),
                        ref_geo.get_id_type('OEASC_ONF_PRF'))

            GROUP BY id_declaration                
        )a
    ),

    areas_localisation AS ( SELECT
        d.id_declaration,
        ARRAY_AGG(DISTINCT c.id_area) AS areas,
        ref_geo.get_area_names(ARRAY_AGG(DISTINCT c.id_area)) AS names
        
        FROM oeasc.t_declarations d
        JOIN oeasc.cor_areas_declarations c
            ON d.id_declaration = c.id_declaration
        JOIN ref_geo.l_areas l
            ON l.id_area = c.id_area
        WHERE 
            l.id_type IN (ref_geo.get_id_type('OEASC_ONF_UG'), ref_geo.get_id_type('OEASC_CADASTRE'))
        GROUP BY d.id_declaration
    ),

    areas_foret AS ( SELECT
        d.id_declaration,
        ARRAY_AGG(DISTINCT c.id_area) AS areas,
        ref_geo.get_area_names(ARRAY_AGG(DISTINCT c.id_area)) AS names
        
        FROM oeasc.t_declarations d
        JOIN oeasc.cor_areas_forets c
            ON d.id_declaration = c.id_foret
        JOIN ref_geo.l_areas l
            ON l.id_area = c.id_area
        WHERE 
            l.id_type IN (ref_geo.get_id_type('OEASC_ONF_FRT'), ref_geo.get_id_type('OEASC_DGD'))
        GROUP BY d.id_declaration
    )

    SELECT
    d.id_declaration,
    TO_CHAR(d.meta_create_date, 'DD-MM-YYYY') AS declaration_date,
    d.commentaire,

    u.id_declarant,
    u.declarant,
    u.organisme,

    f.id_foret,
    f.label_foret,
    f.statut_public,
    f.document,
    f.b_statut_public,
    f.b_document,

    c.noms AS communes,
    s.noms AS secteur,
    pa.noms AS parcelles,

    p.peuplement_surface,

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
    p.peuplement_acces_mnemo,

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
    peuplement_acces_label,

    deg.degat_types_mnemo,
    deg.degat_types_label,

    ce.centroid,
    af.areas AS areas_foret,
    ad.areas AS areas_localisation,
    af.names AS names_foret,
    ad.names AS names_localisation

    FROM oeasc.t_declarations d
    JOIN declarant u
        ON u.id_declarant = d.id_declarant
        JOIN foret f
        ON f.id_foret = d.id_foret
    LEFT JOIN communes c
        ON c.id_foret = f.id_foret
    JOIN parcelles pa
        ON pa.id_declaration = d.id_declaration
    JOIN secteurs s
        ON s.id_declaration = d.id_declaration
    JOIN peuplement p
        ON p.id_declaration = d.id_declaration
    JOIN peuplement_nomenclatures pn
        ON pn.id_declaration = d.id_declaration
    JOIN degat_type deg
        ON deg.id_declaration = d.id_declaration
    JOIN centroid ce
        ON ce.id_declaration = d.id_declaration
    JOIN areas_localisation ad
        ON ad.id_declaration = d.id_declaration
    JOIN areas_foret af
        ON af.id_declaration = d.id_declaration;


DROP VIEW IF EXISTS oeasc.v_degats CASCADE;
CREATE OR REPLACE VIEW oeasc.v_degats AS

    SELECT 
        d.id_declaration AS id_declaration_degat,

        ref_nomenclatures.get_nomenclature_mnemonique(d.id_nomenclature_degat_type) AS degat_type_mnemo,
        ref_nomenclatures.get_nomenclature_mnemonique(de.id_nomenclature_degat_essence) AS degat_essence_mnemo,
        ref_nomenclatures.get_nomenclature_mnemonique(de.id_nomenclature_degat_gravite) AS degat_gravite_mnemo,
        ref_nomenclatures.get_nomenclature_mnemonique(de.id_nomenclature_degat_etendue) AS degat_etendue_mnemo,
        ref_nomenclatures.get_nomenclature_mnemonique(de.id_nomenclature_degat_anteriorite) AS degat_anteriorite_mnemo,

        ref_nomenclatures.get_nomenclature_label(d.id_nomenclature_degat_type) AS degat_type_label,
        ref_nomenclatures.get_nomenclature_label(de.id_nomenclature_degat_essence) AS degat_essence_label,
        ref_nomenclatures.get_nomenclature_label(de.id_nomenclature_degat_gravite) AS degat_gravite_label,
        ref_nomenclatures.get_nomenclature_label(de.id_nomenclature_degat_etendue) AS degat_etendue_label,
        ref_nomenclatures.get_nomenclature_label(de.id_nomenclature_degat_anteriorite) AS degat_anteriorite_label
        
    FROM oeasc.t_degats d
    LEFT JOIN oeasc.t_degat_essences de
        ON de.id_degat = d.id_degat
    ORDER BY id_declaration
    ;


-- pour la carteaffichage degat???
DROP VIEW IF EXISTS oeasc.v_declaration_degats CASCADE;
CREATE OR REPLACE VIEW oeasc.v_declaration_degats AS

    SELECT 
        vd.*,
        vdeg.*
        FROM oeasc.v_declarations vd
        JOIN oeasc.v_degats vdeg
            ON vdeg.id_declaration_degat = vd.id_declaration;


DROP VIEW IF EXISTS oeasc.v_declaration_geoms CASCADE;
CREATE OR REPLACE VIEW oeasc.v_declaration_geoms AS

    SELECT 
        c.id_declaration,
        ST_UNION(geom_4326) AS geom
        
    FROM oeasc.cor_areas_declarations c    
    JOIN ref_geo.l_areas l
        ON l.id_area = c.id_area
            AND l.id_type IN (ref_geo.get_id_type('OEASC_CADASTRE'), ref_geo.get_id_type('OEASC_ONF_UG'))
    GROUP BY id_declaration
    ;


-- vues pour les CSV 1 ligne / declaration
DROP VIEW IF EXISTS oeasc.v_export_declarations_csv CASCADE;
CREATE OR REPLACE VIEW oeasc.v_export_declarations_csv AS

    SELECT 
        vd.id_declaration AS "id",
        vd.declaration_date AS "Date",
        vd.declarant AS "Déclarant",
        vd.organisme AS "Organisme",
        vd.label_foret AS "Nom forêt",
        vd.statut_public AS "Statut forêt",
        vd.document AS "Documentée",
        vd.communes AS "Commune(s)",
        vd.secteur AS "Secteur",
        vd.parcelles AS "Parcelle(s)",
        vd.peuplement_type_mnemo AS "Peu. type",
        vd.peuplement_origine_mnemo AS "Peu. ori.",    
        vd.peuplement_maturite_mnemo AS "Peu. mat.",
        vd.peuplement_ess_1_mnemo AS "Ess. 1",
        vd.peuplement_ess_2_mnemo AS "Ess. 2",
        vd.peuplement_ess_3_mnemo AS "Ess. 3",
        vd.peuplement_paturage_statut_mnemo AS "Pât. stat.",
        vd.peuplement_paturage_frequence_mnemo AS "Pât. freq.",
        vd.peuplement_paturage_type_mnemo AS "Pât. type",
        vd.peuplement_paturage_saison_mnemo AS "Pât. sais.",
        vd.peuplement_protection_type_mnemo AS "Pro. type",
        vd.espece_mnemo AS "Espèce(s)",
        vd.degat_types_mnemo AS "Dég. types"
        
        FROM oeasc.v_declarations vd
        ;


-- vues pour les CSV 1 degat / ligne
DROP VIEW IF EXISTS oeasc.v_export_declaration_degats_csv CASCADE;
CREATE OR REPLACE VIEW oeasc.v_export_declaration_degats_csv AS

    SELECT 
        ved.*,
        vdeg.degat_type_mnemo AS "Dég. type",
        vdeg.degat_essence_mnemo AS "Dég. ess.",
        vdeg.degat_gravite_mnemo AS "Dég. grâ.",
        vdeg.degat_etendue_mnemo AS "Dég. éten.",
        vdeg.degat_anteriorite_mnemo AS "Dég. ant."
        
        FROM oeasc.v_export_declarations_csv ved
        JOIN oeasc.v_degats vdeg
            ON vdeg.id_declaration_degat = ved.id
        ;


-- shape avec 1 déclaration / ligne
DROP VIEW IF EXISTS oeasc.v_export_declarations_shape CASCADE;
CREATE OR REPLACE VIEW oeasc.v_export_declarations_shape AS

    SELECT 
        ved.*,
        vg.geom
            
        FROM oeasc.v_export_declarations_csv ved
        JOIN oeasc.v_declaration_geoms vg
            ON vg.id_declaration = ved.id
        ;


-- shape avec 1 declaration / dégât
DROP VIEW IF EXISTS oeasc.v_export_declaration_degats_shape CASCADE;
CREATE OR REPLACE VIEW oeasc.v_export_declaration_degats_shape AS

    SELECT 
        ved.*,
        vg.geom
            
        FROM oeasc.v_export_declaration_degats_csv ved
        JOIN oeasc.v_declaration_geoms vg
            ON vg.id_declaration = ved.id
        ;

SELECT * FROM oeasc.v_declarations;
--SELECT * FROM oeasc.v_declaration_degats;
--SELECT * FROM oeasc.v_export_declarations_csv;
--SELECT * FROM oeasc.v_export_declaration_degats_csv;
--SELECT * FROM oeasc.v_declaration_geoms;
--SELECT * FROM oeasc.v_export_declarations_shape;
--SELECT * FROM oeasc.v_export_declaration_degats_shape;

