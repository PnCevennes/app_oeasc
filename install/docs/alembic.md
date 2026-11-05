# Migrations Alembic

Les migrations sont dans `backend/oeasc/migrations/versions/`. Commandes depuis `backend/`, virtualenv activé :

```bash
flask db heads                  # une tête par branche (voir ci-dessous)
flask db current                # révisions appliquées
flask db history                # arbre complet
flask db upgrade <révision>
flask db downgrade <révision>
```

## ⚠ Plusieurs branches : toujours une révision explicite

La base porte **plusieurs branches Alembic** : celle d'OEASC et celles des dépendances (utilisateurs, nomenclatures,
ref_geo, taxonomie, sql_utils...). Donc `flask db upgrade` / `downgrade` « nus » ou `-1` peuvent toucher une autre
branche (un `downgrade` nu a déjà rétrogradé une branche de dépendance). Toujours :

```bash
flask db upgrade e5b7d3a91c24                 # ou le label : flask db upgrade oeasc@head
flask db downgrade <révision_précédente>
```

## Branches (`flask db heads`)

| Branche | Rôle | Tête |
|---|---|---|
| `oeasc` | schémas `oeasc_*` de l'application | `e5b7d3a91c24` |
| `utilisateurs` | schéma `utilisateurs` (UsersHub) | `b3dec57f13d8` |
| `nomenclatures` | schéma `ref_nomenclatures` | `b820c66d8daa` |
| `ref_geo` + `ref_geo_*` | `ref_geo`, données INPN / communes (inutiles en OEASC, le référentiel est chargé par `flask refresh-ref-geo`) | — |
| `taxonomie`, `taxhub-standalone`, `sql_utils`... | dépendances | — |

`flask db heads` est la référence (les têtes ci-dessus évoluent).

## Branche `oeasc` (ordre d'application)

| Révision | Objet |
|---|---|
| `8857f2169f96` | installation initiale |
| `3fc01cbe83a2`, `f90cb83dcdfb` | suppriment puis restituent les vues en conflit avec la migration utilisateurs `f9d3b95946cd` |
| `437c188c6344`, `0a44db773490` | clés primaires `cor_dgd_cadastre` / `t_communes` (doublons à retirer avant : [correction_doublon_bdd.md](correction_doublon_bdd.md)) |
| `96ebff8bac23` | table hiérarchie des areas |
| `136abe8be18e`, `e70bfbc2094b`, `42abbaaa4dbb` | `auteur_tir` en texte, suppression de `t_personne`, lieu-dit/lat/lon sur `t_realisation` |
| `41042f593f9f`, `d15f8142f4ed` | archivage des déclarations, tags IN |
| `117bec8ed8d2`, `8bf1a1d4e2c7`, `3e5c666af390`, `a1b2c3d4e5f6` | `cor_area_intersect`, garde-fous ref_geo, `t_foret`, `id_foret_prive` (prérequis de `flask refresh-ref-geo`) |
| `bb34c60299a3` | nettoyage **après** `flask refresh-ref-geo` (supprime notamment `t_proprietaires`) |
| `71ace03ca6a3`, `c9d4e8f1a2b3` | superficie `t_zone_indicatives`, simplification de `vm_lareas_simples` |
| `d7a1c3e5f9b2`, `e8b2d4f6a1c3` | schéma `oeasc_agricole`, cultures et unités de gestion ([degats_agricoles.md](degats_agricoles.md)) |
| `f3a9c5e7b1d4` | unité des dagues cm → mm |
| `a7c2e91b4d30` | `t_standards_mesures` ([donnees_aberrantes.md](donnees_aberrantes.md)) |
| `c4e8a1f6d205` | suppression d'index doublons sur `l_areas` |
| `e5b7d3a91c24` | suppression des vues inutilisées |

## Règles de développement

- Toute modification de schéma = modèle SQLAlchemy **et** migration (nom de fichier explicite).
- Tester `upgrade` (et `downgrade` si prévu) sur une copie de base avant de proposer la migration.
- Les migrations `3fc01cbe83a2` et `f90cb83dcdfb` lisent `data/oeasc_views/oeasc_commons_views.sql` : lancer `flask db` depuis le dossier du projet.
- Une base neuve n'utilise pas ces migrations une par une : `flask init-db` crée les tables depuis les modèles
  puis fait `stamp oeasc@head` ([install_db.md](install_db.md)).
