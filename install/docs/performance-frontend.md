# Performance du frontend — décisions et points ouverts

## Fait
- **Cartes Leaflet** : `map_declaration.vue` libère sa carte (`off()` + `remove()`) dans `beforeUnmount` ;
  `restitution-map.vue` ne cumule plus d'écouteurs `layer-data` à chaque `processConfig` et les retire au démontage.
  Les instances `L.map` sont créées avec `markRaw` (pas de proxy réactif profond sur les objets Leaflet).
- **Tri des colonnes** de `store/utils.js` : table de rangs (`Map`) au lieu d'un `indexOf` par comparaison.
- **Vuetify 3** : `generic-table.vue` (`density`, `items-per-page-options`), `size="small"` à la place de `small`,
  couleurs `x-lighten-n` / `x-darken-n`, `<v-tooltip location="…">`.

## Choix assumé : bundle Vue avec compilateur
`vite.config.js` impose `vue/dist/vue.esm-bundler.js` (compilateur inclus, ~+30 % de Vue) pour le seul besoin de
`vue3-runtime-template` (contenu CMS compilé à l'exécution). Voir aussi `securite-frontend.md`.

## Non fait, volontairement
- **`structuredClone` à la place de `JSON.parse(JSON.stringify())`** : `structuredClone` lève une `DataCloneError`
  sur un proxy réactif Vue et sur les fonctions, que le clone JSON ignorait silencieusement. Les 4 usages
  (`restitution.js`, `restitution-settings.vue`, `restitution2/restitution-form.vue`, `util.js#jsoncopy`)
  copient des objets réactifs : à migrer avec `toRaw` et un test réel.
- **Watchers `deep: true`** (≈ 25) : la plupart observent des props de graphiques alimentées par mutation en place ;
  les remplacer sans profilage risque de supprimer des rafraîchissements. À traiter au cas par cas, en mesurant.
- **`setTimeout`** : ceux qui subsistent sont des délais fonctionnels (message avant redirection, 1 s avant
  réaffichage d'un formulaire, 100 ms de synchronisation de formulaires, attente du rendu de cartes), pas de
  simples « attentes du DOM » ; à reprendre avec test visuel.
- **`actualites-bandeau.vue`** charge tout le contenu CMS : un paramètre `limit` côté backend est nécessaire
  (la liste est aussi mise en cache par le store `commonsContent` pour les pages CMS).
