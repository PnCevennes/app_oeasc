# Chasse : pages, imports et exports

Données du plan de chasse et des réalisations (schéma `oeasc_chasse`). Code : `backend/oeasc/modules/oeasc/chasse/`
(API `api.py`), `frontend/src/modules/chasse/`. Les tables de référence (saisons, zones cynégétiques, types de
bracelet, lieux de tir et synonymes, attributions, standards de mesures...) sont éditables par les routes
génériques (droit >= 4 pour créer / modifier / supprimer, lecture libre) ; configuration dans `modules/chasse/config/store-*.js`
([Configuration_des_stores.md](Configuration_des_stores.md)).

## Pages

| Page | Accès | Rôle |
|---|---|---|
| `#/chasse/restitution_bilan_detaille` | public | analyse détaillée (graphiques) |
| `#/chasse/restitution_gd_public`, `#/chasse/restitution_indices_performances` | public | pages de contenu CMS ([content.md](content.md)) |
| `#/chasse/bilan` | | bilan des données de chasse |
| `#/chasse/imports` | droit >= 4 | import des réalisations (CSV Géochasse) |
| `#/chasse/export` | droit >= 4 | exports |
| `#/chasse/donnees-aberrantes` | droit >= 4 | contrôle et correction des poids / dagues : [donnees_aberrantes.md](donnees_aberrantes.md) |
| `#/chasse/imports-attributions` | droit >= 5 | import du plan de chasse annuel |

## Imports (asynchrones)

Les trois types d'import (réalisations, plan de chasse, dégâts agricoles) partagent le même mécanisme
(`chasse/import_async.py`) : le fichier est enregistré, un fichier de suivi JSON est créé et le traitement s'exécute dans un thread.
La réponse (202) donne un `id_import` ; le frontend interroge `GET /api/chasse/import/status/<id_import>`
(polling). Les imports sont aussi tracés dans la table `t_imports_chasse`.

### Réalisations (CSV Géochasse)

`POST /api/chasse/import/traitement-csv` (droit >= 4) : paramètres `saison`, `update` (`true` = met à jour les
réalisations existantes) et `file`. Traitement : `importation_csv.py` (nettoyage du CSV exporté par Géochasse, colonnes
décalées ou inutiles ignorées). Les erreurs sont téléchargeables via `GET import/download-erreurs-csv/<fichier>`.
Les bilans CSV de synonymes de lieux de tir sont écrits dans `data/archives_lieux_dits/` (voir `data/README.md`).

### Plan de chasse annuel (attributions)

`#/chasse/imports-attributions`, droit >= 5. Trois imports CSV **séquentiels**, chacun conditionné par le précédent
(`GET import-attributions/etat` pilote le déverrouillage des étapes) :

1. `saison-dates` → `oeasc_chasse.t_saison_dates`
2. `massifs` → `oeasc_chasse.t_attribution_massifs`
3. `attributions` → `oeasc_chasse.t_attributions`

`POST /api/chasse/import-attributions/<etape>` ; la saison visée est **la saison courante** (`current`). Si plusieurs
saisons sont marquées « en cours », tout import est refusé. Ces imports remplacent les anciens scripts SQL manuels.

## Exports

- `GET /api/chasse/export/csv` : réalisations en CSV (paramètres `id_saison_debut`, `id_saison_fin`...) ;
- `GET /api/chasse/export/ods` : bilan de chasse d'une saison, généré depuis le modèle
  `backend/oeasc/templates/ods/template_bilan_chasse.ods`.

## Vues SQL

Les fonctions et vues de `oeasc_chasse` (dont `fct_poid_vide`, `fct_custom_results_t`) viennent de
`data/oeasc_views/oeasc_chasse_views.sql`, exécuté par `flask init-db` ([install_db.md](install_db.md)).

## Page « Gestion des lieux de tirs » (Administration → Chasse)

Route `/chasse/lieux-tir` (`chasse.lieux_tir`, droit ≥ 5), visualisation cartographique des lieux de tir (`oeasc_chasse.t_lieu_tirs`).

- Liste des lieux avec case à cocher (décochée par défaut) : un lieu coché s'affiche sur la carte ; cliquer sur son nom le coche et ouvre son encart.
- Filtres : commune, zone cynégétique, zone indicative (la liste des ZI suit la ZC choisie) et recherche texte (nom, code, synonymes). Le contour de chaque filtre actif est tracé sur la carte (commune en bleu, ZI en rouge, ZC en noir).
- Clic sur un lieu de la carte : encart avec nom, code, commune, ZI, ZC et liste des synonymes.

API (`chasse/lieux_tir.py`, routes dans `chasse/api.py`, droit ANIMATEUR) :
- `GET /api/chasse/lieux-tir/carte` : lieux en GeoJSON WGS84 (avec zones et synonymes) + listes des filtres ;
- `GET /api/chasse/lieux-tir/contour?type=commune|zone_indicative|zone_cynegetique&id=…` : contour simplifié (la ZC est l'union de ses ZI, elle n'a pas de géométrie propre).

Les géométries sont stockées en Lambert-93 (EPSG:2154) bien que typées 4326 dans les modèles : la reprojection est faite en SQL. La commune d'un lieu est déterminée par sa position (`ST_Intersects` avec les communes `ref_geo.l_areas`, type 327) : `t_lieu_tirs.id_area_commune` est incohérent avec la géométrie et `label_commune` (ex. « la quille », Hures-la-Parade, pointe vers Saint-Privat-de-Vallongue) ; il n'est pas utilisé par la page. La zone cynégétique d'un lieu est `t_lieu_tirs.id_zone_cynegetique`, à défaut celle de sa zone indicative.

### Modification et suppression des lieux de tir

- Chaque ligne de la liste a une icône crayon (modifier) et une icône poubelle (supprimer).
- **Suppression** : modale de confirmation ; supprime le lieu **et ses synonymes**. Les réalisations rattachées ne sont pas supprimées : leur `id_lieu_tir_synonyme` passe à NULL (`lieu_tir_txt` conservé).
- **Modification** : la colonne de gauche est remplacée par un formulaire (nom, code, synonymes). Sur la carte, seuls les points du lieu sont affichés : clic = ajouter un point, glisser = déplacer, clic droit ou double-clic sur un point = supprimer (au moins 1 point requis). Les synonymes retirés sont supprimés (le lien des réalisations concernées passe à NULL).
- API (droit ANIMATEUR) : `PATCH /api/chasse/lieux-tir/<id>` (`nom_lieu_tir`, `code_lieu_tir`, `id_zone_indicative`, `synonymes`, `geometry` MultiPoint WGS84, reprojeté en 2154 en SQL) et `DELETE /api/chasse/lieux-tir/<id>`.
- La commune et la zone cynégétique affichées sont déduites de la position / de la zone indicative : elles se mettent à jour après enregistrement.
- **Commune et zones automatiques** : à chaque modification des points, `POST /api/chasse/lieux-tir/zones` calcule la commune, la zone indicative et la zone cynégétique, affichées dans le formulaire et leurs contours tracés sur la carte (commune bleu, ZI rouge, ZC noir). À l'enregistrement, `id_area_commune`, `label_commune`, `id_zone_indicative` et `id_zone_cynegetique` sont réécrits avec ce calcul (`calculer_zones`, `lieux_tir.py`). En cas de chevauchement, on retient la zone qui contient le plus de points, puis celle dont l'intersection avec l'enveloppe du lieu (zone tampon de 100 m autour des points) est la plus grande. La ZC est celle de la ZI retenue ; sans ZI, la ZC la mieux placée.
