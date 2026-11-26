# Droits d'accès

Le niveau d'un utilisateur (`max_level_profil` / `id_droit_max`) est le `code_profil` de son groupe
UsersHub pour l'application OEASC. Les niveaux sont **cumulatifs** : un niveau N a aussi les droits
des niveaux inférieurs. Les intitulés des groupes viennent de UsersHub (`GET /api/user/libelles_droits`).

## Constantes (ne pas écrire de niveau en dur)

| Constante | Niveau |
|---|---|
| `VISITEUR` | 0 |
| `CONNECTE` | 1 |
| `ORGANISME` | 2 (le niveau 3 a exactement les mêmes droits) |
| `ADMIN` | 4 (« modérateur ») |
| `ANIMATEUR` | 5 |
| `GESTIONNAIRE` | 6 |

- Backend : `backend/oeasc/modules/oeasc/user/droits.py` (+ `DROITS_ADMIN`, `DROITS_ANIMATEUR`,
  `DROITS_GESTIONNAIRE` pour les dictionnaires C/R/U/D des routes génériques).
- Frontend : `frontend/src/config/droits.js` (`DROITS`), disponible dans les composants via
  `this.$droits` / `$droits` (enregistré dans `main.js`).
- Les deux fichiers sont à garder synchronisés.

## Ce que permet chaque niveau

| Niveau | Droits (en plus des niveaux inférieurs) |
|---|---|
| 0 visiteur | Tout « Résultats des suivis » et `#/chasse/bilan` (« Bilan données chasse ») : pages et API publiques. Lecture des référentiels chasse. **Aucune déclaration** (pas d'accès à « Alertes signalées »). |
| 1 connecté | Voir **ses** alertes, en créer, modifier celles non périmées, **renouveler ou clôturer** les périmées (une périmée ne peut être modifiée que par un admin, backend et frontend), export de la liste, espace utilisateur, restitution, liste des utilisateurs. |
| 2 et 3 | Mêmes droits : voir, **modifier** (non périmées), **renouveler/clôturer** les déclarations de **son organisme** (sauf « Autre (préciser) », « Pas d'organisme », « Aucun » : limité aux siennes). |
| 4 modérateur | Supprimer / valider une déclaration ; modifier une déclaration expirée ; voir les infos du propriétaire d'une déclaration d'autrui ; modifier un utilisateur (e-mail, droit) **de droit strictement inférieur**. Chasse : consultation des données (`#/chasse/admin`, tables en lecture seule : boutons de modification masqués, via `droitModification` des configStore), export, correction des données aberrantes. Indices nocturnes : consultation et modification (`#/in/admin`, validation des réalisations, référentiels IN). |
| 5 animateur | **Tous les droits sauf ceux du niveau 6** (voir ci-dessous) : toutes les déclarations (choix du déclarant, validation directe), tous les utilisateurs, contenus éditoriaux et téléversement de fichiers, relances automatiques, dégâts agricoles (import et données). Chasse : saisie, import des réalisations, import du plan de chasse annuel, création/modification/suppression des données chasse. Consultation seule des zones cynégétiques/indicatives et des référentiels « commons » (secteurs, espèces, nomenclatures). |
| 6 gestionnaire | **Tous les droits**, dont ce qui lui est propre : modification des zones cynégétiques/indicatives et des référentiels « commons » (secteurs, espèces, communes, nomenclatures). Il peut modifier **n'importe quel utilisateur**, y compris un autre gestionnaire, et attribuer tous les niveaux jusqu'à 6 (`peut_gerer_utilisateur`, `droits.py` / `peutGererUtilisateur`, `droits.js`). |

## Où les droits sont appliqués

1. **Backend (source de vérité)** : `@check_auth_redirect_login(NIVEAU)` sur les routes ; clé `droits`
   (C/R/U/D) des définitions de routes génériques (`generic/decorator.py`) ; filtres de visibilité des
   déclarations (`get_filtres_droits_declarations`, `declaration/repository.py`).
2. **Frontend (confort, pas de sécurité)** : `access` des routes (garde de redirection, `router/guards.js`),
   `hidden` des entrées de menu, `v-if` sur `$store.getters.droitMax`.
3. **Changement de droit d'un utilisateur** : la route de la librairie `register/post_usershub/change_application_right` est contrôlée par `controle_changement_droit` (`user/api.py`, `before_request`) : cible de droit strictement inférieur et niveau attribué strictement inférieur, sauf niveau 6.
