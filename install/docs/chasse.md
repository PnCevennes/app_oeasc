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
| `#/chasse/imports-attributions` | droit >= 6 | import du plan de chasse annuel |

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

`#/chasse/imports-attributions`, droit >= 6. Trois imports CSV **séquentiels**, chacun conditionné par le précédent
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
