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
        <in-table v-if="tab.type == 'in-table'"></in-table>
      </v-tab-item>
    </v-tabs-items>
  </div>
</template>

<script>
import genericTable from "@/components/table/generic-table";
import inTable from "@/modules/in/in-table";

export default {
  name: "generic-admin",
  components: {
    genericTable,
    inTable,
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
