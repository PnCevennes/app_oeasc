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
ON CONFLICT DO NOTHING;

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
FROM import_chasse.saison_chasse;

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

-- zone cinegetique

INSERT INTO oeasc_chasse.t_zone_cinegetiques(nom_zone_cinegetique, code_zone_cinegetique)
VALUES
('Aigoual nord', 'AIGO_N'),
('Aigoual sud (Gard)', 'AIGO_S'),
('Causse Méjean', 'CAUS'),
('Mont Lozère est (Gard),', 'MTLO_E_30'),
('Mont Lozère nord, ouest et est (Lozère)', 'MTLO_ONE_48'),
('Mont Lozère sud, Bougès nord', 'MTLO_S'),
('Vallées cévenoles', 'VALC'),
('Zone coeur', 'ZC')
ON CONFLICT DO NOTHING
;

UPDATE oeasc_chasse.t_zone_cinegetiques zc
SET id_secteur=(
SELECT --id_zone_cinegetique, 
s.id_secteur
--, code_zone_cinegetique, code_secteur 
FROM oeasc_chasse.t_zone_cinegetiques zc2
JOIN oeasc_commons.t_secteurs s ON s.code_secteur = SPLIT_PART(zc2.code_zone_cinegetique, '_', 1)
 WHERE zc2.id_zone_cinegetique = zc.id_zone_cinegetique
)
;

-- zone interet

INSERT INTO oeasc_chasse.t_zone_interets (nom_zone_interet, code_zone_interet, id_zone_cinegetique)
SELECT DISTINCT 
	z_i_affectee, z_i_affectee, zc.id_zone_cinegetique
	FROM import_chasse.plan_chasse ipc
	LEFT JOIN oeasc_chasse.t_zone_cinegetiques zc
		ON zc.nom_zone_cinegetique = ipc.massif_affecte
ON CONFLICT DO NOTHING
;
