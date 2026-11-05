# Sécurité du frontend — points d'attention

## Tableau générique (`components/table/generic-table.vue`)

Les cellules sont rendues en **texte** par défaut. Une colonne ne peut produire du HTML que si sa
`headerDef` déclare `html: true`; sa fonction `display` doit alors échapper elle-même toute valeur
saisie par un utilisateur avec `escapeHtml()` (`core/js/util/util.js`). Exemple :
`modules/declaration/config/table-declaration.js` (colonnes `id_declaration`, `label_foret`).

## Contenu CMS = code exécutable

Le markdown des pages CMS (`modules/content/content.vue`) est converti par `marked` puis **compilé comme
template Vue** (`vue3-runtime-template`). Un contenu peut donc exécuter n'importe quelle expression JS.
C'est voulu (les pages embarquent des composants), mais cela impose :

- l'édition réservée au droit >= 5, **vérifiée côté backend** : routes génériques `commonsContent`
  (`droits` C/U/D = 5 dans `commons/api.py`) et `POST /api/commons/add_file/<img|doc>` (droit >= 5 depuis 2026-10-29) ;
- de ne pas ajouter DOMPurify sans `ADD_TAGS` (liste des composants de `modules/content/config/components.js`),
  sous peine de casser le CMS ;
- les snippets générés par l'éditeur (`getImg`, `getDoc`) échappent leurs valeurs.

Un compte de droit >= 5 compromis donne une XSS persistante sur toutes les pages : le protéger en conséquence.

## Bundle Vue avec compilateur

`vite.config.js` impose `vue/dist/vue.esm-bundler.js` (compilateur inclus, ~+30 % de Vue) pour le seul
besoin de `vue3-runtime-template`. Compromis assumé.
