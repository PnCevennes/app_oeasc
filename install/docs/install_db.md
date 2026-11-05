# Création de la base : `flask init-db`

Prérequis : base PostgreSQL vide, utilisateur et base créés (cf. `install/config_principal.yaml`),
dépendances Python installées.

```bash
cd backend
flask init-db [--skip-views] [--skip-data]
```

Étapes (la commande est relançable, chaque étape ne fait que ce qui manque) :

1. Extensions PostgreSQL (postgis, uuid-ossp, unaccent, intarray, pg_trgm...). Nécessite un superutilisateur.
2. Schémas des dépendances via leurs migrations Alembic : utilisateurs, ref_nomenclatures, ref_geo (SRID local 2154).
3. Tables de l'application créées depuis les **modèles SQLAlchemy** (source de vérité), puis `stamp oeasc@head`.
   Si les tables existent déjà, rien n'est touché : utiliser `flask db upgrade <révision>`.
4. Fonctions, vues et triggers SQL (liste `FICHIERS_SQL` dans `backend/oeasc/commands/init_db.py`).
   Les vues de chasse viennent de `data/oeasc_views/oeasc_chasse_views.sql`, généré depuis la base de production ;
   les anciens `install/data/chasse/*.sql` et `oeasc_in_views.sql` sont périmés et ne sont plus utilisés.
5. Données initiales : nomenclatures OEASC, organismes, application, groupes et administrateur (section `administrateur` du yaml).

Limites connues : les tables temporaires / d'import de la production (`t_import_zi`, `tmp_*`, `oeasc_in.import_data`...)
et les fonctions `oeasc_forets.fct_trg_cor_areas_forets` / `get_id_proprietaire_from_name` ne sont pas recréées.
Les données métier (déclarations, chasse, ref_geo) ne sont pas chargées : voir `flask refresh-ref-geo` et les imports.
