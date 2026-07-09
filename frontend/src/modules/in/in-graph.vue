<template>
  <!--
    Ce composant affiche un graphique Highcharts basé sur les données IN.
    - Le graphique est affiché si les options sont prêtes (chartOptions).
    - Sinon, une barre de progression est affichée pendant le chargement.
    - Les commentaires éventuels sont affichés en dessous du graphique.
    Props utilisées :
      - height, width : dimensions du graphique.
      - chartOptions : options du graphique Highcharts.
      - hcInstance : instance Highcharts.
      - commentaires : texte HTML à afficher sous le graphique.
  -->
  <div :style="`height:${height || '400px'}; width: 100%`">
    <!-- Affiche le graphique si les options sont disponibles -->
    <highcharts
      v-if="chartOptions"
      :style="`width:${width || '100%'}; height:${height || '400px'}`"
      :options="chartOptions"
      :highcharts="hcInstance"
    ></highcharts>
    <!-- Affiche une barre de progression pendant le chargement des données -->
    <v-progress-linear
      v-else
      active
      indeterminate
    ></v-progress-linear>
    <!-- Affiche les commentaires si présents -->
    <div
      v-if="commentaires"
      class="commentaires"
      v-html="commentaires"
    ></div>
  </div>
</template>

<script>
import Highcharts from 'highcharts';
import exportingInit from 'highcharts/modules/exporting';
import offlineExporting from 'highcharts/modules/offline-exporting';
import chroma from 'chroma-js';
import { round } from '@/core/js/util/util.js';
exportingInit(Highcharts);
offlineExporting(Highcharts);

export default {
  compatConfig: { MODE: 3 }, // verrouille les acquis Phase 4 (composant testé sans warning au 2026-07-10)
  name: 'in-graph',
  props: [
    'displayTitle',
    'dataIn',
    'nom_espece',
    'ugs',
    'ug',
    'width',
    'height',
    'displayReg',
    'commentaires',
  ],
  data: () => ({
    /*
     * dataGraph: Contient les données à afficher dans le graphique.
     *            Cette propriété est généralement alimentée par une requête API ou une transformation de données.
     *
     * chartOptions: Stocke les options de configuration du graphique Highcharts.
     *               Elle permet de personnaliser l'apparence et le comportement du graphique (axes, légendes, couleurs, etc.).
     *
     * hcInstance: Référence à l'instance Highcharts utilisée pour générer le graphique.
     *             Utile pour accéder aux méthodes et propriétés natives de Highcharts.
     */
    dataGraph: null,
    chartOptions: null,
    hcInstance: Highcharts,
  }),
  computed: {
    /**
     * Retourne la liste des UGS (Unités de Gestion).
     *
     * Cette fonction vérifie d'abord si la propriété `ugs` existe et contient au moins un élément.
     * - Si oui, elle retourne directement cette liste.
     * - Sinon, elle vérifie si la propriété `ug` existe :
     *   - Si oui, elle retourne un tableau contenant uniquement cet élément.
     *   - Si aucune des deux propriétés n'est définie, elle retourne `null`.
     *
     * Cette fonction est généralement utilisée pour obtenir la liste des UGS à afficher dans le graphique,
     * en fonction des données disponibles dans le composant.
     */
    getUgs() {
      return this.ugs && this.ugs.length ? this.ugs : this.ug ? [this.ug] : null;
    },
  },
  watch: {
    dataIn() {
      this.initGraph();
    },
    nom_espece() {
      this.initGraph();
    },
    ug() {
      this.initGraph();
    },
    displayReg() {
      this.initGraph();
    },
  },
  methods: {
    /**
     * Retourne une couleur associée à un groupe d'unités géographiques (ug) et à un type spécifique.
     *
     * @param {string} ug - Le nom de l'unité géographique (ex: "Méjean", "Aigoual", etc.).
     * @param {string} type - Le type de couleur à retourner ("error", "reglin", ou autre).
     *
     * Fonctionnement :
     * - Associe chaque unité géographique à une couleur prédéfinie.
     * - Si le type est "error" ou "reglin", la couleur est assombrie.
     * - Retourne la couleur sous forme de chaîne de caractères.
     * - Si l'unité géographique n'est pas reconnue, la fonction ne retourne rien.
     *
     * Utilisation :
     * Cette fonction est utilisée pour colorer dynamiquement des éléments graphiques (ex: courbes ou points sur un graphique)
     * selon l'unité géographique et le contexte (erreur ou régression linéaire).
     */
    color(ug, type) {
      const colors = {
        Méjean: '#e8e805',
        Aigoual: 'red',
        'Mont Lozère': 'blue',
        'Vallées cévenoles': 'green',
      };

      var color = colors[ug];

      if (!color) {
        return;
      }

      color = chroma(color);

      if (type == 'error') {
        color = color.darken(1);
      }

      if (type == 'reglin') {
        color = color.darken(1);
      }

      return color.toString();
    },

    /**
     * Initialise et configure le graphique Highcharts à partir des données IN.
     *
     * Cette fonction est appelée :
     * - Lors du montage du composant (mounted)
     * - À chaque changement des props : dataIn, nom_espece, ug, displayReg (via watch)
     *
     * Fonctionnement :
     * 1. Met à jour dataGraph avec dataIn si disponible.
     * 2. Réinitialise chartOptions pour forcer le rechargement du graphique.
     * 3. Après un court délai (setTimeout), vérifie que les données et l'espèce sont présentes.
     * 4. Pour chaque UGS (unité de gestion) de l'espèce sélectionnée :
     *    - Construit les séries de données principales, les barres d'erreur et la régression linéaire.
     *    - Ajoute chaque série au tableau `series` avec les options graphiques adaptées.
     * 5. Configure les options du graphique Highcharts (titre, axes, export, etc.) et les assigne à chartOptions.
     */
    initGraph() {
      // Si des données IN sont passées en props, les utiliser
      if (this.dataIn) {
        this.dataGraph = this.dataIn;
      }
      // Réinitialise les options du graphique pour forcer le rechargement
      this.chartOptions = null;
      setTimeout(() => {
        // Vérifie que les données et le nom de l'espèce sont disponibles
        if (!(this.dataGraph && this.nom_espece)) {
          return;
        }
        const nom_espece = this.nom_espece;
        const series = [];
        // Récupère les données pour l'espèce sélectionnée
        const data_espece = this.dataGraph.nom_especes[nom_espece];
        // Parcourt chaque UGS (unité de gestion) de l'espèce
        for (const [ug, data_ug] of Object.entries(data_espece.ugs)) {
          // Si la liste des UGS à afficher est définie, ne garde que celles présentes
          if (this.getUgs && !this.getUgs.includes(ug)) {
            continue;
          }
          // Prépare les tableaux pour les différentes séries
          const serie = [], // Série principale (moyenne IN par année)
            error = [], // Barres d'erreur (intervalle de confiance)
            regLin = []; // Série de régression linéaire

          // Parcourt les années pour chaque UGS
          for (const [annee, data_annee] of Object.entries(data_ug.annees)) {
            // Ajoute la moyenne IN pour chaque année
            serie.push([parseInt(annee), data_annee.moy]);
            // Ajoute les barres d'erreur si disponibles
            if (data_annee.sup) {
              error.push([parseInt(annee), data_annee.inf, data_annee.sup]);
            }
            // Calcule la valeur de la régression linéaire pour chaque année
            regLin.push([
              parseInt(annee),
              parseInt(annee) * data_ug.reg_lin.params[0] + data_ug.reg_lin.params[1],
            ]);
          }

          var dec = 2; // Nombre de décimales pour l'affichage

          // Ajoute la série de régression linéaire si la p-value est significative
          const pValue = data_ug.reg_lin.pvalues[0];
          if (pValue && pValue <= 0.1) {
            series.push({
              name: `y = ${round(data_ug.reg_lin.params[0], dec)}x + ${round(
                data_ug.reg_lin.params[1],
                dec
              )} (R2=${round(data_ug.reg_lin.R2, dec)})`,
              data: regLin,
              linkedTo: ug,
              dashStyle: pValue <= 0.05 ? 'Solid' : 'Dash', // Style selon la significativité
              enableMouseTracking: false,
              color: 'grey',
              lineWidth: 1 * (this.displayReg !== undefined),
              marker: {
                enabled: false,
              },
            });
          }
          // Ajoute la série principale (points IN)
          series.push({
            id: ug,
            name: ug,
            data: serie,
            lineWidth: 0, // Pas de ligne, uniquement les points
            color: this.color(ug),
            tooltip: {
              // Format personnalisé du tooltip au survol d'un point
              pointFormatter: function () {
                var point = this;
                var y = point.options.y;
                var out = `Secteur : <b>${ug}</b><br>`;
                out += `IN : <b>${round(y, 2)}</b><br>`;
                return out;
              },
            },
            cursor: 'pointer',
            point: {
              events: {
                // Émet un événement lors du clic sur un point du graphique
                click: (e) => {
                  this.$emit('clickPoint', e.point.options.x);
                },
              },
            },
          });
          // Ajoute la série des barres d'erreur
          series.push({
            type: 'errorbar',
            linkedTo: ug,
            data: error,
            enableMouseTracking: false,
            maxPointWidth: 40,
            color: this.color(ug, 'error'),
          });

          // Configure les options du graphique Highcharts
          this.chartOptions = {
            exporting: {
              buttons: {
                contextButton: {
                  menuItems: [
                    {
                      text: "Télécharger l'image au format JPEG",
                      onclick: function () {
                        this.exportChart({
                          type: 'image/jpeg',
                        });
                      },
                    },
                  ],
                },
              },
              chartOptions: {
                // Options spécifiques pour l'image exportée
                plotOptions: {
                  series: {
                    dataLabels: {
                      // enabled: true,
                    },
                  },
                },
              },
              fallbackToExportServer: false,
            },
            title: {
              // Affiche le titre si displayTitle est activé
              text: this.displayTitle && `Indices nocturnes (${nom_espece}, ${ug})`,
            },
            xAxis: {
              title: {
                text: 'Année',
              },
            },
            yAxis: {
              min: -0.01,
              endOnTick: false,
              startOnTick: false,
              title: {
                text: 'IN (individu / km)',
              },
            },
            series: series,
            height: '600px',
            width: '600px',
          };
        }
      }, 10); // Petit délai pour garantir la mise à jour des données
    },
  },

  mounted() {
    if (!this.dataIn) {
      this.$store.dispatch('inResults').then((data) => {
        this.dataGraph = data;
        this.initGraph();
      });
    } else {
      this.initGraph();
    }
  },
};
</script>
<style>
.commentaires {
  color: rgb(100, 100, 100);
}
</style>
