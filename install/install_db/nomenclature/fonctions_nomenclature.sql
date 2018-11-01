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
