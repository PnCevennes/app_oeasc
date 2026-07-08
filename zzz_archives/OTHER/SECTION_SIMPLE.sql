DROP FUNCTION IF EXISTS ref_geo.simplify_by_id_type(mytype_code character varying, mytype_code_new character varying, tolerance float);

CREATE OR REPLACE FUNCTION ref_geo.simplify_by_id_type(mytype_code character varying, mytype_code_new character varying, tolerance float)
    RETURNS VOID AS
    $$
    BEGIN
        DROP TABLE IF EXISTS temp;

        CREATE TABLE temp AS SELECT id_area, geom FROM ref_geo.l_areas WHERE id_type=ref_geo.get_id_type(mytype_code);

        DROP TABLE IF EXISTS temp_simple;

        CREATE TABLE temp_simple AS SELECT * FROM simplifyLayerPreserveTopology('' ,'temp', 'id_area', 'geom', tolerance) as (id_area int, geom geometry);

        DELETE FROM ref_geo.l_areas WHERE id_type=ref_geo.get_id_type(mytype_code_new);

        INSERT INTO ref_geo.l_areas(id_type, area_name, area_code, geom, geom_4326, centroid, source, comment, enable)
            SELECT ref_geo.get_id_type(mytype_code_new), l.area_name, l.area_code, t.geom, ST_TRANSFORM(t.geom, 4326), ST_CENTROID(t.geom), 'OEASC', '', true
            FROM temp_simple as t, ref_geo.l_areas as l
            WHERE t.id_area=l.id_area;
END;
$$ language plpgsql strict;

DELETE FROM ref_geo.l_areas WHERE id_type=333;

DELETE FROM ref_geo.bib_areas_types WHERE id_type=333;

INSERT INTO ref_geo.bib_areas_types (
    id_type, type_name, type_code, type_desc, ref_name, ref_version, num_version)
    VALUES
        (333, 'dgd simplifié', 'OEASC_DGD_SIMPLE', 'dgd simplifiées', 'OEASC', 2018, '');



SELECT ref_geo.simplify_by_id_type('OEASC_DGD', 'OEASC_DGD_SIMPLE', 0);
