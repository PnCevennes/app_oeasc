-- Function: ref_geo.intersect_rel_area(INTEGER, CHARACTER VARYING, DOUBLE PRECISION)

DROP FUNCTION IF EXISTS ref_geo.intersect_rel_area(INTEGER, CHARACTER VARYING, DOUBLE PRECISION) CASCADE;

CREATE OR REPLACE FUNCTION ref_geo.intersect_rel_area(
  myidarea INTEGER,
  mytypecode CHARACTER VARYING,
  seuil DOUBLE PRECISION)

  RETURNS TABLE (id_area INT) AS
--
-- Returns the id_area(s) of the areas of type code intersecting with area id_area
--
$$
BEGIN
RETURN QUERY 
	WITH test AS (SELECT l.geom as geom
		FROM ref_geo.l_areas as l
		WHERE L.id_area=myidarea)
	SELECT(c.id_area)
		FROM (
			SELECT a.id_area  
				FROM (
					SELECT l.id_area, l.geom
						FROM ref_geo.l_areas as l, test
						WHERE l.id_type = ref_geo.get_id_type(mytypecode) AND
						ST_INTERSECTS(l.geom, test.geom)
					)a, test
			WHERE ST_AREA(ST_INTERSECTION(a.geom, test.geom))*(1.0/ST_AREA(a.geom) + 1.0/ST_AREA(test.geom))/2 > seuil)c;
  END;
$$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;

DROP TABLE IF EXISTS temp;

DELETE FROM oeasc.t_forets;

CREATE TABLE temp (dept text, ccod_frt text, nom_proprietaire text);

COPY temp
    FROM '/home/joel/Info/PNC/OEASC/app_oeasc/install/scripts_db/script_oeasc/liens_proprietaires_publics_forets.csv'
    WITH DELIMITER ';' CSV QUOTE AS '''';

INSERT INTO oeasc.t_forets (
    id_proprietaire, b_statut_public, b_regime_forestier,
        nom_foret, superficie)
	SELECT  oeasc.get_id_proprietaire_from_name(t.nom_proprietaire), true, true, l.area_name, ROUND(ST_AREA(l.geom)/10000*10)/10
		FROM ref_geo.l_areas as l, temp as t
		WHERE id_type = ref_geo.get_id_type('OEASC_ONF_FRT')
			AND l.area_code = CONCAT(t.dept, '-', t.ccod_frt)
		ORDER BY area_name;


INSERT INTO oeasc.cor_areas_forets(
    id_area, id_foret)
	SELECT  l.id_area, f.id_foret
		FROM ref_geo.l_areas as l, oeasc.t_forets as f
		WHERE id_type = ref_geo.get_id_type('OEASC_ONF_FRT')
			AND f.nom_foret = l.area_name
		ORDER BY area_name;

INSERT INTO oeasc.cor_areas_forets(
	id_area, id_foret)
	SELECT b.id_area, a.id_foret, --a.area_name, b.area_name, ST_AREA(ST_INTERSECTION(b.geom, a.geom))*(1./ST_AREA(b.geom) + 1./ST_AREA(a.geom))
		FROM ref_geo.l_areas as b,
		(SELECT l.id_area as id_area, c.id_foret, l.area_name,  ref_geo.intersect_rel_area(c.id_area,'OEASC_COMMUNE',0.05) as id_com, geom
			FROM oeasc.cor_areas_forets as c, ref_geo.l_areas as l
			WHERE l.id_type = ref_geo.get_id_type('OEASC_ONF_FRT') AND l.id_area = c.id_area) a
		WHERE b.id_area = a.id_com
		ORDER BY a.area_name, b.area_name;

INSERT INTO oeasc.cor_areas_forets(
	id_area, id_foret)
	SELECT b.id_area, a.id_foret, --a.area_name, b.area_name, ST_AREA(ST_INTERSECTION(b.geom, a.geom))*(1./ST_AREA(b.geom) + 1./ST_AREA(a.geom))
		FROM ref_geo.l_areas as b,
		(SELECT l.id_area as id_area, c.id_foret, l.area_name,  ref_geo.intersect_rel_area(c.id_area,'OEASC_DEPARTEMENT',0.05) as id_com, geom
			FROM oeasc.cor_areas_forets as c, ref_geo.l_areas as l
			WHERE l.id_type = ref_geo.get_id_type('OEASC_ONF_FRT') AND l.id_area = c.id_area) a
		WHERE b.id_area = a.id_com
		ORDER BY a.area_name, b.area_name
