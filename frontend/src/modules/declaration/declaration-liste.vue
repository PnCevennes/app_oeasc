<!--
Remplace l'ancienne version declaration-list.vue qui utilisait une vue. C'était trop compliqué à gérer si on voulait faire des modifs.
Page affichant le tableau avec la liste des declarations. Affiche aussi un bouton pour exporter les données 
 un fenetre s'affichera pour proposer 4 type de format d'exportation
 -->

<template>
  <div>
    <div>
      <div>
        <v-btn
          v-if="$store.getters.isAuth"
          @click="bDialogExport = true"
          color="primary"
        >
          Exporter les données
        </v-btn>
        <v-spacer></v-spacer>

        <v-dialog
          v-model="bDialogExport"
          max-width="500"
        >
          <v-card>
            <v-card-title class="headline">Exporter les données</v-card-title>

            <v-card-text>
              <div
                v-for="(item, index) of exports"
                :key="index"
              >
                <v-btn
                  :href="item.href"
                  color="success"
                  class="btn-spaced"
                >
                  {{ item.label }}
                </v-btn>
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
import { config } from '@/config/config.js';
import genericTable from '@/components/table/generic-table';
import '@/core/css/main.scss';
import configDeclarationTable from './config/table-declaration.js';

export default {
  components: { genericTable },
  data() {
    return {
      exports: [
        {
          href: `${config.URL_APPLICATION}/api/declaration/export_liste_declarations?type_out=declaration&type_file=csv`,
          label: 'Export CSV',
          subLabel: 'une ligne par décaration',
        },
        {
          href: `${config.URL_APPLICATION}/api/declaration/export_liste_declarations?type_out=degat&type_file=csv`,
          label: 'Export CSV',
          subLabel: 'une ligne par dégât',
        },
        {
          href: `${config.URL_APPLICATION}/api/declaration/export_liste_declarations?type_out=declaration&type_file=gpkg`,
          label: 'Export GPKG',
          subLabel: 'une ligne par décaration',
        },
        {
          href: `${config.URL_APPLICATION}/api/declaration/export_liste_declarations?type_out=degat&type_file=gpkg`,
          label: 'Export GPKG',
          subLabel: 'une ligne par dégât',
        },
      ],
      bDialogExport: false,
      configTable: configDeclarationTable,
      declarations: [],
    };
  },
  name: 'declaration-liste',
  methods: {
    /**
     * Charge les déclarations depuis le store et les trie par date de création.
     */
    loadDeclarations() {
      this.$store.dispatch('declarations').then((declarations) => {
        declarations.sort((a, b) => {
          return b.id_declaration - a.id_declaration;
        });
        this.declarations = declarations;
        this.configTable.items = declarations;
        this.configTable = { ...this.configTable };
        console.log('Déclarations chargées :', this.declarations);
      });
    },
  },
  created: function () {
    this.loadDeclarations();
  },
};
</script>
