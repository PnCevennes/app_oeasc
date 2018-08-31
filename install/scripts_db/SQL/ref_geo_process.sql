-- ref_geo process

UPDATE ref_geo.l_OEASC_ONF_FRT
    SET geom=a.geom FROM (
        SELECT CONCAT(dept,'-',ccod_frt) as ccod, ST_MULTI(ST_UNION(geom)) as geom
        FROM ref_geo.l_OEASC_ONF_FRT
        GROUP BY ccod
        HAVING COUNT(*) > 1
        )a

    WHERE a.ccod=CONCAT(dept,'-',ccod_frt);

DELETE FROM ref_geo.l_OEASC_ONF_FRT
    WHERE id IN (SELECT id
        FROM (SELECT id,
            ROW_NUMBER() OVER (partition BY CONCAT(dept,'-',ccod_frt) ORDER BY id) AS rnum
            FROM ref_geo.l_OEASC_ONF_FRT) t
                WHERE t.rnum > 1);


UPDATE ref_geo.l_OEASC_ONF_PRF
    SET geom=a.geom FROM (
        SELECT CONCAT(dept,'-',ccod_frt,'-',ccod_prf) as ccod, ST_MULTI(ST_UNION(geom)) as geom
        FROM ref_geo.l_OEASC_ONF_PRF
        GROUP BY ccod
        HAVING COUNT(*) > 1
        )a

    WHERE a.ccod=CONCAT(dept,'-',ccod_frt,'-',ccod_prf);

DELETE FROM ref_geo.l_OEASC_ONF_PRF
    WHERE id IN (SELECT id
        FROM (SELECT id,
            ROW_NUMBER() OVER (partition BY CONCAT(dept,'-',ccod_frt,'-',ccod_prf) ORDER BY id) AS rnum
            FROM ref_geo.l_OEASC_ONF_PRF) t
                WHERE t.rnum > 1);


ALTER TABLE ref_geo.l_OEASC_ONF_UG DROP COLUMN IF EXISTS suffix;
ALTER TABLE ref_geo.l_OEASC_ONF_UG ADD COLUMN suffix integer;

UPDATE ref_geo.l_OEASC_ONF_UG as c
    SET suffix=b.suffix_b
    FROM (
        SELECT id, CONCAT(dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix) as ccod,
            row_number() OVER (
                PARTITION BY CONCAT(dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix)
                    ORDER BY CONCAT(dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix), id) AS suffix_b
            FROM (
                SELECT COUNT(*) as c, CONCAT(dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix) as ccod
                    FROM ref_geo.l_OEASC_ONF_UG as b
                    GROUP BY ccod
                    HAVING COUNT(*) >1
                    ORDER BY ccod
            )a, ref_geo.l_OEASC_ONF_UG
        WHERE a.ccod = CONCAT(dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix)
        ORDER BY a.ccod
    )b
    WHERE b.ccod = CONCAT(dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix) and b.id = c.id;

-- l_areas

SELECT pg_terminate_backend(pid), * FROM active_locks;


DROP TABLE IF EXISTS ref_geo.l_areas_cadastre CASCADE;

-- ajouter id_type dans bib_areas_type

DROP TABLE IF EXISTS oeasc.cor_areas_declaration CASCADE;


DROP TABLE IF EXISTS ref_geo.li_OEASC_ONF_FRT CASCADE;


DROP TABLE IF EXISTS ref_geo.li_OEASC_ONF_PRF CASCADE;


DROP TABLE IF EXISTS ref_geo.li_OEASC_ONF_UG CASCADE;


DROP TABLE IF EXISTS ref_geo.li_OEASC_DGD CASCADE;


DROP TABLE IF EXISTS ref_geo.li_OEASC_CADASTRE CASCADE;


-- bib_areas_type

DELETE FROM ref_geo.l_areas
    WHERE id_type >= 300 and id_type <= 400;

SELECT setval('ref_geo.l_areas_id_area_seq', (SELECT max(id_area)  FROM ref_geo.l_areas), true);

DELETE FROM ref_geo.bib_areas_types CASCADE
    WHERE id_type >= 300 and id_type <= 400;

UPDATE ref_geo.bib_areas_types
    SET type_code='COMMUNES'
    WHERE id_type=101;

UPDATE ref_geo.bib_areas_types
    SET type_code='DEPARTEMENTS'
    WHERE id_type=102;


INSERT INTO ref_geo.bib_areas_types (
    id_type, type_name, type_code, type_desc, ref_name, ref_version, num_version)

    VALUES(301, 'ONF Forêts', 'OEASC_ONF_FRT', 'Forêts ONF', 'ONF', 2018, ''),
        (302, 'ONF Parcelles', 'OEASC_ONF_PRF', 'Parcelles ONF', 'ONF', 2018, ''),
        (303, 'ONF UG', 'OEASC_ONF_UG', 'Unités de gestion ONF', 'ONF', 2018, ''),
        (304, 'DGD', 'OEASC_DGD', 'Document de gestion durable', 'ONF', 2018, ''),
        (305, 'CADASTRE', 'OEASC_CADASTRE', 'Cadastre pour l''oeasc', 'OEASC', 2018, ''),
        (306, 'COMMUNES OEASC', 'OEASC_COMMUNE', 'Communes de l''oeasc', 'OEASC', 2018, ''),
        (307, 'DEPARTEMENTS OEASC', 'OEASC_DEPARTEMENT', 'Départements de l''oeasc', 'OEASC', 2018, ''),
        (320, 'OEASC Périmètre', 'OEASC_PERIMETRE', 'Périmetre de l''OEASC', 'OEASC', 2018, '');


-- communes oeasc

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_COMMUNE'), a.area_name, a.area_code, a.geom, a.centroid, 'OEASC', '', true
        FROM (
            SELECT t.area_name, t.area_code, t.geom, t.centroid
                FROM ref_geo.l_areas as t
                    WHERE id_type=ref_geo.get_id_type('COMMUNES') AND enable
                    )a, ref_geo.perimetre_OEASC as p
       WHERE ST_INTERSECTS(a.geom, p.geom);

-- departements oeasc

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_DEPARTEMENT'), a.area_name, a.area_code, a.geom, a.centroid, 'OEASC', '', true
        FROM (
            SELECT t.area_name, t.area_code, t.geom, t.centroid
                FROM ref_geo.l_areas as t
                    WHERE id_type=ref_geo.get_id_type('DEPARTEMENTS') AND enable
                    )a, ref_geo.perimetre_OEASC as p
       WHERE ST_INTERSECTS(a.geom, p.geom);


-- insert OEASC Périmetre

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_PERIMETRE'), 'Périmètre OEASC', 'OEASC_PERIMETRE', geom, ST_CENTROID(geom), 'OEASC', '', true
    FROM ref_geo.perimetre_oeasc;

-- placer dans l_areas et faire les tables d attributs

INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_ONF_FRT'), CONCAT(dept,'-',llib_frt), CONCAT(dept,'-',ccod_frt), geom, ST_CENTROID(geom), 'OEASC', '', true
    FROM ref_geo.l_OEASC_ONF_FRT;


INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_ONF_PRF'), CONCAT(ccod_prf,'-',llib_prf), CONCAT(dept,'-',ccod_frt,'-',ccod_prf), geom, ST_CENTROID(geom), 'OEASC', '', true
    FROM ref_geo.l_OEASC_ONF_PRF;


INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_ONF_UG'), CONCAT(ccod_prf,'-',ccod_ug), CONCAT(dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix), geom, ST_CENTROID(geom), 'OEASC', '', true
    FROM ref_geo.l_OEASC_ONF_UG;


INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_DGD'), CONCAT(forinsee,'-',fornom), CONCAT(proref), geom, ST_CENTROID(geom), 'OEASC', '', true
    FROM ref_geo.l_OEASC_DGD;


INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, centroid, source, comment, enable)
    SELECT ref_geo.get_id_type('OEASC_CADASTRE'), CONCAT(insee_com,'-',section,'-',num_parc), CONCAT(id_parc), geom, ST_CENTROID(geom), 'OEASC', '', true
    FROM ref_geo.l_OEASC_CADASTRE;


-- add column geom_4326

ALTER TABLE ref_geo.l_areas ADD COLUMN geom_4326 geometry(MultiPolygon,4326);


UPDATE ref_geo.l_areas SET geom_4326 = st_transform(geom, 4326);


-- bidouille pour ne pas avoir deux fois le nom 48-bougès pff

UPDATE ref_geo.l_areas
    SET area_name='48-bougès_sj'
    WHERE area_code LIKE '%BOUGESSJ';


-- index

DROP INDEX ref_geo.idx_l_areas_type_code_area;

CREATE INDEX idx_l_areas_type_code_area
    ON ref_geo.l_areas
    USING btree
    (id_type, area_code);


DROP INDEX ref_geo.idx_l_areas_type;

CREATE INDEX idx_l_areas_type
    ON ref_geo.l_areas
    USING btree
    (id_type);


DROP INDEX ref_geo.idx_l_areas_code_area;

CREATE INDEX idx_l_areas_code_area
    ON ref_geo.l_areas
    USING btree
    (area_code);

-- create ref_geo.li_${name}

DROP VIEW IF EXISTS ref_geo.vl_OEASC_ONF_FRT;
DROP TABLE IF EXISTS ref_geo.li_OEASC_ONF_FRT;

CREATE TABLE ref_geo.li_OEASC_ONF_FRT
(
    id serial NOT NULL,
    id_area integer NOT NULL,
    area_code character varying(25),
    ccod_frt character varying(11),
    ccod_tpde character varying(4),
    ccod_ut character varying(8),
    llib_frt character varying(80),
    llib_ut character varying(50),
    qsret_frt double precision,
    dept character varying(4),
    date_maj character varying(10),
    CONSTRAINT pk_li_OEASC_ONF_FRT PRIMARY KEY (id),
    CONSTRAINT fk_li_OEASC_ONF_FRT_id_area FOREIGN KEY (id_area)
    REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE NO ACTION
)
WITH (
    OIDS=FALSE
);

INSERT INTO ref_geo.li_OEASC_ONF_FRT (id_area, area_code, ccod_frt, ccod_tpde, ccod_ut, llib_frt, llib_ut, qsret_frt, dept, date_maj)
    SELECT la.id_area, la.area_code, ccod_frt, ccod_tpde, ccod_ut, llib_frt, llib_ut, qsret_frt, dept, date_maj
        FROM ref_geo.l_OEASC_ONF_FRT, ref_geo.l_areas as la
        WHERE la.id_type = ref_geo.get_id_type('OEASC_ONF_FRT') and la.area_code = CONCAT(dept,'-',ccod_frt);

-- create ref_geo.li_${name}

DROP VIEW IF EXISTS ref_geo.vl_OEASC_ONF_PRF;
DROP TABLE IF EXISTS ref_geo.li_OEASC_ONF_PRF;

CREATE TABLE ref_geo.li_OEASC_ONF_PRF
(
    id serial NOT NULL,
    id_area integer NOT NULL,
    area_code character varying(25),
    objectid integer,
    ccod_tpde character varying(5),
    ccod_frt character varying(8),
    llib_ut character varying(50),
    llib_prf character varying(50),
    qsret_prf double precision,
    dept character varying(4),
    ccod_pst character varying(10),
    ccod_ut bigint,
    llib_frt character varying(50),
    agent_pst character varying(50),
    ccod_prf character varying(5),
    date_maj character varying(10),
    concat character varying(50),
    CONSTRAINT pk_li_OEASC_ONF_PRF PRIMARY KEY (id),
    CONSTRAINT fk_li_OEASC_ONF_PRF_id_area FOREIGN KEY (id_area)
    REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE NO ACTION
)
WITH (
    OIDS=FALSE
);


INSERT INTO ref_geo.li_OEASC_ONF_PRF (id_area, area_code, objectid, ccod_tpde, ccod_frt, llib_ut, llib_prf, qsret_prf,
        dept, ccod_pst, ccod_ut, llib_frt, agent_pst, ccod_prf, date_maj, concat)
    SELECT la.id_area, la.area_code, objectid, ccod_tpde, ccod_frt, llib_ut, llib_prf, qsret_prf,
        dept, ccod_pst, ccod_ut, llib_frt, agent_pst, ccod_prf, date_maj, concat
        FROM ref_geo.l_OEASC_ONF_PRF, ref_geo.l_areas as la
        WHERE la.id_type = ref_geo.get_id_type('OEASC_ONF_PRF') and la.area_code = CONCAT(dept,'-',ccod_frt,'-',ccod_prf);

-- create ref_geo.li_${name}

DROP VIEW IF EXISTS ref_geo.vl_OEASC_ONF_UG;
DROP TABLE IF EXISTS ref_geo.li_OEASC_ONF_UG;

CREATE TABLE ref_geo.li_OEASC_ONF_UG
(
    id serial NOT NULL,
    id_area integer NOT NULL,
    area_code character varying(25),
    objectid bigint,
    ccod_frt character varying(11),
    ccod_prf character varying(11),
    ccod_ug character varying(10),
    ccod_ut character varying(9),
    maj_date character varying(10),
    camgt_prf character varying(12),
    llib_prf character varying(25),
    qsret_prf double precision,
    qsret_ugs double precision,
    qssy_ugs double precision,
    cgrpl_ug character varying(11),
    cgrpn_ug character varying(11),
    llib_grpn character varying(16),
    concat character varying(20),
    dept character varying(4),
    ccod_tpde character varying(4),
    llib_frt character varying(200),
    agent_pst character varying(50),
    ccod_pst character varying(10),
    cvrai_ug character varying(1),
    llib_ut character varying(50),
    concat_ug character varying(40),
    suffix integer,
    CONSTRAINT pk_li_OEASC_ONF_UG PRIMARY KEY (id),
    CONSTRAINT fk_li_OEASC_ONF_UG_id_area FOREIGN KEY (id_area)
    REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE NO ACTION
)
WITH (
    OIDS=FALSE
);


INSERT INTO ref_geo.li_OEASC_ONF_UG (id_area, area_code, objectid, ccod_frt, ccod_prf, ccod_ug, ccod_ut, maj_date, 
       camgt_prf, llib_prf, qsret_prf, qsret_ugs, qssy_ugs, cgrpl_ug, 
       cgrpn_ug, llib_grpn, concat, dept, ccod_tpde, llib_frt, agent_pst, 
       ccod_pst, cvrai_ug, llib_ut, concat_ug, suffix)
    SELECT la.id_area, la.area_code, objectid, ccod_frt, ccod_prf, ccod_ug, ccod_ut, maj_date, 
       camgt_prf, llib_prf, qsret_prf, qsret_ugs, qssy_ugs, cgrpl_ug, 
       cgrpn_ug, llib_grpn, concat, dept, ccod_tpde, llib_frt, agent_pst, 
       ccod_pst, cvrai_ug, llib_ut, concat_ug, suffix
        FROM ref_geo.l_OEASC_ONF_UG, ref_geo.l_areas as la
        WHERE la.id_type = ref_geo.get_id_type('OEASC_ONF_UG') and la.area_code = CONCAT(dept,'-',ccod_frt,'-',ccod_prf,'-',ccod_ug,'-',suffix);

-- create ref_geo.li_${name}

DROP VIEW IF EXISTS ref_geo.vl_OEASC_DGD;
DROP TABLE IF EXISTS ref_geo.li_OEASC_DGD;

CREATE TABLE ref_geo.li_OEASC_DGD
(
  id serial NOT NULL,
  id_area integer NOT NULL,
  area_code character varying(25),
  forid bigint,
  fornom character varying(50),
  forsur numeric,
  forinsee character varying(5),
  dgdtype character varying(5),
  proid bigint,
  proref character varying(14),
  prosur numeric,
  progen character varying(30),
  proetat character varying(2),
  proexp character varying(30),
  prodecdat character varying(30),
  prop character varying(38),
  perlig1 character varying(38),
  perlig2 character varying(38),
  perlig3 character varying(38),
  perlig4 character varying(38),
  percp character varying(5),
  perbur character varying(35),
  x numeric,
  y numeric,
  surface numeric,
  CONSTRAINT pk_li_OEASC_DGD PRIMARY KEY (id),
  CONSTRAINT fk_li_OEASC_DGD_id_area FOREIGN KEY (id_area)
  REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
  ON UPDATE CASCADE ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);


INSERT INTO ref_geo.li_OEASC_DGD (id_area, area_code, forid, fornom, forsur, forinsee, dgdtype, proid, proref,
            prosur, progen, proetat, proexp, prodecdat, prop, perlig1, perlig2,
            perlig3, perlig4, percp, perbur, x, y, surface)
    SELECT la.id_area, la.area_code, forid, fornom, forsur, forinsee, dgdtype, proid, proref,
            prosur, progen, proetat, proexp, prodecdat, prop, perlig1, perlig2,
            perlig3, perlig4, percp, perbur, x, y, surface
        FROM ref_geo.l_OEASC_DGD, ref_geo.l_areas as la
        WHERE la.id_type = ref_geo.get_id_type('OEASC_DGD') and la.area_code = CONCAT(proref);

-- create ref_geo.li_${name}

DROP VIEW IF EXISTS ref_geo.vl_OEASC_CADASTRE;
DROP TABLE IF EXISTS ref_geo.li_OEASC_CADASTRE;

CREATE TABLE ref_geo.li_OEASC_CADASTRE
(
  id serial NOT NULL,
  id_area integer NOT NULL,
  area_code character varying(25),
  insee_com character varying(5),
  nom_com character varying(30),
  id_parc character varying(19),
  annee character varying(4),
  section character varying(2),
  num_parc character varying(4),
  surf_parc bigint,
  cpte_com character varying(15),
--  lib_prop character varying(60),
--  civilite character varying(3),
--  date_acte date,
--  val_droit character varying(51),
--  nat_dem character varying(22),
--  type_pers character varying(8),
--  gr_pers_m character varying(46),
--  tous_prop character varying(250),
  CONSTRAINT pk_li_OEASC_CADASTRE PRIMARY KEY (id),
  CONSTRAINT fk_li_OEASC_CADASTRE_id_area FOREIGN KEY (id_area)
  REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
  ON UPDATE CASCADE ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);


INSERT INTO ref_geo.li_OEASC_CADASTRE (id_area, area_code, insee_com, nom_com, id_parc, annee, section, num_parc,
       surf_parc, cpte_com
--      ,lib_prop, civilite, date_acte, val_droit, nat_dem, type_pers, gr_pers_m, tous_prop
      )
    SELECT la.id_area, la.area_code, insee_com, nom_com, id_parc, annee, section, num_parc,
       surf_parc, cpte_com
--       , lib_prop, civilite, date_acte, val_droit, nat_dem, type_pers, gr_pers_m, tous_prop
        FROM ref_geo.l_OEASC_CADASTRE, ref_geo.l_areas as la
        WHERE la.id_type = ref_geo.get_id_type('OEASC_CADASTRE') and la.area_code = CONCAT(id_parc);

