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

--------------------
--PUBLIC FUNCTIONS--
--------------------
CREATE OR REPLACE FUNCTION public.fct_trg_meta_dates_change()
  RETURNS trigger AS
$BODY$
begin
        if(TG_OP = 'INSERT') THEN
                NEW.meta_create_date = NOW();
        ELSIF(TG_OP = 'UPDATE') THEN
                NEW.meta_update_date = NOW();
                if(NEW.meta_create_date IS NULL) THEN
                        NEW.meta_create_date = NOW();
                END IF;
        end IF;
        return NEW;
end;
$BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE TRIGGER tri_meta_dates_change_t_contents
  BEFORE INSERT OR UPDATE
  ON oeasc_commons.t_contents
  FOR EACH ROW
  EXECUTE PROCEDURE public.fct_trg_meta_dates_change();
