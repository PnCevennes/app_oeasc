# Dégâts agricoles

Données d'indemnisation des dégâts agricoles de grand gibier (tableur fourni par la FDC), stockées dans le schéma `oeasc_agricole`.

## Modélisation

Schéma créé par la migration `d7a1c3e5f9b2_create_schema_oeasc_agricole`, complété par `e8b2d4f6a1c3_add_t_cultures_and_t_ug_agricole`.

| Table | Contenu |
| --- | --- |
| `t_saison_agricole` | Saisons (« campagnes comptables ») : `nom_saison` (ex. `2016-2017`), `date_debut` (1er juillet), `date_fin` (30 juin), `current` |
| `t_type_culture` | Catégories de cultures : `id_type_culture`, `nom_type_culture` (CEREALES, FRUITS ET LEGUMES, PRAIRIES, MÉLANGE) |
| `t_cultures` | Cultures telles que nommées dans le fichier importé : `id_culture`, `nom_culture`, `id_type_culture` (ex. PRAIRIES TEMPORAIRES → PRAIRIES) |
| `t_ug_agricole` | Unités de gestion agricoles (colonne « Secteur » du fichier) : `id_ug_agricole`, `nom_ug_agricole` (ex. `09 / MONT LOZERE`), `in_oeasc` |
| `t_declaration_agricole` | Une ligne par déclaration de dégât : saison, n° de dossier, dates, unité de gestion, commune, culture, espèce, surfaces, volume, montants |

- Un **dossier** est identifié par son numéro et regroupe plusieurs déclarations ; des lignes identiques dans un même dossier sont normales.
- La correspondance culture → type de culture vient de `data/degat_agricoles/table_cultures.xlsx` ; elle est chargée par la migration `e8b2d4f6a1c3` et se modifie ensuite dans l'onglet `Cultures` de la page d'administration. « BLE BARBUT DU ROUSSILLON », présente dans le fichier importé mais absente de ce tableur, est rattachée à CEREALES par la migration. Une culture créée ensuite par un import a un `id_type_culture` vide.
- Jusqu'à la migration `e8b2d4f6a1c3`, les cultures étaient enregistrées par erreur dans `t_type_culture` : cette table a été renommée `t_cultures` (id conservés).
- `in_oeasc` : les unités de gestion `06 / GARDILLE/CHASSEZAC` et `07 / SAUVETERRE` ne font pas partie de l'OEASC (faux), même si quelques-unes de leurs déclarations portent sur des communes de l'OEASC ; `08 / MEJEAN`, `09 / MONT LOZERE`, `10 / AIGOUAL` et `11 / CEVENNES` en font partie (vrai).
- `id_ug_agricole` est vide sur les déclarations importées avant l'ajout du champ : réimporter le fichier avec « Mettre à jour les données existantes » pour le renseigner.
- `id_espece` référence `oeasc_commons.t_especes`.
- `id_commune` référence `ref_geo.communes_aoa.id`, **sans contrainte de clé étrangère** : `flask refresh-ref-geo` vide puis recharge cette table, ce qu'une contrainte empêcherait.
- `current` vaut `true` uniquement sur la saison la plus récente ; il est recalculé à chaque import.

## Import

Page `#/degats_agricoles/imports` (menu `Administration` → `Importation dégâts agricoles`), droit >= 5.

Formats acceptés : `.csv` (séparateur `;`, `,` ou tabulation, UTF-8 ou Windows-1252), `.xls`, `.ods`. Un fichier modèle se trouve dans `data/degat_agricoles/`.

### Colonnes attendues

Campagnes comptables, Date de création, N° dossier, Date document, Secteur (facultative), Code insee, Culture, Surface détruite (ha), Volume détruit (qtx), Unité de la quantité détruite expertisé, Pourcentage, Espèce, Montant payé PR (€), Surface RESSEMIS (ha), Montant payé RESSEMIS (€), Montant total payé (€).

La colonne « Commune du dossier » est ignorée (la commune est retrouvée par son code INSEE). Si la colonne « Secteur » est absente, les déclarations sont importées sans unité de gestion (avertissement dans le journal).

Les entêtes sont comparées sans tenir compte de la casse, des accents ni de la ponctuation. Une entête légèrement différente est rapprochée du nom attendu le plus proche (RapidFuzz, ressemblance >= 85 %) ; chaque rapprochement est signalé dans le journal. Si une colonne reste introuvable ou ambiguë, l'import est refusé.

### Règles

- La saison vient de la colonne « Campagnes comptables » (format `AAAA-AAAA`). Une saison absente de la base est créée (1er juillet → 30 juin).
- Une culture absente de la base est créée dans `t_cultures` avec le libellé du fichier, sans type de culture (avertissement dans le journal : le type est à renseigner dans la page d'administration).
- Une unité de gestion (colonne « Secteur ») absente de la base est créée dans `t_ug_agricole` avec `in_oeasc` à faux (avertissement dans le journal : à corriger au besoin dans la page d'administration).
- L'espèce doit exister dans `t_especes` ; « cervidé » est rattaché à **Cerf**.
- Le code INSEE doit correspondre à une commune de `ref_geo.communes_aoa`.
- **Tout ou rien** : la moindre ligne invalide (saison, code INSEE, espèce, date ou nombre) annule l'import ; les lignes en cause sont listées dans le journal.
- Case « Mettre à jour les données existantes » :
  - décochée : les dossiers déjà en base sont ignorés, seuls les nouveaux dossiers sont ajoutés ;
  - cochée : toutes les déclarations dont le numéro de dossier figure dans le fichier sont supprimées (quelle que soit leur saison en base), puis remplacées par celles du fichier. Après l'import, ces dossiers ne contiennent donc que les lignes du fichier. Les dossiers absents du fichier ne sont jamais modifiés.

- Avant chaque insertion, la numérotation de `id_declaration` repart juste après le plus grand id encore présent : un import avec mise à jour ne fait donc pas grimper les id (les id libérés par les dossiers supprimés sont réutilisés s'ils étaient en fin de numérotation).

### Fonctionnement technique

- Route `POST api/agricole/import` : enregistre le fichier et lance le traitement dans un thread (mécanisme de suivi partagé avec les imports chasse, `chasse/import_async.py`, type `degats_agricoles`). Avancement via `GET api/agricole/import/status/<id_import>`.
- Traitement : `backend/oeasc/modules/oeasc/agricole/importation.py` (`traitement_import_degats_agricoles`).
- Dépendances de lecture : `xlrd` (xls) et `odfpy` (ods).

## Administration

Page `#/degats_agricoles/admin` (menu `Administration` → `Données dégâts agricoles`), droit >= 5.

Cinq onglets (tableaux génériques avec filtre par colonne, modification et suppression) : `Déclaration dégâts`, `Saisons`, `Cultures`, `Types de culture`, `Unités de gestion`. Les routes sont celles du module générique : `api/generic/agricole/declaration`, `saison`, `culture`, `type_culture`, `ug_agricole`, et `commune` en lecture seule.

## Restitution publique

Page `#/degats_agricoles/restitution_gd_public` (menu `Résultats des suivis` → `Dégâts agricoles`), accessible sans connexion. Composant : `frontend/src/modules/degats_agricoles/page-degats-agricoles.vue`.

Contenu :

- cinq graphiques en barres avec la saison en abscisse : montant total indemnisé, nombre de déclarations, nombre de dossiers, surface détruite et surface remise en état (ressemis), surface détruite cumulée ;
- un camembert des types de culture touchés pour une saison, au choix en nombre de déclarations, surface détruite ou montant indemnisé (en affichage par culture, les parts de moins de 2 % sont regroupées dans « Autres cultures » ; les types de culture sont toujours affichés séparément, du moins au plus important à partir du haut dans le sens horaire, sauf le plus petit — MÉLANGE — placé en dernier : son libellé s'affiche ainsi en haut à gauche, du côté opposé aux autres). Deux cases à droite du champ de saison : « Cumuler toutes les saisons » (désactive le champ de saison et affiche le cumul de toutes les saisons) et « Afficher par culture » (détail par culture de `t_cultures` au lieu des types de `t_type_culture`). Une part garde la même couleur d'une saison et d'une mesure à l'autre ;
- une carte des communes pour une saison : couleur selon la surface détruite (noir : plus de 10 ha, rouge : 5 à 10 ha, orange : 1 à 5 ha, vert : moins de 1 ha, blanc : 0 ha), infobulle avec le total indemnisé et le nombre de dossiers. En cumul, les seuils sont les quartiles des surfaces cumulées des communes touchées (hors communes à 0 ha), recalculés à chaque affichage et arrondis au dixième d'hectare : environ un quart des communes touchées par classe. La case « Toutes les années cumulées », à droite du champ de saison, désactive ce champ et affiche le cumul de toutes les saisons (surface détruite, total indemnisé, nombre de dossiers).

La saison du camembert et celle de la carte se choisissent séparément avec un champ numérique sur l'année de début de la saison (2024 pour 2024-2025).

**Surfaces** : seules les déclarations dont l'unité est `ha` sont comptées dans les surfaces. Les déclarations évaluées en nombre de plants ou en kilogrammes (colonne « Unité de la quantité détruite expertisé ») portent dans la colonne « surface » une valeur qui n'est pas en hectares ; elles restent comptées dans les montants, les déclarations et les dossiers.

Routes (publiques, zone OEASC), requêtes dans `backend/oeasc/modules/oeasc/agricole/repository.py` :

- `GET api/agricole/results/saisons` : indicateurs par saison ;
- `GET api/agricole/results/cultures?id_saison=` : indicateurs par culture, avec le `nom_type_culture` de chacune (le regroupement par type est fait côté frontend). Avec `?toutes_saisons=true`, cumul de toutes les saisons ;
- `GET api/agricole/results/communes?id_saison=` : GeoJSON des communes de `ref_geo.communes_aoa` (géométries simplifiées, WGS84) avec les indicateurs de la saison. Avec `?toutes_saisons=true` (sans `id_saison`), les indicateurs sont cumulés sur toutes les saisons.

L'ancien contenu CMS `degats_agricoles_restitution_gd_public` (« page en cours de construction ») n'est plus utilisé.
