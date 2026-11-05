"""drop_vues_inutilisees

Suppression des vues qui ne sont plus utilisées par le projet (aucune référence dans le
backend, le frontend ni les contenus CMS ; vérifié le 2026-11-05) :
  - import_chasse : 13 vues de rapports / QGIS d'anciens imports
  - oeasc_chasse : 5 vues v_chasse_* (massifs, QGIS) remplacées par export_chasse.py
  - oeasc_declarations.v_degats
  - oeasc_resultats : 5 vues v_nb_degat_*_mnemo
Pas de CASCADE : la migration échoue si une autre vue en dépend encore.
Les vues utilisateurs.* (UsersHub) et les tables de import_chasse ne sont pas touchées.

Revision ID: e5b7d3a91c24
Revises: c4e8a1f6d205
Create Date: 2026-11-05 16:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "e5b7d3a91c24"
down_revision = "c4e8a1f6d205"
branch_labels = None
depends_on = None


def upgrade():
    # une seule instruction : PostgreSQL gère l'ordre entre vues interdépendantes
    op.execute(
        "DROP VIEW IF EXISTS "
        + ", ".join(
            [
                "import_chasse.v_chasse_massifcerf_countby_sexe_saisonencours",
                "import_chasse.v_chasse_massifchevreuil_countby_sexe_saisonencours",
                "import_chasse.v_chasse_qgis_cerf_countby_sexe_saisonencours",
                "import_chasse.v_chasse_qgis_lieuchasse",
                "import_chasse.v_chasse_qgis_lieuchasse_saisonencours",
                "import_chasse.v_chasse_qgis_toutessp_countby_saisonencours",
                "import_chasse.v_chasse_qgis_toutessp_countby_saisonencours_zi",
                "import_chasse.v_lieu_dit_synonymes",
                "import_chasse.v_rapport_bilan_attribution_massif",
                "import_chasse.v_rapport_bilan_group",
                "import_chasse.v_rapport_bilan_historique",
                "import_chasse.v_rapport_bilan_nobracelet",
                "import_chasse.v_rapport_realisation_saison",
                "oeasc_chasse.v_chasse_massifcerf_countby_sexe_saisonencours",
                "oeasc_chasse.v_chasse_massifchevreuil_countby_sexe_saisonencours",
                "oeasc_chasse.v_chasse_qgis_cerf_countby_sexe_saisonencours",
                "oeasc_chasse.v_chasse_qgis_toutessp_countby_saisonencours",
                "oeasc_chasse.v_chasse_qgis_toutessp_countby_saisonencours_zi",
                "oeasc_declarations.v_degats",
                "oeasc_resultats.v_nb_degat_anteriorite_mnemo",
                "oeasc_resultats.v_nb_degat_essence_mnemo",
                "oeasc_resultats.v_nb_degat_etendue_mnemo",
                "oeasc_resultats.v_nb_degat_gravite_mnemo",
                "oeasc_resultats.v_nb_degat_type_mnemo",
            ]
        )
    )


def downgrade():
    op.execute(
        """
CREATE OR REPLACE VIEW import_chasse.v_rapport_bilan_nobracelet AS
SELECT s.saison,
    p.nom_vern,
    p.massif_affecte,
    p.no_bracelet,
    lower(btrim("substring"((p.no_bracelet)::text, '^.* '::text))) AS type,
    p.z_i_affectee AS num_zi_affectee,
    (((p.z_i_affectee)::text || ' '::text) || (tzi.libelle)::text) AS z_i_affectee,
    p.date_exacte,
        CASE
            WHEN ((p.sexe)::text = 'Femelle'::text) THEN 1
            ELSE NULL::integer
        END AS s_femelle,
        CASE
            WHEN (((p.sexe)::text = 'Mâle'::text) AND (NOT (p.date_exacte IS NULL))) THEN 1
            ELSE NULL::integer
        END AS s_male,
        CASE
            WHEN ((p.sexe)::text = 'Indéterminé'::text) THEN 1
            ELSE NULL::integer
        END AS s_ind,
        CASE
            WHEN (p.date_exacte = '1970-01-01'::date) THEN 1
            ELSE NULL::integer
        END AS date_ind,
        CASE
            WHEN ((NOT (p.date_exacte = '1970-01-01'::date)) AND (date_part('month'::text, p.date_exacte) = (9)::double precision)) THEN 1
            ELSE NULL::integer
        END AS sept,
        CASE
            WHEN ((NOT (p.date_exacte = '1970-01-01'::date)) AND (date_part('month'::text, p.date_exacte) = (10)::double precision)) THEN 1
            ELSE NULL::integer
        END AS oct,
        CASE
            WHEN ((NOT (p.date_exacte = '1970-01-01'::date)) AND (date_part('month'::text, p.date_exacte) = (11)::double precision)) THEN 1
            ELSE NULL::integer
        END AS nov,
        CASE
            WHEN ((NOT (p.date_exacte = '1970-01-01'::date)) AND (date_part('month'::text, p.date_exacte) = (12)::double precision)) THEN 1
            ELSE NULL::integer
        END AS "dec",
        CASE
            WHEN ((NOT (p.date_exacte = '1970-01-01'::date)) AND (date_part('month'::text, p.date_exacte) = (1)::double precision)) THEN 1
            ELSE NULL::integer
        END AS janv,
        CASE
            WHEN ((NOT (p.date_exacte = '1970-01-01'::date)) AND (date_part('month'::text, p.date_exacte) = (2)::double precision)) THEN 1
            ELSE NULL::integer
        END AS fev,
        CASE
            WHEN (((p.classe_age)::text = 'Indéterminé'::text) AND (NOT (p.date_exacte IS NULL))) THEN 1
            ELSE NULL::integer
        END AS a_ind,
        CASE
            WHEN (((p.classe_age)::text = 'Adulte'::text) AND (NOT (p.date_exacte IS NULL))) THEN 1
            ELSE NULL::integer
        END AS a_ad,
        CASE
            WHEN (((p.classe_age)::text = 'Sub adulte'::text) AND (NOT (p.date_exacte IS NULL))) THEN 1
            ELSE NULL::integer
        END AS a_sub,
        CASE
            WHEN (((p.classe_age)::text = 'Jeune'::text) AND (NOT (p.date_exacte IS NULL))) THEN 1
            ELSE NULL::integer
        END AS a_juv,
    p.poids_ind,
    p.poids_entier,
    p.poids_vide,
    p.poids_c_f_p,
        CASE
            WHEN ((p.mode_chasse)::text = 'Indéterminé'::text) THEN 1
            ELSE NULL::integer
        END AS mc_ind,
        CASE
            WHEN ((p.mode_chasse)::text = 'Battue'::text) THEN 1
            ELSE NULL::integer
        END AS mc_battue,
        CASE
            WHEN ((p.mode_chasse)::text = 'Approche'::text) THEN 1
            ELSE NULL::integer
        END AS mc_approche,
        CASE
            WHEN ((p.mode_chasse)::text = 'Affut'::text) THEN 1
            ELSE NULL::integer
        END AS mc_affut,
        CASE
            WHEN (p.cors_nb = '-1'::integer) THEN 1
            ELSE NULL::integer
        END AS nb_cors_ind,
        CASE
            WHEN (p.cors_nb > 0) THEN p.cors_nb
            ELSE NULL::integer
        END AS nb_cors,
    p.parc_onf
   FROM ((import_chasse.plan_chasse p
     JOIN import_chasse.saison_chasse s ON ((s.id = p.fk_saison)))
     JOIN ( SELECT tthesaurus.id AS pk,
            tthesaurus.id_type,
            tthesaurus.code,
            tthesaurus.libelle,
            tthesaurus.description,
            tthesaurus.fk_parent,
            tthesaurus.hierarchie
           FROM import_chasse.tthesaurus
          WHERE (tthesaurus.id_type = 4)) tzi ON (((p.z_i_affectee)::text = (tzi.code)::text)));
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW import_chasse.v_chasse_massifcerf_countby_sexe_saisonencours AS
WITH nb_rel AS (
         SELECT v_rapport_bilan_nobracelet.nom_vern,
            v_rapport_bilan_nobracelet.massif_affecte,
            v_rapport_bilan_nobracelet.type,
            count(*) AS count
           FROM import_chasse.v_rapport_bilan_nobracelet
          WHERE ((NOT (v_rapport_bilan_nobracelet.date_exacte IS NULL)) AND ((v_rapport_bilan_nobracelet.saison)::text = (( SELECT saison_chasse.saison
                   FROM import_chasse.saison_chasse
                  WHERE (saison_chasse.current = true)))::text))
          GROUP BY v_rapport_bilan_nobracelet.nom_vern, v_rapport_bilan_nobracelet.massif_affecte, v_rapport_bilan_nobracelet.type
        )
 SELECT DISTINCT row_number() OVER () AS row_number,
    cerf.massif_affecte,
    cerf.nom_vern,
    COALESCE(cem.count, (0)::bigint) AS males,
    COALESCE(ceff.count, (0)::bigint) AS femelles
   FROM ((( SELECT DISTINCT nb_rel.massif_affecte,
            nb_rel.nom_vern
           FROM nb_rel
          WHERE ((nb_rel.nom_vern)::text ~~* 'cerf%'::text)) cerf
     LEFT JOIN ( SELECT nb_rel.nom_vern,
            nb_rel.massif_affecte,
            nb_rel.type,
            nb_rel.count
           FROM nb_rel
          WHERE (nb_rel.type = 'cem'::text)) cem ON (((cerf.massif_affecte)::text = (cem.massif_affecte)::text)))
     LEFT JOIN ( SELECT nb_rel.nom_vern,
            nb_rel.massif_affecte,
            nb_rel.type,
            nb_rel.count
           FROM nb_rel
          WHERE (nb_rel.type = 'ceff'::text)) ceff ON (((cerf.massif_affecte)::text = (ceff.massif_affecte)::text)))
  ORDER BY cerf.massif_affecte;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW import_chasse.v_chasse_massifchevreuil_countby_sexe_saisonencours AS
SELECT row_number() OVER () AS row_number,
    nom_vern,
    massif_affecte,
    count(*) AS count
   FROM import_chasse.v_rapport_bilan_nobracelet
  WHERE ((NOT (date_exacte IS NULL)) AND ((saison)::text = (( SELECT saison_chasse.saison
           FROM import_chasse.saison_chasse
          WHERE (saison_chasse.current = true)))::text) AND ((nom_vern)::text = 'Chevreuil européen'::text))
  GROUP BY nom_vern, massif_affecte, type;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW import_chasse.v_chasse_qgis_lieuchasse_saisonencours AS
SELECT c.id AS pk,
    l.geom,
    c.code_lieu_dit,
    c.insee,
    lower(btrim("substring"((c.no_bracelet)::text, '^.* '::text))) AS type,
    c.no_bracelet,
    c.auteur_tir,
    c.auteur_constat,
    c.date_exacte,
    c.sexe,
    c.classe_age,
    c.nom_vern,
    saison.saison
   FROM ((import_chasse.plan_chasse c
     JOIN import_chasse.lieux_tir l ON (((c.code_lieu_dit)::integer = l.code_lieudit)))
     JOIN ( SELECT saison_chasse.id AS pk,
            saison_chasse.date_min,
            saison_chasse.date_max,
            saison_chasse.saison,
            saison_chasse.current
           FROM import_chasse.saison_chasse
          WHERE (saison_chasse.current = true)) saison ON ((c.fk_saison = saison.pk)));
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW import_chasse.v_lieu_dit_synonymes AS
SELECT DISTINCT s.id,
    t.code_lieudit,
    t.nom_lieudit,
    s.libelle_lieudit AS synonyme,
    t.code_com,
    t.nom_com,
    ((((COALESCE(s.libelle_lieudit, ''::character varying))::text || ' ['::text) || (t.nom_lieudit)::text) || ']'::text) AS syn_lieudit
   FROM (import_chasse.lieux_tir t
     JOIN import_chasse.lieu_tir_synonymes s USING (code_lieudit));
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW import_chasse.v_chasse_qgis_cerf_countby_sexe_saisonencours AS
WITH nb_rel AS (
         SELECT DISTINCT v_chasse_qgis_lieuchasse_saisonencours.geom,
            v_chasse_qgis_lieuchasse_saisonencours.code_lieu_dit,
            v_chasse_qgis_lieuchasse_saisonencours.nom_vern,
            v_chasse_qgis_lieuchasse_saisonencours.type,
            count(DISTINCT v_chasse_qgis_lieuchasse_saisonencours.no_bracelet) AS count,
            v_lieu_dit_synonymes.nom_lieudit,
            v_lieu_dit_synonymes.nom_com
           FROM (import_chasse.v_chasse_qgis_lieuchasse_saisonencours
             JOIN import_chasse.v_lieu_dit_synonymes ON (((v_chasse_qgis_lieuchasse_saisonencours.code_lieu_dit)::integer = v_lieu_dit_synonymes.code_lieudit)))
          GROUP BY v_chasse_qgis_lieuchasse_saisonencours.geom, v_chasse_qgis_lieuchasse_saisonencours.code_lieu_dit, v_chasse_qgis_lieuchasse_saisonencours.nom_vern, v_chasse_qgis_lieuchasse_saisonencours.type, v_lieu_dit_synonymes.nom_lieudit, v_lieu_dit_synonymes.nom_com
        )
 SELECT DISTINCT row_number() OVER () AS row_number,
    cerf.geom,
    cerf.code_lieu_dit,
    cerf.nom_vern,
    cerf.nom_lieudit,
    cerf.nom_com,
    COALESCE(cem.count, (0)::bigint) AS cem,
    COALESCE(ceff.count, (0)::bigint) AS ceff
   FROM ((( SELECT DISTINCT nb_rel.geom,
            nb_rel.code_lieu_dit,
            nb_rel.nom_vern,
            nb_rel.count,
            nb_rel.nom_lieudit,
            nb_rel.nom_com
           FROM nb_rel
          WHERE ((nb_rel.nom_vern)::text ~~* 'cerf%'::text)) cerf
     LEFT JOIN ( SELECT nb_rel.geom,
            nb_rel.code_lieu_dit,
            nb_rel.nom_vern,
            nb_rel.type,
            nb_rel.count,
            nb_rel.nom_lieudit,
            nb_rel.nom_com
           FROM nb_rel
          WHERE (nb_rel.type = 'cem'::text)) cem ON ((cerf.geom = cem.geom)))
     LEFT JOIN ( SELECT nb_rel.geom,
            nb_rel.code_lieu_dit,
            nb_rel.nom_vern,
            nb_rel.type,
            nb_rel.count,
            nb_rel.nom_lieudit,
            nb_rel.nom_com
           FROM nb_rel
          WHERE (nb_rel.type = 'ceff'::text)) ceff ON ((cerf.geom = ceff.geom)));
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW import_chasse.v_chasse_qgis_lieuchasse AS
SELECT c.id AS pk,
    l.geom,
    c.code_lieu_dit,
    c.insee,
    c.no_bracelet,
    c.auteur_tir,
    c.auteur_constat,
    c.date_exacte,
    c.sexe,
    c.classe_age,
    c.nom_vern,
    saison.saison
   FROM ((import_chasse.plan_chasse c
     JOIN import_chasse.lieux_tir l ON (((c.code_lieu_dit)::integer = l.code_lieudit)))
     JOIN ( SELECT saison_chasse.id AS pk,
            saison_chasse.date_min,
            saison_chasse.date_max,
            saison_chasse.saison,
            saison_chasse.current
           FROM import_chasse.saison_chasse) saison ON ((c.fk_saison = saison.pk)));
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW import_chasse.v_chasse_qgis_toutessp_countby_saisonencours AS
SELECT row_number() OVER () AS row_number,
    l.geom,
    c.code_lieu_dit,
    lower(btrim("substring"((c.no_bracelet)::text, '^.* '::text))) AS type,
    c.nom_vern,
    count(*) AS count,
    l.nom_lieudit,
    l.nom_com
   FROM ((import_chasse.plan_chasse c
     JOIN import_chasse.lieux_tir l ON (((c.code_lieu_dit)::integer = l.code_lieudit)))
     JOIN ( SELECT saison_chasse.id AS pk,
            saison_chasse.date_min,
            saison_chasse.date_max,
            saison_chasse.saison,
            saison_chasse.current
           FROM import_chasse.saison_chasse
          WHERE (saison_chasse.current = true)) saison ON ((c.fk_saison = saison.pk)))
  GROUP BY l.geom, c.code_lieu_dit, (lower(btrim("substring"((c.no_bracelet)::text, '^.* '::text)))), c.nom_vern, l.nom_lieudit, l.nom_com;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW import_chasse.v_chasse_qgis_toutessp_countby_saisonencours_zi AS
SELECT row_number() OVER () AS row_number,
    l.geom,
    c.code_lieu_dit,
    count(*) FILTER (WHERE (lower(btrim("substring"((c.no_bracelet)::text, '^.* '::text))) = 'chi'::text)) AS count_chi,
    count(*) FILTER (WHERE (lower(btrim("substring"((c.no_bracelet)::text, '^.* '::text))) = 'cem'::text)) AS count_cem,
    count(*) FILTER (WHERE (lower(btrim("substring"((c.no_bracelet)::text, '^.* '::text))) = 'ceff'::text)) AS count_ceff,
    l.nom_lieudit,
    l.nom_com,
    c.z_i_affectee,
    zi.libelle AS zi
   FROM (((import_chasse.plan_chasse c
     JOIN import_chasse.lieux_tir l ON (((c.code_lieu_dit)::integer = l.code_lieudit)))
     JOIN ( SELECT saison_chasse.id AS pk
           FROM import_chasse.saison_chasse
          WHERE (saison_chasse.current = true)) saison ON ((c.fk_saison = saison.pk)))
     JOIN ( SELECT tthesaurus.code,
            tthesaurus.libelle
           FROM import_chasse.tthesaurus
          WHERE (tthesaurus.id_type = 4)) zi ON (((zi.code)::text = (c.z_i_affectee)::text)))
  GROUP BY l.geom, c.code_lieu_dit, l.nom_lieudit, l.nom_com, c.z_i_affectee, zi.libelle;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW import_chasse.v_rapport_bilan_historique AS
SELECT h.nom_vern,
    h.saison,
    h.massif_affecte,
    h.z_i_affectee,
    h.nb_affecte_max,
    h.nb_affecte_min,
    h.nb_realise,
    h.nb_realise_avant11,
    tzi.libelle AS z_i_affectee_libelle
   FROM (( SELECT p.nom_vern,
            s.saison,
            p.massif_affecte,
            p.z_i_affectee,
            count(DISTINCT p.no_bracelet) AS nb_affecte_max,
            NULL::integer AS nb_affecte_min,
            count(( SELECT DISTINCT p.date_exacte
                  WHERE (NOT (p.date_exacte IS NULL)))) AS nb_realise,
            count(( SELECT DISTINCT p.date_exacte
                  WHERE ((date_part('month'::text, p.date_exacte) < (11)::double precision) AND (date_part('year'::text, p.date_exacte) = ((split_part((s.saison)::text, '-'::text, 1))::integer)::double precision)))) AS nb_realise_avant11
           FROM (import_chasse.plan_chasse p
             JOIN import_chasse.saison_chasse s ON ((s.id = p.fk_saison)))
          GROUP BY s.saison, p.nom_vern, p.massif_affecte, p.z_i_affectee
        UNION
         SELECT bilan_chasse_historique.nom_vern,
            bilan_chasse_historique.saison,
            bilan_chasse_historique.massif_affecte,
            bilan_chasse_historique.z_i_affectee,
            bilan_chasse_historique.nb_affecte_max,
            bilan_chasse_historique.nb_affecte_min,
            bilan_chasse_historique.nb_realise,
            bilan_chasse_historique.nb_realise_avant11
           FROM import_chasse.bilan_chasse_historique) h
     JOIN ( SELECT tthesaurus.id AS pk,
            tthesaurus.id_type,
            tthesaurus.code,
            tthesaurus.libelle,
            tthesaurus.description,
            tthesaurus.fk_parent,
            tthesaurus.hierarchie
           FROM import_chasse.tthesaurus
          WHERE (tthesaurus.id_type = 4)) tzi ON (((h.z_i_affectee)::text = (tzi.code)::text)));
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW import_chasse.v_rapport_bilan_attribution_massif AS
SELECT m.id AS pk,
    m.nom_vern,
    m.saison,
    m.massif,
    m.nb_affecte_max,
    COALESCE(m.nb_affecte_min, 0) AS nb_affecte_min,
    rel.nb_realise,
    COALESCE(rel.nb_realise_avant11, (0)::numeric) AS nb_realise_avant11
   FROM (import_chasse.plan_chasse_attribution_massif m
     LEFT JOIN ( SELECT v_rapport_bilan_historique.nom_vern,
            v_rapport_bilan_historique.saison,
            v_rapport_bilan_historique.massif_affecte,
            sum(v_rapport_bilan_historique.nb_realise) AS nb_realise,
            sum(v_rapport_bilan_historique.nb_realise_avant11) AS nb_realise_avant11
           FROM import_chasse.v_rapport_bilan_historique
          GROUP BY v_rapport_bilan_historique.nom_vern, v_rapport_bilan_historique.saison, v_rapport_bilan_historique.massif_affecte) rel ON ((((m.nom_vern)::text = (rel.nom_vern)::text) AND ((m.saison)::text = (rel.saison)::text) AND ((m.massif)::text = (rel.massif_affecte)::text))))
  ORDER BY m.nom_vern, m.massif, m.saison;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW import_chasse.v_rapport_bilan_group AS
SELECT saison,
    nom_vern,
    massif_affecte,
    num_zi_affectee,
    z_i_affectee,
    count(DISTINCT no_bracelet) AS nb_affecte,
    count(( SELECT DISTINCT v_rapport_bilan_nobracelet.date_exacte
          WHERE (NOT (v_rapport_bilan_nobracelet.date_exacte IS NULL)))) AS nb_realise,
    count(s_femelle) AS s_femelle,
    count(s_male) AS s_male,
    count(s_ind) AS s_ind,
    count(date_ind) AS date_ind,
    count(sept) AS sept,
    count(oct) AS oct,
    count(nov) AS nov,
    count("dec") AS "dec",
    count(janv) AS janv,
    count(fev) AS fev,
    count(a_ind) AS a_ind,
    count(a_ad) AS a_ad,
    count(a_sub) AS a_sub,
    count(a_juv) AS a_juv,
    count(poids_ind) AS poids_ind,
    avg(poids_entier) AS poids_entier,
    avg(poids_vide) AS poids_vide,
    avg(poids_c_f_p) AS poids_c_f_p,
    count(mc_ind) AS mc_ind,
    count(mc_battue) AS mc_battue,
    count(mc_approche) AS mc_approche,
    count(mc_affut) AS mc_affut,
    count(nb_cors_ind) AS nb_cors_ind,
    avg(nb_cors) AS nb_cors,
    count(parc_onf) AS parc_onf
   FROM import_chasse.v_rapport_bilan_nobracelet
  GROUP BY saison, nom_vern, massif_affecte, z_i_affectee, num_zi_affectee;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW import_chasse.v_rapport_realisation_saison AS
SELECT type,
    saison,
    nom_vern,
    massif_affecte,
    num_zi_affectee,
    z_i_affectee,
    nb_affecte,
    nb_realise,
    nb_realise_avant11,
    ((nb_realise)::double precision / (nb_affecte)::double precision) AS fraction_realise,
    ((nb_realise_avant11)::double precision / (nb_affecte)::double precision) AS fraction_realise_avant11
   FROM ( SELECT lower(btrim("substring"((p.no_bracelet)::text, '^.* '::text))) AS type,
            s.saison,
            p.nom_vern,
            p.massif_affecte,
            p.z_i_affectee AS num_zi_affectee,
            (((p.z_i_affectee)::text || ' '::text) || (tzi.libelle)::text) AS z_i_affectee,
            count(DISTINCT p.no_bracelet) AS nb_affecte,
            count(( SELECT DISTINCT p.date_exacte
                  WHERE (NOT (p.date_exacte IS NULL)))) AS nb_realise,
            count(( SELECT DISTINCT p.date_exacte
                  WHERE ((date_part('month'::text, p.date_exacte) < (11)::double precision) AND (date_part('year'::text, p.date_exacte) = ((split_part((s.saison)::text, '-'::text, 1))::integer)::double precision)))) AS nb_realise_avant11
           FROM ((import_chasse.plan_chasse p
             JOIN import_chasse.saison_chasse s ON ((s.id = p.fk_saison)))
             JOIN ( SELECT tthesaurus.id AS pk,
                    tthesaurus.id_type,
                    tthesaurus.code,
                    tthesaurus.libelle,
                    tthesaurus.description,
                    tthesaurus.fk_parent,
                    tthesaurus.hierarchie
                   FROM import_chasse.tthesaurus
                  WHERE (tthesaurus.id_type = 4)) tzi ON (((p.z_i_affectee)::text = (tzi.code)::text)))
          GROUP BY (lower(btrim("substring"((p.no_bracelet)::text, '^.* '::text)))), s.saison, p.nom_vern, p.massif_affecte, (((p.z_i_affectee)::text || ' '::text) || (tzi.libelle)::text), p.z_i_affectee) a;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW oeasc_chasse.v_chasse_massifcerf_countby_sexe_saisonencours AS
WITH current_saison AS (
         SELECT ts.id_saison,
            ts.nom_saison
           FROM oeasc_chasse.t_saisons ts
          WHERE (ts.current = true)
        )
 SELECT row_number() OVER () AS row_number,
    tzc.nom_zone_cynegetique AS massif_affecte,
    te.nom_espece AS nom_vern,
    count(*) FILTER (WHERE ((ttb.code_type_bracelet)::text = 'CEM'::text)) AS cem,
    count(*) FILTER (WHERE ((ttb.code_type_bracelet)::text = 'CEFF'::text)) AS ceff,
    count(*) FILTER (WHERE ((ttb.code_type_bracelet)::text = 'CEFFD'::text)) AS ceffd
   FROM (((((oeasc_chasse.t_realisations tr
     JOIN oeasc_chasse.t_attributions ta ON ((tr.id_attribution = ta.id_attribution)))
     JOIN oeasc_chasse.t_type_bracelets ttb ON ((ttb.id_type_bracelet = ta.id_type_bracelet)))
     JOIN ref_nomenclatures.t_nomenclatures tn ON ((tn.id_nomenclature = tr.id_nomenclature_sexe)))
     JOIN oeasc_chasse.t_zone_cynegetiques tzc ON ((tzc.id_zone_cynegetique = ta.id_zone_cynegetique_affectee)))
     JOIN oeasc_commons.t_especes te ON ((te.id_espece = ttb.id_espece)))
  WHERE ((ta.id_saison = ( SELECT current_saison.id_saison
           FROM current_saison
         LIMIT 1)) AND (ttb.id_espece = 1))
  GROUP BY tzc.nom_zone_cynegetique, te.nom_espece;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW oeasc_chasse.v_chasse_massifchevreuil_countby_sexe_saisonencours AS
WITH current_saison AS (
         SELECT ts.id_saison,
            ts.nom_saison
           FROM oeasc_chasse.t_saisons ts
          WHERE (ts.current = true)
        )
 SELECT row_number() OVER () AS row_number,
    tzc.nom_zone_cynegetique AS massif_affecte,
    te.nom_espece AS nom_vern,
    count(*) AS count
   FROM (((((oeasc_chasse.t_realisations tr
     JOIN oeasc_chasse.t_attributions ta ON ((tr.id_attribution = ta.id_attribution)))
     JOIN oeasc_chasse.t_type_bracelets ttb ON ((ttb.id_type_bracelet = ta.id_type_bracelet)))
     JOIN ref_nomenclatures.t_nomenclatures tn ON ((tn.id_nomenclature = tr.id_nomenclature_sexe)))
     JOIN oeasc_chasse.t_zone_cynegetiques tzc ON ((tzc.id_zone_cynegetique = ta.id_zone_cynegetique_affectee)))
     JOIN oeasc_commons.t_especes te ON ((te.id_espece = ttb.id_espece)))
  WHERE ((ta.id_saison = ( SELECT current_saison.id_saison
           FROM current_saison
         LIMIT 1)) AND (ttb.id_espece = 2))
  GROUP BY tzc.nom_zone_cynegetique, te.nom_espece;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW oeasc_chasse.v_chasse_qgis_cerf_countby_sexe_saisonencours AS
WITH current_saison AS (
         SELECT ts.id_saison,
            ts.nom_saison
           FROM oeasc_chasse.t_saisons ts
          WHERE (ts.current = true)
        )
 SELECT row_number() OVER () AS row_number,
    tlt.geom,
    tlt.code_lieu_tir AS code_lieu_dit,
    count(*) FILTER (WHERE ((ttb.code_type_bracelet)::text = 'CEM'::text)) AS count_cem,
    count(*) FILTER (WHERE ((ttb.code_type_bracelet)::text ~~* 'CEFF'::text)) AS count_ceff,
    count(*) FILTER (WHERE ((ttb.code_type_bracelet)::text ~~* 'CEFFD'::text)) AS count_ceffd,
    tlt.nom_lieu_tir AS nom_lieudit,
    tlt.label_commune AS nom_com
   FROM (((((oeasc_chasse.t_realisations tr
     JOIN oeasc_chasse.t_attributions ta ON ((tr.id_attribution = ta.id_attribution)))
     JOIN oeasc_chasse.t_type_bracelets ttb ON ((ttb.id_type_bracelet = ta.id_type_bracelet)))
     JOIN oeasc_chasse.t_lieu_tir_synonymes tlts ON ((tlts.id_lieu_tir_synonyme = tr.id_lieu_tir_synonyme)))
     JOIN oeasc_chasse.t_lieu_tirs tlt ON ((tlt.id_lieu_tir = tlts.id_lieu_tir)))
     JOIN oeasc_chasse.t_zone_cynegetiques tzc ON ((tzc.id_zone_cynegetique = ta.id_zone_cynegetique_affectee)))
  WHERE ((ta.id_saison = ( SELECT current_saison.id_saison
           FROM current_saison
         LIMIT 1)) AND (ttb.id_espece = 1))
  GROUP BY tlt.geom, tlt.code_lieu_tir, tlt.nom_lieu_tir, tlt.label_commune;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW oeasc_chasse.v_chasse_qgis_toutessp_countby_saisonencours AS
WITH current_saison AS (
         SELECT ts.id_saison,
            ts.nom_saison
           FROM oeasc_chasse.t_saisons ts
          WHERE (ts.current = true)
        )
 SELECT row_number() OVER () AS row_number,
    tlt.geom,
    tlt.code_lieu_tir AS code_lieu_dit,
    te.nom_espece,
    ttb.code_type_bracelet AS type,
    count(*) AS count,
    tlt.nom_lieu_tir AS nom_lieudit,
    tlt.label_commune AS nom_com
   FROM ((((((oeasc_chasse.t_realisations tr
     JOIN oeasc_chasse.t_attributions ta ON ((tr.id_attribution = ta.id_attribution)))
     JOIN oeasc_chasse.t_type_bracelets ttb ON ((ttb.id_type_bracelet = ta.id_type_bracelet)))
     JOIN oeasc_chasse.t_lieu_tir_synonymes tlts ON ((tlts.id_lieu_tir_synonyme = tr.id_lieu_tir_synonyme)))
     JOIN oeasc_chasse.t_lieu_tirs tlt ON ((tlt.id_lieu_tir = tlts.id_lieu_tir)))
     JOIN oeasc_chasse.t_zone_cynegetiques tzc ON ((tzc.id_zone_cynegetique = ta.id_zone_cynegetique_affectee)))
     JOIN oeasc_commons.t_especes te ON ((te.id_espece = ttb.id_espece)))
  WHERE (ta.id_saison = ( SELECT current_saison.id_saison
           FROM current_saison
         LIMIT 1))
  GROUP BY tlt.geom, tlt.code_lieu_tir, te.nom_espece, ttb.code_type_bracelet, tlt.nom_lieu_tir, tlt.label_commune;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW oeasc_chasse.v_chasse_qgis_toutessp_countby_saisonencours_zi AS
WITH current_saison AS (
         SELECT ts.id_saison,
            ts.nom_saison
           FROM oeasc_chasse.t_saisons ts
          WHERE (ts.current = true)
        )
 SELECT row_number() OVER () AS row_number,
    tlt.geom,
    tlt.code_lieu_tir AS code_lieu_dit,
    count(*) FILTER (WHERE ((ttb.code_type_bracelet)::text = 'CHI'::text)) AS count_chi,
    count(*) FILTER (WHERE ((ttb.code_type_bracelet)::text = 'CEM'::text)) AS count_cem,
    count(*) FILTER (WHERE ((ttb.code_type_bracelet)::text = 'CEFF'::text)) AS count_ceff,
    tlt.nom_lieu_tir AS nom_lieudit,
    tlt.label_commune AS nom_com,
    tzc.code_zone_cynegetique AS z_i_affectee,
    tzc.nom_zone_cynegetique AS zi
   FROM (((((oeasc_chasse.t_realisations tr
     JOIN oeasc_chasse.t_attributions ta ON ((tr.id_attribution = ta.id_attribution)))
     JOIN oeasc_chasse.t_type_bracelets ttb ON ((ttb.id_type_bracelet = ta.id_type_bracelet)))
     JOIN oeasc_chasse.t_lieu_tir_synonymes tlts ON ((tlts.id_lieu_tir_synonyme = tr.id_lieu_tir_synonyme)))
     JOIN oeasc_chasse.t_lieu_tirs tlt ON ((tlt.id_lieu_tir = tlts.id_lieu_tir)))
     JOIN oeasc_chasse.t_zone_cynegetiques tzc ON ((tzc.id_zone_cynegetique = ta.id_zone_cynegetique_affectee)))
  WHERE (ta.id_saison = ( SELECT current_saison.id_saison
           FROM current_saison
         LIMIT 1))
  GROUP BY tlt.geom, tlt.code_lieu_tir, tlt.nom_lieu_tir, tlt.label_commune, tzc.code_zone_cynegetique, tzc.nom_zone_cynegetique;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW oeasc_declarations.v_degats AS
SELECT d.id_declaration AS id_declaration_degat,
    ref_nomenclatures.get_nomenclature_mnemonique(d.id_nomenclature_degat_type) AS degat_type_mnemo,
    ref_nomenclatures.get_nomenclature_mnemonique(de.id_nomenclature_degat_essence) AS degat_essence_mnemo,
    ref_nomenclatures.get_nomenclature_mnemonique(de.id_nomenclature_degat_gravite) AS degat_gravite_mnemo,
    ref_nomenclatures.get_nomenclature_mnemonique(de.id_nomenclature_degat_etendue) AS degat_etendue_mnemo,
    ref_nomenclatures.get_nomenclature_mnemonique(de.id_nomenclature_degat_anteriorite) AS degat_anteriorite_mnemo,
    ref_nomenclatures.get_nomenclature_label(d.id_nomenclature_degat_type) AS degat_type_label,
    ref_nomenclatures.get_nomenclature_label(de.id_nomenclature_degat_essence) AS degat_essence_label,
    ref_nomenclatures.get_nomenclature_label(de.id_nomenclature_degat_gravite) AS degat_gravite_label,
    ref_nomenclatures.get_nomenclature_label(de.id_nomenclature_degat_etendue) AS degat_etendue_label,
    ref_nomenclatures.get_nomenclature_label(de.id_nomenclature_degat_anteriorite) AS degat_anteriorite_label,
    ref_nomenclatures.get_nomenclature_code(d.id_nomenclature_degat_type) AS degat_type_code,
    ref_nomenclatures.get_nomenclature_code(de.id_nomenclature_degat_essence) AS degat_essence_code,
    ref_nomenclatures.get_nomenclature_code(de.id_nomenclature_degat_gravite) AS degat_gravite_code,
    ref_nomenclatures.get_nomenclature_code(de.id_nomenclature_degat_etendue) AS degat_etendue_code,
    ref_nomenclatures.get_nomenclature_code(de.id_nomenclature_degat_anteriorite) AS degat_anteriorite_code
   FROM (oeasc_declarations.t_degats d
     LEFT JOIN oeasc_declarations.t_degat_essences de ON ((de.id_degat = d.id_degat)))
  ORDER BY d.id_declaration;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW oeasc_resultats.v_nb_degat_anteriorite_mnemo AS
SELECT count(*) AS value,
    degat_anteriorite_mnemo AS label
   FROM oeasc_declarations.v_degats
  WHERE (degat_anteriorite_mnemo IS NOT NULL)
  GROUP BY degat_anteriorite_mnemo
  ORDER BY (count(*)) DESC;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW oeasc_resultats.v_nb_degat_essence_mnemo AS
SELECT count(*) AS value,
    degat_essence_mnemo AS label
   FROM oeasc_declarations.v_degats
  WHERE (degat_essence_mnemo IS NOT NULL)
  GROUP BY degat_essence_mnemo
  ORDER BY (count(*)) DESC;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW oeasc_resultats.v_nb_degat_etendue_mnemo AS
SELECT count(*) AS value,
    degat_etendue_mnemo AS label
   FROM oeasc_declarations.v_degats
  WHERE (degat_etendue_mnemo IS NOT NULL)
  GROUP BY degat_etendue_mnemo
  ORDER BY (count(*)) DESC;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW oeasc_resultats.v_nb_degat_gravite_mnemo AS
SELECT count(*) AS value,
    degat_gravite_mnemo AS label
   FROM oeasc_declarations.v_degats
  WHERE (degat_gravite_mnemo IS NOT NULL)
  GROUP BY degat_gravite_mnemo
  ORDER BY (count(*)) DESC;
"""
    )

    op.execute(
        """
CREATE OR REPLACE VIEW oeasc_resultats.v_nb_degat_type_mnemo AS
SELECT count(*) AS value,
    degat_type_mnemo AS label
   FROM oeasc_declarations.v_degats
  WHERE (degat_type_mnemo IS NOT NULL)
  GROUP BY degat_type_mnemo
  ORDER BY (count(*)) DESC;
"""
    )
