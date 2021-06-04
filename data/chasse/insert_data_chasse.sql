-- correct 
ALTER TABLE import_chasse.plan_chasse DISABLE trigger ALL;
update import_chasse.plan_chasse pc set date_exacte = date_exacte - interval '1 year' 
where date_exacte > '2021-07-01';


    -- PREPA ESPECES
--
-- TODO ajouter cd_nom ??



ALTER TABLE oeasc_commons.t_especes DROP CONSTRAINT IF EXISTS oeasc_commons_t_espece_unique_code_espece;
ALTER TABLE oeasc_commons.t_especes ADD CONSTRAINT oeasc_commons_t_espece_unique_code_espece UNIQUE(code_espece);
INSERT INTO oeasc_commons.t_especes(nom_espece, code_espece)
VALUES 
('Cerf', 'CF'),
('Chevreuil', 'CH'),
('Lièvre', 'LI'),
('Renard', 'RE'),
('Mouflon', 'MF'),
('Daim', 'DA')
ON CONFLICT DO NOTHING
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
SELECT DISTINCT nom_personne FROM auteur
WHERE nom_personne IS NOT NULL AND nom_personne NOT IN ('', '?')
ORDER BY nom_personne
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

-- zone interet

INSERT INTO oeasc_chasse.t_zone_indicatives (nom_zone_indicative, code_zone_indicative, id_zone_cynegetique)
SELECT DISTINCT 
	z_i_affectee, z_i_affectee, zc.id_zone_cynegetique
	FROM import_chasse.plan_chasse ipc
	LEFT JOIN oeasc_chasse.t_zone_cynegetiques zc
		ON 
        regexp_replace(zc.nom_zone_cynegetique, ',? \(.*\),?', '') = 
        regexp_replace(ipc.massif_affecte, ',? \(.*\),?', '')
ON CONFLICT DO NOTHING
;

-- lieu tir
-- synonymes à faire plus tard

insert into oeasc_chasse.t_lieu_tirs
    (nom_lieu_tir, code_lieu_tir, id_zone_indicative, id_area_commune, synonymes, geom)
    select nom_lieudit, code_lieudit, zc.id_zone_cynegetique, id_area, NULL, lt.geom
    from import_chasse.lieux_tir lt 
    left join oeasc_chasse.t_zone_cynegetiques zc 
        on regexp_replace(zc.nom_zone_cynegetique, ',? \(.*\),?', '') = lt.zon_cyne0
    join ref_geo.l_areas la
        on ST_INTERSECTS(la.geom, lt.geom) 
    join ref_geo.bib_areas_types bat
        on bat.id_type = la.id_type 
    where bat.type_code = 'OEASC_COMMUNE'
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
select 
	id_espece, 
	'BRACELET_' || code_espece as code_type_bracelet,
	'Bracelet pour l''espece ' || nom_espece as description_type_bracelet
	from oeasc_commons.t_especes te 
;

-- oeasc_chasse.t_attributions
-- test double

with saison_dates as(
	select 
		id_saison,
		TO_DATE(SPLIT_PART(nom_saison, '-', 1) || '0701', 'YYYYMMDD') as date_debut, 
		TO_DATE(SPLIT_PART(nom_saison, '-', 2) || '0601', 'YYYYMMDD') as date_fin 
		from oeasc_chasse.t_saisons ts 
)
insert into oeasc_chasse.t_attributions (id_saison, id_type_bracelet, id_zone_cynegetique_affectee, id_zone_indicative_affectee, numero_bracelet)
select id_saison, id_type_bracelet, tzc.id_zone_cynegetique, tzi.id_zone_indicative, no_bracelet
	from import_chasse.plan_chasse pc 
	left join oeasc_commons.t_especes te on te.nom_espece = split_part(pc.nom_vern, ' ', 1) 
	left join oeasc_chasse.t_type_bracelets ttb on ttb.id_espece = te.id_espece 
	left join oeasc_chasse.t_zone_cynegetiques tzc 
		on 	regexp_replace(tzc.nom_zone_cynegetique, ',? \(.*\),?', '') = 
	   		regexp_replace(pc.massif_affecte, ',? \(.*\),?', '')
	left join oeasc_chasse.t_zone_indicatives tzi on tzi.code_zone_indicative = pc.z_i_affectee 
	join saison_dates s on date_exacte > s.date_debut and date_exacte < s.date_fin
	WHERE massif_realise IS NOT NULL AND pc.id NOT IN (6687, 4965, 10849, 9113)
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
),saison_dates as(
	select 
		id_saison,
		TO_DATE(SPLIT_PART(nom_saison, '-', 1) || '0701', 'YYYYMMDD') as date_debut, 
		TO_DATE(SPLIT_PART(nom_saison, '-', 2) || '0601', 'YYYYMMDD') as date_fin 
		from oeasc_chasse.t_saisons ts 
)
insert into oeasc_chasse.t_realisations(
	id_attribution,
	id_zone_cynegetique_realisee,
	id_zone_indicative_realisee,
	id_lieu_tir,
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
	tzc.id_zone_cynegetique ,
	tzi.id_zone_indicative,
	tlt.id_lieu_tir,
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
left join saison_dates s on date_exacte > s.date_debut and date_exacte < s.date_fin
join oeasc_chasse.t_attributions ta on ta.numero_bracelet = pc.no_bracelet and ta.id_saison=s.id_saison
left join oeasc_chasse.t_zone_cynegetiques tzc 
	on 	regexp_replace(tzc.nom_zone_cynegetique, ',? \(.*\),?', '') = 
	   		regexp_replace(pc.massif_affecte, ',? \(.*\),?', '')
left join oeasc_chasse.t_zone_indicatives tzi on tzi.code_zone_indicative = pc.z_i_affectee 
left join oeasc_chasse.t_personnes tp on tp.nom_personne = pc.auteur_tir 
left join oeasc_chasse.t_personnes tp2 on tp2.nom_personne = pc.auteur_constat
left join oeasc_chasse.t_lieu_tirs tlt on tlt.code_lieu_tir = pc.code_lieu_dit 
left join nomenclature_sexe ns on ns.label_fr = pc.sexe
left join nomenclature_age na on na.label_fr = replace(replace(classe_age, 'Jeune', 'Juvénile'), ' ', '-')
left join nomenclature_mode_chasse nc on nc.label_fr = pc.mode_chasse 
;
