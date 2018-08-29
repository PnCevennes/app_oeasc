-- ajout des proprietaires pour les forets publiques"

DROP TABLE IF EXISTS temp;

CREATE TABLE temp (type text, name text, telephone text, email text, adresse text, code_postal text, commune text);

COPY temp
    FROM '/home/joel/Info/PNC/OEASC/app_oeasc/install/scripts_db/script_oeasc/liste_proprietaires_publics_oeasc.csv'
    WITH DELIMITER ';' CSV QUOTE AS '''';

DELETE FROM oeasc.t_proprietaires;

INSERT INTO oeasc.t_proprietaires (id_nomenclature_proprietaire_type, s_nom_proprietaire, s_telephone, s_email, s_adresse, s_code_postal, s_commune_proprietaire)
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
    id_proprietaire, b_statut_public, b_document, s_nom_foret, d_superficie)
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
        AND f.s_nom_foret = l.area_name
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
