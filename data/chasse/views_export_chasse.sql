DROP VIEW IF EXISTS oeasc_chasse.v_export_realisation CASCADE;
CREATE VIEW oeasc_chasse.v_export_realisation AS (
SELECT
	ta.numero_bracelet,
	ttb.code_type_bracelet,
	te.nom_espece,
	te.code_espece,
	te.cd_nom,
	ts.nom_saison,
	tsec.nom_secteur,
	tsec.code_secteur,
	tzcr.nom_zone_cynegetique AS nom_zone_cynegetique_realisee,
	tzcr.code_zone_cynegetique AS code_zone_cynegetique_realisee,
	tzir.nom_zone_indicative  AS nom_zone_indicative_realisee,
	tzir.code_zone_indicative  AS code_zone_indicative_realisee,
	tzca.nom_zone_cynegetique AS nom_zone_cynegetique_attribuee,
	tzca.code_zone_cynegetique AS code_zone_cynegetique_attribuee,
	tzia.nom_zone_indicative  AS nom_zone_indicative_attribuee,
	tzia.code_zone_indicative  AS code_zone_indicative_attribuee,
	tr.date_exacte,
	tr.date_enreg,
	tr.mortalite_hors_pc,
	tns.label_fr AS sexe,
	tnmc.label_fr AS mode_chasse,
	tnca.label_fr AS classe_age,
	tr.poid_entier,
	tr.poid_vide,
	tr.poid_c_f_p,
	tr.long_dagues_droite,
	tr.long_dagues_gauche,
	tr.long_mandibules_droite,
	tr.long_mandibules_gauche,
	tr.cors_nb,
	tr.cors_commentaires,
	tr.gestation,
	tr.commentaire,
	tr.parcelle_onf,
	tr.poid_indique,
	tr.cors_indetermine,
	tr.long_mandibule_indetermine
	FROM oeasc_chasse.t_realisations tr
	LEFT JOIN oeasc_chasse.t_attributions ta  ON ta.id_attribution = tr.id_attribution
	LEFT JOIN oeasc_chasse.t_zone_cynegetiques tzcr ON tzcr.id_zone_cynegetique = tr.id_zone_cynegetique_realisee
	LEFT JOIN oeasc_chasse.t_zone_indicatives tzir ON tzir.id_zone_indicative = tr.id_zone_indicative_realisee
	LEFT JOIN oeasc_commons.t_secteurs tsec ON tsec.id_secteur = tzcr.id_secteur
	LEFT JOIN oeasc_chasse.t_lieu_tir_synonymes tlts ON tlts.id_lieu_tir_synonyme = tr.id_lieu_tir_synonyme
	LEFT JOIN oeasc_chasse.t_lieu_tirs tlt ON tlt.id_lieu_tir =tlts.id_lieu_tir
	LEFT JOIN oeasc_chasse.t_personnes tpat ON tpat.id_personne = tr.id_auteur_tir
	LEFT JOIN oeasc_chasse.t_personnes tpac ON tpac.id_personne = tr.id_auteur_constat
	LEFT JOIN oeasc_chasse.t_saisons ts ON ts.id_saison = ta.id_saison
	LEFT JOIN oeasc_chasse.t_zone_cynegetiques tzca ON tzca.id_zone_cynegetique = ta.id_zone_cynegetique_affectee
	LEFT JOIN oeasc_chasse.t_zone_indicatives tzia ON tzia.id_zone_indicative = ta.id_zone_indicative_affectee
	LEFT JOIN oeasc_chasse.t_type_bracelets ttb ON ttb.id_type_bracelet = ta.id_type_bracelet
	LEFT JOIN oeasc_commons.t_especes te ON te.id_espece = ttb.id_espece
	LEFT JOIN ref_nomenclatures.t_nomenclatures tns ON tns.id_nomenclature = tr.id_nomenclature_sexe
	LEFT JOIN ref_nomenclatures.t_nomenclatures tnca ON tnca.id_nomenclature = tr.id_nomenclature_classe_age
	LEFT JOIN ref_nomenclatures.t_nomenclatures tnmc ON tnmc.id_nomenclature = tr.id_nomenclature_mode_chasse
);

DROP VIEW IF EXISTS oeasc_chasse.v_export_realisation_csv CASCADE;
CREATE VIEW oeasc_chasse.v_export_realisation_csv AS (
	SELECT * FROM oeasc_chasse.v_export_realisation
);
