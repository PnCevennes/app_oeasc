
if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file


name=OEASC_ONF_FRT
table=table_$name
table=${!table}
keys=keys_$name
keys=${!keys}
echo '-- create ref_geo.li_${name}'

cat << EOF

DROP VIEW IF EXISTS ref_geo.vl_${name};
DROP TABLE IF EXISTS ref_geo.li_${name};

CREATE TABLE ref_geo.li_${name}
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
    CONSTRAINT pk_li_${name} PRIMARY KEY (id),
    CONSTRAINT fk_li_${name}_id_area FOREIGN KEY (id_area)
    REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE NO ACTION
)
WITH (
    OIDS=FALSE
);

INSERT INTO ref_geo.li_${name} (id_area, area_code, ccod_frt, ccod_tpde, ccod_ut, llib_frt, llib_ut, qsret_frt, dept, date_maj)
    SELECT la.id_area, la.area_code, ccod_frt, ccod_tpde, ccod_ut, llib_frt, llib_ut, qsret_frt, dept, date_maj
        FROM ref_geo.${table}, ref_geo.l_areas as la
        WHERE la.id_type = ref_geo.get_id_type('$name') and la.area_code = CONCAT($keys);

EOF

name=OEASC_ONF_PRF
table=table_$name
table=${!table}
keys=keys_$name
keys=${!keys}
echo '-- create ref_geo.li_${name}'

cat <<EOF

DROP VIEW IF EXISTS ref_geo.vl_${name};
DROP TABLE IF EXISTS ref_geo.li_${name};

CREATE TABLE ref_geo.li_${name}
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
    CONSTRAINT pk_li_${name} PRIMARY KEY (id),
    CONSTRAINT fk_li_${name}_id_area FOREIGN KEY (id_area)
    REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE NO ACTION
)
WITH (
    OIDS=FALSE
);


INSERT INTO ref_geo.li_${name} (id_area, area_code, objectid, ccod_tpde, ccod_frt, llib_ut, llib_prf, qsret_prf,
        dept, ccod_pst, ccod_ut, llib_frt, agent_pst, ccod_prf, date_maj, concat)
    SELECT la.id_area, la.area_code, objectid, ccod_tpde, ccod_frt, llib_ut, llib_prf, qsret_prf,
        dept, ccod_pst, ccod_ut, llib_frt, agent_pst, ccod_prf, date_maj, concat
        FROM ref_geo.${table}, ref_geo.l_areas as la
        WHERE la.id_type = ref_geo.get_id_type('$name') and la.area_code = CONCAT($keys);

EOF

# exit 1;

name=OEASC_ONF_UG
table=table_$name
table=${!table}
keys=keys_$name
keys=${!keys}
echo '-- create ref_geo.li_${name}'

cat <<EOF

DROP VIEW IF EXISTS ref_geo.vl_${name};
DROP TABLE IF EXISTS ref_geo.li_${name};

CREATE TABLE ref_geo.li_${name}
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
    CONSTRAINT pk_li_${name} PRIMARY KEY (id),
    CONSTRAINT fk_li_${name}_id_area FOREIGN KEY (id_area)
    REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
    ON UPDATE CASCADE ON DELETE NO ACTION
)
WITH (
    OIDS=FALSE
);


INSERT INTO ref_geo.li_${name} (id_area, area_code, objectid, ccod_frt, ccod_prf, ccod_ug, ccod_ut, maj_date, 
       camgt_prf, llib_prf, qsret_prf, qsret_ugs, qssy_ugs, cgrpl_ug, 
       cgrpn_ug, llib_grpn, concat, dept, ccod_tpde, llib_frt, agent_pst, 
       ccod_pst, cvrai_ug, llib_ut, concat_ug, suffix)
    SELECT la.id_area, la.area_code, objectid, ccod_frt, ccod_prf, ccod_ug, ccod_ut, maj_date, 
       camgt_prf, llib_prf, qsret_prf, qsret_ugs, qssy_ugs, cgrpl_ug, 
       cgrpn_ug, llib_grpn, concat, dept, ccod_tpde, llib_frt, agent_pst, 
       ccod_pst, cvrai_ug, llib_ut, concat_ug, suffix
        FROM ref_geo.${table}, ref_geo.l_areas as la
        WHERE la.id_type = ref_geo.get_id_type('$name') and la.area_code = CONCAT($keys);

EOF

name=OEASC_DGD
table=table_$name
table=${!table}
keys=keys_$name
keys=${!keys}
echo '-- create ref_geo.li_${name}'

cat <<EOF

DROP VIEW IF EXISTS ref_geo.vl_${name};
DROP TABLE IF EXISTS ref_geo.li_${name};

CREATE TABLE ref_geo.li_${name}
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
  CONSTRAINT pk_li_${name} PRIMARY KEY (id),
  CONSTRAINT fk_li_${name}_id_area FOREIGN KEY (id_area)
  REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
  ON UPDATE CASCADE ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);


INSERT INTO ref_geo.li_${name} (id_area, area_code, forid, fornom, forsur, forinsee, dgdtype, proid, proref,
            prosur, progen, proetat, proexp, prodecdat, prop, perlig1, perlig2,
            perlig3, perlig4, percp, perbur, x, y, surface)
    SELECT la.id_area, la.area_code, forid, fornom, forsur, forinsee, dgdtype, proid, proref,
            prosur, progen, proetat, proexp, prodecdat, prop, perlig1, perlig2,
            perlig3, perlig4, percp, perbur, x, y, surface
        FROM ref_geo.${table}, ref_geo.l_areas as la
        WHERE la.id_type = ref_geo.get_id_type('$name') and la.area_code = CONCAT($keys);

EOF



name=OEASC_CADASTRE
table=table_$name
table=${!table}
keys=keys_$name
keys=${!keys}
echo '-- create ref_geo.li_${name}'

cat <<EOF

DROP VIEW IF EXISTS ref_geo.vl_${name};
DROP TABLE IF EXISTS ref_geo.li_${name};

CREATE TABLE ref_geo.li_${name}
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
  CONSTRAINT pk_li_${name} PRIMARY KEY (id),
  CONSTRAINT fk_li_${name}_id_area FOREIGN KEY (id_area)
  REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
  ON UPDATE CASCADE ON DELETE NO ACTION
)
WITH (
  OIDS=FALSE
);


INSERT INTO ref_geo.li_${name} (id_area, area_code, insee_com, nom_com, id_parc, annee, section, num_parc,
       surf_parc, cpte_com
--      ,lib_prop, civilite, date_acte, val_droit, nat_dem, type_pers, gr_pers_m, tous_prop
      )
    SELECT la.id_area, la.area_code, insee_com, nom_com, id_parc, annee, section, num_parc,
       surf_parc, cpte_com
--       , lib_prop, civilite, date_acte, val_droit, nat_dem, type_pers, gr_pers_m, tous_prop
        FROM ref_geo.${table}, ref_geo.l_areas as la
        WHERE la.id_type = ref_geo.get_id_type('$name') and la.area_code = CONCAT($keys);

EOF
