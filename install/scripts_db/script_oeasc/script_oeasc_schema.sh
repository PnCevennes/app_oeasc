
if [[ "$ROOT_DIR" = "" ]]; then
    ROOT_DIR=$(readlink -e "${0%/*}")/../../..
fi
config_file=${ROOT_DIR}/install/scripts_db/script_config.sh
. $config_file


echo '-- oeasc schema'


cat << EOF

SELECT pg_terminate_backend(pid), * FROM active_locks;

EOF


cat << EOF

DROP SCHEMA IF EXISTS oeasc CASCADE;

CREATE SCHEMA IF NOT EXISTS oeasc;

EOF


cat << EOF

DROP TABLE IF EXISTS oeasc.t_proprietaires;

CREATE TABLE IF NOT EXISTS oeasc.t_proprietaires
(

    id_proprietaire serial NOT NULL,

    nom_proprietaire CHARACTER VARYING(250),
    telephone CHARACTER VARYING(20),
    email CHARACTER VARYING(250),
    adresse CHARACTER VARYING(250),
    s_code_postal CHARACTER VARYING(10),
    s_commune CHARACTER VARYING(100),

    id_nomenclature_proprietaire_declarant INTEGER,
    id_nomenclature_proprietaire_type INTEGER,

    -- contraintes cle primaire

    CONSTRAINT pk_t_proprietaires_id_proprietaire PRIMARY KEY (id_proprietaire),

    -- contraintes nomenclature

    CONSTRAINT fk_t_proprietaires_id_nomenclature_proprietaire_declarant FOREIGN KEY (id_nomenclature_proprietaire_declarant)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_proprietaire_id_nomenclature_proprietaire_declarant CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_proprietaire_declarant, 'OEASC_PROPRIETAIRE_DECLARANT')) NOT VALID,

    CONSTRAINT fk_t_proprietaires_id_nomenclature_proprietaire_type FOREIGN KEY (id_nomenclature_proprietaire_type)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_proprietaire_id_nomenclature_proprietaire_type CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_proprietaire_type, 'OEASC_PROPRIETAIRE_TYPE')) NOT VALID

);


DROP TABLE IF EXISTS oeasc.t_forets;

CREATE TABLE IF NOT EXISTS oeasc.t_forets
(
    id_foret serial NOT NULL,

    id_proprietaire INTEGER,

    b_statut_public BOOLEAN,
    b_regime_forestier BOOLEAN,
    b_document_de_gestion BOOLEAN,

    nom_foret CHARACTER VARYING(256),

    superficie DOUBLE PRECISION,

    -- contraintes cle primaire

    CONSTRAINT pk_t_forets_id_foret PRIMARY KEY (id_foret),

    -- contraintes clés étrangères

    CONSTRAINT fk_t_forets_id_proprietaire FOREIGN KEY (id_proprietaire)
        REFERENCES oeasc.t_proprietaires (id_proprietaire) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION
);


DROP TABLE IF EXISTS oeasc.t_declarations;

CREATE TABLE IF NOT EXISTS oeasc.t_declarations
(
    id_declaration serial NOT NULL,

    -- localisation

    id_nomenclature_foret_type INTEGER,

    -- peuplement

    id_nomenclature_peuplement_origine INTEGER,
    id_nomenclature_peuplement_type INTEGER,
    id_nomenclature_peuplement_paturage_frequence INTEGER,
    id_nomenclature_peuplement_acces INTEGER,
    id_nomenclature_peuplement_essence_principale INTEGER,

    b_peuplement_protection_existence BOOLEAN,
    b_peuplement_paturage_presence BOOLEAN,

    commentaire text,

    meta_create_date timestamp without time zone,
    meta_update_date timestamp without time zone,

    -- contraintes cle primaire

    CONSTRAINT pk_t_declaration_id_declaration PRIMARY KEY (id_declaration),

    -- contraintes localisation

    CONSTRAINT fk_t_declarations_id_nomenclature_foret_type FOREIGN KEY (id_nomenclature_foret_type)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_declarations_id_nomenclature_foret_type CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_foret_type, 'OEASC_FORET_TYPE')) NOT VALID,

    -- contraintes cor nomenclatures peuplement

    CONSTRAINT fk_t_declarations_id_nomenclature_peuplement_essence_principale FOREIGN KEY (id_nomenclature_peuplement_essence_principale)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_declarations_id_nomenclature_peuplement_essence_principale CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_peuplement_essence_principale, 'OEASC_PEUPLEMENT_ESSENCE')) NOT VALID,

    CONSTRAINT fk_t_declarations_id_nomenclature_peuplement_origine FOREIGN KEY (id_nomenclature_peuplement_origine)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_declarations_id_nomenclature_peuplement_origine CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_peuplement_origine, 'OEASC_PEUPLEMENT_ORIGINE')) NOT VALID,

    CONSTRAINT fk_t_declarations_id_nomenclature_peuplement_type FOREIGN KEY (id_nomenclature_peuplement_type)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_declarations_id_nomenclature_peuplement_type CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_peuplement_type, 'OEASC_PEUPLEMENT_TYPE')) NOT VALID,

    CONSTRAINT fk_t_declarations_id_nomenclature_peuplement_paturage_frequence FOREIGN KEY (id_nomenclature_peuplement_paturage_frequence)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_declarations_id_nomenclature_peuplement_paturage_frequence CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_peuplement_paturage_frequence, 'OEASC_PEUPLEMENT_PATURAGE_FREQUENCE')) NOT VALID,

    CONSTRAINT fk_t_declarations_id_nomenclature_peuplement_acces FOREIGN KEY (id_nomenclature_peuplement_acces)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_declarations_id_nomenclature_peuplement_acces CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_peuplement_acces, 'OEASC_PEUPLEMENT_ACCES')) NOT VALID
);

-- gestion des dates

CREATE TRIGGER tri_meta_dates_change_t_declarations
   BEFORE INSERT OR UPDATE
   ON oeasc.t_declarations
   FOR EACH ROW
   EXECUTE PROCEDURE public.fct_trg_meta_dates_change();


DROP TABLE IF EXISTS oeasc.t_degats;

CREATE TABLE IF NOT EXISTS oeasc.t_degats
(
    id_degat serial NOT NULL,

    id_declaration INTEGER,

    id_nomenclature_degat_type serial NOT NULL,

    CONSTRAINT pk_t_degats_id_degat PRIMARY KEY (id_degat),

    CONSTRAINT fk_t_degats_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_t_degats_id_nomenclature_degat_type FOREIGN KEY (id_nomenclature_degat_type)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION,
    CONSTRAINT check_t_degats_id_nomenclature_degat_type CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_degat_type, 'OEASC_DEGAT_TYPE')) NOT VALID

);


DROP TABLE IF EXISTS oeasc.t_degat_essences;

CREATE TABLE IF NOT EXISTS oeasc.t_degat_essences
(
    id_degat_essence serial NOT NULL,

    id_degat INTEGER,

    id_nomenclature_degat_essence INTEGER,
    id_nomenclature_degat_etendue INTEGER,
    id_nomenclature_degat_gravite INTEGER,
    id_nomenclature_degat_anteriorite INTEGER,

    CONSTRAINT pk_t_degat_essences_id_degat_essence PRIMARY KEY (id_degat_essence),

    CONSTRAINT fk_t_degat_id_degat FOREIGN KEY (id_degat)
        REFERENCES oeasc.t_degats (id_degat) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_t_degat_essences_id_nomenclature_degat_essence FOREIGN KEY (id_nomenclature_degat_essence)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT check_t_degat_type_id_nomenclature_degat_essence CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_degat_essence, 'OEASC_PEUPLEMENT_ESSENCE')) NOT VALID,

    CONSTRAINT fk_t_degat_essences_id_nomenclature_degat_etendue FOREIGN KEY (id_nomenclature_degat_etendue)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT check_t_degat_type_id_nomenclature_degat_etendue CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_degat_etendue, 'OEASC_DEGAT_ETENDUE')) NOT VALID,

    CONSTRAINT fk_t_degat_essences_id_nomenclature_degat_gravite FOREIGN KEY (id_nomenclature_degat_gravite)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT check_t_degat_type_id_nomenclature_degat_gravite CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_degat_gravite, 'OEASC_DEGAT_GRAVITE')) NOT VALID,

    CONSTRAINT fk_t_degat_essences_id_nomenclature_degat_anteriorite FOREIGN KEY (id_nomenclature_degat_anteriorite)
        REFERENCES ref_nomenclatures.t_nomenclatures (id_nomenclature) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT check_t_degat_type_id_nomenclature_degat_anteriorite CHECK (ref_nomenclatures.check_nomenclature_type_by_mnemonique(
        id_nomenclature_degat_anteriorite, 'OEASC_DEGAT_ANTERIORITE')) NOT VALID

);
EOF


echo '-- oeasc.cor_areas_declarations'

cat << EOF

DROP TABLE IF EXISTS oeasc.cor_areas_declarations;

CREATE TABLE IF NOT EXISTS oeasc.cor_areas_declarations
(
    id_declaration integer NOT NULL,
    id_area integer NOT NULL,

    CONSTRAINT pk_cor_areas_declaration PRIMARY KEY (id_declaration, id_area),

    CONSTRAINT fk_cor_areas_declaration_id_declaration FOREIGN KEY (id_declaration)
        REFERENCES oeasc.t_declarations (id_declaration) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_cor_areas_foret_id_area FOREIGN KEY (id_area)
        REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION
);

EOF

echo '-- oeasc.cor_areas_forets'

cat << EOF

DROP TABLE IF EXISTS oeasc.cor_areas_forets;

CREATE TABLE IF NOT EXISTS oeasc.cor_areas_forets
(
    id_foret integer NOT NULL,
    id_area integer NOT NULL,

    CONSTRAINT pk_cor_areas_foret PRIMARY KEY (id_foret, id_area),

    CONSTRAINT fk_cor_areas_foret_id_foret FOREIGN KEY (id_foret)
        REFERENCES oeasc.t_forets (id_foret) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,

    CONSTRAINT fk_cor_areas_foret_id_area FOREIGN KEY (id_area)
        REFERENCES ref_geo.l_areas (id_area) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE NO ACTION
);

EOF


echo '-- correlations nomenclature declaration'

${ROOT_DIR}/install/scripts_db/script_oeasc/script_cor_nomenclature.sh declaration OEASC_PEUPLEMENT_ESSENCE _essence_secondaire
${ROOT_DIR}/install/scripts_db/script_oeasc/script_cor_nomenclature.sh declaration OEASC_PEUPLEMENT_ESSENCE _essence_complementaire
${ROOT_DIR}/install/scripts_db/script_oeasc/script_cor_nomenclature.sh declaration OEASC_PEUPLEMENT_MATURITE _maturite
${ROOT_DIR}/install/scripts_db/script_oeasc/script_cor_nomenclature.sh declaration OEASC_PEUPLEMENT_PROTECTION_TYPE _protection_type
${ROOT_DIR}/install/scripts_db/script_oeasc/script_cor_nomenclature.sh declaration OEASC_PEUPLEMENT_PATURAGE_TYPE _paturage_type
${ROOT_DIR}/install/scripts_db/script_oeasc/script_cor_nomenclature.sh declaration OEASC_PEUPLEMENT_PATURAGE_STATUT _paturage_statut
${ROOT_DIR}/install/scripts_db/script_oeasc/script_cor_nomenclature.sh declaration OEASC_PEUPLEMENT_ESPECE _espece

${ROOT_DIR}/install/scripts_db/script_oeasc/script_cor_nomenclature.sh foret OEASC_COMMUNE _commune
${ROOT_DIR}/install/scripts_db/script_oeasc/script_cor_nomenclature.sh foret OEASC_DEPARTEMENT _departement


cat << EOF

-- Function: oeasc_get_id_proprietaire_from_name(character varying)

DROP FUNCTION IF EXISTS oeasc.get_id_proprietaire_from_name(character varying);

CREATE OR REPLACE FUNCTION oeasc.get_id_proprietaire_from_name(
    myname CHARACTER VARYING)

    RETURNS INTEGER AS
    \$BODY\$
    --
    -- Returns id_proprietaire from the name
    --
        DECLARE theidproprietaire INTEGER;
        BEGIN
            EXECUTE format( ' SELECT  n.id_proprietaire
                FROM oeasc.t_proprietaires n
                WHERE nom_proprietaire = ''%s'' ', REPLACE(myname,'''','''''') ) INTO theidproprietaire;
            return theidproprietaire;
        END;
    \$BODY\$
    LANGUAGE plpgsql IMMUTABLE
    COST 100;

EOF


cat << EOF
-- ajout des proprietaires pour les forets publiques"

DROP TABLE IF EXISTS temp;

CREATE TABLE temp (type text, name text, telephone text, email text, adresse text, code_postal text, commune text);

COPY temp
    FROM '/home/joel/Info/PNC/OEASC/app_oeasc/install/scripts_db/script_oeasc/liste_proprietaires_publics_oeasc.csv'
    WITH DELIMITER ';' CSV QUOTE AS '''';

DELETE FROM oeasc.t_proprietaires;

INSERT INTO oeasc.t_proprietaires (id_nomenclature_proprietaire_type, nom_proprietaire, telephone, email, adresse, s_code_postal, s_commune)
    SELECT ref_nomenclatures.get_nomenclature_id_from_label(type, 'OEASC_PROPRIETAIRE_TYPE'), name, telephone, email, adresse, code_postal, commune
    FROM temp;

DROP TABLE temp;


-- insertion des forets pour les forets publiques

DROP TABLE IF EXISTS temp;

DELETE FROM oeasc.t_forets;

CREATE TABLE temp (dept text, ccod_frt text, nom_proprietaire text);

COPY temp
    FROM '/home/joel/Info/PNC/OEASC/app_oeasc/install/scripts_db/script_oeasc/liens_proprietaires_publics_forets.csv'
    WITH DELIMITER ';' CSV QUOTE AS '''';


INSERT INTO oeasc.t_forets (
    id_proprietaire, b_statut_public, b_regime_forestier, nom_foret, superficie)
SELECT  oeasc.get_id_proprietaire_from_name(t.nom_proprietaire), true, true, l.area_name, ROUND(ST_AREA(l.geom)/10000*10)/10
    FROM ref_geo.l_areas as l, temp as t
    WHERE id_type = ref_geo.get_id_type('OEASC_ONF_FRT')
        AND l.area_code = CONCAT(t.dept, '-', t.ccod_frt)
        ORDER BY area_name;



-- correlation foret publique, l_areas

INSERT INTO oeasc.cor_areas_forets(
    id_area, id_foret)
SELECT  l.id_area, f.id_foret
    FROM ref_geo.l_areas as l, oeasc.t_forets as f
    WHERE id_type = ref_geo.get_id_type('OEASC_ONF_FRT')
        AND f.nom_foret = l.area_name
        ORDER BY area_name;


-- insertion des forets pour les forets privée avec DGD


-- renseignement des communes et des departements :

INSERT INTO oeasc.cor_areas_forets(
    id_area, id_foret)
    SELECT b.id_area, a.id_foret --,a.area_name, b.area_name, ST_AREA(ST_INTERSECTION(b.geom, a.geom))*(1./ST_AREA(b.geom) + 1./ST_AREA(a.geom))
        FROM ref_geo.l_areas as b,
        (SELECT l.id_area as id_area, c.id_foret, l.area_name,  ref_geo.intersect_rel_area(c.id_area,'OEASC_COMMUNE',0.05) as id_com, geom
            FROM oeasc.cor_areas_forets as c, ref_geo.l_areas as l
            WHERE l.id_type = ref_geo.get_id_type('OEASC_ONF_FRT') AND l.id_area = c.id_area) a
        WHERE b.id_area = a.id_com
        ORDER BY a.area_name, b.area_name;

INSERT INTO oeasc.cor_areas_forets(
    id_area, id_foret)
    SELECT b.id_area, a.id_foret --,a.area_name, b.area_name, ST_AREA(ST_INTERSECTION(b.geom, a.geom))*(1./ST_AREA(b.geom) + 1./ST_AREA(a.geom))
        FROM ref_geo.l_areas as b,
        (SELECT l.id_area as id_area, c.id_foret, l.area_name,  ref_geo.intersect_rel_area(c.id_area,'OEASC_DEPARTEMENT',0.05) as id_com, geom
            FROM oeasc.cor_areas_forets as c, ref_geo.l_areas as l
            WHERE l.id_type = ref_geo.get_id_type('OEASC_ONF_FRT') AND l.id_area = c.id_area) a
        WHERE b.id_area = a.id_com
        ORDER BY a.area_name, b.area_name;

EOF
