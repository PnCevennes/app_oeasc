DROP SCHEMA IF EXISTS oeasc_in CASCADE;

CREATE SCHEMA IF NOT EXISTS oeasc_in;


CREATE TABLE IF NOT EXISTS oeasc_in.t_circuits
(
    id_circuit serial NOT NULL,
    nom_circuit CHARACTER VARYING,
    numero_circuit INTEGER,
    ug CHARACTER VARYING,
    km DOUBLE PRECISION,
    geom geometry(MultiPolygon, 2154),
    
    CONSTRAINT pk_t_circuits_id_circuit PRIMARY KEY (id_circuit)
);

CREATE TABLE IF NOT EXISTS oeasc_in.t_realisations
(
    id_realisation SERIAL NOT NULL,
    id_circuit INTEGER NOT NULL,
    serie INTEGER,
    observers CHARACTER VARYING[],
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

CREATE TABLE IF NOT EXISTS oeasc_in.t_observations
(
    id_observation SERIAL NOT NULL,
    id_realisation INTEGER NOT NULL,
    espece CHARACTER VARYING,
    nb INTEGER,
    valid BOOLEAN DEFAULT TRUE,

    CONSTRAINT pk_t_observations_id_observation PRIMARY KEY (id_observation),

    CONSTRAINT fk_t_observations_id_realisation FOREIGN KEY (id_realisation)
        REFERENCES oeasc_in.t_realisations (id_realisation) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE
);

