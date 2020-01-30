-- schema oeasc_commons

-- oeasc_commons.liste_organismes liste des organisme de l'oeasc (pour la liste à l'inscription)

CREATE SCHEMA IF NOT EXISTS oeasc_commons;

CREATE TABLE oeasc_commons.t_liste_organismes (
	id_organisme INT,
	CONSTRAINT pk_cor_organismes_id_organisme PRIMARY KEY (id_organisme),
	CONSTRAINT fk_cor_organismes_id_organisme FOREIGN KEY (id_organisme)
		REFERENCES utilisateurs.bib_organismes (id_organisme) MATCH SIMPLE
		ON UPDATE CASCADE ON DELETE CASCADE
)
