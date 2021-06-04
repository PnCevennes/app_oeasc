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
);


CREATE TRIGGER tri_meta_dates_change_t_contents
  BEFORE INSERT OR UPDATE
  ON oeasc_commons.t_contents
  FOR EACH ROW
  EXECUTE PROCEDURE public.fct_trg_meta_dates_change();



CREATE TABLE IF NOT EXISTS oeasc_commons.t_tags
(
    id_tag serial NOT NULL,
    nom_tag CHARACTER VARYING,
    code_tag CHARACTER VARYING,

    CONSTRAINT pk_t_tags_id_tag PRIMARY KEY (id_tag)

);


CREATE TABLE IF NOT EXISTS oeasc_commons.cor_content_tag
(
    id_content INTEGER,
    id_tag INTEGER,

    CONSTRAINT pk_cor_content_tag PRIMARY KEY (id_content, id_tag),
    CONSTRAINT fk_cor_content_tag_id_content FOREIGN KEY (id_content)
        REFERENCES oeasc_commons.t_contents (id_content) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE,
    CONSTRAINT fk_cor_content_tag_id_tag FOREIGN KEY (id_tag)
        REFERENCES oeasc_commons.t_tags (id_tag) MATCH SIMPLE
        ON UPDATE CASCADE ON DELETE CASCADE
);

CREATE TRIGGER tri_meta_dates_change_t_contents
   BEFORE INSERT OR UPDATE
   ON oeasc_commons.t_contents
   FOR EACH ROW
   EXECUTE PROCEDURE public.fct_trg_meta_dates_change();


CREATE TABLE IF NOT EXISTS oeasc_commons.t_especes
(
    id_espece serial NOT NULL,
    nom_espece CHARACTER VARYING,
    code_espece CHARACTER VARYING,

    CONSTRAINT pk_t_especes_id_espece PRIMARY KEY (id_espece)
);
