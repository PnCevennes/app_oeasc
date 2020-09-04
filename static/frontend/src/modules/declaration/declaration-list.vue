<template>
  <div>
    <div>
      <div>
        <v-btn @click="bDialogExport = true" color="primary">Exporter les données</v-btn>
        <v-spacer></v-spacer>

        <v-dialog v-model="bDialogExport" max-width="500">
          <v-card>
            <v-card-title class="headline">Exporter les données</v-card-title>

            <v-card-text>
              <div v-for="(item, index) of exports" :key="index">
                <v-btn :href="item.href" color="success" class="btn-spaced">{{ item.label }}</v-btn>
                <i>{{ item.subLabel }}</i>
              </div>
            </v-card-text>
          </v-card>
        </v-dialog>
      </div>
      <generic-table :config="configTable"></generic-table>
    </div>
  </div>
</template>

<script>
import { config } from "@/config/config.js";
import genericTable from "@/components/table/generic-table";
import "@/core/css/main.scss";
import configDeclarationTable from "./config/table-declaration"


export default {
  components: { genericTable },
  data() {
    return {
      exports: [
        {
          href: `${config.URL_APPLICATION}/api/declaration/declarations_csv`,
          label: "Export CSV",
          subLabel: "une ligne par décaration",
        },
        {
          href: `${config.URL_APPLICATION}/api/declaration/declarations_csv?type_out=degat`,
          label: "Export CSV",
          subLabel: "une ligne par dégât",
        },
        {
          href: `${config.URL_APPLICATION}/api/declaration/declarations_shape`,
          label: "Export SHAPE",
          subLabel: "une ligne par décaration",
        },
        {
          href: `${config.URL_APPLICATION}/api/declaration/declarations_shape?type_out=degat`,
          label: "Export SHAPE",
          subLabel: "une ligne par dégât",
        },
      ],
      bDialogExport: false,
      configTable: configDeclarationTable,
      declarations: [],
    };
  },
  name: "declaration-list",
  methods: {
    loadDeclarations() {
      this.$store.dispatch("declarations").then((declarations) => {
        declarations.sort((a, b) => {
          return b.id_declaration - a.id_declaration;
        });
        this.declarations = declarations;
        this.configTable.items = declarations;
        this.configTable = { ...this.configTable };
      });
    },
  },
  created: function () {
    this.loadDeclarations();
  },
};
</script>
