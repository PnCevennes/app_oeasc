    -- function qui prend en entree un id_lieu_tir synonyme et qui renvoie
    -- le label 
    -- dep commune - nom lieu tir synonyme - [ nom lieu tir]
    -- ou 
    -- dep commune - nom lieu tir
    -- si nom lieu tir synonyme = nom lieu tir




    DROP FUNCTION IF EXISTS oeasc_chasse.get_lieu_tir_synonyme_label;
    CREATE OR REPLACE FUNCTION oeasc_chasse.get_lieu_tir_synonyme_label(
        IN my_id_lieu_tir_synonyme INTEGER
        )
        RETURNS CHARACTER VARYING AS
        $BODY$
        DECLARE lieu_tir_synonyme_label CHARACTER VARYING;
        BEGIN
        SELECT INTO lieu_tir_synonyme_label 
            CASE 
                WHEN tlts.nom_lieu_tir_synonyme = tlt.nom_lieu_tir  
                    THEN tlt.label_commune || ' - ' || tlt.nom_lieu_tir
                ELSE tlt.label_commune || ' - ' || tlts.nom_lieu_tir_synonyme || ' [' || tlt.nom_lieu_tir || ']'
            END
        FROM oeasc_chasse.t_lieu_tir_synonymes tlts
        JOIN oeasc_chasse.t_lieu_tirs tlt ON tlt.id_lieu_tir = tlts.id_lieu_tir
        WHERE tlts.id_lieu_tir_synonyme = my_id_lieu_tir_synonyme;
        RETURN lieu_tir_synonyme_label;
        END;
        $BODY$
        LANGUAGE plpgsql IMMUTABLE
        COST 100;
