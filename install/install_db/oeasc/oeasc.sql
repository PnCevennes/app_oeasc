-- oeasc

-- oeasc schema

SELECT pg_terminate_backend(pid), * FROM active_locks;


DROP SCHEMA IF EXISTS oeasc CASCADE;

CREATE SCHEMA IF NOT EXISTS oeasc;


DROP TABLE IF EXISTS oeasc.t_proprietaires;

CREATE TABLE IF NOT EXISTS oeasc.t_proprietaires
(

    id_proprietaire serial NOT NULL,

    nom_proprietaire CHARACTER VARYING(250),
    telephone CHARACTER VARYING(20),
    email CHARACTER VARYING(250),
    adresse CHARACTER VARYING(250),
    s_code_postal CHARACTER VARYING(10),
    s_commune_proprietaire CHARACTER VARYING(100),

    id_nomenclature_proprietaire_type INTEGER,

    id_declarant INTEGER,

    -- contraintes cle primaire

    CONSTRAINT pk_t_proprietaires_id_proprietaire PRIMARY KEY (id_proprietaire),

    -- contraintes nomenclature

    CONSTRAINT fk_t_proprietaires_id_nomenclature_proprietaire_type FOREIGN KEY (id_nomenclature_proprietaire_type)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_proprietaire_id_nomenclature_proprietaire_type CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_proprietaire_type, 'OEASC_PROPRIETAIRE_TYPE')) NOT VALID,

    CONSTRAINT fk_t_forets_id_declarant FOREIGN KEY (id_declarant)
        REFERENCES utilisateurs.t_roles (id_role) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION

);


DROP TABLE IF EXISTS oeasc.t_forets;

CREATE TABLE IF NOT EXISTS oeasc.t_forets
(
    id_foret serial NOT NULL,

    id_proprietaire INTEGER,

    b_statut_public BOOLEAN,

    b_document BOOLEAN,

    nom_foret CHARACTER VARYING(256),
    code_foret CHARACTER VARYING(256),
    label_foret CHARACTER VARYING(256),

    surface_renseignee DOUBLE PRECISION,
    surface_calculee DOUBLE PRECISION,

    -- contraintes cle primaire

    CONSTRAINT pk_t_forets_id_foret PRIMARY KEY (id_foret),

    -- contraintes clés étrangères

    CONSTRAINT fk_t_forets_id_proprietaire FOREIGN KEY (id_proprietaire)
        REFERENCES oeasc.t_proprietaires (id_proprietaire) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION
);


DROP TABLE IF EXISTS oeasc.t_declarations;

CREATE TABLE IF NOT EXISTS oeasc.t_declarations
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
    id_nomenclature_peuplement_acces INTEGER,
    id_nomenclature_peuplement_essence_principale INTEGER,

    b_peuplement_protection_existence BOOLEAN,
    b_peuplement_paturage_presence BOOLEAN,

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
        REFERENCES oeasc.t_forets (id_foret) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,

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

CREATE TRIGGER tri_meta_dates_change_t_declarations
   BEFORE INSERT OR UPDATE
   ON oeasc.t_declarations
   FOR EACH ROW
   EXECUTE PROCEDURE public.fct_trg_meta_dates_change();


DROP TABLE IF EXISTS oeasc.t_degats;

CREATE TABLE IF NOT EXISTS oeasc.t_degats
(
    id_degat serial NOT NULL,

    id_declaration INTEGER,

    id_nomenclature_degat_type serial NOT NULL,

    CONSTRAINT pk_t_degats_id_degat PRIMARY KEY (id_degat),

    CONSTRAINT fk_t_degats_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_t_degats_id_nomenclature_degat_type FOREIGN KEY (id_nomenclature_degat_type)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_degats_id_nomenclature_degat_type CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_degat_type, 'OEASC_DEGAT_TYPE')) NOT VALID

);


DROP TABLE IF EXISTS oeasc.t_degat_essences;

CREATE TABLE IF NOT EXISTS oeasc.t_degat_essences
(
    id_degat_essence serial NOT NULL,

    id_degat INTEGER,

    id_nomenclature_degat_essence INTEGER,
    id_nomenclature_degat_etendue INTEGER,
    id_nomenclature_degat_gravite INTEGER,
    id_nomenclature_degat_anteriorite INTEGER,

    CONSTRAINT pk_t_degat_essences_id_degat_essence PRIMARY KEY (id_degat_essence),

    CONSTRAINT fk_t_degat_id_degat FOREIGN KEY (id_degat)
        REFERENCES oeasc.t_degats (id_degat) MATCH SIMPLE
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
-- oeasc.cor_areas_declarations

DROP TABLE IF EXISTS oeasc.cor_areas_declarations;

CREATE TABLE IF NOT EXISTS oeasc.cor_areas_declarations
(
    id_declaration integer NOT NULL,
    id_area integer NOT NULL,

    CONSTRAINT pk_cor_areas_declaration PRIMARY KEY (id_declaration, id_area),

    CONSTRAINT fk_cor_areas_declaration_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_cor_areas_foret_id_area FOREIGN KEY (id_area)
        REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION
);

-- oeasc.cor_areas_forets

DROP TABLE IF EXISTS oeasc.cor_areas_forets;

CREATE TABLE IF NOT EXISTS oeasc.cor_areas_forets
(
    id_foret integer NOT NULL,
    id_area integer NOT NULL,

    CONSTRAINT pk_cor_areas_foret PRIMARY KEY (id_foret, id_area),

    CONSTRAINT fk_cor_areas_foret_id_foret FOREIGN KEY (id_foret)
        REFERENCES oeasc.t_forets (id_foret) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_cor_areas_foret_id_area FOREIGN KEY (id_area)
        REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION
);

-- correlations nomenclature declaration

DROP TABLE IF EXISTS oeasc.cor_nomenclature_declarations_essence_secondaire CASCADE;

CREATE TABLE IF NOT EXISTS oeasc.cor_nomenclature_declarations_essence_secondaire
(
    id_declaration integer NOT NULL,
    id_nomenclature integer NOT NULL,

    CONSTRAINT pk_cor_nomenclature_declarations_essence_secondaire PRIMARY KEY (id_declaration, id_nomenclature),

    CONSTRAINT fk_cor_nomenclature_declarations_essence_secondaire_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_cor_nomenclature_declarations_essence_secondaire_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_cor_nomenclature_declarations_essence_secondaire_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature, 'OEASC_PEUPLEMENT_ESSENCE')) NOT VALID
);


DROP TABLE IF EXISTS oeasc.cor_nomenclature_declarations_essence_complementaire CASCADE;

CREATE TABLE IF NOT EXISTS oeasc.cor_nomenclature_declarations_essence_complementaire
(
    id_declaration integer NOT NULL,
    id_nomenclature integer NOT NULL,

    CONSTRAINT pk_cor_nomenclature_declarations_essence_complementaire PRIMARY KEY (id_declaration, id_nomenclature),

    CONSTRAINT fk_cor_nomenclature_declarations_essence_complementaire_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_cor_nomenclature_declarations_essence_complementaire_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_cor_nomenclature_declarations_essence_complementaire_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature, 'OEASC_PEUPLEMENT_ESSENCE')) NOT VALID
);


DROP TABLE IF EXISTS oeasc.cor_nomenclature_declarations_maturite CASCADE;

CREATE TABLE IF NOT EXISTS oeasc.cor_nomenclature_declarations_maturite
(
    id_declaration integer NOT NULL,
    id_nomenclature integer NOT NULL,

    CONSTRAINT pk_cor_nomenclature_declarations_maturite PRIMARY KEY (id_declaration, id_nomenclature),

    CONSTRAINT fk_cor_nomenclature_declarations_maturite_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_cor_nomenclature_declarations_maturite_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_cor_nomenclature_declarations_maturite_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature, 'OEASC_PEUPLEMENT_MATURITE')) NOT VALID
);


DROP TABLE IF EXISTS oeasc.cor_nomenclature_declarations_protection_type CASCADE;

CREATE TABLE IF NOT EXISTS oeasc.cor_nomenclature_declarations_protection_type
(
    id_declaration integer NOT NULL,
    id_nomenclature integer NOT NULL,

    CONSTRAINT pk_cor_nomenclature_declarations_protection_type PRIMARY KEY (id_declaration, id_nomenclature),

    CONSTRAINT fk_cor_nomenclature_declarations_protection_type_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_cor_nomenclature_declarations_protection_type_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_cor_nomenclature_declarations_protection_type_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature, 'OEASC_PEUPLEMENT_PROTECTION_TYPE')) NOT VALID
);


DROP TABLE IF EXISTS oeasc.cor_nomenclature_declarations_paturage_type CASCADE;

CREATE TABLE IF NOT EXISTS oeasc.cor_nomenclature_declarations_paturage_type
(
    id_declaration integer NOT NULL,
    id_nomenclature integer NOT NULL,

    CONSTRAINT pk_cor_nomenclature_declarations_paturage_type PRIMARY KEY (id_declaration, id_nomenclature),

    CONSTRAINT fk_cor_nomenclature_declarations_paturage_type_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_cor_nomenclature_declarations_paturage_type_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_cor_nomenclature_declarations_paturage_type_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature, 'OEASC_PEUPLEMENT_PATURAGE_TYPE')) NOT VALID
);


DROP TABLE IF EXISTS oeasc.cor_nomenclature_declarations_paturage_statut CASCADE;

CREATE TABLE IF NOT EXISTS oeasc.cor_nomenclature_declarations_paturage_statut
(
    id_declaration integer NOT NULL,
    id_nomenclature integer NOT NULL,

    CONSTRAINT pk_cor_nomenclature_declarations_paturage_statut PRIMARY KEY (id_declaration, id_nomenclature),

    CONSTRAINT fk_cor_nomenclature_declarations_paturage_statut_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_cor_nomenclature_declarations_paturage_statut_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_cor_nomenclature_declarations_paturage_statut_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature, 'OEASC_PEUPLEMENT_PATURAGE_STATUT')) NOT VALID
);


DROP TABLE IF EXISTS oeasc.cor_nomenclature_declarations_espece CASCADE;

CREATE TABLE IF NOT EXISTS oeasc.cor_nomenclature_declarations_espece
(
    id_declaration integer NOT NULL,
    id_nomenclature integer NOT NULL,

    CONSTRAINT pk_cor_nomenclature_declarations_espece PRIMARY KEY (id_declaration, id_nomenclature),

    CONSTRAINT fk_cor_nomenclature_declarations_espece_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_cor_nomenclature_declarations_espece_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_cor_nomenclature_declarations_espece_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature, 'OEASC_PEUPLEMENT_ESPECE')) NOT VALID
);


DROP TABLE IF EXISTS oeasc.cor_nomenclature_forets_commune CASCADE;

CREATE TABLE IF NOT EXISTS oeasc.cor_nomenclature_forets_commune
(
    id_foret integer NOT NULL,
    id_nomenclature integer NOT NULL,

    CONSTRAINT pk_cor_nomenclature_forets_commune PRIMARY KEY (id_foret, id_nomenclature),

    CONSTRAINT fk_cor_nomenclature_forets_commune_id_foret FOREIGN KEY (id_foret)
        REFERENCES oeasc.t_forets (id_foret) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_cor_nomenclature_forets_commune_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_cor_nomenclature_forets_commune_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature, 'OEASC_COMMUNE')) NOT VALID
);


DROP TABLE IF EXISTS oeasc.cor_nomenclature_forets_departement CASCADE;

CREATE TABLE IF NOT EXISTS oeasc.cor_nomenclature_forets_departement
(
    id_foret integer NOT NULL,
    id_nomenclature integer NOT NULL,

    CONSTRAINT pk_cor_nomenclature_forets_departement PRIMARY KEY (id_foret, id_nomenclature),

    CONSTRAINT fk_cor_nomenclature_forets_departement_id_foret FOREIGN KEY (id_foret)
        REFERENCES oeasc.t_forets (id_foret) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE CASCADE,

    CONSTRAINT fk_cor_nomenclature_forets_departement_id_nomenclature FOREIGN KEY (id_nomenclature)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE NO ACTION ON DELETE NO ACTION,

    CONSTRAINT check_cor_nomenclature_forets_departement_mnemonique CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature, 'OEASC_DEPARTEMENT')) NOT VALID
);


-- Function: oeasc_get_id_proprietaire_from_name(character varying)

DROP FUNCTION IF EXISTS oeasc.get_id_proprietaire_from_name(character varying);

CREATE OR REPLACE FUNCTION oeasc.get_id_proprietaire_from_name(
    myname CHARACTER VARYING)

    RETURNS INTEGER AS
    $BODY$
    --
    -- Returns id_proprietaire from the name
    --
        DECLARE theidproprietaire INTEGER;
        BEGIN
            EXECUTE format( ' SELECT  n.id_proprietaire
                FROM oeasc.t_proprietaires n
                WHERE nom_proprietaire = ''%s'' ', REPLACE(myname,'''','''''') ) INTO theidproprietaire;
            return theidproprietaire;
        END;
    $BODY$
    LANGUAGE plpgsql IMMUTABLE
    COST 100;



DROP FUNCTION IF EXISTS oeasc.get_declarations_structure_declarant(integer);

CREATE OR REPLACE FUNCTION oeasc.get_declarations_structure_declarant(
    IN myid_declarant integer)
  RETURNS TABLE(id_declaration integer) AS
    $BODY$
        BEGIN
            RETURN QUERY
                SELECT d.id_declaration 
            FROM oeasc.t_declarations as d, 
                (SELECT id_role 
                    FROM utilisateurs.t_roles r, 
                        (SELECT id_organisme 
                            FROM utilisateurs.t_roles 
                            WHERE id_role = myid_declarant
                        )a
                    WHERE r.id_organisme = a.id_organisme
                )b
            WHERE d.id_declarant = b.id_role;
          END;
    $BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100
  ROWS 1000;

