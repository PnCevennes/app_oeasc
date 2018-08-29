-- Table: oeasc.identifiant_foret



CREATE TABLE oeasc.identifiant_foret
(
  id serial NOT NULL,
  A1_statut character varying(6), -- public ou privé
  A2_regime_forestier boolean, -- regime forestier si vrai
  A3_domaniale boolean, -- forêt domaniale si vrai
  A4_type_proprietaire character varying(20), -- oui nom propre, oui associe foncier, oui associé sc ou ep, non  
  A5_nom_proprietaire character varying(200), -- nom (prenom) proprio ou raison sociale 
  A6_telephone_proprietaire character varying(15),
  A7_email_proprietaire character varying(80),
  A8_adresse_proprietaire character varying(100),
  A9_commune_proprietaire character varying(100),
  A10_doc_gestion_durable boolean, -- existence DGD
  A11_departement character varying(4), -- dept
  A12_communes  character varying(50), -- commune
  A13_nom_foret character varying(50), -- nom foret
  A14_superficie_foret double precision, --superficie
  CONSTRAINT documents_gestion_durable_pec_pkey PRIMARY KEY (id)
)
WITH (
  OIDS=FALSE
);
ALTER TABLE oeasc.identifiant_foret
  OWNER TO dbadmin;
