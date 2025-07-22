<template>
  <div style="width: 100%; margin-top: 50px; margin-left: 25px;">

    <h1> Données chasse - Page d'administation</h1>

    <!-- <h2 v-for="(value, key) in onglets" :key="key"> {{ key }}: {{ value.labels }}</h2> -->

    <v-tabs v-model="page_formulaire" fixed>
      <v-tabs-slider color="yellow"></v-tabs-slider>

      <v-tab v-for="(values_onglet, key_onglets) in onglets" :key="key_onglets.storeName">
        {{ values_onglet.labels }} ({{ nbElems[key_onglets] }})

      </v-tab>

    </v-tabs>

    <div style=" margin-top: 10px;">
      <v-tabs-items v-model="page_formulaire">
        <v-tab-item
          v-for="(values_onglet, key_onglets) in onglets"
          :key="key_onglets.storeName"
        >
          <component
            :is="values_onglet.storeName"
            :config="values_onglet.configTable"
            :key="key_onglets.storeName"
          ></component>
        </v-tab-item>
      </v-tabs-items>


    </div>

    
    <!-- <v-tabs-items v-model="tab">
      <v-tab-item v-for="[key, tab] of Object.entries(config.tabs)" :key="key">
        <generic-table
          v-if="['generic-table', undefined].includes(tab.type) && configStores[key]"
          :config="configStores[key].configTable"
          :key="key"
        ></generic-table>
        <in-table v-if="tab.type == 'in-table'"></in-table>
      </v-tab-item>
    </v-tabs-items> -->
  </div>
</template>





<script>
// import genericTable from "@/components/table/generic-table";
// import formRealisation from "./form/formRealisation";
import formAttribution from "./form/formAttribution";
import tableChasse from "./table/table_chasse";

const ONGLETS = {
    "realisation": {
      labels: "Réalisations", // titre de l'onglet
      storeName: tableChasse // formulaire correspondant importé plus haut
    },
    "attribution": {
      labels: "Attributions",
      storeName: formAttribution
    },
  };


export default {
  name: "donneesChasse",
  components: {
    // genericTable,
    // inTable,
    
  },
  
  props: ["config"],
  data: () => ({
    page_formulaire: null,
    configStores: {},
    nbElems: {},
    onglets: ONGLETS,
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
      // pour avoir le nombre d'éléments dans chaque onglet
      for (const [key, tab] of Object.entries(this.config.tabs)) {
        const storeName = tab && tab.storeName;
        // if (!storeName) {
        //   continue;
        // }
        const configStore = this.$store.getters.configStore(storeName);
        // this.configStores[key] = configStore;
        // tab.labels = tab.labels || configStore.labels;
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
