DROP VIEW IF EXISTS oeasc_in.v1 CASCADE;


-- etape 1
CREATE VIEW oeasc_in.v1 AS
SELECT 
    o.id_observation,
	o.nb,
    o.groupes,
	r.serie,
	to_char(r.date_realisation, 'DD/MM/YYYY') AS date,
	c.id_circuit,
    c.nom_circuit,
    c.numero_circuit,
	c.ug,
	c.km,
    espece,
    valid,
	nb/km as nbkm,
	to_char(r.date_realisation, 'YYYY') AS annee
	
	FROM oeasc_in.t_observations o
	JOIN oeasc_in.t_realisations r ON r.id_realisation = o.id_realisation
	JOIN oeasc_in.t_circuits c ON c.id_circuit = r.id_circuit
;

-- etape 2
CREATE VIEW  oeasc_in.v2 AS
	SELECT SUM(nbkm)/COUNT(*) AS res2, ug, serie, annee
	FROM oeasc_in.v1
	GROUP BY annee, ug, serie
	ORDER BY annee, ug, serie
;

-- etape 3
CREATE VIEW  oeasc_in.v3 AS
	SELECT SUM(res2)/COUNT(*) as res3, ug, annee
	FROM oeasc_in.v2
	GROUP BY annee, ug
	ORDER BY annee, ug
;

-- etape 4
CREATE VIEW  oeasc_in.v4 AS
SELECT v2.ug, v2.annee, serie, v2.res2 - v3.res3 as res4
	FROM oeasc_in.v2 v2
	JOIN oeasc_in.v3 v3 ON v3.ug = v2.ug AND v3.annee = v2.annee
;

-- etape 5
CREATE VIEW  oeasc_in.v5 AS
SELECT ug, annee, SUM(res4* res4) AS res5, COUNT(*) AS nb_series 
	FROM oeasc_in.v4 v4
	GROUP BY ug, annee
;

-- etape 6
CREATE VIEW  oeasc_in.v6 AS
SELECT ug, annee, res5 / ( nb_series * (nb_series -1)) as res6
	FROM oeasc_in.v5 v5
	WHERE nb_series > 1
;

-- etape 7 et fin
CREATE VIEW  oeasc_in.v7 AS
SELECT v3.ug, v3.annee::int, res3 AS In, SQRT(res6) as variance
	FROM oeasc_in.v6 v6
	JOIN oeasc_in.v3 v3 ON v3.annee = v6.annee AND v3.ug = v6.ug
;



SELECT * FROM oeasc_in.v1;
SELECT * FROM oeasc_in.v2;
SELECT * FROM oeasc_in.v3;
SELECT * FROM oeasc_in.v4;
SELECT * FROM oeasc_in.v5;
SELECT * FROM oeasc_in.v6;
SELECT * FROM oeasc_in.v7;
