-- Table: ref_geo.l_areas

-- DROP TABLE ref_geo.l_areas;

ALTER TABLE ref_geo.l_areas ADD COLUMN IF NOT EXISTS geom_4326 geometry(MultiPolygon,4326);

CREATE TABLE IF NOT EXISTS ref_geo.li_areas
(
  id_info serial NOT NULL,
  id_area serial NOT NULL,
  id_type integer NOT NULL,
  area_name character varying(250),
  area_code character varying(25),
  source character varying(250),
  enable boolean NOT NULL DEFAULT true,
  label character varying(250),
  surface_renseignee numeric,
  surface_calculee numeric,
  dept character varying(3),

  CONSTRAINT pk_li_areas PRIMARY KEY (id_info),
  CONSTRAINT fk_li_areas_id_areas FOREIGN KEY (id_area)
      REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION,
  CONSTRAINT fk_li_areas_id_type FOREIGN KEY (id_type)
      REFERENCES ref_geo.bib_areas_types (id_type) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

CREATE TABLE IF NOT EXISTS ref_geo.l_areas_simples
(
  id_area_simple serial NOT NULL,
  id_area serial NOT NULL,
  id_type integer NOT NULL,
  area_name character varying(250),
  area_code character varying(25),
  source character varying(250),
  tolerance numeric,
  geom_4326 geometry(MultiPolygon,4326),
  CONSTRAINT pk_l_areas_simples PRIMARY KEY (id_area_simple),
  CONSTRAINT fk_l_areas_simples_id_areas FOREIGN KEY (id_area)
      REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION,
  CONSTRAINT fk_l_areas_simples_id_type FOREIGN KEY (id_type)
      REFERENCES ref_geo.bib_areas_types (id_type) MATCH SIMPLE
      ON UPDATE CASCADE ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);

DROP VIEW IF EXISTS ref_geo.vl_areas;

CREATE OR REPLACE VIEW ref_geo.vl_areas AS
    SELECT li.id_area, li.id_type, l.geom_4326, l.geom, li.area_code, li.label, li.area_name, li.surface_calculee, li.surface_renseignee, li.source, li.enable
        FROM ref_geo.l_areas l, ref_geo.li_areas li
        WHERE  l.id_area=li.id_area;

DROP VIEW IF EXISTS ref_geo.vl_areas_simples;

CREATE OR REPLACE VIEW ref_geo.vl_areas_simples AS
    SELECT li.id_area, li.id_type, l.geom_4326, li.area_code, li.label, li.area_name, li.surface_calculee, li.surface_renseignee, li.source, li.enable
        FROM ref_geo.l_areas_simples l, ref_geo.li_areas li
        WHERE  l.id_area=li.id_area;

CREATE INDEX index_l_areas_type ON ref_geo.l_areas (id_type);
CREATE INDEX index_l_areas_area ON ref_geo.l_areas (id_area);
CREATE INDEX index_l_areas_code ON ref_geo.l_areas (area_code);
