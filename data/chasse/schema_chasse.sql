DROP SCHEMA IF EXISTS oeasc_plan_chasse CASCADE;

CREATE SCHEMA oeasc_plan_chasse;

ALTER TABLE oeasc_in.t_especes SET SCHEMA oeasc_commons;


CREATE TABLE oeasc_plan_chasse.t_personnes
{
    id_personne INTEGER NOT NULL,
    nom_personne CHARACTER VARYING,

    CONSTRAINT pk_t_personnes_id_personne PRIMARY KEY (id_personne)
}
;


CREATE oeasc_plan_chasse.t_zone_cinegetiques
{
    id_zone_cinegetique INTEGER NOT NULL,
    nom_zone_cinegetique CHARACTER VARYING,
    code_zone_cinegetique CHARACTER VARYING,
    id_secteur INTEGER,

    CONSTRAINT pk_t_zone_cinegetiques_id_zone_cinegetique PRIMARY KEY (id_zone_cinegetique),
    CONSTRAINT fk_t_zone_cinegetiques_t_secteurs FOREIGN KEY (id_secteur)
        REFERENCES oeasc_commons.t_secteurs(id_secteur) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE
}
;


CREATE oeasc_plan_chasse.t_zone_interets
{
    id_zone_interet INTEGER NOT NULL,
    nom_zone_interet CHARACTER VARYING,
    code_zone_interet CHARACTER VARYING,
    id_secteur INTEGER,

    CONSTRAINT pk_t_zone_interets_id_zone_interet PRIMARY KEY (id_zone_interet),
    CONSTRAINT fk_t_zone_interets_t_zone_cinegetiques FOREIGN KEY (id_zone_cinegetique)
        REFERENCES oeasc_plan_chasse.t_zone_cinegetiques(id_zone_cinegetique) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE
}
;


CREATE oeasc_plan_chasse.t_lieu_tirs
{
    id_lieu_tir INTEGER NOT NULL,
    nom_lieu_tir CHARACTER VARYING,
    code_lieu_tir CHARACTER VARYING,
    id_zone_interet INTEGER,
    id_commune INTEGER,
    synonymes CHARACTER VARYING[],

    CONSTRAINT pk_t_lieu_tirs_id_lieu_tir PRIMARY KEY (id_lieu_tir),
    CONSTRAINT fk_t_lieu_tirs_t_zone_interets FOREIGN KEY (id_zone_interet)
        REFERENCES oeasc_plan_chasse.t_zone_interets(id_zone_interet) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_t_lieu_tirs_l_municipalities FOREIGN KEY (id_municipality)
        REFERENCES ref_geo.l_municipalities(id_municipality) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE
}
;


CREATE oeasc_plan_chasse.t_saisons
{
    id_saison INTEGER NOT NULL,
    nom_saison CHARACTER VARYING,

    CONSTRAINT pk_t_saisons PRIMARY KEY (id_saison),
}
;


CREATE oeasc_plan_chasse.t_saison_dates
{
    id_saison INTEGER NOT NULL,
    id_espece INTEGER NOT NULL,
    nom_saison CHARACTER VARYING,
    date_debut timestamp without time zone,
    date_fin timestamp without time zone,
    id_nomenclature_type_chasse INTEGER,
    id_espece INTEGER,

    CONSTRAINT pk_t_saisons PRIMARY KEY (id_saison),
    CONSTRAINT fk_t_saison_dates_t_saisons FOREIGN KEY (id_saison)
    REFERENCES oeasc_plan_chasse.t_saisons(id_saison) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_t_saison_dates_t_especes FOREIGN KEY (id_espece)
    REFERENCES oeasc_commons.t_especes(id_espece) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE CASCADE
}
;


CREATE oeasc_plan_chasse.t_attribution_massifs
{
    id_attribution_massif INTEGER NOT NULL,
    id_espece INTEGER NOT NULL,
    id_zone_cinegetique INTEGER NOT NULL,
    id_saison INTEGER NOT NULL,
    nb_affecte_min INTEGER,
    nb_affecte_max INTEGER,

    CONSTRAINT pk_t_attribution_massifs PRIMARY KEY (id_attribution_massif),
    CONSTRAINT fk_t_attribution_massifs_t_especes FOREIGN KEY (id_espece)
        REFERENCES oeasc_commons.t_especes(id_espece) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_t_attribution_massif_t zone_cinegetiques FOREIGN KEY (id_zone_cinegetique)
        REFERENCES oeasc_plan_chasse.t_zone_cinegetiques(id_zone_cinegetique) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_t_attribution_massif_t saisons FOREIGN KEY (id_saison)
        REFERENCES oeasc_plan_chasse.t_saisons(id_saison) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE
;

CREATE oeasc_type_bracelet {
    id_type_bracelet INTEGER NOT NULL,
    code_type_bracelet INTEGER NOT NULL,
    description_type_bracelet INTEGER NOT NULL,
    id_espece INTEGER NOT NULL,

    CONSTRAINT pk_t_type_bracelets PRIMARY KEY (id_type_bracelet),
    CONSTRAINT fk_t_type_bracelets_t_especes FOREIGN KEY (id_espece)
        REFERENCES oeasc_commons.t_especes(id_espece) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
}


CREATE oeasc_plan_chasse.attribution
{
    id_attribution INTEGER NOT NULL,
    numero_bracelet CHARACTER VARYING,
    id_zone_cinegetique_affectee INTEGER NOT NULL,
    id_zone_interet_affectee INTEGER NOT NULL,
    id_type_bracelet INTEGER NOT NULL,

    CONSTRAINT pk_t_attributions PRIMARY KEY (id_attribution),
    CONSTRAINT fk_t_attributions_t zone_cinegetiques FOREIGN KEY (id_zone_cinegetique_affectee)
        REFERENCES oeasc_plan_chasse.t_zone_cinegetiques(id_zone_cinegetique) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_t_attributions_t zone_interets FOREIGN KEY (id_zone_interet_affectee)
        REFERENCES oeasc_plan_chasse.t_zone_interets(id_zone_interet) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE
}


CREATE oeasc_plan_chasse.realisation
{
    id_attribution INTEGER NOT NULL, -- relation 1-1
    id_zone_cinegetique_realisee INTEGER NOT NULL,
    id_zone_interet_realisee INTEGER NOT NULL,
    id_lieu_tir INTEGER NOT NULL,

    mortalite_hors_pc BOOLEAN,
    id_auteur_tir INTEGER,
    id_auteur_constat INTEGER, 

    id_nomenclature_sexe INTEGER,
    id_nomenclature_classe_age INTEGER,

    poid_entier INTEGER,
    poid_vide INTEGER,
    poid_c_f_p, INTEGER,

    longeur_dague_droite INTEGER,
    longeur_dague_gauche INTEGER,
    longeur_mandibule_droite INTEGER,
    longeur_mandibule_gauche INTEGER,

    cors_nb INTEGER,
    cors_commentaires CHARACTER VARYING,

    gestation BOOLEAN,
    id_nomenclature_mode_chasse INTEGER,
    commentaire CHARACTER VARYING,




    CONSTRAINT pk_t_realisations PRIMARY KEY (id_attribution),
    CONSTRAINT fk_t_realisations_t_attributions FOREIGN KEY (id_attribution)
        REFERENCES oeasc_plan_chasse.t_attributions(id_attribution) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_t_realisations_t_zone_cinegetiques FOREIGN KEY (id_zone_cinegetique_realisee)
        REFERENCES oeasc_plan_chasse.t_zone_cinegetiques(id_zone_cinegetique) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_t_realisations_t_zone_interets FOREIGN KEY (id_zone_interet_realisee)
        REFERENCES oeasc_plan_chasse.t_zone_interets(id_zone_interet) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_t_realisations_t_lieu_tirs FOREIGN KEY (id_lieu_tir)
        REFERENCES oeasc_plan_chasse.t_lieu_tirs(id_lieu_tir) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_t_realisations_t_personnes FOREIGN KEY (id_auteur_tir)
        REFERENCES oeasc_plan_chasse.t_personnes(id_personne) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_t_realisations_t_personnes FOREIGN KEY (id_auteur_constat)
        REFERENCES oeasc_plan_chasse.t_personnes(id_personne) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,

}

