-- corrections des dates

UPDATE import_chasse.plan_chasse SET date_exacte='2016-12-06' WHERE no_bracelet='CEFF 4870' and fk_saison=4;
UPDATE import_chasse.plan_chasse SET date_exacte='2019-12-26' WHERE no_bracelet='CEFF 5315' and fk_saison=7;




-- voir les doublons

with saison_dates as(
	select 
		id_saison,
        nom_saison,
		TO_DATE(SPLIT_PART(nom_saison, '-', 1) || '0701', 'YYYYMMDD') as date_debut, 
		TO_DATE(SPLIT_PART(nom_saison, '-', 2) || '0601', 'YYYYMMDD') as date_fin 
		from oeasc_chasse.t_saisons ts 
)
select id_saison, nom_saison, no_bracelet, count(*), array_agg(massif_realise), array_agg(date_exacte), array_agg(id) as ids
	from import_chasse.plan_chasse pc 
	left join oeasc_commons.t_especes te on te.nom_espece = split_part(pc.nom_vern, ' ', 1) 
	left join oeasc_chasse.t_type_bracelet ttb on ttb.id_espece = te.id_espece 
	left join oeasc_chasse.t_zone_cynegetiques tzc 
		on 	regexp_replace(tzc.nom_zone_cynegetique, ',? \(.*\),?', '') = 
	   		regexp_replace(pc.massif_affecte, ',? \(.*\),?', '')
	left join oeasc_chasse.t_zone_interets tzi on tzi.code_zone_interet = pc.z_i_affectee 
	left join saison_dates s on date_exacte > s.date_debut and date_exacte < s.date_fin
	WHERE massif_realise IS NOT NULL
group by id_saison, no_bracelet, nom_saison
having count(*)>1
;
