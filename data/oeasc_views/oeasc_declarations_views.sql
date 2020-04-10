

-- vue pour tableau et base pour les reste
DROP VIEW IF EXISTS oeasc_declarations.v_declarations CASCADE;
CREATE OR REPLACE VIEW oeasc_declarations.v_declarations AS

    WITH

    foret AS ( SELECT 
        f.id_foret,
        label_foret,
        b_document,
        b_statut_public,

        CASE WHEN b_statut_public THEN 'Public' ELSE 'Privé' END AS statut_public,

        CASE WHEN b_document THEN 'Oui' ELSE 'Non' END AS document,

        CASE 
            WHEN b_statut_public AND b_document THEN 'Public (avec DGD)' 
            WHEN b_statut_public AND NOT b_document THEN 'Public (sans DGD)'
            WHEN NOT b_statut_public AND b_document THEN 'Privé (avec DGD)' 
            WHEN NOT b_statut_public AND NOT b_document THEN 'Privé (sans DGD)'
            ELSE ''
        END AS type_foret,

        ref_nomenclatures.get_nomenclature_label(p.id_nomenclature_proprietaire_type) AS foret_type_label


        FROM oeasc_forets.t_forets f 
        JOIN oeasc_forets.t_proprietaires p
            ON p.id_proprietaire = f.id_proprietaire
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
        ref_nomenclatures.get_nomenclature_label(id_nomenclature_peuplement_acces) AS peuplement_acces_label,
        
        ref_nomenclatures.get_nomenclature_code(id_nomenclature_peuplement_type) AS peuplement_type_code,
        ref_nomenclatures.get_nomenclature_code(id_nomenclature_peuplement_origine) AS peuplement_origine_code,
        ref_nomenclatures.get_nomenclature_code(id_nomenclature_peuplement_essence_principale) AS peuplement_ess_1_code,
        ref_nomenclatures.get_nomenclature_code(id_nomenclature_peuplement_paturage_statut) AS peuplement_paturage_statut_code,
        ref_nomenclatures.get_nomenclature_code(id_nomenclature_peuplement_paturage_frequence) AS peuplement_paturage_frequence_code,
        ref_nomenclatures.get_nomenclature_code(id_nomenclature_peuplement_acces) AS peuplement_acces_code

        FROM oeasc_declarations.t_declarations d
    ),
    
    peuplement_nomenclatures AS ( SELECT
        d.id_declaration,



        ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT c_maturite.id_nomenclature)) AS peuplement_maturite_mnemo,
        ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT c_origine.id_nomenclature)) AS peuplement_origine2_mnemo,
        ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT c_ess_2.id_nomenclature)) AS peuplement_ess_2_mnemo,
        ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT c_ess_3.id_nomenclature)) AS peuplement_ess_3_mnemo,
        ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT c_paturage_type.id_nomenclature)) AS peuplement_paturage_type_mnemo,
        ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT c_paturage_saison.id_nomenclature)) AS peuplement_paturage_saison_mnemo,
        ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT c_protection_type.id_nomenclature)) AS peuplement_protection_type_mnemo,
        ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT c_espece.id_nomenclature)) AS espece_mnemo,

        ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT c_maturite.id_nomenclature)) AS peuplement_maturite_label,
        ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT c_origine.id_nomenclature)) AS peuplement_origine2_label,
        ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT c_ess_2.id_nomenclature)) AS peuplement_ess_2_label,
        ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT c_ess_3.id_nomenclature)) AS peuplement_ess_3_label,
        ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT c_paturage_type.id_nomenclature)) AS peuplement_paturage_type_label,
        ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT c_paturage_saison.id_nomenclature)) AS peuplement_paturage_saison_label,
        ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT c_protection_type.id_nomenclature)) AS peuplement_protection_type_label,
        ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT c_espece.id_nomenclature)) AS espece_label,
        
        ref_nomenclatures.get_nomenclature_codes(ARRAY_AGG(DISTINCT c_maturite.id_nomenclature)) AS peuplement_maturite_code,
        ref_nomenclatures.get_nomenclature_codes(ARRAY_AGG(DISTINCT c_origine.id_nomenclature)) AS peuplement_origine2_code,
        ref_nomenclatures.get_nomenclature_codes(ARRAY_AGG(DISTINCT c_ess_2.id_nomenclature)) AS peuplement_ess_2_code,
        ref_nomenclatures.get_nomenclature_codes(ARRAY_AGG(DISTINCT c_ess_3.id_nomenclature)) AS peuplement_ess_3_code,
        ref_nomenclatures.get_nomenclature_codes(ARRAY_AGG(DISTINCT c_paturage_type.id_nomenclature)) AS peuplement_paturage_type_code,
        ref_nomenclatures.get_nomenclature_codes(ARRAY_AGG(DISTINCT c_paturage_saison.id_nomenclature)) AS peuplement_paturage_saison_code,
        ref_nomenclatures.get_nomenclature_codes(ARRAY_AGG(DISTINCT c_protection_type.id_nomenclature)) AS peuplement_protection_type_code,
        ref_nomenclatures.get_nomenclature_codes(ARRAY_AGG(DISTINCT c_espece.id_nomenclature)) AS espece_code

        FROM oeasc_declarations.t_declarations d
        LEFT JOIN oeasc_declarations.cor_nomenclature_declarations_essence_secondaire c_ess_2
            ON d.id_declaration = c_ess_2.id_declaration
        LEFT JOIN oeasc_declarations.cor_nomenclature_declarations_essence_complementaire c_ess_3
            ON d.id_declaration = c_ess_3.id_declaration
        LEFT JOIN oeasc_declarations.cor_nomenclature_declarations_maturite c_maturite
            ON d.id_declaration = c_maturite.id_declaration
        LEFT JOIN oeasc_declarations.cor_nomenclature_declarations_paturage_type c_paturage_type
            ON d.id_declaration = c_paturage_type.id_declaration
        LEFT JOIN oeasc_declarations.cor_nomenclature_declarations_paturage_saison c_paturage_saison
            ON d.id_declaration = c_paturage_saison.id_declaration
        LEFT JOIN oeasc_declarations.cor_nomenclature_declarations_protection_type c_protection_type
            ON d.id_declaration = c_protection_type.id_declaration
        LEFT JOIN oeasc_declarations.cor_nomenclature_declarations_espece AS c_espece
            ON d.id_declaration = c_espece.id_declaration
        LEFT JOIN oeasc_declarations.cor_nomenclature_declarations_origine AS c_origine
            ON d.id_declaration = c_origine.id_declaration

        GROUP BY d.id_declaration
    ),

    degat_type AS ( SELECT
        deg.id_declaration,
        ref_nomenclatures.get_nomenclature_mnemoniques(ARRAY_AGG(DISTINCT deg.id_nomenclature_degat_type)) AS degat_types_mnemo,
        ref_nomenclatures.get_nomenclature_labels(ARRAY_AGG(DISTINCT deg.id_nomenclature_degat_type)) AS degat_types_label,
        ref_nomenclatures.get_nomenclature_codes(ARRAY_AGG(DISTINCT deg.id_nomenclature_degat_type)) AS degat_types_code

        FROM oeasc_declarations.t_degats deg
        GROUP BY deg.id_declaration
    )

    SELECT
    d.id_declaration,
    TO_CHAR(d.meta_create_date, 'DD/MM/YYYY') AS declaration_date,
    meta_create_date,
    d.commentaire,

    d.b_peuplement_protection_existence,
    d.b_peuplement_paturage_presence,
    d.b_autorisation,
    vu.id_role AS id_declarant,
    vu.nom_complet AS declarant,
    vu.organisme,
    vu.organisme_group,

    f.id_foret,
    f.label_foret,
    f.statut_public,
    f.document,
    f.b_statut_public,
    f.b_document,
    f.type_foret,
    f.foret_type_label, 

    oeasc_declarations.get_area_names(d.id_declaration, 'OEASC_COMMUNE') AS communes,
    oeasc_declarations.get_area_names(d.id_declaration, 'OEASC_SECTEUR') AS secteur,
    CASE WHEN f.b_statut_public AND f.b_document THEN 
	oeasc_declarations.get_area_names(d.id_declaration, 'OEASC_ONF_UG')
    ELSE 
	oeasc_declarations.get_area_names(d.id_declaration, 'OEASC_CADASTRE')
    END AS parcelles,

    p.peuplement_surface,

    p.peuplement_type_mnemo,
    p.peuplement_origine_mnemo,    
    pn.peuplement_origine2_mnemo,    
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
    deg.degat_types_mnemo,

    p.peuplement_type_label,
    p.peuplement_origine_label,    
    pn.peuplement_origine2_label,    
    pn.peuplement_maturite_label,
    p.peuplement_ess_1_label,
    pn.peuplement_ess_2_label,
    pn.peuplement_ess_3_label,
    p.peuplement_paturage_statut_label,
    p.peuplement_paturage_frequence_label,
    pn.peuplement_paturage_type_label,
    pn.peuplement_paturage_saison_label,
    CASE 
	WHEN d.autre_protection IS NOT NULL THEN REPLACE(pn.peuplement_protection_type_label, 'Autre (préciser)', d.autre_protection)
	ELSE pn.peuplement_protection_type_label
	END AS peuplement_protection_type_label,
    pn.espece_label,
    peuplement_acces_label,
    deg.degat_types_label,

    p.peuplement_type_code,
    p.peuplement_origine_code,    
    pn.peuplement_origine2_code,    
    pn.peuplement_maturite_code,
    p.peuplement_ess_1_code,
    pn.peuplement_ess_2_code,
    pn.peuplement_ess_3_code,
    p.peuplement_paturage_statut_code,
    p.peuplement_paturage_frequence_code,
    pn.peuplement_paturage_type_code,
    pn.peuplement_paturage_saison_code,
    pn.peuplement_protection_type_code,
    pn.espece_code,
    peuplement_acces_code,
    deg.degat_types_code,
	
    d.centroid,

    CASE 
	WHEN f.b_statut_public AND f.b_document THEN oeasc_declarations.get_id_areas(d.id_declaration, 'OEASC_ONF_FRT')
	WHEN NOT f.b_statut_public AND f.b_document THEN oeasc_declarations.get_id_areas(d.id_declaration, 'OEASC_DGD')
	ELSE oeasc_declarations.get_id_areas(d.id_declaration, 'OEASC_SECTION')
    END AS areas_foret,

    CASE 
	WHEN f.b_statut_public AND f.b_document THEN oeasc_declarations.get_area_names(d.id_declaration, 'OEASC_ONF_FRT')
	WHEN NOT f.b_statut_public AND f.b_document THEN oeasc_declarations.get_area_names(d.id_declaration, 'OEASC_DGD')
	ELSE oeasc_declarations.get_area_names(d.id_declaration, 'OEASC_SECTION')
    END AS areas_foret_names,

    CASE
        WHEN b_valid = TRUE THEN 'Validé' 
        WHEN b_valid = FALSE THEN 'Non validé' 
        ELSE 'En attente'
    END AS valide,



    CASE 
	WHEN f.b_statut_public AND f.b_document THEN oeasc_declarations.get_id_areas(d.id_declaration, 'OEASC_ONF_UG')
    ELSE
	oeasc_declarations.get_id_areas(d.id_declaration, 'OEASC_CADASTRE')
    END AS areas_localisation
    
    FROM oeasc_declarations.t_declarations d
    JOIN oeasc_commons.v_users vu
        ON vu.id_role = d.id_declarant
    JOIN foret f
        ON f.id_foret = d.id_foret
    JOIN peuplement p
        ON p.id_declaration = d.id_declaration
    JOIN peuplement_nomenclatures pn
        ON pn.id_declaration = d.id_declaration
    JOIN degat_type deg
        ON deg.id_declaration = d.id_declaration
;

DROP VIEW IF EXISTS oeasc_declarations.vl_declarations CASCADE;
CREATE OR REPLACE VIEW oeasc_declarations.vl_declarations AS
SELECT 
    v.*,
    d.geom, 
    d.geom_4326

    FROM oeasc_declarations.v_declarations v
    JOIN oeasc_declarations.t_declarations d ON d.id_declaration = v.id_declaration;


DROP VIEW IF EXISTS oeasc_declarations.v_degats CASCADE;
CREATE OR REPLACE VIEW oeasc_declarations.v_degats AS

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
        ref_nomenclatures.get_nomenclature_label(de.id_nomenclature_degat_anteriorite) AS degat_anteriorite_label,
        
        ref_nomenclatures.get_nomenclature_code(d.id_nomenclature_degat_type) AS degat_type_code,
        ref_nomenclatures.get_nomenclature_code(de.id_nomenclature_degat_essence) AS degat_essence_code,
        ref_nomenclatures.get_nomenclature_code(de.id_nomenclature_degat_gravite) AS degat_gravite_code,
        ref_nomenclatures.get_nomenclature_code(de.id_nomenclature_degat_etendue) AS degat_etendue_code,
        ref_nomenclatures.get_nomenclature_code(de.id_nomenclature_degat_anteriorite) AS degat_anteriorite_code

    FROM oeasc_declarations.t_degats d
    LEFT JOIN oeasc_declarations.t_degat_essences de
        ON de.id_degat = d.id_degat
    ORDER BY id_declaration
    ;


-- pour la carteaffichage degat???
DROP VIEW IF EXISTS oeasc_declarations.v_declaration_degats CASCADE;
CREATE OR REPLACE VIEW oeasc_declarations.v_declaration_degats AS

    SELECT 
        vd.*,
        vdeg.*
        FROM oeasc_declarations.v_declarations vd
        JOIN oeasc_declarations.v_degats vdeg
            ON vdeg.id_declaration_degat = vd.id_declaration;



-- vues pour les CSV 1 ligne / declaration
DROP VIEW IF EXISTS oeasc_declarations.v_export_declarations_csv CASCADE;
CREATE OR REPLACE VIEW oeasc_declarations.v_export_declarations_csv AS

    SELECT 
        vd.id_declaration AS "id",
        vd.declaration_date AS "Date",
        vd.declarant AS "Déclarant",
        vd.organisme AS "Organisme",
        vd.label_foret AS "Nom forêt",
        vd.statut_public AS "Statut forêt",
        vd.document AS "Documentée",
        --vd.communes AS "Commune(s)",
        vd.secteur AS "Secteur",
        vd.parcelles AS "Parcelle(s)",
        vd.peuplement_type_mnemo AS "Peu. type",
        vd.peuplement_origine_mnemo AS "Peu. ori.",    
        vd.peuplement_origine2_mnemo AS "Peu. ori. 2",    
        vd.peuplement_maturite_mnemo AS "Peu. mat.",
        vd.peuplement_ess_1_mnemo AS "Ess. 1",
        vd.peuplement_ess_2_mnemo AS "Ess. 2",
        vd.peuplement_ess_3_mnemo AS "Ess. 3",
        vd.peuplement_paturage_statut_mnemo AS "Pât. stat.",
        vd.peuplement_paturage_frequence_mnemo AS "Pât. freq.",
        vd.peuplement_paturage_type_mnemo AS "Pât. type",
        vd.peuplement_paturage_saison_mnemo AS "Pât. sais.",
        vd.peuplement_protection_type_mnemo AS "Pro. type",
        --vd.espece_mnemo AS "Espèce(s)",
        vd.degat_types_mnemo AS "Dég. types"
        
        FROM oeasc_declarations.v_declarations vd
        ;


-- vues pour les CSV 1 degat / ligne
DROP VIEW IF EXISTS oeasc_declarations.v_export_declaration_degats_csv CASCADE;
CREATE OR REPLACE VIEW oeasc_declarations.v_export_declaration_degats_csv AS

    SELECT 
        ved."id",
        ved."Date",
        ved."Déclarant",
        ved."Organisme",
        ved."Nom forêt",
        ved."Statut forêt",
        ved."Documentée",
        ved."Secteur",
        ved."Peu. type",
        ved."Peu. ori.",    
        ved."Peu. mat.",
        ved."Ess. 1",
        ved."Ess. 2",
        ved."Pât. stat.",
        ved."Pât. freq.",
        ved."Pât. type",
        ved."Pât. sais.",
        ved."Pro. type",
        vdeg.degat_type_mnemo AS "Dég. type",
        vdeg.degat_essence_mnemo AS "Dég. ess.",
        vdeg.degat_gravite_mnemo AS "Dég. grâ.",
        vdeg.degat_etendue_mnemo AS "Dég. éten.",
        vdeg.degat_anteriorite_mnemo AS "Dég. ant."
        
        FROM oeasc_declarations.v_export_declarations_csv ved
        JOIN oeasc_declarations.v_degats vdeg
            ON vdeg.id_declaration_degat = ved.id
        ;


-- shape avec 1 déclaration / ligne
DROP VIEW IF EXISTS oeasc_declarations.v_export_declarations_shape CASCADE;
CREATE OR REPLACE VIEW oeasc_declarations.v_export_declarations_shape AS

    SELECT 
        ved.*,
        vl.geom
            
        FROM oeasc_declarations.v_export_declarations_csv ved
        JOIN oeasc_declarations.vl_declarations vl
            ON vl.id_declaration = ved.id
        ;


-- shape avec 1 declaration / dégât
DROP VIEW IF EXISTS oeasc_declarations.v_export_declaration_degats_shape CASCADE;
CREATE OR REPLACE VIEW oeasc_declarations.v_export_declaration_degats_shape AS

    SELECT 
        ved.*,
        vl.geom
            
        FROM oeasc_declarations.v_export_declaration_degats_csv ved
        JOIN oeasc_declarations.vl_declarations vl
            ON vl.id_declaration = ved.id
        ;

GRANT SELECT ON oeasc_declarations.v_declarations TO PUBLIC;
GRANT SELECT ON oeasc_declarations.v_degats TO PUBLIC;
GRANT SELECT ON oeasc_declarations.v_export_declarations_csv TO PUBLIC;
GRANT SELECT ON oeasc_declarations.v_export_declaration_degats_csv TO PUBLIC;
GRANT SELECT ON oeasc_declarations.v_export_declarations_shape TO PUBLIC;
GRANT SELECT ON oeasc_declarations.v_export_declaration_degats_shape TO PUBLIC;


-- SELECT * FROM oeasc_declarations.v_declarations WHERE id_declaration>=80;
-- SELECT * FROM oeasc_declarations.v_export_declarations_csv;
-- SELECT * FROM oeasc_declarations.v_export_declarations_csv;
-- SELECT * FROM oeasc_declarations.v_export_declaration_degats_csv;
-- SELECT * FROM oeasc_declarations.v_export_declarations_shape;
-- SELECT * FROM oeasc_declarations.v_export_declaration_degats_shape;
--SELECT peuplement_protection_type_label FROM oeasc_declarations.v_declarations WHERE id_declaration = 71
