DELETE FROM ref_geo.bib_areas_types as t
WHERE t.id_type = 301 
OR t.id_type = 302
OR t.id_type = 303;

INSERT INTO ref_geo.bib_areas_types (
id_type, type_name, type_code, type_desc, ref_name, ref_version, num_version)
VALUES(301, 'ONF Forêts', 'OEASC', 'Forêts ONF', 'ONF', 2018, ''),
(302, 'ONF Parcelles', 'OEASC', 'Parcelles ONF', 'ONF', 2018, ''),
(303, 'ONF UG', 'OEASC', 'Unités de gestion ONF', 'ONF', 2018, '')

