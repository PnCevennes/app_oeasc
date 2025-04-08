<template>
  <div style="width: 100%">
    <h1>{{ config.title }} - Page d'administation</h1>
    <v-tabs v-model="tab" fixed>
      <v-tabs-slider color="yellow"></v-tabs-slider>

      <v-tab v-for="[key, tab] of Object.entries(config.tabs)" :key="key">
        {{ tab.labels }} {{ nbElems[key] ? `(${nbElems[key]})` : "" }}
      </v-tab>
    </v-tabs>

    <v-tabs-items v-model="tab">
      <v-tab-item v-for="[key, tab] of Object.entries(config.tabs)" :key="key">
        <generic-table
          v-if="['generic-table', undefined].includes(tab.type) && configStores[key]"
          :config="configStores[key].configTable"
          :key="key"
        ></generic-table>
        <!-- affiche les tables des indices nocturnes -->
        <!-- <in-table v-if="tab.type == 'in-table'"></in-table> -->

      </v-tab-item>
    </v-tabs-items>
  </div>
</template>

<script>
import genericTable from "./table/generic-table.vue";
// import inTable from "@/modules/in/in-table";

export default {
  name: "generic-admin",
  components: {
    genericTable,
    // inTable,
  },
  props: ["config"],
  data: () => ({
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
    init() {
      for (const [key, tab] of Object.entries(this.config.tabs)) { // parcours les tabs définis dans index.js -> config.tabs
        // récupèle un store et vérifie s'il existe
        const storeName = tab && tab.storeName;
        if (!storeName) {
          continue;
        }
        
        // configure un store en via la methode configStore qui est dans store/utils.js
        // storeName: sera du type chasse<Table>ConfigStore
        // ca ajoute des get, post, patch, delete, getAll, count, find
        // api: l'url de l'api pour avoir un ele
        // apis: l'url de l'api pour avoir tous les elements
        const configStore = this.$store.getters.configStore(storeName);
        //ajoute le configStore nouvellement créé au tableau configStores qui sera générique
        this.configStores[key] = configStore;
        
        // si labels n'est pas défini on le récupère dans le configStore
        tab.labels = tab.labels || configStore.labels;

        // l'action count du configStore retourne le nombre d'éléments. Pour être affiché à côté du label
        this.$store.dispatch(configStore.count).then((count) => {
          this.nbElems[key] = count; // on stocke le nombre d'éléments dans un tableau nbElems qui sera parcouru dans vuetify pour les clé d'onglet
          this.nbElems = { ...this.nbElems }; // on recréé l'objet pour forcer la réactivité de vueJs. 
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
