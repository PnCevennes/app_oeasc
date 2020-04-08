<template>
  <div>
    <h1>Liste des déclarations</h1>
    <div v-if="loading">
      Chargement en cours
    </div>
    <div v-else>
      <v-data-table :headers="headers" :items="declarations">
        <template v-slot:item.actions="{ item }">
          <v-icon small class="mr-2" @click="viewDeclaration(item)">
            mdi-eye
          </v-icon>
          <v-icon small @click="editDeclaration(item)">
            mdi-pencil
          </v-icon>
        </template>
      </v-data-table>
    </div>
  </div>
</template>

<script>
import { sortDate } from "@/core/js/util/util.js";

export default {
  data: () => ({
    loading: true,
    headers: [
      {
        text: "Actions",
        value: "actions",
        sortable: false
      },
      {
        text: "Id",
        value: "id_declaration"
      },
      {
        text: "Déclarant",
        value: "declarant"
      },
      {
        text: "Organisme",
        value: "organisme"
      },
      {
        text: "Secteur",
        value: "secteur"
      },
      {
        text: "Date",
        value: "declaration_date",
        sort: sortDate
      },
      {
        text: "Nom forêt",
        value: "label_foret"
      },
      {
        text: "Ess. objectif",
        value: "peuplement_ess_1_mnemo"
      },
      {
        text: "Parcelle(s)",
        value: "parcelles"
      },
      {
        text: "Type peupl.",
        value: "peuplement_type_mnemo"
      },
      {
        text: "Ori. peupl.",
        value: "peuplement_origine_mnemo"
      },
      {
        text: "Type dégâts",
        value: "degat_types_mnemo"
      }
    ],
    declarations: []
  }),
  name: "declaration-list",
  methods: {
      viewDeclaration(item) {
          this.$router.push({'path': `/declaration/voir_declaration/${item.id_declaration}`})
      },
      editDeclaration(item) {
          this.$router.push({'path': `/declaration/declarer_en_ligne/${item.id_declaration}`})
      },
    loadDeclarations() {
      this.$store.dispatch("declarations").then(declarations => {
        declarations.sort((a, b) => {
          return b.id_declaration - a.id_declaration;
        });
        this.declarations = declarations;
        this.loading = false;
      });
    }
  },
  created: function() {
    this.loadDeclarations();
  }
};
</script>
