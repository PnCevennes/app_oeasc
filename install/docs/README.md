# Documentation OEASC

Toute la documentation technique et fonctionnelle est ici (`install/docs/`). La règle du projet est de la mettre à jour
en même temps que le code. Pour la structure générale, la stack et les conventions : `.claude/CLAUDE.md`. Pour les
dossiers de données : `data/README.md`.

## Installation et exploitation

| Document | Contenu |
|---|---|
| [Mise_en_production.md](Mise_en_production.md) | installation, reprise de base, proxy de tuiles, commandes de maintenance |
| [configuration.md](configuration.md) | `install/config_principal.yaml` et qui le lit |
| [install_db.md](install_db.md) | création de la base : `flask init-db` |
| [alembic.md](alembic.md) | migrations, branches, ordre des révisions `oeasc` |
| [mise_a_jour_ref_geo.md](mise_a_jour_ref_geo.md) | `flask refresh-ref-geo` |
| [correction_doublon_bdd.md](correction_doublon_bdd.md) | nettoyage des doublons de l'ancienne base |

## Fonctionnel

| Document | Contenu |
|---|---|
| [chasse.md](chasse.md) | pages, imports (Géochasse, attributions) et exports chasse |
| [donnees_aberrantes.md](donnees_aberrantes.md) | contrôle des poids et dagues |
| [degats_agricoles.md](degats_agricoles.md) | dégâts agricoles : modèle, import, administration, restitution |
| [in.md](in.md) | indices nocturnes |
| [content.md](content.md) | gestion des contenus (CMS), actualités |
| [cartes.md](cartes.md) | fonds de carte, proxy de tuiles |

## Frontend

| Document | Contenu |
|---|---|
| [Configuration_des_stores.md](Configuration_des_stores.md) | stores Vuex générés par `addStore` |
| [formulaires/formulaires.md](formulaires/formulaires.md) | `generic-form`, `dynamic-form-group`, `dynamic-form` |
| [securite-frontend.md](securite-frontend.md) | points d'attention (XSS, CMS exécutable) |
| [performance-frontend.md](performance-frontend.md) | décisions et points ouverts |

## Notes de travail

[todo-components-table.md](todo-components-table.md), [todo-restitution2.md](todo-restitution2.md),
[changelog.md](changelog.md) (historique 2022, archivé).
