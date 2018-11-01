
$psqla -f $dir_script/nomenclature/fonctions_nomenclature.sql >> $log_file


cat << EOF | $psqla

DELETE FROM ref_nomenclatures.t_nomenclatures
    WHERE source = 'OEASC';

DELETE FROM ref_nomenclatures.bib_nomenclatures_types
    WHERE source = 'OEASC';

SELECT setval('ref_nomenclatures.t_nomenclatures_id_nomenclature_seq', COALESCE((SELECT MAX(id_nomenclature)+1 FROM ref_nomenclatures.t_nomenclatures), 1), false);
SELECT setval('<ref_nomenclatures class="bib_nomenclatures_types_id"></ref_nomenclatures>_type_seq', COALESCE((SELECT MAX(id_type)+1 FROM ref_nomenclatures.bib_nomenclatures_types), 1), false);

DROP TABLE IF EXISTS temp;

CREATE TABLE temp (type_code text, label text, definition text);

\COPY temp FROM $dir_data/csv/nomenclature/oeasc_bib_nomenclature.csv WITH DELIMITER ';' CSV QUOTE AS '''';

INSERT INTO ref_nomenclatures.bib_nomenclatures_types (mnemonique, label_default, definition_default, label_fr, definition_fr, source)
    SELECT type_code, label, definition, label, definition, 'OEASC'
        FROM temp;

DROP TABLE IF EXISTS temp;

CREATE TABLE temp (type_code text, mnemonique text, label text, definition text);

\COPY temp FROM $dir_data/csv/nomenclature/oeasc_nomenclature.csv WITH DELIMITER ';' CSV QUOTE AS '''';


DROP SEQUENCE IF EXISTS serial;

CREATE SEQUENCE serial START 1;

DROP TABLE IF EXISTS temp2;

CREATE TABLE temp2 AS SELECT nextval('serial') as id, type_code, mnemonique, label, definition FROM temp;

--INSERT INTO ref_nomenclatures.t_nomenclatures (id_type, mnemonique,
--label_default, definition_default, label_fr, definition_fr, source)
--    SELECT  ref_nomenclatures.get_id_nomenclature_type(t.type_code),
--     t.mnemonique, t.label, t.definition , t.label, t.definition, 'OEASC'
--        FROM temp as t;

 INSERT INTO ref_nomenclatures.t_nomenclatures (id_type, cd_nomenclature, mnemonique,
 label_default, definition_default, label_fr, definition_fr, source)
    SELECT  ref_nomenclatures.get_id_nomenclature_type(t.type_code),
     row_number() OVER (
        PARTITION BY type_code
            ORDER BY type_code, id) - 1,
     t.mnemonique, t.label, t.definition , t.label, t.definition, 'OEASC'
        FROM temp2 as t;

DROP TABLE IF EXISTS temp, temp2;


EOF
