DROP TABLE oeasc_commons.t_contents
CREATE TABLE oeasc_commons.t_contents (
	id_content SERIAL,
    code CHARACTER VARYING,
    md text,
    meta_create_date timestamp without time zone,
    meta_update_date timestamp without time zone,

	CONSTRAINT pk_t_contents_id_content PRIMARY KEY (id_content)
);

-- CREATE TRIGGER tri_meta_dates_change_t_contents
--    BEFORE INSERT OR UPDATE
--    ON oeasc_commons.t_contents
--    FOR EACH ROW
--    EXECUTE PROCEDURE public.fct_trg_meta_dates_change();

-- CREATE TABLE oeasc_commons.t_communes (
-- 	id_commune INT,
--     code_postal CHARACTER VARYING(5),
--     nom_commune text,
-- 	CONSTRAINT pk_t_communes_id_commune PRIMARY KEY (id_commune)
-- );

