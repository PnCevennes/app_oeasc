## 0.0.1 2022-11-23
* correction de la prise en compte des droits de l'utilisateur pour savoir quelles déclarations lui sont accessibles

## 0.0.1 2022-10-12
 * Ajout de la possibilité de mettre des séparations dans les menus (`'-'`)
 * Ouverture de l'accès aux pages de restitution
## 0.0.1 2022-08-30
 * Integration de sentry : Ajout d'un paramètre de configuration `SENTRY_DSN`
 * Prenettoyage de requirements.txt

**migration**
 * Mettre a jour le virtualenv: `pip install -r requirements.txt`
 * Voir le supprimer et le recréer `rm -r venv; python3 -m venv venv` avant l'installation des paquets

## 0.0.1 2022-08-29
 * Possibilité de paramétrer les champs du filtre chasse :
   * configFormContentChasse(['id_saison', 'id_espece', 'id_secteur', 'id_zone_cynegetique', 'id_zone_indicative'])
 * Renommage de la page `page_type` en `restitution_bilan_detaille`
 * Configuration des listes de valeurs des selects (list-form)

```js
  displayFieldName: "nom_saison", // Champ affichage
  displayFieldValue: "id_saison", // Champ stockage
  displayFieldSortDesc: true, // Sens d'ordonancement
```

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
