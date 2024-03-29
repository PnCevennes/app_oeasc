﻿-- schema oeasc_chasse

-- DROP SCHEMA IF EXISTS oeasc_chasse CASCADE;

-- CREATE SCHEMA oeasc_chasse;

ALTER TABLE IF EXISTS oeasc_in.t_especes SET SCHEMA oeasc_commons;


CREATE TABLE oeasc_chasse.t_personnes
(
    id_personne SERIAL NOT NULL,
    nom_personne CHARACTER VARYING,

    CONSTRAINT pk_t_personnes_id_personne PRIMARY KEY (id_personne),
    CONSTRAINT unique_nom_personne UNIQUE(nom_personne)
)
;


CREATE TABLE oeasc_chasse.t_zone_cynegetiques
(
    id_zone_cynegetique SERIAL NOT NULL,
    nom_zone_cynegetique CHARACTER VARYING,
    code_zone_cynegetique CHARACTER VARYING,
    id_secteur INTEGER,

    CONSTRAINT pk_t_zone_cynegetiques_id_zone_cynegetique PRIMARY KEY (id_zone_cynegetique),
    CONSTRAINT fk_t_zone_cynegetiques_t_secteurs FOREIGN KEY (id_secteur)
        REFERENCES oeasc_commons.t_secteurs(id_secteur) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT unique_code_zone_cynegetique UNIQUE(code_zone_cynegetique)

)
;


CREATE TABLE oeasc_chasse.t_zone_indicatives
(
    id_zone_indicative SERIAL NOT NULL,
    code_zone_indicative CHARACTER VARYING,
    nom_zone_indicative CHARACTER VARYING,
    id_zone_cynegetique INTEGER,
    geom GEOMETRY,
    CONSTRAINT pk_t_zone_indicatives_id_zone_indicative PRIMARY KEY (id_zone_indicative),
    CONSTRAINT fk_t_zone_indicatives_t_zone_cynegetiques FOREIGN KEY (id_zone_cynegetique)
        REFERENCES oeasc_chasse.t_zone_cynegetiques(id_zone_cynegetique) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT unique_code_zone_indicative_id_zone_cynegetique UNIQUE(code_zone_indicative, id_zone_cynegetique)
)
;


CREATE TABLE oeasc_chasse.t_lieu_tirs
(
    id_lieu_tir SERIAL NOT NULL,
    nom_lieu_tir CHARACTER VARYING,
    code_lieu_tir CHARACTER VARYING,
    id_zone_indicative INTEGER,
    id_zone_cynegetique INTEGER,
    id_area_commune INTEGER,
    label_commune CHARACTER VARYING,
    geom GEOMETRY,

    CONSTRAINT pk_t_lieu_tirs_id_lieu_tir PRIMARY KEY (id_lieu_tir),
    CONSTRAINT fk_t_lieu_tirs_t_zone_indicatives FOREIGN KEY (id_zone_indicative)
    REFERENCES oeasc_chasse.t_zone_indicatives(id_zone_indicative) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT id_zone_cynegetique FOREIGN KEY (id_zone_cynegetique)
    REFERENCES oeasc_chasse.t_zone_cynegetiques(id_zone_cynegetique) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT fk_t_lieu_tirs_l_areas FOREIGN KEY (id_area_commune)
        REFERENCES ref_geo.l_areas(id_area) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION
)
;

CREATE TABLE oeasc_chasse.t_lieu_tir_synonymes
(
    id_lieu_tir_synonyme SERIAL NOT NULL,
    nom_lieu_tir_synonyme CHARACTER VARYING,
    id_lieu_tir INTEGER NOT NULL,

    CONSTRAINT pk_t_lieu_tir_synonymes_id_lieu_tir_synonymes PRIMARY KEY (id_lieu_tir_synonyme),
    CONSTRAINT fk_t_lieu_tirs_synonymes_t_lieu_tirs FOREIGN KEY (id_lieu_tir)
        REFERENCES oeasc_chasse.t_lieu_tirs(id_lieu_tir) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION
)
;

CREATE TABLE oeasc_chasse.t_saisons
(
    id_saison SERIAL NOT NULL,
    nom_saison CHARACTER VARYING,
    date_debut date,
    date_fin date,
    current BOOLEAN,
    commentaire CHARACTER VARYING,

    CONSTRAINT pk_t_saisons PRIMARY KEY (id_saison)
)
;


CREATE TABLE oeasc_chasse.t_saison_dates
(
    id_saison_date SERIAL NOT NULL,
    id_saison INTEGER NOT NULL,
    id_espece INTEGER NOT NULL,
    date_debut date,
    date_fin date,
    id_nomenclature_type_chasse INTEGER,

    CONSTRAINT pk_t_saison_dates PRIMARY KEY (id_saison_date),
    CONSTRAINT fk_t_saison_dates_t_saisons FOREIGN KEY (id_saison)
    REFERENCES oeasc_chasse.t_saisons(id_saison) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT fk_t_saison_dates_t_especes FOREIGN KEY (id_espece)
    REFERENCES oeasc_commons.t_especes(id_espece) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE NO ACTION
)
;


CREATE TABLE oeasc_chasse.t_attribution_massifs
(
    id_attribution_massif SERIAL NOT NULL,
    id_espece INTEGER NOT NULL,
    id_zone_cynegetique INTEGER NOT NULL,
    id_saison INTEGER NOT NULL,
    nb_affecte_min INTEGER,
    nb_affecte_max INTEGER,

    CONSTRAINT pk_t_attribution_massifs PRIMARY KEY (id_attribution_massif),
    CONSTRAINT fk_t_attribution_massifs_t_especes FOREIGN KEY (id_espece)
        REFERENCES oeasc_commons.t_especes(id_espece) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT fk_t_attribution_massif_t_zone_cynegetiques FOREIGN KEY (id_zone_cynegetique)
        REFERENCES oeasc_chasse.t_zone_cynegetiques(id_zone_cynegetique) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT fk_t_attribution_massif_t_saisons FOREIGN KEY (id_saison)
        REFERENCES oeasc_chasse.t_saisons(id_saison) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION
)
;

CREATE TABLE oeasc_chasse.t_type_bracelets (
    id_type_bracelet SERIAL NOT NULL,
    code_type_bracelet CHARACTER VARYING NOT NULL,
    description_type_bracelet CHARACTER VARYING,
    id_espece INTEGER NOT NULL,

    CONSTRAINT pk_t_type_bracelets PRIMARY KEY (id_type_bracelet),
    CONSTRAINT fk_t_type_bracelets_t_especes FOREIGN KEY (id_espece)
        REFERENCES oeasc_commons.t_especes(id_espece) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION
)
;

CREATE TABLE oeasc_chasse.t_attributions
(
    id_attribution SERIAL NOT NULL,
    id_saison INTEGER NOT NULL,
    numero_bracelet CHARACTER VARYING,
    id_zone_cynegetique_affectee INTEGER NOT NULL,
    id_zone_indicative_affectee INTEGER NOT NULL,
    id_type_bracelet INTEGER NOT NULL,
    meta_create_date timestamp without time zone,
    meta_update_date timestamp without time zone,

    CONSTRAINT pk_t_attributions PRIMARY KEY (id_attribution),
    CONSTRAINT fk_t_attributions_t_zone_cynegetiques FOREIGN KEY (id_zone_cynegetique_affectee)
        REFERENCES oeasc_chasse.t_zone_cynegetiques(id_zone_cynegetique) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT fk_t_attributions_t_saisons FOREIGN KEY (id_saison)
        REFERENCES oeasc_chasse.t_saisons(id_saison ) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT fk_t_attributions_t_zone_indicatives FOREIGN KEY (id_zone_indicative_affectee)
        REFERENCES oeasc_chasse.t_zone_indicatives(id_zone_indicative) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT fk_t_attributions_t_type_bracelets FOREIGN KEY (id_type_bracelet)
        REFERENCES oeasc_chasse.t_type_bracelets(id_type_bracelet) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION

)
;


CREATE TABLE oeasc_chasse.t_realisations
(
    id_realisation SERIAL NOT NULL,
    id_attribution INTEGER NOT NULL, -- relation 1-1 -> contrainte unicité
    id_zone_cynegetique_realisee INTEGER NOT NULL,
    id_zone_indicative_realisee INTEGER NOT NULL,
    id_lieu_tir_synonyme INTEGER,

    date_exacte DATE,
    date_enreg DATE,

    mortalite_hors_pc BOOLEAN,
    id_auteur_tir INTEGER,
    id_auteur_constat INTEGER,

    id_nomenclature_sexe INTEGER,
    id_nomenclature_classe_age INTEGER,

    poid_entier FLOAT,
    poid_vide FLOAT,
    poid_c_f_p FLOAT,

    long_dagues_droite INTEGER,
    long_dagues_gauche INTEGER,
    long_mandibules_droite INTEGER,
    long_mandibules_gauche INTEGER,

    cors_nb INTEGER,
    cors_commentaires CHARACTER VARYING,

    gestation BOOLEAN,
    id_nomenclature_mode_chasse INTEGER,
    commentaire CHARACTER VARYING,

    parcelle_onf BOOLEAN,
    poid_indique BOOLEAN,
    cors_indetermine BOOLEAN,
    long_mandibule_indetermine BOOLEAN,

    id_numerisateur INTEGER,

    meta_create_date timestamp without time zone,
    meta_update_date timestamp without time zone,

    UNIQUE(id_attribution),

    CONSTRAINT pk_t_realisations PRIMARY KEY (id_attribution),

    CONSTRAINT fk_t_realisations_t_attributions FOREIGN KEY (id_attribution)
        REFERENCES oeasc_chasse.t_attributions(id_attribution) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT fk_t_realisations_t_zone_cynegetiques FOREIGN KEY (id_zone_cynegetique_realisee)
        REFERENCES oeasc_chasse.t_zone_cynegetiques(id_zone_cynegetique) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT fk_t_realisations_t_zone_indicatives FOREIGN KEY (id_zone_indicative_realisee)
        REFERENCES oeasc_chasse.t_zone_indicatives(id_zone_indicative) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT fk_t_realisations_t_lieu_tir_synonymes FOREIGN KEY (id_lieu_tir_synonyme)
        REFERENCES oeasc_chasse.t_lieu_tir_synonymes(id_lieu_tir_synonyme) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT fk_t_realisations_t_personne_tirs FOREIGN KEY (id_auteur_tir)
        REFERENCES oeasc_chasse.t_personnes(id_personne) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT fk_t_realisations_t_personne_constats FOREIGN KEY (id_auteur_constat)
        REFERENCES oeasc_chasse.t_personnes(id_personne) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT fk_t_realisations_t_roles FOREIGN KEY (id_numerisateur)
        REFERENCES utilisateurs.t_roles(id_role) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION

);

-- ALTER TABLE oeasc_chasse.t_realisations ADD UNIQUE (id_realisation);

CREATE TRIGGER tri_meta_dates_change_t_realisations
  BEFORE INSERT OR UPDATE
  ON oeasc_chasse.t_realisations
  FOR EACH ROW
  EXECUTE PROCEDURE public.fct_trg_meta_dates_change();


CREATE TRIGGER tri_meta_dates_change_t_attributions
  BEFORE INSERT OR UPDATE
  ON oeasc_chasse.t_attributions
  FOR EACH ROW
  EXECUTE PROCEDURE public.fct_trg_meta_dates_change();


CREATE TABLE oeasc_chasse.t_bilan_chasse_historique
(
    id_bilan_chasse_historique SERIAL NOT NULL,
    id_saison INTEGER NOT NULL,
    id_espece INTEGER NOT NULL,
    id_zone_indicative INTEGER NOT NULL,
    nb_affecte_min INTEGER,
    nb_affecte_max INTEGER,
    nb_realise INTEGER,
    nb_realise_avant_11 INTEGER,

    CONSTRAINT pk_t_bilan_chasse_historique PRIMARY KEY (id_bilan_chasse_historique),
    CONSTRAINT fk_t_bilan_chasse_historique_t_saisons FOREIGN KEY (id_saison)
    REFERENCES oeasc_chasse.t_saisons(id_saison) MATCH SIMPLE,
    CONSTRAINT fk_t_bilan_chasse_historique_t_especes FOREIGN KEY (id_espece)
    REFERENCES oeasc_commons.t_especes(id_espece) MATCH simple,
    CONSTRAINT fk_t_bilan_chasse_historique_t_zone_indicatives FOREIGN KEY (id_zone_indicative)
    REFERENCES oeasc_chasse.t_zone_indicatives(id_zone_indicative) MATCH SIMPLE
)
;

ALTER TABLE oeasc_chasse.t_bilan_chasse_historique
    ADD CONSTRAINT unique_t_bilan_chasse_historique_saison_espece_zi
    UNIQUE (id_saison, id_espece, id_zone_indicative)
;