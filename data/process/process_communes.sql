DROP TABLE IF EXISTS ref_geo.cor_old_communes;

CREATE TABLE temp(area_code character varying(256), area_name character varying(256), geom GEOMETRY);

INSERT INTO temp(area_code, geom)
    SELECT SUBSTR(area_code, 1,5) as code, ST_UNION(geom) as geom
        FROM ref_geo.l_areas
        WHERE id_type = ref_geo.get_id_type('OEASC_SECTION')
        GROUP BY code
        ORDER BY code;

DROP TABLE IF EXISTS ref_geo.cor_old_communes;

CREATE TABLE IF NOT EXISTS ref_geo.cor_old_communes(
    area_code character varying,
    old_area_codes character varying[],

    CONSTRAINT pk_cor_old_communes PRIMARY KEY (area_code)

);

INSERT INTO ref_geo.cor_old_communes
SELECT l.area_code, array_sort_unique(array_agg(t.area_code))
    FROM temp AS t, ref_geo.l_areas AS l
    WHERE l.id_type = ref_geo.get_id_type('OEASC_COMMUNE')
    AND ST_INTERSECTS(t.geom, l.geom)
    AND ST_AREA(ST_INTERSECTION(t.geom, l.geom)) * ( 1.0 / ST_AREA(t.geom) + 1.0 / ST_AREA(l.geom) ) > 0.5
    GROUP BY l.area_code
    ORDER BY l.area_code;

DROP TABLE IF EXISTS oeasc_forets.cor_dgd_cadastre;

CREATE TABLE oeasc_forets.cor_dgd_cadastre
(
    area_code_dgd CHARACTER VARYING,
    area_code_cadastre CHARACTER VARYING
);

INSERT INTO oeasc_forets.cor_dgd_cadastre
    SELECT a.area_code, l.area_code
        FROM ref_geo.l_areas as l, (SELECT area_code, ref_geo.intersect_rel_area(id_area, 'OEASC_CADASTRE', 0.1) as id_area_cadastre
            FROM ref_geo.l_areas
            WHERE id_type=ref_geo.get_id_type('OEASC_DGD'))a
        WHERE l.id_area = a.id_area_cadastre;

