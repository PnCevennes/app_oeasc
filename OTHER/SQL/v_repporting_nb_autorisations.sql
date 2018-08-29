DROP VIEW autorisations.v_repporting_nb_autorisations;
CREATE OR REPLACE VIEW autorisations.v_repporting_nb_autorisations AS 
 WITH data AS (
         SELECT suivi_autorisations.id,
            regexp_split_to_table(suivi_autorisations.massif::text, ','::text) AS massif,
            date_part('YEAR'::text, suivi_autorisations.d_ar_dossier_complet) AS annee,
            suivi_autorisations.thematique,
            suivi_autorisations.objet,
            suivi_autorisations.type_demande,
            suivi_autorisations.d_ar_refus,
            COALESCE(suivi_autorisations.d_reponse::text, suivi_autorisations.lien_reponse::text, suivi_autorisations.num_document_reponse::text) AS rep,
            suivi_autorisations.avis_interne
           FROM autorisations.suivi_autorisations
        )
 SELECT 
    row_number() OVER() as unique_id,
    data.massif,
    data.thematique,
    data.objet,
    data.type_demande,
    data.annee,
    count(*) AS nb_demandes,
    count(data.d_ar_refus) AS nb_refus,
    count(data.rep) AS nb_reponse,
    count(data.avis_interne) FILTER (WHERE data.avis_interne::text = 'Favorable'::text) AS avis_int_favorable,
    count(data.avis_interne) FILTER (WHERE data.avis_interne::text = 'Préconisation'::text) AS avis_int_preconisation,
    count(data.avis_interne) FILTER (WHERE data.avis_interne::text = 'Défavorable'::text) AS avis_int_defavorable
   FROM data
  GROUP BY data.massif, data.thematique, data.objet, data.type_demande, data.annee;


SELECT row_number() OVER(PARTITION BY massif) as unique_id, *
FROM autorisations.v_repporting_nb_autorisations