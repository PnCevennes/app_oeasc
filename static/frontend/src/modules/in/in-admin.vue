<template>
  <div style="width:100%">
    <h1>Indices nocturnes - Page d'administation</h1>
    <v-tabs v-model="tab" fixed>
      <v-tabs-slider color="yellow"></v-tabs-slider>

      <v-tab v-for="[key, config] of Object.entries(configTables)" :key="key">
        {{ config.label }}
      </v-tab>
    </v-tabs>

    <v-tabs-items v-model="tab">
      <v-tab-item
        v-for="[key, config] of Object.entries(configTables)"
        :key="key"
      >
        <generic-table
          v-if="config.type == 'generic-table'"
          :config="config.config"
          :key="key"
        ></generic-table>
        <in-table v-if="config.type == 'in-table'"></in-table>
      </v-tab-item>
    </v-tabs-items>
  </div>
</template>

<script>
import genericTable from "@/components/table/generic-table";
import inTable from "@/modules/in/in-table";
import configRealisationTable from "./config/table-realisation";
import configCircuitTable from "./config/table-circuit";
import configSecteurTable from "./config/table-secteur";

export default {
  name: "in-admin",
  components: {
    genericTable,
    inTable
  },
  data: () => ({
    tab: null,
    configTables: {
      graphiques: {
        label: "Statistiques",
        type: "in-table"
      },
      realisation: {
        config: configRealisationTable,
        label: "Réalisation",
        type: "generic-table"
      },
      circuit: {
        config: configCircuitTable,
        label: "Circuits",
        type: "generic-table"
      },
      secteur: {
        config: configSecteurTable,
        label: "Secteurs",
        type: "generic-table"
      }
    }
  })
};
</script>
