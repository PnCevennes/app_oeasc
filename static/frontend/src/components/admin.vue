<template>
  <div style="width:100%">
    <h1>{{ config.title }} - Page d'administation</h1>
    <v-tabs v-model="tab" fixed>
      <v-tabs-slider color="yellow"></v-tabs-slider>

      <v-tab v-for="[key, tab] of Object.entries(config.tabs)" :key="key">
        {{ tab.label }} {{ nbElems[key] ? `(${nbElems[key]})` : '' }}
      </v-tab>
    </v-tabs>

    <v-tabs-items v-model="tab">
      <v-tab-item v-for="[key, tab] of Object.entries(config.tabs)" :key="key">
        <generic-table
          v-if="tab.type == 'generic-table'"
          :config="tab.config"
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
  name: "in-admin",
  components: {
    genericTable,
    inTable
  },
  props: ["config"],
  data: () => ({
    tab: null
  }),
  computed: {
    nbElems() {
      console.log("nb_elems");
      const nbElems = {};
      for (const [key, tab] of Object.entries(this.config.tabs)) {
        const storeName = tab && tab.config && tab.config.storeName;
        if (!storeName) {
          nbElems[key] = "";
          continue;
        }
        const configStore = this.$store.getters.configStore(storeName);
        nbElems[key] = this.$store.getters[configStore.count];
      }
      return nbElems;
    }
  },
  mounted() {
    for (const tab of Object.values(this.config.tabs)) {
      const storeName = tab && tab.config && tab.config.storeName;
      if (!storeName) {
        continue;
      }
      const configStore = this.$store.getters.configStore(storeName);
      this.$store.dispatch(configStore.getAll);
    }
  }
};
</script>
