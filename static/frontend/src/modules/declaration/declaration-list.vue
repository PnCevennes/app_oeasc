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
import { displayParcelles } from "./declaration";

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
      configTable: {
        idFieldName: "id_declaration",
        dense: true,
        striped: true,
        small: true,
        headers: {
          actions: {
            noSearch: true,
            width: "90px",
            text: "Actions",
            list: [
              {
                title: "Voir la déclaration",
                icon: "mdi-eye",
                to: ({ item }) =>
                  `/declaration/voir_declaration/${item.id_declaration}`,
              },
              {
                title: "Éditer la déclaration",
                icon: "mdi-pencil",
                to: ({ item }) =>
                  `/declaration/declarer_en_ligne/${item.id_declaration}?keySession=all`,
                condition: ({ item, $store }) => {
                  return (
                    $store.getters.droitMax > item.id_droit_max ||
                    $store.getters.user.id_role == item.id_declarant
                  );
                },
              },
            ],
            sortable: false,
          },
          id_declaration: {
            text: "Id",
          },
          declarant: {
            text: "Déclarant",
          },
          org_mnemo: {
            text: "Organisme",
          },
          // organisme: {
          //   text: "Organisme"
          // },
          secteur: {
            text: "Secteur",
          },
          declaration_date: {
            text: "Date",
            type: "date",
          },
          label_foret: {
            text: "Nom forêt",
          },
          peuplement_ess_1_mnemo: {
            text: "Ess. objectif",
          },
          parcelles: {
            text: "Parcelle(s)",
            display: (val) => displayParcelles(val),
          },
          peuplement_type_mnemo: {
            text: "Type peupl.",
          },
          peuplement_origine2_mnemo: {
            text: "Origine plants touchés",
          },
          degat_types_mnemo: {
            text: "Type dégâts",
          },
          b_valid: {
            display: (val) =>
              val === true ? "Oui" : val === false ? "Non" : "?",
            width: "100px",
            text: "Validé",
            condition: ({ $store }) => $store.getters.droitMax >= 5,
            edit: {
              preLoadData: ({ config, $store, id }) => {
                return new Promise((resolve) => {
                  $store
                    .dispatch("declarationForm", id)
                    .then((declaration) => {
                      config.value = declaration;
                      resolve();
                    });
                });
              },
              action: {
                onSuccess: ({ data }) => {
                  this.configTable.items.find(
                    (d) => d.id_declaration == data.id_declaration
                  ).b_valid = data.b_valid;
                },
                request: {
                  url: "api/degat_foret/declaration",
                  method: "POST",
                },
              },
              formDefs: {
                b_valid: {
                  label: "Valider cette déclaration (admin seulement)",
                  type: "bool_radio",
                  labels: ["Oui", "Non"],
                },
              },
            },
          },
        },
      },
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
