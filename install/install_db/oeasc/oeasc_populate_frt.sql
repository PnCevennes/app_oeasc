-- ajout des proprietaires pour les forets publiques"

DROP TABLE IF EXISTS temp;

CREATE TABLE temp (type text, name text, telephone text, email text, adresse text, code_postal text, commune text);

\COPY temp FROM '/tmp/liste_proprietaires_publics_oeasc.csv' WITH DELIMITER ';' CSV QUOTE AS '''';

DELETE FROM oeasc.t_proprietaires;

INSERT INTO oeasc.t_proprietaires (id_nomenclature_proprietaire_type, nom_proprietaire, telephone, email, adresse, s_code_postal, s_commune_proprietaire)
    SELECT ref_nomenclatures.get_nomenclature_id_from_label(type, 'OEASC_PROPRIETAIRE_TYPE'), name, telephone, email, adresse, code_postal, commune
    FROM temp;

DROP TABLE temp;

-- ajout des proprietaires des forets privées

INSERT INTO oeasc.t_proprietaires (id_nomenclature_proprietaire_type, nom_proprietaire, telephone, email, adresse, s_code_postal, s_commune_proprietaire)
    SELECT ref_nomenclatures.get_nomenclature_id_from_label('Privé', 'OEASC_PROPRIETAIRE_TYPE'), prop, '', '', CONCAT(perlig1,' ', perlig2,' ', perlig3,' ', perlig4), percp, perbur
        FROM ref_geo.temp_oeasc_dgd
        GROUP BY prop, CONCAT(perlig1,' ', perlig2,' ', perlig3,' ', perlig4), percp, perbur;



-- insertion des forets pour les forets publiques

DELETE FROM oeasc.t_forets;

DROP TABLE IF EXISTS temp;

CREATE TABLE temp (area_code text, nom_proprietaire text);
\COPY temp FROM '/tmp/liens_proprietaires_publics_forets.csv' WITH DELIMITER ';' CSV QUOTE AS '''';


INSERT INTO oeasc.t_forets (
    id_proprietaire, b_statut_public, b_document, code_foret, nom_foret, label_foret, surface_renseignee, surface_calculee)
SELECT  oeasc.get_id_proprietaire_from_name(t.nom_proprietaire), true, true, l.area_code, l.area_name, l.label, l.surface_renseignee, l.surface_calculee
    FROM ref_geo.li_areas as l, temp as t
    WHERE id_type = ref_geo.get_id_type('OEASC_ONF_FRT')
        AND l.area_code = t.area_code
        ORDER BY area_name;

-- correlation foret publique, l_areas

INSERT INTO oeasc.cor_areas_forets(
    id_area, id_foret)
SELECT  l.id_area, f.id_foret
    FROM ref_geo.li_areas as l, oeasc.t_forets as f
    WHERE id_type = ref_geo.get_id_type('OEASC_ONF_FRT')
        AND f.code_foret = l.area_code
        ORDER BY area_name;


-- insertion des forets pour les forets privée avec DGD

INSERT INTO oeasc.t_forets (
    id_proprietaire, b_statut_public, b_document, code_foret, nom_foret, label_foret, surface_renseignee, surface_calculee)
    SELECT oeasc.get_id_proprietaire_from_name(p.nom_proprietaire), false, true, l.area_code, l.area_name, l.label, l.surface_renseignee, l.surface_calculee
        FROM oeasc.t_proprietaires as p, ref_geo.temp_oeasc_dgd as d, ref_geo.li_areas as l
        WHERE p.nom_proprietaire = d.prop
        AND CONCAT(d.forid,'-', d.proref) = l.area_code;

INSERT INTO oeasc.cor_areas_forets(
    id_area, id_foret)
SELECT  l.id_area, f.id_foret
    FROM ref_geo.li_areas as l, oeasc.t_forets as f
    WHERE id_type = ref_geo.get_id_type('OEASC_DGD')
        AND f.code_foret = l.area_code;

-- renseignement des communes et des departements :

INSERT INTO oeasc.cor_areas_forets(
     id_area, id_foret)
SELECT ref_geo.intersect_rel_area(l.id_area, 'OEASC_COMMUNE', 0.05), c.id_foret
    FROM oeasc.cor_areas_forets as c, ref_geo.l_areas as l
    WHERE (l.id_type = ref_geo.get_id_type('OEASC_ONF_FRT') OR l.id_type = ref_geo.get_id_type('OEASC_DGD')) AND l.id_area = c.id_area
    ORDER BY c.id_foret;
