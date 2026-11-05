# Mise à jour du référentiel géographique (`flask refresh-ref-geo`)

Reconstruit entièrement `ref_geo.l_areas` (et les tables dérivées) depuis des fichiers GeoPackage.
Code : `backend/oeasc/commands/refresh_ref_geo.py`. Contexte et nature des fichiers : `data/README.md`.

1. Appliquer la migration `a1b2c3d4e5f6` (`flask db upgrade a1b2c3d4e5f6`, la commande exige cette révision).
2. Placer les fichiers dans `data/ref_geo/`, avec exactement ces noms :

   ```
   cadastres.gpkg
   communes_aoa.gpkg
   forets_dgd.gpkg
   forets_gestion_onf_aoa.gpkg
   parcelles_forets_onf_new.gpkg
   unites_gestion_forets_onf.gpkg
   ```

3. Lancer depuis `backend/` :

   ```bash
   flask refresh-ref-geo --dry-run   # construit les tables *_new sans toucher aux tables vivantes
   flask refresh-ref-geo --force     # exécution réelle sans confirmation interactive
   ```

   Autre option : `--skip-load` (réutilise `l_areas_new` si elle existe déjà).

4. Si tout est correct, appliquer la migration de nettoyage `bb34c60299a3` (`flask db upgrade bb34c60299a3`).

Toujours cibler une révision explicite pour les migrations : voir [alembic.md](alembic.md).
