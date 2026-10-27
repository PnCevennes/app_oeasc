# data/

Données utilisées par l'application une fois installée. Les données qui ne servent qu'à l'installation (CSV de nomenclatures, shapefiles des limites du parc, schémas SQL, etc.) sont dans `install/data/`.

La plupart des fichiers volumineux (`*.gpkg`, `*.csv`, `cache/`, `degat_agricoles/*`) sont ignorés par git : ils sont à copier à la main sur chaque machine.

| Dossier | Fonction |
|---|---|
| `ref_geo/` | Fichiers GeoPackage (`*.gpkg`) de référence géographique : cadastres, communes de l'AOA, forêts DGD, forêts de gestion ONF, parcelles et unités de gestion ONF. Lus par la commande `flask refresh-ref-geo` (`backend/oeasc/commands/refresh_ref_geo.py`) pour reconstruire `ref_geo.l_areas`. Noms attendus : `cadastres`, `communes_aoa`, `forets_dgd`, `forets_gestion_onf_aoa`, `parcelles_forets_onf_new`, `unites_gestion_forets_onf`. Procédure : `install/docs/mise_a_jour_ref_geo.md`. |
| `oeasc_views/` | Vues SQL (`oeasc_commons_views.sql`, `oeasc_declarations_views.sql`, `oeasc_resultats_views.sql`). Lues par des migrations Alembic qui suppriment et recréent les vues, et par `init_views.sh`, qui les recrée en même temps que celles de `install/data/chasse/` et `install/data/in/`. |
| `cache/` | Cache disque généré au runtime : tuiles du fond IGN Plan IGN v2 (`cache/tile/`), servies par le backend avec une validité de 7 jours. Peut être vidé sans risque. |
| `degat_agricoles/` | Fichiers sources de l'import des dégâts agricoles : `degats_lozere.xls` (indemnisations) et `table_cultures.xlsx` (correspondance culture -> type, reprise dans la migration `e8b2d4f6a1c3`). |
| `archives_lieux_dits/` | Bilans CSV des synonymes de lieux de tir trouvés à chaque import Géochasse (écrits par `importation_csv.py`). Conservés pour un futur système de localisation des tirs (voir `c_est_quoi_ce_dossier.md`). |
