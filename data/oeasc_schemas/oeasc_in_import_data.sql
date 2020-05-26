-- oeasc_in_import_data.sql

DROP TABLE IF exists oeasc_in.import_data;

CREATE TABLE IF NOT EXISTS oeasc_in.import_data (
	ug character varying,
	annee integer,
	date_realisation character varying,
	serie integer,
	numero_circuit integer,
	nom_circuit character varying,
	nb integer,
	km double precision
);

COPY oeasc_in.import_data
--(ug, annee, date_realisation, numero_circuit, nom_circuit, nb, km) 
FROM '/tmp/oeasc_in.csv' DELIMITER ';' CSV HEADER;


-- circuits
DELETE FROM oeasc_in.t_circuits CASCADE;
INSERT INTO oeasc_in.t_circuits(ug, numero_circuit, nom_circuit, km)
SELECT 
	ug, numero_circuit, nom_circuit, km 
	FROM oeasc_in.import_data
	GROUP BY ug, numero_circuit, km, nom_circuit
	ORDER BY ug, numero_circuit
;

-- realisations
INSERT INTO oeasc_in.t_realisations (id_circuit, serie, date_realisation)
SELECT id_circuit, serie, to_date(date_realisation, '%dd%mm%yyyy')
FROM oeasc_in.import_data d
JOIN oeasc_in.t_circuits c ON d.nom_circuit = c.nom_circuit
WHERE nb >= 0;


-- observations (cerf)
INSERT INTO oeasc_in.t_observations (id_realisation, espece, nb)
SELECT 
	r.id_realisation, 'cerf', nb
	---, *
	FROM oeasc_in.import_data d
	JOIN oeasc_in.t_realisations r ON r.date_realisation = to_date(d.date_realisation, '%dd%mm%yyyy')
	JOIN oeasc_in.t_circuits c ON c.id_circuit = r.id_circuit 
	WHERE c.nom_circuit = d.nom_circuit AND r.serie = d.serie
	ORDER BY r.id_realisation;

SELECT  * FROM 
(SELECT COUNT(*) FROM oeasc_in.t_observations)a,
(SELECT COUNT(*) FROM oeasc_in.t_realisations)b,
(SELECT COUNT(*) FROM oeasc_in.t_circuits)c

