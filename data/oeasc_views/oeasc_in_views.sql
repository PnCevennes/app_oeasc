DROP VIEW IF EXISTS oeasc_in.v1 CASCADE;

CREATE VIEW oeasc_in.v1 AS
SELECT 
    o.id_observation,
	o.nb,
    r.groupes,
	r.serie,
	to_char(r.date_realisation, 'DD/MM/YYYY') AS date,
	c.id_circuit,
    c.nom_circuit,
    c.numero_circuit,
	c.ug,
	c.km,
    UNNEST(c.ug_tags) AS ug_tag,
    espece,
    r.valid,
    r.id_realisation,
	nb/km as nbkm,
	to_char(r.date_realisation, 'YYYY') AS annee
	
	FROM oeasc_in.t_observations o
	JOIN oeasc_in.t_realisations r ON r.id_realisation = o.id_realisation
	JOIN oeasc_in.t_circuits c ON c.id_circuit = r.id_circuit
;

DROP VIEW IF EXISTS oeasc_in.v2 CASCADE;
CREATE VIEW oeasc_in.v2 AS
SELECT 
    id_observation,
	nb,
    groupes,
	serie,
	date,
	id_circuit,
    nom_circuit,
    numero_circuit,
	REPLACE(CONCAT(ug, '_', ug_tag), '_all', '') as ug,
	km,
    espece,
    valid,
	nbkm,
	annee,
    id_realisation
	
	FROM oeasc_in.v1
;


DROP VIEW IF EXISTS oeasc_in.v_observers CASCADE;
CREATE VIEW oeasc_in.v_observers AS 

SELECT observer FROM
(SELECT DISTINCT
    UNNEST(
    observers
    ) observer

    FROM oeasc_in.t_realisations
    WHERE observers IS NOT NULL)a
    WHERE observer != ''
    ;

DROP VIEW IF EXISTS oeasc_in.v_circuits CASCADE;

CREATE VIEW oeasc_in.v_circuits AS
SELECT 
    id_circuit,
    nom_circuit,
    ug,
    CONCAT(ug, ' ',nom_circuit) as label

    FROM oeasc_in.t_circuits
    ORDER BY ug, nom_circuit
