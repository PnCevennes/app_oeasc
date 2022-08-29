
## 0.0.1 2022-08-29
 * Possibilité de paramétrer les champs du filtre chasse :
   * configFormContentChasse(['id_saison', 'id_espece', 'id_secteur', 'id_zone_cynegetique', 'id_zone_indicative'])
 * Renommage de la page `page_type` en `restitution_bilan_detaille`

** migration **
 * Remplacer `configFormContentChasse` par `configFormContentChasse()` dans les pages de type content

```sql
UPDATE oeasc_commons.t_contents AS tc SET md = REPLACE(md, '$store.getters.configFormContentChasse', '$store.getters.configFormContentChasse()')
WHERE md ILIKE '%$store.getters.configFormContentChasse%'
```

## 0.0.1 2022-08-26
 * Centralisation de la configuration des menus
 * Refonte gestion du graphique => Bilan du plan de chasse

** migration **
 * Créer la vue oeasc_chasse.v_plan_chasse_realisation_bilan `data/upgrade/update_bilan_chasse.sql`
