-- oeasc_populate_organismes.sql

DROP TABLE IF EXISTS temp;


CREATE TABLE temp (nom_organisme text, adresse_organisme text, cp_organisme text,
            ville_organisme text, tel_organisme text, email_organisme text);


COPY temp
    FROM '${ROOT_DIR}/app_oeasc/install/scripts_db/script_oeasc/organismes.csv'
    WITH DELIMITER ';' CSV QUOTE AS '''';


DELETE FROM utilisateurs.cor_organism_tag as c
    USING utilisateurs.t_tags as tags
            WHERE c.id_tag = tags.id_tag AND tags.tag_code = 'ORG_OEASC';


DELETE FROM utilisateurs.t_roles
    USING utilisateurs.bib_organismes as b, temp as t
    WHERE t_roles.id_organisme = b.id_organisme and b.nom_organisme = t.nom_organisme;

DELETE FROM utilisateurs.bib_organismes as b USING temp as t
    WHERE b.nom_organisme = t.nom_organisme;


INSERT INTO utilisateurs.bib_organismes (nom_organisme, adresse_organisme, cp_organisme, ville_organisme, tel_organisme, email_organisme)
SELECT * FROM temp;



DELETE FROM utilisateurs.t_tags
WHERE tag_code = 'ORG_OEASC';


INSERT INTO utilisateurs.t_tags(
            id_tag_type, tag_code, tag_name, tag_label, tag_desc)
    VALUES (4, 'ORG_OEASC', 'Organismes oeasc', 'Organismes oeasc', 'Liste des organismes_oeasc');


INSERT INTO utilisateurs.cor_organism_tag (id_tag, id_organism)
    SELECT tags.id_tag, b.id_organisme
        FROM utilisateurs.t_tags as tags, temp as t, utilisateurs.bib_organismes as b
            WHERE b.nom_organisme = t.nom_organisme AND tag_code = 'ORG_OEASC';


DROP TABLE temp;
