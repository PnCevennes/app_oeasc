-- Schema oeasc_declarations

-- oeasc_declarations.t_declarations : table des déclarations
-- oeasc_declarations.t_degats : table des dégats par type de degat
-- oeasc_declarations.t_degat_essences : table des degats par essence pour chaque type de degat
-- oeasc_declarations.t_liste_nomenclature_types : liste de type de nomenclature pour les correlation declaration - nomenclature

CREATE SCHEMA IF NOT EXISTS oeasc_declarations;

CREATE TABLE IF NOT EXISTS oeasc_declarations.t_declarations
(
    id_declaration serial NOT NULL,

    -- role pour declarant

    id_declarant INTEGER,

    --foret

    id_foret INTEGER,

    -- localisation

    id_nomenclature_foret_type INTEGER,

    -- proprietaire-declarant

    id_nomenclature_proprietaire_declarant INTEGER,

    -- peuplement

    id_nomenclature_peuplement_origine INTEGER,
    id_nomenclature_peuplement_type INTEGER,
    id_nomenclature_peuplement_paturage_frequence INTEGER,
    id_nomenclature_peuplement_paturage_statut INTEGER,
    id_nomenclature_peuplement_acces INTEGER,
    id_nomenclature_peuplement_essence_principale INTEGER,
    peuplement_surface DOUBLE PRECISION,


    b_peuplement_protection_existence BOOLEAN,
    b_peuplement_paturage_presence BOOLEAN,
    b_autorisation BOOLEAN,

    autre_protection text,
    precision_localisation text,

    -- geom geometry(MultiPolygon, 2154),
    
    commentaire text,

    meta_create_date timestamp without time zone,
    meta_update_date timestamp without time zone,

    -- contraintes cle primaire

    CONSTRAINT pk_t_declaration_id_declaration PRIMARY KEY (id_declaration),

    --contrainte cle etrangere role

    CONSTRAINT fk_t_declarations_id_declarant FOREIGN KEY (id_declarant)
        REFERENCES utilisateurs.t_roles (id_role) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,

    --contrainte cle etrangere foret

    CONSTRAINT fk_t_declarations_id_foret FOREIGN KEY (id_foret)
        REFERENCES oeasc_forets.t_forets (id_foret) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    -- contraintes localisation

    CONSTRAINT fk_t_declarations_id_nomenclature_foret_type FOREIGN KEY (id_nomenclature_foret_type)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_declarations_id_nomenclature_foret_type CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_foret_type, 'OEASC_FORET_TYPE')) NOT VALID,

    -- contraintes fk nomenclatures peuplement

    CONSTRAINT fk_t_declarations_id_nomenclature_peuplement_essence_principale FOREIGN KEY (id_nomenclature_peuplement_essence_principale)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_declarations_id_nomenclature_peuplement_essence_principale CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_peuplement_essence_principale, 'OEASC_PEUPLEMENT_ESSENCE')) NOT VALID,

    CONSTRAINT fk_t_declarations_id_nomenclature_peuplement_origine FOREIGN KEY (id_nomenclature_peuplement_origine)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_declarations_id_nomenclature_peuplement_origine CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_peuplement_origine, 'OEASC_PEUPLEMENT_ORIGINE')) NOT VALID,

    CONSTRAINT fk_t_declarations_id_nomenclature_peuplement_type FOREIGN KEY (id_nomenclature_peuplement_type)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_declarations_id_nomenclature_peuplement_type CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_peuplement_type, 'OEASC_PEUPLEMENT_TYPE')) NOT VALID,

    CONSTRAINT fk_t_declarations_id_nomenclature_peuplement_paturage_frequence FOREIGN KEY (id_nomenclature_peuplement_paturage_frequence)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_declarations_id_nomenclature_peuplement_paturage_frequence CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_peuplement_paturage_frequence, 'OEASC_PEUPLEMENT_PATURAGE_FREQUENCE')) NOT VALID,

    CONSTRAINT fk_t_declarations_id_nomenclature_peuplement_acces FOREIGN KEY (id_nomenclature_peuplement_acces)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_declarations_id_nomenclature_peuplement_acces CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_peuplement_acces, 'OEASC_PEUPLEMENT_ACCES')) NOT VALID,

    CONSTRAINT fk_t_declarations_id_nomenclature_proprietaire_declarant FOREIGN KEY (id_nomenclature_proprietaire_declarant)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_declarations_id_nomenclature_proprietaire_declarant CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_proprietaire_declarant, 'OEASC_PROPRIETAIRE_DECLARANT')) NOT VALID

);


-- gestion des dates pour les declarations
DROP TRIGGER IF EXISTS trg_cor_areas_declarations ON oeasc_declarations.t_declarations;

CREATE TRIGGER tri_meta_dates_change_t_declarations
   BEFORE INSERT OR UPDATE
   ON oeasc_declarations.t_declarations
   FOR EACH ROW
   EXECUTE PROCEDURE public.fct_trg_meta_dates_change();


-- degats par type de degat

CREATE TABLE IF NOT EXISTS oeasc_declarations.t_degats
(
    id_degat serial NOT NULL,

    id_declaration INTEGER,

    id_nomenclature_degat_type serial NOT NULL,

    CONSTRAINT pk_t_degats_id_degat PRIMARY KEY (id_degat),

    CONSTRAINT fk_t_degats_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc_declarations.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_t_degats_id_nomenclature_degat_type FOREIGN KEY (id_nomenclature_degat_type)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_degats_id_nomenclature_degat_type CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_degat_type, 'OEASC_DEGAT_TYPE')) NOT VALID
);


-- degats par essence pour chaque type de degat

CREATE TABLE IF NOT EXISTS oeasc_declarations.t_degat_essences
(
    id_degat_essence serial NOT NULL,

    id_degat INTEGER,

    id_nomenclature_degat_essence INTEGER,
    id_nomenclature_degat_etendue INTEGER,
    id_nomenclature_degat_gravite INTEGER,
    id_nomenclature_degat_anteriorite INTEGER,

    CONSTRAINT pk_t_degat_essences_id_degat_essence PRIMARY KEY (id_degat_essence),

    CONSTRAINT fk_t_degat_id_degat FOREIGN KEY (id_degat)
        REFERENCES oeasc_declarations.t_degats (id_degat) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_t_degat_essences_id_nomenclature_degat_essence FOREIGN KEY (id_nomenclature_degat_essence)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT check_t_degat_type_id_nomenclature_degat_essence CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_degat_essence, 'OEASC_PEUPLEMENT_ESSENCE')) NOT VALID,

    CONSTRAINT fk_t_degat_essences_id_nomenclature_degat_etendue FOREIGN KEY (id_nomenclature_degat_etendue)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT check_t_degat_type_id_nomenclature_degat_etendue CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_degat_etendue, 'OEASC_DEGAT_ETENDUE')) NOT VALID,

    CONSTRAINT fk_t_degat_essences_id_nomenclature_degat_gravite FOREIGN KEY (id_nomenclature_degat_gravite)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT check_t_degat_type_id_nomenclature_degat_gravite CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_degat_gravite, 'OEASC_DEGAT_GRAVITE')) NOT VALID,

    CONSTRAINT fk_t_degat_essences_id_nomenclature_degat_anteriorite FOREIGN KEY (id_nomenclature_degat_anteriorite)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT check_t_degat_type_id_nomenclature_degat_anteriorite CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_degat_anteriorite, 'OEASC_DEGAT_ANTERIORITE')) NOT VALID

);



-- correlations nomenclature declaration

DROP TABLE IF EXISTS oeasc_declarations.cor_nomenclature_declarations_essence_secondaire CASCADE;

CREATE TABLE IF NOT EXISTS oeasc_declarations.cor_nomenclature_declarations_essence_secondaire
(
    id_declaration integer NOT NULL,
    id_nomenclature integer NOT NULL,

    CONSTRAINT pk_cor_nomenclature_declarations_essence_secondaire PRIMARY KEY (id_declaration, id_nomenclature),

    CONSTRAINT fk_cor_nomenclature_declarations_essence_secondaire_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc_declarations.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_cor_nomenclature_declarations_essence_secondaire_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_cor_nomenclature_declarations_essence_secondaire_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature, 'OEASC_PEUPLEMENT_ESSENCE')) NOT VALID
);


DROP TABLE IF EXISTS oeasc_declarations.cor_nomenclature_declarations_essence_complementaire CASCADE;

CREATE TABLE IF NOT EXISTS oeasc_declarations.cor_nomenclature_declarations_essence_complementaire
(
    id_declaration integer NOT NULL,
    id_nomenclature integer NOT NULL,

    CONSTRAINT pk_cor_nomenclature_declarations_essence_complementaire PRIMARY KEY (id_declaration, id_nomenclature),

    CONSTRAINT fk_cor_nomenclature_declarations_essence_complementaire_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc_declarations.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_cor_nomenclature_declarations_essence_complementaire_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_cor_nomenclature_declarations_essence_complementaire_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature, 'OEASC_PEUPLEMENT_ESSENCE')) NOT VALID
);


DROP TABLE IF EXISTS oeasc_declarations.cor_nomenclature_declarations_maturite CASCADE;

CREATE TABLE IF NOT EXISTS oeasc_declarations.cor_nomenclature_declarations_maturite
(
    id_declaration integer NOT NULL,
    id_nomenclature integer NOT NULL,

    CONSTRAINT pk_cor_nomenclature_declarations_maturite PRIMARY KEY (id_declaration, id_nomenclature),

    CONSTRAINT fk_cor_nomenclature_declarations_maturite_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc_declarations.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_cor_nomenclature_declarations_maturite_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_cor_nomenclature_declarations_maturite_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature, 'OEASC_PEUPLEMENT_MATURITE')) NOT VALID
);


DROP TABLE IF EXISTS oeasc_declarations.cor_nomenclature_declarations_protection_type CASCADE;

CREATE TABLE IF NOT EXISTS oeasc_declarations.cor_nomenclature_declarations_protection_type
(
    id_declaration integer NOT NULL,
    id_nomenclature integer NOT NULL,

    CONSTRAINT pk_cor_nomenclature_declarations_protection_type PRIMARY KEY (id_declaration, id_nomenclature),

    CONSTRAINT fk_cor_nomenclature_declarations_protection_type_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc_declarations.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_cor_nomenclature_declarations_protection_type_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_cor_nomenclature_declarations_protection_type_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature, 'OEASC_PEUPLEMENT_PROTECTION_TYPE')) NOT VALID
);


DROP TABLE IF EXISTS oeasc_declarations.cor_nomenclature_declarations_paturage_type CASCADE;

CREATE TABLE IF NOT EXISTS oeasc_declarations.cor_nomenclature_declarations_paturage_type
(
    id_declaration integer NOT NULL,
    id_nomenclature integer NOT NULL,

    CONSTRAINT pk_cor_nomenclature_declarations_paturage_type PRIMARY KEY (id_declaration, id_nomenclature),

    CONSTRAINT fk_cor_nomenclature_declarations_paturage_type_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc_declarations.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_cor_nomenclature_declarations_paturage_type_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_cor_nomenclature_declarations_paturage_type_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature, 'OEASC_PEUPLEMENT_PATURAGE_TYPE')) NOT VALID
);


DROP TABLE IF EXISTS oeasc_declarations.cor_nomenclature_declarations_paturage_saison CASCADE;

CREATE TABLE IF NOT EXISTS oeasc_declarations.cor_nomenclature_declarations_paturage_saison
(
    id_declaration integer NOT NULL,
    id_nomenclature integer NOT NULL,

    CONSTRAINT pk_cor_nomenclature_declarations_paturage_saison PRIMARY KEY (id_declaration, id_nomenclature),

    CONSTRAINT fk_cor_nomenclature_declarations_paturage_saison_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc_declarations.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_cor_nomenclature_declarations_paturage_saison_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_cor_nomenclature_declarations_paturage_saison_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature, 'OEASC_PEUPLEMENT_PATURAGE_SAISON')) NOT VALID
);



DROP TABLE IF EXISTS oeasc_declarations.cor_nomenclature_declarations_espece CASCADE;

CREATE TABLE IF NOT EXISTS oeasc_declarations.cor_nomenclature_declarations_espece
(
    id_declaration integer NOT NULL,
    id_nomenclature integer NOT NULL,

    CONSTRAINT pk_cor_nomenclature_declarations_espece PRIMARY KEY (id_declaration, id_nomenclature),

    CONSTRAINT fk_cor_nomenclature_declarations_espece_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc_declarations.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_cor_nomenclature_declarations_espece_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_cor_nomenclature_declarations_espece_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature, 'OEASC_PEUPLEMENT_ESPECE')) NOT VALID
);


-- cor_areas_declarations

CREATE TABLE IF NOT EXISTS oeasc_declarations.cor_areas_declarations
(
    id_declaration integer NOT NULL,
    id_area integer NOT NULL,

    CONSTRAINT pk_cor_areas_declarations PRIMARY KEY (id_declaration, id_area),

    CONSTRAINT fk_cor_areas_declarations_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc_declarations.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_cor_areas_declarations_id_area FOREIGN KEY (id_area)
        REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION
);

-- trigger cor_areas_declarations
-- CREATE OR REPLACE FUNCTION oeasc_declarations.fct_trg_cor_areas_declarations()
--   RETURNS trigger AS
-- $BODY$
-- BEGIN

-- 	DELETE FROM oeasc_declarations.cor_areas_declarations WHERE id_declaration = NEW.id_declaration;
-- 	INSERT INTO oeasc_declarations.cor_areas_declarations

--         WITH selected_types AS (SELECT UNNEST(ARRAY [          
--             'OEASC_SECTEUR',
--             'OEASC_COMMUNE',
--             'OEASC_SECTION',
--             'OEASC_ONF_FRT',
--             'OEASC_ONF_PRF',
--             'OEASC_ONF_UG',
--             'OEASC_CADASTRE',
--             'OEASC_DGD'
--         ]) AS id_type)
        
--         SELECT 
--             NEW.id_declaration,
--             ref_geo.intersect_geom_type_tol(NEW.geom, selected_types.id_type, 0.05) as id_area
--             FROM selected_types
-- ;
--   RETURN NEW;
-- END;
-- $BODY$
--   LANGUAGE plpgsql VOLATILE
--   COST 100;


-- CREATE TRIGGER trg_cor_areas_declarations
--   AFTER INSERT OR UPDATE OF geom
--   ON oeasc_declarations.t_declarations
--   FOR EACH ROW
--   EXECUTE PROCEDURE oeasc_declarations.fct_trg_cor_areas_declarations();


CREATE OR REPLACE FUNCTION oeasc_declarations.get_area_names(myiddeclaration integer, myareatype character varying)
  RETURNS character varying AS
$BODY$
--Function which return the label from the id_nomenclature
DECLARE
	theareanames character varying;
  BEGIN
  SELECT INTO theareanames STRING_AGG(DISTINCT l.area_name, ', ')
  FROM oeasc_declarations.cor_areas_declarations c
  LEFT JOIN ref_geo.l_areas l
    ON c.id_area = l.id_area
        AND l.id_type = ref_geo.get_id_type(myareatype)
    WHERE id_declaration = myiddeclaration
    ;

return theareanames;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;


CREATE OR REPLACE FUNCTION oeasc_declarations.get_id_areas(myiddeclaration integer, myareatype character varying)
  RETURNS integer[] AS
$BODY$
--Function which return the label from the id_nomenclature
DECLARE
	theidareas character varying;
  BEGIN
  SELECT INTO theidareas ARRAY_AGG(DISTINCT l.id_area)
  FROM oeasc_declarations.cor_areas_declarations c
  LEFT JOIN ref_geo.l_areas l
    ON c.id_area = l.id_area
        AND l.id_type = ref_geo.get_id_type(myareatype)
    WHERE id_declaration = myiddeclaration
    AND l.id_area IS NOT NULL
    ;

return theidareas;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;
