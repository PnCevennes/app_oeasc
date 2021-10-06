-- Nettoyage
TRUNCATE TABLE oeasc_chasse.t_attributions CASCADE;
TRUNCATE TABLE oeasc_chasse.t_saisons CASCADE;
TRUNCATE TABLE oeasc_chasse.t_personnes CASCADE;
TRUNCATE TABLE oeasc_chasse.t_zone_cynegetiques CASCADE;



-- Insertion des taxons
ALTER TABLE oeasc_commons.t_especes DROP CONSTRAINT IF EXISTS oeasc_commons_t_espece_unique_code_espece;
ALTER TABLE oeasc_commons.t_especes ADD CONSTRAINT oeasc_commons_t_espece_unique_code_espece UNIQUE(code_espece);
INSERT INTO oeasc_commons.t_especes(nom_espece, code_espece)
VALUES
('Cerf', 'CF'),
('Chevreuil', 'CH'),
('Lièvre', 'LI'),
('Renard', 'RE'),
('Mouflon', 'MF'),
('Daim', 'DA'),
('Sanglier', 'SG')
ON CONFLICT DO NOTHING
;

ALTER TABLE oeasc_commons.t_especes ADD IF NOT EXISTS cd_nom INTEGER;

UPDATE oeasc_commons.t_especes SET cd_nom = (
	SELECT CASE
		WHEN code_espece = 'CF' THEN 61000
		WHEN code_espece = 'CH' THEN 61057
		WHEN code_espece = 'DA' THEN 61028
		WHEN code_espece = 'LI' THEN 61701
		WHEN code_espece = 'MF' THEN 61110
		WHEN code_espece = 'RE' THEN 60588
		WHEN code_espece = 'SG' THEN 60981
	END
)
;
-- SAISONS

-- - t_saisons

INSERT INTO oeasc_chasse.t_saisons (
	nom_saison,
	date_debut,
	date_fin,
	current,
	commentaire
)
SELECT
	saison AS nom_saison,
	date_min AS date_debut,
	date_max AS date_fin,
	current,
	commentaire
FROM import_chasse.saison_chasse
;

-- t_saison toujours (complement avec la table import_chasse.plan_chasse_attribution_massif pcam)
-- Import des saisons historiques qui n'ont pas de données saisies dans le plan de chasse
-- mais une donnée dans attribution massif
insert into oeasc_chasse.t_saisons (nom_saison)
select distinct saison from import_chasse.plan_chasse_attribution_massif pcam
left join oeasc_chasse.t_saisons ts on ts.nom_saison = pcam.saison
where ts.nom_saison is null
order by saison
;


-- t_saison_dates

INSERT INTO oeasc_chasse.t_saison_dates(id_saison, date_debut, date_fin, id_espece)
WITH saison_date AS(
SELECT
os.id_saison,
date_debut_cerfs AS date_debut,
date_fin_cerfs AS date_fin,
e.id_espece
FROM import_chasse.saison_chasse s
JOIN oeasc_chasse.t_saisons os ON os.nom_saison = s.saison
JOIN oeasc_commons.t_especes e ON e.nom_espece = 'Cerf'
UNION
SELECT
os.id_saison,
date_debut_chevreuils AS date_debut,
date_fin_chevreuils AS date_fin,
e.id_espece
FROM import_chasse.saison_chasse s
JOIN oeasc_chasse.t_saisons os ON os.nom_saison = s.saison
JOIN oeasc_commons.t_especes e ON e.nom_espece = 'Chevreuil'
UNION
SELECT
os.id_saison,
date_debut_mouflons AS date_debut,
date_fin_mouflons AS date_fin,
e.id_espece
FROM import_chasse.saison_chasse s
JOIN oeasc_chasse.t_saisons os ON os.nom_saison = s.saison
JOIN oeasc_commons.t_especes e ON e.nom_espece = 'Mouflon'
UNION
SELECT
os.id_saison,
date_debut_daims AS date_debut,
date_fin_daims AS date_fin,
e.id_espece
FROM import_chasse.saison_chasse s
JOIN oeasc_chasse.t_saisons os ON os.nom_saison = s.saison
JOIN oeasc_commons.t_especes e ON e.nom_espece = 'Daim'
)
SELECT id_saison, date_debut, date_fin, id_espece
FROM saison_date
WHERE date_debut IS NOT NULL
;


-- PERSONNES
-- (TODO corriger les noms dans la table de base)

INSERT INTO oeasc_chasse.t_personnes(nom_personne)
WITH auteur AS (
SELECT auteur_tir AS nom_personne FROM import_chasse.plan_chasse
UNION
SELECT auteur_constat AS nom_personne FROM import_chasse.plan_chasse
)
SELECT DISTINCT min(nom_personne)
FROM auteur
WHERE nom_personne IS NOT NULL AND nom_personne NOT IN ('', '?')
GROUP BY lower(unaccent(nom_personne)) -- suppression des orthographe similaire
ORDER BY min(nom_personne)
;


-- ZONES

-- zone cynegetique

INSERT INTO oeasc_chasse.t_zone_cynegetiques(nom_zone_cynegetique, code_zone_cynegetique)
VALUES
('Aigoual nord', 'AIGO_N'),
('Aigoual sud (Gard)', 'AIGO_S'),
('Causse Méjean', 'CAUS'),
('Mont Lozère est (Gard)', 'MTLO_E_30'),
('Mont Lozère nord, ouest et est (Lozère)', 'MTLO_ONE_48'),
('Mont Lozère sud, Bougès nord', 'MTLO_S'),
('Vallées cévenoles', 'VALC'),
('Zone coeur', 'ZC')
ON CONFLICT DO NOTHING
;

UPDATE oeasc_chasse.t_zone_cynegetiques zc
SET id_secteur=(
SELECT --id_zone_cynegetique,
s.id_secteur
--, code_zone_cynegetique, code_secteur
FROM oeasc_chasse.t_zone_cynegetiques zc2
JOIN oeasc_commons.t_secteurs s ON s.code_secteur = SPLIT_PART(zc2.code_zone_cynegetique, '_', 1)
 WHERE zc2.id_zone_cynegetique = zc.id_zone_cynegetique
)
;

-- zone indicatives
WITH info_zi AS (
	SELECT
		num_zi,
		nom_zi,
		st_multi(ST_UNION(geom)) AS geom
		FROM oeasc_chasse.t_import_zi tiz
		GROUP BY num_zi, nom_zi
)
INSERT INTO oeasc_chasse.t_zone_indicatives (
	code_zone_indicative,
	nom_zone_indicative,
	geom,
	id_zone_cynegetique
)
SELECT DISTINCT
	num_zi,
	iz.nom_zi,
	iz.geom,
	zc.id_zone_cynegetique
FROM  info_zi iz
LEFT JOIN import_chasse.plan_chasse ipc
ON iz.num_zi = z_i_affectee::int
LEFT JOIN oeasc_chasse.t_zone_cynegetiques zc
ON regexp_replace(zc.nom_zone_cynegetique, ',? \(.*\),?', '') = regexp_replace(ipc.massif_affecte, ',? \(.*\),?', '')
ON CONFLICT DO NOTHING;


UPDATE  oeasc_chasse.t_zone_indicatives SET  id_zone_cynegetique = (SELECT id_zone_cynegetique FROM oeasc_chasse.t_zone_cynegetiques WHERE code_zone_cynegetique = 'CAUS')
WHERE code_zone_indicative  IN ('21', '25', '27', '29', '31')
	AND id_zone_cynegetique IS NULL;

-- insertion zc pour daim et mouflons
INSERT INTO oeasc_chasse.t_zone_indicatives
(code_zone_indicative, nom_zone_indicative, id_zone_cynegetique)
SELECT '99', d.nom_zone_cynegetique , id_zone_cynegetique
FROM oeasc_chasse.t_zone_cynegetiques d
WHERE code_zone_cynegetique = 'ZC';

-- lieu tir

insert into oeasc_chasse.t_lieu_tirs
    (nom_lieu_tir, code_lieu_tir, id_zone_indicative, id_zone_cynegetique,  id_area_commune, label_commune, geom)
    select nom_lieudit, code_lieudit, zi.id_zone_indicative, zc.id_zone_cynegetique, id_area, label, lt.geom
    from import_chasse.lieux_tir lt
    LEFT join oeasc_chasse.t_zone_indicatives zi
        on ST_INTERSECTS(zi.geom, lt.geom)
    LEFT join oeasc_chasse.t_zone_cynegetiques zc
        on regexp_replace(zc.nom_zone_cynegetique, ',? \(.*\),?', '') = lt.zon_cyne0
    join ref_geo.vl_areas la
        on ST_INTERSECTS(la.geom, lt.geom)
    join ref_geo.bib_areas_types bat
        on bat.id_type = la.id_type
    where bat.type_code = 'OEASC_COMMUNE'
;

-- corrections fusions communes

UPDATE oeasc_chasse.t_lieu_tirs tlt SET  nom_lieu_tir ='Indéterminé (Bédouès)' WHERE code_lieu_tir = '4802299';
UPDATE oeasc_chasse.t_lieu_tirs tlt SET  nom_lieu_tir ='Indéterminé (Saint-Julien-du-Tournel)' WHERE code_lieu_tir = '4816499';
UPDATE oeasc_chasse.t_lieu_tirs tlt SET  nom_lieu_tir ='Indéterminé (La Salle-Prunet)' WHERE code_lieu_tir = '4818699';
UPDATE oeasc_chasse.t_lieu_tirs tlt SET  nom_lieu_tir ='Indéterminé (Mas-d''Orcières)' WHERE code_lieu_tir = '4809399';
UPDATE oeasc_chasse.t_lieu_tirs tlt SET  nom_lieu_tir ='Indéterminé (Fraissinet-de-Lozère)' WHERE code_lieu_tir = '4806699';
UPDATE oeasc_chasse.t_lieu_tirs tlt SET  nom_lieu_tir ='Indéterminé (Saint-Andéol-de-Clerguemort)' WHERE code_lieu_tir = '4813499';
UPDATE oeasc_chasse.t_lieu_tirs tlt SET  nom_lieu_tir ='Le Villaret (Saint-Maurice-de-Ventalon)' WHERE code_lieu_tir = '4817241';
UPDATE oeasc_chasse.t_lieu_tirs tlt SET  nom_lieu_tir ='Indéterminé (Saint-Maurice-de-Ventalon)' WHERE code_lieu_tir = '4817299';
UPDATE oeasc_chasse.t_lieu_tirs tlt SET  nom_lieu_tir ='Indéterminé (Saint-Julien-d''Arpaon)' WHERE code_lieu_tir = '4816299';
UPDATE oeasc_chasse.t_lieu_tirs tlt SET  nom_lieu_tir ='Indéterminé (Florac)' WHERE code_lieu_tir = '4806199';
UPDATE oeasc_chasse.t_lieu_tirs tlt SET  nom_lieu_tir ='Indéterminé (Saint-Frézal-de-Ventalon)' WHERE code_lieu_tir = '4815299';
UPDATE oeasc_chasse.t_lieu_tirs tlt SET  nom_lieu_tir ='Le Villaret (Le Pont-de-Montvert)' WHERE code_lieu_tir = '4811603';
UPDATE oeasc_chasse.t_lieu_tirs tlt SET  nom_lieu_tir ='Indéterminé (Le Pont-de-Montvert)' WHERE code_lieu_tir = '4811699';
UPDATE oeasc_chasse.t_lieu_tirs tlt SET  nom_lieu_tir ='Indéterminé (Cocurès)' WHERE code_lieu_tir = '4805099';
UPDATE oeasc_chasse.t_lieu_tirs tlt SET  nom_lieu_tir ='Indéterminé (Saint-Laurent-de-Trèves)' WHERE code_lieu_tir = '4816699';


-- synonymes

insert into oeasc_chasse.t_lieu_tir_synonymes
	(id_lieu_tir, nom_lieu_tir_synonyme)
	select distinct on (lt.id_lieu_tir, lts.libelle_lieudit)
		lt.id_lieu_tir,
		lts.libelle_lieudit as nom_lieu_tir
	from import_chasse.lieu_tir_synonymes lts
	join oeasc_chasse.t_lieu_tirs lt on lt.code_lieu_tir::int = lts.code_lieudit
;

-- oeasc_chasse.t_attribution_massifs

insert into oeasc_chasse.t_attribution_massifs
(id_espece, id_zone_cynegetique, id_saison, nb_affecte_min, nb_affecte_max)
select id_espece, tzc.id_zone_cynegetique, id_saison, nb_affecte_min, nb_affecte_max
from import_chasse.plan_chasse_attribution_massif pcam
left join oeasc_commons.t_especes te
	on te.nom_espece = split_part(nom_vern, ' ', 1)
left join oeasc_chasse.t_zone_cynegetiques tzc
	on regexp_replace(pcam.massif, ',? \(.*\),?', '') = regexp_replace(tzc.nom_zone_cynegetique, ',? \(.*\),?', '')
left join oeasc_chasse.t_saisons ts
	on ts.nom_saison = pcam.saison
;

-- oeasc_chasse.t_type_bracelet

insert into oeasc_chasse.t_type_bracelets (id_espece, code_type_bracelet, description_type_bracelet)
WITH info_bracelet AS (
	SELECT
		SPLIT_PART(no_bracelet, ' ', 1) AS code_bracelet,
		sexe,
		classe_age,
		nom_vern
	FROM import_chasse.plan_chasse
)
SELECT
	id_espece,
	code_bracelet,
	'sexe : ' || string_agg(distinct sexe, ', ')
	|| '; classe age : '  || string_agg(distinct classe_age, ', ')
	|| '; espece : ' || string_agg(distinct nom_vern, ', ') AS description
from info_bracelet
LEFT JOIN oeasc_commons.t_especes ON
( code_bracelet = 'CHI' AND code_espece = 'CH' )
OR ( code_bracelet IN ('CEFF', 'CEM', 'CEFFD') AND code_espece = 'CF' )
OR ( code_bracelet IN ('MOM', 'MOF', 'MOM1', 'MOIJ', 'MOI') AND code_espece = 'MF' )
OR ( code_bracelet = 'DAI' AND code_espece = 'DA' )
group by code_bracelet,  nom_espece, id_espece
order by count(*) desc;

-- oeasc_chasse.t_attributions
-- test double

with join_saison as (
	SELECT ts.id_saison , sc.id AS old_id_saison
	FROM oeasc_chasse.t_saisons ts
	JOIN import_chasse.saison_chasse sc
	ON ts.nom_saison = sc.saison
)
insert into oeasc_chasse.t_attributions (id_saison, id_type_bracelet, id_zone_cynegetique_affectee, id_zone_indicative_affectee, numero_bracelet)
select id_saison, id_type_bracelet, tzc.id_zone_cynegetique, tzi.id_zone_indicative, no_bracelet
from import_chasse.plan_chasse pc
left join oeasc_commons.t_especes te on te.nom_espece = split_part(pc.nom_vern, ' ', 1)
left join oeasc_chasse.t_type_bracelets ttb on ttb.code_type_bracelet = SPLIT_PART(no_bracelet, ' ', 1)
left join oeasc_chasse.t_zone_cynegetiques tzc
	on 	regexp_replace(tzc.nom_zone_cynegetique, ',? \(.*\),?', '') = regexp_replace(pc.massif_affecte, ',? \(.*\),?', '')
left join oeasc_chasse.t_zone_indicatives tzi on tzi.code_zone_indicative = pc.z_i_affectee
join join_saison s on s.old_id_saison = pc.fk_saison
;
-- nomenclature mode chasse


create table oeasc_chasse.tmp_nomenclature_mode_chasse (
	label_fr character varying,
	cd_nomenclature character varying
)
;


insert into ref_nomenclatures.bib_nomenclatures_types
(mnemonique, label_fr) VALUES
('OEASC_MOD_CHASSE', 'Mode de chasse')
on conflict do nothing
;

insert into oeasc_chasse.tmp_nomenclature_mode_chasse (label_fr, cd_nomenclature)
values
('Affut','AFF')
,('Approche', 'APP')
,('Battue', 'BAT')
,('Poussée silencieuse', 'POU/SI')
,('Indéterminé', 'IND')
;

delete from ref_nomenclatures.t_nomenclatures n
using ref_nomenclatures.bib_nomenclatures_types t
where n.id_type = t.id_type AND t.mnemonique = 'OEASC_MOD_CHASSE'
;

SELECT setval_max('ref_nomenclatures');


insert into ref_nomenclatures.t_nomenclatures
(id_type, mnemonique, cd_nomenclature, label_fr, label_default, definition_fr, definition_default)
select
	t.id_type,
	n.cd_nomenclature,
	n.cd_nomenclature,
	n.label_fr,
	n.label_fr,
	n.label_fr,
	n.label_fr
from oeasc_chasse.tmp_nomenclature_mode_chasse n
join ref_nomenclatures.bib_nomenclatures_types t on t.mnemonique = 'OEASC_MOD_CHASSE';

drop table oeasc_chasse.tmp_nomenclature_mode_chasse;

-- oeasc_chasse.t_realisations


with nomenclature_mode_chasse as (
	select id_nomenclature, tn.label_fr
	from ref_nomenclatures.t_nomenclatures tn
	join ref_nomenclatures.bib_nomenclatures_types bnt on bnt.id_type =tn.id_type
	where bnt.mnemonique = 'OEASC_MOD_CHASSE'
), nomenclature_sexe as (
	select id_nomenclature, tn.label_fr
	from ref_nomenclatures.t_nomenclatures tn
	join ref_nomenclatures.bib_nomenclatures_types bnt on bnt.id_type =tn.id_type
	where bnt.mnemonique = 'SEXE'
), nomenclature_age as (
	select id_nomenclature, tn.label_fr
	from ref_nomenclatures.t_nomenclatures tn
	join ref_nomenclatures.bib_nomenclatures_types bnt on bnt.id_type =tn.id_type
	where bnt.mnemonique = 'STADE_VIE'
), join_saison as (
	SELECT ts.id_saison , sc.id AS old_id_saison
	FROM oeasc_chasse.t_saisons ts
	JOIN import_chasse.saison_chasse sc
	ON ts.nom_saison = sc.saison
), synonymes as (
    select code_lieu_tir, id_lieu_tir_synonyme
	from oeasc_chasse.t_lieu_tir_synonymes s
	join oeasc_chasse.t_lieu_tirs t on t.id_lieu_tir = s.id_lieu_tir
	where s.nom_lieu_tir_synonyme = t.nom_lieu_tir
	order by code_lieu_tir, id_lieu_tir_synonyme
)
insert into oeasc_chasse.t_realisations(
	id_attribution,
	id_zone_cynegetique_realisee,
	id_zone_indicative_realisee,
	id_lieu_tir_synonyme,
    date_exacte,
    date_enreg,
	mortalite_hors_pc,
	id_auteur_tir,
	id_auteur_constat,
	id_nomenclature_sexe,
	id_nomenclature_classe_age,
	poid_entier,
	poid_vide,
	poid_c_f_p,
	long_dagues_droite,
	long_dagues_gauche,
	long_mandibules_droite,
	long_mandibules_gauche,
	cors_nb,
	cors_commentaires,
	gestation,
	id_nomenclature_mode_chasse,
	commentaire ,
	parcelle_onf,
	poid_indique,
	cors_indetermine,
	long_mandibule_indetermine
)
select
	id_attribution,
	coalesce(tzc.id_zone_cynegetique, ta.id_zone_cynegetique_affectee) ,
	coalesce(tzi.id_zone_indicative, ta.id_zone_indicative_affectee),
	tlt.id_lieu_tir_synonyme,
    pc.date_exacte,
    pc.date_enreg,
	pc.mortalite_hors_pc,
	tp.id_personne as id_auteur_tir,
	tp2.id_personne as id_auteur_constat,
	ns.id_nomenclature as id_nomenclature_sexe,
	na.id_nomenclature as id_nomenclature_classe_age,
	pc.poids_entier,
	pc.poids_vide,
	pc.poids_c_f_p,
	pc.long_dagues_droite,
	pc.long_dagues_gauche,
	pc.long_mandibules_droite,
	pc.long_mandibules_gauche,
	pc.cors_nb,
	pc.cors_commentaire,
	pc.gestation,
	nc.id_nomenclature as id_nomenclature_mode_chasse,
	pc.obs as commentaire,
	pc.parc_onf as parcelle_onf,
	pc.poids_ind as poid_indique,
	pc.cors_indetermine,
	pc.long_mandibules_indertermine
from import_chasse.plan_chasse pc
left join join_saison s on s.old_id_saison = pc.fk_saison
join oeasc_chasse.t_attributions ta on ta.numero_bracelet = pc.no_bracelet and ta.id_saison = s.id_saison
left join oeasc_chasse.t_zone_cynegetiques tzc
	on 	regexp_replace(tzc.nom_zone_cynegetique, ',? \(.*\),?', '') =
	   		regexp_replace(pc.massif_affecte, ',? \(.*\),?', '')
left join oeasc_chasse.t_zone_indicatives tzi on tzi.code_zone_indicative = pc.z_i_affectee
left join oeasc_chasse.t_personnes tp on tp.nom_personne = pc.auteur_tir
left join oeasc_chasse.t_personnes tp2 on tp2.nom_personne = pc.auteur_constat
left join synonymes tlt on tlt.code_lieu_tir = pc.code_lieu_dit
left join nomenclature_sexe ns on ns.label_fr = pc.sexe
left join nomenclature_age na on na.label_fr = replace(replace(classe_age, 'Jeune', 'Juvénile'), ' ', '-')
left join nomenclature_mode_chasse nc on nc.label_fr = pc.mode_chasse
WHERE NOT pc.date_exacte IS NULL
;




-- bilan chasse
insert into oeasc_chasse.t_bilan_chasse_historique(
	id_saison,
	id_espece,
	id_zone_indicative,
	nb_affecte_min,
	nb_affecte_max,
	nb_realise,
	nb_realise_avant_11
)
select
	ts.id_saison,
	te.id_espece,
	tzi.id_zone_indicative,
	nb_affecte_min,
	nb_affecte_max,
	nb_realise,
	nb_realise_avant11
	from import_chasse.bilan_chasse_historique bch
	join oeasc_chasse.t_saisons ts on ts.nom_saison = bch.saison
	join oeasc_commons.t_especes te on nom_vern ilike concat('%', te.nom_espece, '%')
	LEFT join oeasc_chasse.t_zone_indicatives tzi on tzi.code_zone_indicative = bch.z_i_affectee
	order by z_i_affectee::int
;