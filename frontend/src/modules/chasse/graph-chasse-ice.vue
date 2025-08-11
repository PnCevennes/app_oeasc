<!--
  Ce composant Vue.js affiche un graphique Highcharts ou une barre de progression selon l'état des données.

  Props attendues :
    - height (optionnelle) : définit la hauteur du conteneur et du graphique (par défaut 400px).
    - width (optionnelle) : définit la largeur du graphique (par défaut 100%).
    - chartOptions : options de configuration du graphique Highcharts. Si cette prop est définie, le graphique s'affiche.
    - hcInstance : instance de la librairie Highcharts à utiliser.

  Fonctionnement :
    - Si chartOptions est défini, le composant <highcharts> est affiché avec les options et l'instance fournies.
    - Si chartOptions n'est pas encore disponible (par exemple, en attente de chargement des données), une barre de progression indéterminée (<v-progress-linear>) est affichée pour indiquer à l'utilisateur que le contenu est en cours de chargement.

  Cas d'utilisation :
    - Utilisé pour afficher dynamiquement un graphique Highcharts dans une interface utilisateur, tout en gérant l'état de chargement des données.
    - Permet de personnaliser la taille du graphique via les props height et width.
-->
<!-- <template>
  <div :style="`height:${height || '400px'}; width: 100%`">
    <highcharts
      v-if="chartOptions"
      :style="`width:${width || '100%'}; height:${height || '400px'}`"
      :options="chartOptions"
      :highcharts="hcInstance"
    ></highcharts>
    <v-progress-linear v-else active indeterminate></v-progress-linear>
  </div>
</template> -->

<!-- <script>
import Highcharts from "highcharts";
import exportingInit from "highcharts/modules/exporting";
import offlineExporting from "highcharts/modules/offline-exporting";
import { round } from "@/core/js/util/util.js";

exportingInit(Highcharts);
offlineExporting(Highcharts);

export default {
  name: "graph-chasse-ice",
  props: ["id_espece", "id_zone_cynegetique", "width", "height"],
  data: () => ({
    dataBilanChasse: null,
    chartOptions: null,
    hcInstance: Highcharts
  }),
  watch: {
    $props: {
      handler() {
        this.process();
      },
      deep: true,
      immediate: true
    }
  },
  methods: {
    process() {
      if (!(this.id_zone_cynegetique && this.id_espece)) {
        return;
      }

      this.$store
        .dispatch("chasseIce", {
          id_espece: this.id_espece,
          id_zone_cynegetique: this.id_zone_cynegetique
        })
        .then(data => {
          console.log(data);
          const dataGraph = data.res_lm_moy;
          this.chartOptions = {
            title: {
              text: `Evolution des ICE - Masse Corporelle - ${data.nom_espece} - ${data.nom_zone_cynegetique}`
            },
            xAxis: {
              title: {
                text: "Saison"
              },
              labels: {
                enabled: true,
                formatter: function() {
                  return `${this.value}-${this.value + 1}`;
                }
              }
            },
            yAxis: {
              // min: -0.01,
              // endOnTick: false,
              // startOnTick: false,
              title: {
                text: "Poids (kg)"
              }
            },
            series: [
              {
                id: "ice",
                name: "Poids moyen",
                data: Object.keys(dataGraph.x).map(ind => [
                  dataGraph.x[ind],
                  dataGraph.y[ind]
                ])
              },
              {
                type: "errorbar",
                linkedTo: "ice",
                name: "Intervalle de confiance",
                data: Object.keys(dataGraph.x).map(ind => [
                  dataGraph.x[ind],
                  dataGraph.inf[ind],
                  dataGraph.sup[ind]
                ]),
                enableMouseTracking: false,
                maxPointWidth: 40
              },
              {
                name: `Regression (p-value=${round(dataGraph.p_value_slope, 3)})`,
                data: [
                  [dataGraph.x[0], dataGraph.intercept + dataGraph.x[0] * dataGraph.slope],
                  [dataGraph.x[dataGraph.x.length - 1], dataGraph.intercept + dataGraph.x[dataGraph.x.length - 1] * dataGraph.slope],
                ],
                enableMouseTracking: false,
                maxPointWidth: 40
              }
            ],
            height: "600px",
            width: "600px"
          };
        });
    }
  },
  mounted() {
    this.process();
  }
};
</script> -->
