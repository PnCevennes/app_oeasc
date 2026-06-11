# Contexte

Je travaille sur une application Flask/SQLAlchemy/Alembic (app_oeasc) qui utilise 
le schéma `ref_geo` (issu de GeoNature) pour gérer des données géographiques.

Je dois **reconstruire entièrement** les données de la table `ref_geo.l_areas` 
à partir de fichiers GeoPackage externes, car la topologie a changé (fusions, 
scissions, transferts de cadastres entre communes).

# Fichiers sources (GPKG)

```python
GPKG_FILES = {
    'communes':       '/home/thibaut/appli/app_oeasc/data/ref_geo/communes_aoa.gpkg',
    'cadastre':       '/home/thibaut/appli/app_oeasc/data/ref_geo/cadastre_pec.gpkg',
    'foret_dgd':      '/home/thibaut/appli/app_oeasc/data/ref_geo/data_new.gpkg',
    'foret_onf':      '/home/thibaut/appli/app_oeasc/data/ref_geo/forets_gestion_onf_aoa.gpkg',
    'ug_onf':         '/home/thibaut/appli/app_oeasc/data/ref_geo/unites_gestion_foret_publique_aoa.gpkg',
    'parcelle_onf':   '/home/thibaut/appli/app_oeasc/data/ref_geo/parcellaire_foret_publique_aoa.gpkg',
}

# id_type correspondants dans ref_geo.bib_areas_types
ID_TYPES = {
    'communes': 25,
    'cadastre': 332,
    'ug_onf': 330,
    # à compléter : foret_dgd, foret_onf, parcelle_onf, coeur_pnc, aa_pnc, oeasc
}
Modèle cible à remplir
class CorAreaIntersect(CustomModel):
    """ref_geo.cor_area_intersect : table de correspondance spatiale"""
    __tablename__ = "cor_area_intersect"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}

    id = Column(String(25), primary_key=True)
    id_parcelle = Column(Integer)         # parcelle cadastrale (332) ou UG ONF (330)
    id_type_parcelle = Column(Integer)
    id_section_cadastrale = Column(String(25))
    id_commune = Column(String(25))
    id_foret_dgd = Column(Integer)
    id_foret_onf = Column(Integer)
    id_ug_onf = Column(Integer)
    id_secteur = Column(Integer)
    in_coeur = Column(Boolean)
    in_aire_adhesion_pnc = Column(Boolean)
    in_oeasc = Column(Boolean)

    
Tâche
Crée un module Python app/commands/refresh_ref_geo.py exposant une commande 
Flask CLI flask refresh-ref-geo qui réalise les étapes suivantes :
Étape 1 — Préparation

Créer la table ref_geo.l_areas_new via CREATE TABLE LIKE ref_geo.l_areas  INCLUDING ALL
Créer une séquence dédiée pour id_area
Logger le nombre de lignes actuelles de l_areas par id_type

Étape 2 — Chargement des GPKG

Pour chaque GPKG, lire avec geopandas, reprojeter en EPSG:2154
Insérer dans l_areas_new avec les bons id_type, area_code, area_name, 
source
Calculer geom_4326 et centroid après insertion
Créer les index GIST

Étape 3 — Construction de cor_area_intersect

TRUNCATE de la table
Pour chaque entité de type cadastre (332) et UG ONF (330), calculer via PostGIS :
id_commune : commune contenant ST_PointOnSurface(geom)
id_foret_dgd, id_foret_onf : intersection majoritaire
id_ug_onf : UG ONF contenant le centroïde (uniquement pour parcelles ONF)
in_coeur, in_aire_adhesion_pnc, in_oeasc : booléens d'appartenance


Construire id comme '{id_type}_{id_area}'

Étape 4 — Swap des tables

Lister dynamiquement toutes les FK pointant vers ref_geo.l_areas 
(via pg_constraint)
Sauvegarder leur définition (pg_get_constraintdef)
TRUNCATE des tables filles dont les FK pointent vers l_areas (avec confirmation)
DROP des contraintes FK
DROP TABLE l_areas CASCADE
RENAME l_areas_new → l_areas (+ séquence)
Recréer les FK depuis les définitions sauvegardées

Étape 5 — Vérifications post-swap

Comptages par id_type
Détection des géométries invalides (ST_IsValid)
Détection des cadastres sans commune dans cor_area_intersect
Rapport synthétique en sortie console

Contraintes techniques

Tout doit être encapsulé dans une transaction unique (with db.session.begin())
Idempotence : si la commande est relancée, elle doit pouvoir repartir 
proprement (option --force pour bypasser les confirmations)
Logging : utiliser le logger Flask, niveau INFO pour les étapes, DEBUG 
pour le détail SQL
Options CLI :
--dry-run : exécute tout sauf le swap final
--skip-load : reprend à l'étape 3 si l_areas_new existe déjà
--force : pas de confirmation interactive


Gestion d'erreur : en cas d'échec, rollback complet et message clair
Performance : utiliser to_postgis(..., method='multi', chunksize=1000) 
pour les gros GPKG

Structure attendue
app/commands/
├── __init__.py
├── refresh_ref_geo.py        # commande principale
└── refresh_ref_geo_sql/      # requêtes SQL externalisées
    ├── create_l_areas_new.sql
    ├── build_cor_area_intersect.sql
    └── swap_tables.sql
Question préalable
Avant de coder, pose-moi les questions nécessaires pour clarifier :

Les mappings exacts champs GPKG → colonnes l_areas (area_code, area_name) 
pour chaque source
Les id_type manquants dans le dict ID_TYPES
La logique de calcul de id_section_cadastrale (extraction depuis area_code ?)
La logique de id_secteur (qui n'est pas claire pour moi)
Le SRID source de chaque GPKG (si tu peux les inspecter)

Puis propose-moi une architecture détaillée avant d'écrire le code complet.

---

## Conseils d'utilisation

1. **Lancez Claude Code dans le répertoire racine** de votre projet (`app_oeasc`) pour qu'il puisse explorer la structure existante.

2. **Avant le prompt principal**, demandez-lui d'abord :
   Explore la structure du projet, et liste-moi tous les modèles qui ont une 
   ForeignKey vers ref_geo.l_areas. Liste aussi les commandes Flask CLI 
   existantes pour que tu suives le même style.

3. **Adaptez les paths** : modifiez `app/commands/` selon votre arborescence réelle.

4. **Itérez par étape** : si la tâche est trop grosse, dites à Claude Code :
   Implémente uniquement l'étape 1 et 2, puis attends ma validation avant 
   de passer à la suite.

5. **Préparez un GPKG de test** : avant de lancer sur la vraie base, demandez :
   Crée un script pytest qui teste la commande sur une base PostgreSQL/PostGIS 
   éphémère (via testcontainers ou docker) avec des GPKG minimaux générés à 
   la volée.

Voulez-vous que je vous prépare aussi un prompt complémentaire pour la phase de test/validation, ou un script d'inspection préalable des GPKG ?