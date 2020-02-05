-- schema oeasc_forets

-- oeasc_forets.t_proprietaires : table des proprietaires de forets (publiques et privees) 
-- oeasc_forets.t_forets : table des forets (publiques et privees) 
-- oeasc_forets.cor_areas_forets : correlation foret avec d'autres AREAS (dept, communes, massif, ect...)

CREATE SCHEMA IF NOT EXISTS oeasc_forets;


CREATE TABLE IF NOT EXISTS oeasc_forets.t_proprietaires
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

    CONSTRAINT pk_t_proprietaires_id_proprietaire PRIMARY KEY (id_proprietaire),

    CONSTRAINT fk_t_proprietaires_id_nomenclature_proprietaire_type FOREIGN KEY (id_nomenclature_proprietaire_type)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_proprietaire_id_nomenclature_proprietaire_type CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_proprietaire_type, 'OEASC_PROPRIETAIRE_TYPE')) NOT VALID,

    CONSTRAINT fk_t_forets_id_declarant FOREIGN KEY (id_declarant)
        REFERENCES utilisateurs.t_roles (id_role) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION

);


CREATE TABLE IF NOT EXISTS oeasc_forets.t_forets
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

    CONSTRAINT pk_t_forets_id_foret PRIMARY KEY (id_foret),

    CONSTRAINT fk_t_forets_id_proprietaire FOREIGN KEY (id_proprietaire)
        REFERENCES oeasc_forets.t_proprietaires (id_proprietaire) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS oeasc_forets.cor_areas_forets
(
    id_foret integer NOT NULL,
    id_area integer NOT NULL,

    CONSTRAINT pk_cor_areas_foret PRIMARY KEY (id_foret, id_area),

    CONSTRAINT fk_cor_areas_foret_id_foret FOREIGN KEY (id_foret)
        REFERENCES oeasc_forets.t_forets (id_foret) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_cor_areas_foret_id_area FOREIGN KEY (id_area)
        REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION
);


-- trigger cor_areas_forets
CREATE OR REPLACE FUNCTION oeasc_forets.fct_trg_cor_areas_forets()
  RETURNS trigger AS
$BODY$
BEGIN

	DELETE FROM oeasc_forets.cor_areas_forets WHERE id_foret = NEW.id_foret;
	INSERT INTO oeasc_forets.cor_areas_forets

        WITH selected_types AS (SELECT UNNEST(ARRAY [
            'OEASC_SECTEUR',
            'OEASC_COMMUNE',
            'OEASC_SECTION',
            'OEASC_ONF_FRT',
            'OEASC_DGD'
        ]) AS id_type)

        SELECT 
            NEW.id_foret,
            ref_geo.intersect_id_area_type_tol(l.id_area, selected_types.id_type, 0.05) as id_area
            FROM selected_types
            JOIN ref_geo.l_areas l ON l.area_code = NEW.code_foret

;
  RETURN NEW;
END;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

DROP TRIGGER IF EXISTS trg_cor_areas_forets ON oeasc_forets.t_forets;

CREATE TRIGGER trg_cor_areas_forets
  AFTER INSERT OR UPDATE
  ON oeasc_forets.t_forets
  FOR EACH ROW
  EXECUTE PROCEDURE oeasc_forets.fct_trg_cor_areas_forets();



-- Function: oeasc_get_id_proprietaire_from_name(character varying)

DROP FUNCTION IF EXISTS oeasc_forets.get_id_proprietaire_from_name(character varying);
CREATE OR REPLACE FUNCTION oeasc_forets.get_id_proprietaire_from_name(
    myname CHARACTER VARYING)

    RETURNS INTEGER AS
    $BODY$
    --
    -- Returns id_proprietaire from the name
    --
        DECLARE theidproprietaire INTEGER;
        BEGIN
            EXECUTE format( ' SELECT  n.id_proprietaire
                FROM oeasc_forets.t_proprietaires n
                WHERE nom_proprietaire = ''%s'' ', REPLACE(myname,'''','''''') ) INTO theidproprietaire;
            return theidproprietaire;
        END;
    $BODY$
    LANGUAGE plpgsql IMMUTABLE
    COST 100;
