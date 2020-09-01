<template>
  <div class="declaration" id="declaration">
    <div v-if="declaration">
      <h1>Déclaration {{ declaration.id_declaration }}</h1>
      <v-btn
        class="ignorepdf"
        icon
        color="red"
        @click="exportPdf()"
        title="Exporter la déclaration au format pdf"
        ><v-icon>mdi-file-pdf</v-icon></v-btn
      >
      <div>
        <declaration-table :declaration="declaration"></declaration-table>
      </div>
    </div>
    <div class="html2pdf__page-break"></div>
    <template v-for="type in mapList">
      <div v-if="configMaps[type]" :key="type">
        <div small>{{ configMaps[type].title }}</div>
        <base-map
          :mapId="`map_${type}`"
          :config="configMaps[type]"
          height="315px"
        ></base-map>
      </div>
    </template>
  </div>
</template>

<script>
import declarationTable from "./declaration-table";
import baseMap from "@/modules/map/base-map";
import { exportPDF } from "@/modules/export";
import "./declaration.css";

const styles = {
  foret: {
    color: "purple",
    fillColor: "purple",
    weight: 2,
    opacity: 1,
    fillOpacity: 0.5
  },
  parcelles: {
    color: "black",
    fillColor: "green",
    weight: 2,
    opacity: 1,
    fillOpacity: 0.5
  }
};

export default {
  name: "declaration",
  data: () => ({
    id: null,
    declaration: null,
    mapList: ["secteurs", "foret", "parcelles"]
  }),
  components: { declarationTable, baseMap },
  methods: {
    exportPdf() {
      exportPDF(
        "declaration",
        `declaration_${this.declaration.id_declaration}.pdf`,
        this.$store
      ).then(() => {
        console.log("PDF done");
      });
    },
    initDeclaration() {
      this.$store.dispatch("declarations").then(declarations => {
        this.declaration = declarations.find(
          d => this.id == d.id_declaration
        );
        console.log(this.declaration);
        // setTimeout(()=>  {this.exportPdf();}, 5000)
      });
    },
    configMap(type) {
      if (!this.declaration) {
        return;
      }
      const markers = [
        {
          coords: this.declaration.centroid,
        type: 'marker',
        style: {
          color: "blue",
            icon: "map-marker"
          },
        },
      ];
      const markerLegendGroups = [
        {
          legends: [
            {
              icon: "map-marker",
              text: "Localisation des alertes",
              color: "#3689CE"
            }
          ]
        }
      ];
      const titles = {
        secteurs:
          "Localisation de l'alerte dans le périmètre de l'observatoire",
        foret: "Localisation des parcelles",
        parcelles: "Carte des parcelles"
      };
      const layerList = {
        secteurs: {},
        foret: {
          url: `api/ref_geo/areas/l?id_area=${this.declaration.areas_foret.join(
            "&id_area="
          )}`,
          legend: "Forêt concernée par l'alerte",
          style: styles.foret,
          pane: "PANE_LAYER_1"
        },
        parcelles: {
          url: `api/ref_geo/areas/l?id_area=${this.declaration.areas_localisation.join(
            "&id_area="
          )}`,

          legend: "Parcelle(s) concernée(s) par l'alerte",
          style: styles.parcelles,
          pane: "PANE_LAYER_2"
        }
      };

      layerList[type] = {
        ...layerList[type],
        tooltip: {
          permanent: true,
          className: "tooltip-label",
          label: "label"
        },
        zoom: true
      };
      if (type != "secteurs") {
        delete layerList.secteurs;
      }
      return { layerList, title: titles[type], markers, markerLegendGroups };
    }
  },
  computed: {
    id() {
      return this.$route.params.id;
    },
    configMaps() {
      const configMaps = {};
      for (const type of this.mapList) {
        configMaps[type] = this.configMap(type);
      }
      return configMaps;
    }
  },
  created: function() {
    this.initDeclaration();
  },
  watch: {
    $route() {
      this.initDeclaration();
    }
  }
};
</script>
<style scoped>

</style>
