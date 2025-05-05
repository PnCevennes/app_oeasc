


Dans app.py => paragraphe CONFIGURATION DE LA BDD
    il faudra mettre en commentaire la ligne 
    os.environ["FLASK_SQLALCHEMY_DB"] = f"{__name__}.db"



###############################################################################
la table cor_dgd n'a pas de clé primaire et possède des doublons

probleme dans déclaration-model. 
    alter table oeasc_forets.cor_dgd_cadastre add idtmp serial;

    with d as (
        select max(idtmp), array_agg(idtmp), d.area_code_cadastre, d.area_code_dgd
        from oeasc_forets.cor_dgd_cadastre d
        group by d.area_code_cadastre, d.area_code_dgd
    )
    delete from oeasc_forets.cor_dgd_cadastre 
    where idtmp in (select max from d);

    alter table oeasc_forets.cor_dgd_cadastre drop  idtmp;

    vacuum full;



#################################################################################
La table commons.t_commune n'a pas de clé primaire et possède des doublons


ALTER TABLE oeasc_commons.t_communes
ADD COLUMN idtmp BIGINT GENERATED ALWAYS AS IDENTITY;

WITH d AS (
    SELECT code, array_agg(idtmp) AS ids
    FROM oeasc_commons.t_communes
    GROUP BY code
    HAVING COUNT(*) > 1
)
DELETE FROM oeasc_commons.t_communes
WHERE idtmp IN (
    SELECT unnest(ids)
    FROM d
    EXCEPT
    SELECT min(idtmp)
    FROM oeasc_commons.t_communes
    GROUP BY code
);

alter table oeasc_commons.t_communes  drop  idtmp;

vacuum full;
