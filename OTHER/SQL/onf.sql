-- Table: oeasc.onf

DROP TABLE oeasc.onf;

CREATE TABLE oeasc.onf
(
	id serial NOT NULL, 
	id_frt integer NOT NULL,
	
	CONSTRAINT pk_onf PRIMARY KEY (id),
	CONSTRAINT fk_onf_id_frt FOREIGN KEY (id_frt)
	REFERENCES ref_geo.forets_gestion_onf_pec (id) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);
ALTER TABLE oeasc.onf
  OWNER TO dbadmin;
