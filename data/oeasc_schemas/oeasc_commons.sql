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

CREATE TABLE oeasc_commons.t_contents (
	id_content SERIAL,
    code CHARACTER VARYING(),
    md text,
    meta_create_date timestamp without time zone,
    meta_update_date timestamp without time zone,

	CONSTRAINT pk_cor_contents_id_content PRIMARY KEY (id_content),
)

CREATE TRIGGER tri_meta_dates_change_t_contents
   BEFORE INSERT OR UPDATE
   ON oeasc_commons.t_contents
   FOR EACH ROW
   EXECUTE PROCEDURE public.fct_trg_meta_dates_change();
