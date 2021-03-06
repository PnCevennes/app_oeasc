-- Function: ref_nomenclatures.get_nomenclature_id_from_label(character varying, character varying)

DROP FUNCTION IF EXISTS ref_nomenclatures.get_nomenclature_id_from_label(character varying, character varying) CASCADE;

CREATE OR REPLACE FUNCTION ref_nomenclatures.get_nomenclature_id_from_label(
    mylabel CHARACTER VARYING,
    mytype_mnemonique CHARACTER VARYING)

    RETURNS INTEGER AS
    $BODY$
    --
    -- Returns id_nomenclature from the label and the type_code
    --
        DECLARE theidnomenclature INTEGER;
        BEGIN
            EXECUTE format( ' SELECT  n.id_nomenclature
                FROM ref_nomenclatures.t_nomenclatures n
                WHERE id_type = %s AND label_fr = ''%s'' ', ref_nomenclatures.get_id_nomenclature_type(mytype_mnemonique), mylabel)INTO theidnomenclature;
                return theidnomenclature;
        END;
    $BODY$
    LANGUAGE plpgsql IMMUTABLE
    COST 100;


-- Function: ref_nomenclatures.get_nomenclature_mnemonique(integer)

-- DROP FUNCTION ref_nomenclatures.get_nomenclature_mnemonique(integer);

CREATE OR REPLACE FUNCTION ref_nomenclatures.get_nomenclature_mnemonique(myidnomenclature integer DEFAULT NULL::integer)
  RETURNS character varying AS
$BODY$
--Function which return the mnemonique from the id_nomenclature
DECLARE
	themnemonique character varying;
  BEGIN
  SELECT INTO themnemonique mnemonique
  FROM ref_nomenclatures.t_nomenclatures n
  WHERE id_nomenclature = myidnomenclature;
return themnemonique;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;
ALTER FUNCTION ref_nomenclatures.get_nomenclature_mnemonique(integer)
  OWNER TO dbadmin;


-- DROP FUNCTION ref_nomenclatures.get_nomenclature_code(integer);

CREATE OR REPLACE FUNCTION ref_nomenclatures.get_nomenclature_code(myidnomenclature integer DEFAULT NULL::integer)
  RETURNS character varying AS
$BODY$
--Function which return the code from the id_nomenclature
DECLARE
	thecode character varying;
  BEGIN
  SELECT INTO thecode cd_nomenclature
  FROM ref_nomenclatures.t_nomenclatures n
  WHERE id_nomenclature = myidnomenclature;
return thecode;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;
ALTER FUNCTION ref_nomenclatures.get_nomenclature_code(integer)
  OWNER TO dbadmin;


--
CREATE OR REPLACE FUNCTION ref_nomenclatures.get_nomenclature_mnemoniques(myidsnomenclature integer[])
  RETURNS character varying AS
$BODY$
--Function which return the label from the id_nomenclature
DECLARE
	themnemoniques character varying;
  BEGIN
  SELECT INTO themnemoniques STRING_AGG(mnemonique, ', ')
  FROM (SELECT ref_nomenclatures.get_nomenclature_mnemonique(UNNEST(myidsnomenclature)) AS mnemonique)a;
return themnemoniques;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;
ALTER FUNCTION ref_nomenclatures.get_nomenclature_mnemoniques(integer[])
  OWNER TO dbadmin;


  --
CREATE OR REPLACE FUNCTION ref_nomenclatures.get_nomenclature_labels(myidsnomenclature integer[])
  RETURNS character varying AS
$BODY$
--Function which return the label from the id_nomenclature
DECLARE
	thelabels character varying;
  BEGIN
  SELECT INTO thelabels STRING_AGG(label, ', ')
  FROM (SELECT ref_nomenclatures.get_nomenclature_label(UNNEST(myidsnomenclature)) AS label)a;
return thelabels;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;
ALTER FUNCTION ref_nomenclatures.get_nomenclature_labels(integer[])
  OWNER TO dbadmin;


CREATE OR REPLACE FUNCTION ref_nomenclatures.get_nomenclature_codes(myidsnomenclature integer[])
  RETURNS character varying AS
$BODY$

DECLARE
	thecodes character varying;
  BEGIN
  SELECT INTO thecodes STRING_AGG(code, ', ')
  FROM (SELECT ref_nomenclatures.get_nomenclature_code(UNNEST(myidsnomenclature)) AS code)a;
return thecodes;
  END;
$BODY$
  LANGUAGE plpgsql IMMUTABLE
  COST 100;
ALTER FUNCTION ref_nomenclatures.get_nomenclature_codes(integer[])
  OWNER TO dbadmin;
