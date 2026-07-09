<!--
  Composant VueJS d'administration affichant une interface avec des onglets dynamiques.
  - Affiche le titre de la page d'administration à partir de la configuration.
  - Utilise des onglets (v-tabs) pour naviguer entre différentes sections configurées dans `config.tabs`.
  - Chaque onglet affiche le label défini dans la configuration et, si disponible, le nombre d'éléments correspondant.
  - Pour chaque onglet, le contenu est affiché dans `v-tabs-items` :
    - Si le type de l'onglet est "generic-table" ou non défini, et que la configuration du store existe, affiche le composant `generic-table` avec la configuration appropriée.
    - Si le type de l'onglet est "in-table", affiche le composant `in-table` (utilisé pour les indices nocturnes).
  - La gestion des onglets et du contenu est entièrement dynamique, basée sur la configuration passée au composant.
-->

<template>
  <div style="width: 100%">
    <h1>{{ config.title }} - Page d'administation</h1>
    <v-tabs
      v-model="tab"
      fixed
    >
      <v-tab
        v-for="[key, tab] of Object.entries(config.tabs)"
        :key="key"
      >
        {{ tab.labels }} {{ nbElems[key] ? `(${nbElems[key]})` : '' }}
      </v-tab>
    </v-tabs>

    <v-window v-model="tab">
      <v-window-item
        v-for="[key, tab] of Object.entries(config.tabs)"
        :key="key"
      >
        <generic-table
          v-if="['generic-table', undefined].includes(tab.type) && configStores[key]"
          :config="configStores[key].configTable"
          :key="key"
        ></generic-table>
        <!-- affiche les tables des indices nocturnes -->
        <in-table v-if="tab.type == 'in-table'"></in-table>
      </v-window-item>
    </v-window>
  </div>
</template>

<script>
import genericTable from '@/components/table/generic-table.vue';
import inTable from '@/modules/in/in-table.vue';

export default {
  name: 'generic-admin',
  components: {
    genericTable,
    inTable,
  },
  props: ['config'],
  data: () => ({
    // La variable 'tab' est initialisée à null et sert probablement à stocker l'onglet actuellement sélectionné dans l'interface utilisateur.
    // 'configStores' est un objet vide destiné à contenir la configuration des différents magasins ou modules utilisés dans l'application.
    // 'nbElems' est un objet vide qui va probablement stocker le nombre d'éléments pour différentes catégories ou entités gérées par le composant.
    tab: null,
    configStores: {},
    nbElems: {},
  }),
  watch: {
    $route(to, from) {
      to;
      from;
      this.init();
    },
  },
  methods: {
    /**
     * Initialise les onglets de configuration dans le composant admin.
     * Pour chaque onglet défini dans la configuration :
     * - Récupère le nom du store associé à l'onglet.
     * - Ignore l'onglet si aucun store n'est défini.
     * - Récupère le store de configuration via le getter Vuex.
     * - Stocke le store dans l'objet local `configStores` pour un accès rapide.
     * - Définit les labels de l'onglet à partir du store si non déjà présents.
     * - Déclenche une action Vuex pour compter les éléments du store,
     *   puis met à jour le nombre d'éléments dans l'objet `nbElems` pour l'onglet courant.
     *   Utilise la syntaxe de copie d'objet pour assurer la réactivité de Vue.
     */
    init() {
      for (const [key, tab] of Object.entries(this.config.tabs)) {
        const storeName = tab && tab.storeName;
        if (!storeName) {
          continue;
        }
        const configStore = this.$store.getters.configStore(storeName);
        this.configStores[key] = configStore;
        tab.labels = tab.labels || configStore.labels;
        this.$store.dispatch(configStore.count).then((count) => {
          this.nbElems[key] = count;
          this.nbElems = { ...this.nbElems };
        });
      }
    },
  },
  mounted() {
    this.init();
  },
};
</script>
<style scoped>
.v-tab {
  text-transform: none !important;
}
</style>
