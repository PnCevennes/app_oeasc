DROP SCHEMA IF EXISTS oeasc_in CASCADE;

CREATE SCHEMA IF NOT EXISTS oeasc_in;

DROP TABLE IF EXISTS oeasc_commons.t_secteurs;
CREATE TABLE IF NOT EXISTS oeasc_commons.t_secteurs
(
    id_secteur serial NOT NULL,
    nom_secteur CHARACTER VARYING,
    code_secteur CHARACTER VARYING,

    CONSTRAINT pk_t_secteurs_id_secteur PRIMARY KEY (id_secteur)

);

CREATE TABLE IF NOT EXISTS oeasc_in.t_tags
(
    id_tag serial NOT NULL,
    nom_tag CHARACTER VARYING,

    CONSTRAINT pk_t_tags_id_tag PRIMARY KEY (id_tag)

);

CREATE TABLE IF NOT EXISTS oeasc_in.t_circuits
(
    id_circuit serial NOT NULL,
    nom_circuit CHARACTER VARYING,
    numero_circuit INTEGER,
    id_secteur INTEGER,
    km DOUBLE PRECISION,
    geom geometry(MultiPolygon, 2154),

    
    CONSTRAINT pk_t_circuits_id_circuit PRIMARY KEY (id_circuit),
    CONSTRAINT fk_t_circuits_t_secteurs FOREIGN KEY (id_secteur)
        REFERENCES oeasc_commons.t_secteurs(id_secteur) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE

);

CREATE TABLE IF NOT EXISTS oeasc_in.t_realisations
(
    id_realisation SERIAL NOT NULL,
    id_circuit INTEGER NOT NULL,
    serie INTEGER,
    vent CHARACTER VARYING,
    temps CHARACTER VARYING,
    temperature CHARACTER VARYING,
    date_realisation DATE,
    groupes INTEGER,
    
    CONSTRAINT pk_t_realisations_id_realisation PRIMARY KEY (id_realisation),

    CONSTRAINT fk_t_realisations_id_circuit FOREIGN KEY (id_circuit)
        REFERENCES oeasc_in.t_circuits (id_circuit) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE oeasc_in.cor_realisation_tag
(
    id_realisation INTEGER,
    id_tag INTEGER,
    valid BOOLEAN DEFAULT TRUE,

    CONSTRAINT pk_cor_realisation_tag PRIMARY KEY (id_realisation, id_tag),
    CONSTRAINT fk_cor_realisation_tag_id_realisation FOREIGN KEY (id_realisation)
        REFERENCES oeasc_in.t_realisations (id_realisation) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_cor_realisation_tag_id_tag FOREIGN KEY (id_tag)
        REFERENCES oeasc_in.t_tags (id_tag) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TABLE oeasc_in.t_observers
(
    id_observer SERIAL NOT NULL,
    nom_observer CHARACTER VARYING,

    CONSTRAINT pk_t_observers_id_observer PRIMARY KEY (id_observer)

);

CREATE TABLE oeasc_in.cor_realisation_observer(
    id_realisation INTEGER,
    id_observer INTEGER,

    CONSTRAINT pk_cor_realisation_observer PRIMARY KEY (id_realisation, id_observer),
    CONSTRAINT fk_cor_realisation_observer_id_realisation FOREIGN KEY (id_realisation)
        REFERENCES oeasc_in.t_realisations (id_realisation) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_cor_realisation_observer_id_observer FOREIGN KEY (id_observer)
        REFERENCES oeasc_in.t_observers (id_observer) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE

);


CREATE TABLE IF NOT EXISTS oeasc_in.t_observations
(
    id_observation SERIAL NOT NULL,
    id_realisation INTEGER NOT NULL,
    espece CHARACTER VARYING,
    nb INTEGER,

    CONSTRAINT pk_t_observations_id_observation PRIMARY KEY (id_observation),

    CONSTRAINT fk_t_observations_id_realisation FOREIGN KEY (id_realisation)
        REFERENCES oeasc_in.t_realisations (id_realisation) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE
);

