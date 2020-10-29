-- oeasc_in_import_data.sql

DROP TABLE IF exists oeasc_in.import_data;

CREATE TABLE IF NOT EXISTS oeasc_in.import_data (
    
	espece character varying,
    nom_secteur character varying,
	date_realisation character varying,
	serie integer,
	numero_circuit integer,
	nom_circuit character varying,
	nb integer,
	km double precision,
    not_valid character varying
);

COPY oeasc_in.import_data
--(ug, annee, date_realisation, numero_circuit, nom_circuit, nb, km) 
FROM '/tmp/oeasc_in.csv' DELIMITER ',' CSV HEADER;

 
-- secteurs
INSERT INTO oeasc_commons.t_secteurs(nom_secteur, code_secteur)
VALUES 
('Vallées cévenoles', 'VALC'),
('Mont Aigoual', 'MAIG'),
('Mont Lozère', 'MLOZ'),
('Méjean', 'MEJ')
;

-- tags
INSERT INTO oeasc_in.t_tags(nom_tag)
VALUES
('all'),
('coeur')
;

-- circuits
DELETE FROM oeasc_in.t_circuits CASCADE;
INSERT INTO oeasc_in.t_circuits(id_secteur, numero_circuit, nom_circuit, km)
SELECT 
	id_secteur, numero_circuit, nom_circuit, km
    -- CASE 
    --     WHEN nom_circuit IN ('Fretma', 'Le Pradal') THEN ARRAY['all', 'coeur']
    --     ELSE ARRAY['all']
    -- END
	FROM oeasc_in.import_data d
    JOIN oeasc_commons.t_secteurs s
        ON s.nom_secteur = d.nom_secteur
	GROUP BY id_secteur, numero_circuit, km, nom_circuit
	ORDER BY id_secteur, numero_circuit
;

-- realisations
ALTER TABLE oeasc_in.t_realisations ADD COLUMN valid BOOLEAN;


INSERT INTO oeasc_in.t_realisations (id_circuit, serie, date_realisation, valid)
SELECT id_circuit, serie, to_date(date_realisation, '%yy-%mm-%dd'), COUNT(not_valid) = 0
    FROM oeasc_in.import_data d
    JOIN oeasc_in.t_circuits c
        ON d.nom_circuit = c.nom_circuit
    WHERE nb >= 0
    GROUP BY id_circuit, serie, date_realisation;


-- cor_relalisation tag
-- all
INSERT INTO oeasc_in.cor_realisation_tag(id_realisation, id_tag, valid)
SELECT id_realisation, id_tag, valid
    FROM oeasc_in.t_realisations
    JOIN oeasc_in.t_tags 
        ON nom_tag = 'all'
;

-- méjean coeur
INSERT INTO oeasc_in.cor_realisation_tag(id_realisation, id_tag, valid)
SELECT id_realisation, id_tag, TRUE
    FROM oeasc_in.t_realisations r
    JOIN oeasc_in.t_tags 
        ON nom_tag = 'coeur'
    JOIN oeasc_in.t_circuits c
        ON r.id_circuit = c.id_circuit
    WHERE c.nom_circuit IN ('Fretma', 'Le Pradal');



-- observations
INSERT INTO oeasc_in.t_observations (id_realisation, espece, nb)
SELECT 
	r.id_realisation, espece, nb

	FROM oeasc_in.import_data d
	JOIN oeasc_in.t_realisations r ON r.date_realisation = to_date(d.date_realisation, '%yy-%mm-%dd')
	JOIN oeasc_in.t_circuits c ON c.id_circuit = r.id_circuit 
	WHERE c.nom_circuit = d.nom_circuit AND r.serie = d.serie
	ORDER BY r.id_realisation;

SELECT  * FROM 
(SELECT COUNT(*) FROM oeasc_in.t_observations)a,
(SELECT COUNT(*) FROM oeasc_in.t_realisations)b,
(SELECT COUNT(*) FROM oeasc_in.t_circuits)c
;

ALTER TABLE oeasc_in.t_realisations DROP COLUMN valid;
