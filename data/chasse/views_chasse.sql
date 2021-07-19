-- 
DROP VIEW IF EXISTS oeasc_chasse.v_bilan CASCADE; 
CREATE VIEW oeasc_chasse.v_bilan AS
select 
	id_saison, 
	id_espece, 
	tzc.id_zone_cynegetique, 
	SUM(nb_affecte_min) as nb_affecte_min, 
	SUM(nb_affecte_max) as nb_affecte_max, 
	SUM(nb_realise) as nb_realise,
	SUM(nb_realise_avant_11) as nb_realise_avant_11
from oeasc_chasse.t_bilan_chasse_historique tbch
join oeasc_chasse.t_zone_indicatives tzi on tzi.id_zone_indicative = tbch.id_zone_indicative
join oeasc_chasse.t_zone_cynegetiques tzc on tzc.id_zone_cynegetique = tzi.id_zone_cynegetique
group by 	
    id_saison, 
    id_espece, 
	tzc.id_zone_cynegetique 	
union
select
ta.id_saison,
ttb.id_espece,
tr.id_zone_cynegetique_realisee as id_zone_cynegetique,
tam.nb_affecte_min,
tam.nb_affecte_max,
COUNT(*) as nb_realise,
count(*) filter (where date_exacte <= (CONCAT(SPLIT_PART(ts.nom_saison, '-', 1), '-11-30'))::date) nb_realise_avant_11
from oeasc_chasse.t_realisations tr 
join oeasc_chasse.t_attributions ta on ta.id_attribution = tr.id_attribution 
join oeasc_chasse.t_saisons ts on ts.id_saison = ta.id_saison 
join oeasc_chasse.t_type_bracelets ttb on ttb.id_type_bracelet = ta.id_type_bracelet 
join oeasc_chasse.t_attribution_massifs tam on tam.id_saison = ta.id_saison and tam.id_espece = ttb.id_espece and tr.id_zone_cynegetique_realisee = tam.id_zone_cynegetique 
--where ta.id_saison=3 and ttb.id_espece=1
group by 
	ttb.id_espece,
	tr.id_zone_cynegetique_realisee ,
	ta.id_saison,
	tam.nb_affecte_min,
	tam.nb_affecte_max
order by id_saison, id_espece, id_zone_cynegetique
;


drop view if exists oeasc_chasse.v_bilan_pretty;
create view oeasc_chasse.v_bilan_pretty as
select 
vb.id_saison,
nom_saison,
vb.id_espece,
nom_espece,
code_espece,
vb.id_zone_cynegetique,
nom_zone_cynegetique,
code_zone_cynegetique,
nb_affecte_min,
nb_affecte_max,
nb_realise,
nb_realise_avant_11
from oeasc_chasse.v_bilan vb
join oeasc_chasse.t_saisons ts on ts.id_saison =vb.id_saison
join oeasc_chasse.t_zone_cynegetiques tzc on tzc.id_zone_cynegetique = vb.id_zone_cynegetique
join oeasc_commons.t_especes te on te.id_espece = vb.id_espece
order by nom_saison
;

--select * from oeasc_chasse.v_bilan_pretty
 