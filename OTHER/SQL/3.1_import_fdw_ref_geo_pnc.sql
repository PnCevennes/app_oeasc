DROP TABLE IF EXISTS ref_geo.li_grids;


CREATE TABLE ref_geo.li_grids
(
  id_grid character varying(50) NOT NULL,
  id_area integer NOT NULL,
  cxmin integer,
  cxmax integer,
  cymin integer,
  cymax integer,
  zc boolean,
  code_maille_10k character varying(20),
  CONSTRAINT pk_li_grids PRIMARY KEY (id_grid),
  CONSTRAINT fk_li_grids_id_area FOREIGN KEY (id_area)
      REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION
);


INSERT INTO ref_geo.li_grids
SELECT * 
FROM import_ref_geo.li_grids;


DROP TABLE IF EXISTS ref_geo.li_municipalities;

CREATE TABLE ref_geo.li_municipalities
(
  id_municipality character varying(25) NOT NULL,
  id_area integer NOT NULL,
  status character varying(22),
  insee_com character varying(5),
  nom_com character varying(50),
  insee_arr character varying(2),
  nom_dep character varying(30),
  insee_dep character varying(3),
  nom_reg character varying(35),
  insee_reg character varying(2),
  code_epci character varying(9),
  plani_precision double precision,
  siren_code character varying(10),
  canton character varying(200),
  population integer,
  multican character varying(3),
  cc_nom character varying(250),
  cc_siren bigint,
  cc_nature character varying(5),
  cc_date_creation character varying(10),
  cc_date_effet character varying(10),
  insee_commune_nouvelle character varying(5),
  meta_create_date timestamp without time zone,
  meta_update_date timestamp without time zone,
  zc boolean,
  aa boolean,
  pec boolean,
  apa boolean,
  massif character varying(50),
  arrondisst character varying(50),
  CONSTRAINT pk_li_municipalities PRIMARY KEY (id_municipality),
  CONSTRAINT fk_li_municipalities_id_area FOREIGN KEY (id_area)
      REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION
);


INSERT INTO ref_geo.li_municipalities
SELECT * 
FROM import_ref_geo.li_municipalities;



CREATE MATERIALIZED VIEW ref_geo.l_municipalities AS 
 SELECT m.id_municipality,
    m.status,
    m.insee_com,
    m.nom_com,
    m.insee_arr,
    m.nom_dep,
    m.insee_dep,
    m.nom_reg,
    m.insee_reg,
    m.code_epci,
    m.plani_precision,
    m.siren_code,
    m.canton,
    m.population,
    m.multican,
    m.cc_nom,
    m.cc_siren,
    m.cc_nature,
    m.cc_date_creation,
    m.cc_date_effet,
    m.insee_commune_nouvelle,
    m.zc,
    m.aa,
    m.pec,
    m.apa,
    m.massif,
    m.arrondisst,
    a.enable,
    a.geom
   FROM ref_geo.li_municipalities m
     JOIN ref_geo.l_areas a ON m.id_area = a.id_area
WITH DATA;


CREATE OR REPLACE VIEW ref_geo.aa AS 
 SELECT a.id_area,
    a.id_type,
    a.area_code,
    a.area_name,
    a.geom
   FROM ref_geo.l_areas a
  WHERE a.id_type = 20;

CREATE OR REPLACE VIEW ref_geo.pec AS 
 SELECT a.id_area,
    a.id_type,
    a.area_code,
    a.area_name,
    a.geom
   FROM ref_geo.l_areas a
  WHERE a.id_type = 23;


CREATE OR REPLACE VIEW ref_geo.zc AS 
 SELECT a.id_area,
    a.id_type,
    a.area_code,
    a.area_name,
    a.geom
   FROM ref_geo.l_areas a
  WHERE a.id_type = 1;
