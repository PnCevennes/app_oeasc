DROP VIEW IF EXISTS oeasc_in.v1 CASCADE;

DROP VIEW IF EXISTS oeasc_in.v_result  CASCADE;
CREATE VIEW oeasc_in.v_result AS
SELECT
    o.id_observation,
	o.nb,
    r.groupes,
	r.serie,
	to_char(r.date_realisation, 'DD/MM/YYYY') AS date,
	c.id_circuit,
    c.nom_circuit,
    c.numero_circuit,
	s.nom_secteur,
	c.km,
    cor.valid,
    t.nom_tag,
    t.id_tag,
    REPLACE(CONCAT(s.nom_secteur, '_', t.nom_tag), '_all', '') as ug,
    e.nom_espece,
    r.id_realisation,
	nb/km as nbkm,
	to_char(r.date_realisation, 'YYYY') AS annee

	FROM oeasc_in.t_observations o
	JOIN oeasc_in.t_realisations r
        ON r.id_realisation = o.id_realisation
	JOIN oeasc_in.t_circuits c
        ON c.id_circuit = r.id_circuit
    JOIN oeasc_commons.t_secteurs s
        ON s.id_secteur = c.id_secteur
    JOIN oeasc_in.cor_realisation_tag cor
        ON cor.id_realisation = r.id_realisation
    JOIN oeasc_in.t_tags t
        ON t.id_tag = cor.id_tag
    JOIN oeasc_commons.t_especes e
        ON e.id_espece = o.id_espece
;
