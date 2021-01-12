<template>
  <div class="in-table">
    <div>
      <v-row dense v-if="ready">
        <v-col
          v-for="[type, config] of Object.entries(configChoix)
          /**  .filter(
            ([type, config]) => {
              return graphOnly != undefined ? type == 'nom_espece' : true;
            }
          ) */
          "
          :key="type"
        >
          <list-form
            v-if="ready && config && config.items.length"
            :config="config"
            :baseModel="settings"
          ></list-form>
        </v-col>
      </v-row>
      <v-row v-if="dataUg && graphOnly == undefined">
        <v-col>
          <v-simple-table dense class="stats" v-if="dataUg">
            <thead>
              <tr>
                <th>Année</th>
                <th>Nb Séries</th>
                <th>Nb Circuits(min)</th>
                <th>Nb Circuits(max)</th>
              </tr>
            </thead>

            <tbody>
              <tr v-for="(row, index) of resNbCircuits()" :key="index">
                <td>{{ row.annee }}</td>
                <td>{{ row.nbSeries }}</td>
                <td>{{ row.nbCircuitsMin }}</td>
                <td>{{ row.nbCircuitsMax }}</td>
              </tr>
            </tbody>
          </v-simple-table>
        </v-col>
      </v-row>

      <v-row
        v-for="ug in [settings.ug]"
        :key="ug"
      >
        <v-col>
          <in-graph
            :class="{'graph-chained': graphOnly != undefined}"
            v-if="settings.nom_espece"
            :displayReg="settings.displayReg"
            :dataIn="dataIn"
            :nom_espece="settings.nom_espece"
            :ug="ug"
            width="100%"
            height="400px"
            :commentaires="
              commentaires &&
                commentaires[settings.nom_espece] &&
                commentaires[settings.nom_espece][ug]
            "
          ></in-graph>
        </v-col>
      </v-row>
      <v-row v-if="graphOnly == undefined">
        <v-col cols="2" class="col-switch">
          <dynamic-form
            v-if="ready"
            :config="configSwitchReg"
            :baseModel="settings"
          ></dynamic-form>
        </v-col>
        <v-col>
          <transition name="fade">
            <div v-if="dataUg && this.settings.displayReg">
              <v-simple-table dense class="stats">
                <thead>
                  <tr>
                    <th>y = ax + b</th>
                    <th>a</th>
                    <th>b</th>
                    <!-- <th>R<sup>2</sup></th> -->
                    <th>p-val</th>
                    <!-- <th>p-val b</th> -->
                  </tr>
                </thead>
                <tbody>
                  <td></td>
                  <td>{{ round(dataUg.reg_lin.params[0], dec) }}</td>
                  <td>{{ round(dataUg.reg_lin.params[1], dec) }}</td>
                  <!-- <td>
                  {{ round(dataUg.reg_lin.R2, dec) }}
                  </td>-->
                  <td>{{ round(dataUg.reg_lin.pvalues[0], dec) }}</td>
                  <!-- <td>
                  {{ round(dataUg.reg_lin.pvalues[1], dec) }}
                  </td>-->
                </tbody>
              </v-simple-table>
            </div>
          </transition>
        </v-col>
      </v-row>

      <div v-if="dataUg && graphOnly == undefined">
        <h4>Indices nocturnes {{ settings.nom_espece }} {{ settings.ug }}</h4>

        <v-tabs centered dark grow>
          <v-tab
            v-for="annee of Object.keys(dataUg.annees)"
            :key="annee"
            :href="`#tab-${annee}`"
            >{{ annee }}</v-tab
          >

          <v-tab-item
            v-for="[annee, dataAnnee] of Object.entries(dataUg.annees)"
            :key="annee"
            :value="'tab-' + annee"
          >
            <v-simple-table dense class="stats">
              <thead>
                <tr>
                  <th>IN</th>
                  <th>E</th>
                  <th>inf</th>
                  <th>sup</th>
                </tr>
              </thead>
              <tbody>
                <td>{{ round(dataAnnee.moy, dec) }}</td>
                <td>{{ round(dataAnnee.E, dec) }}</td>
                <td>{{ round(dataAnnee.inf, dec) }}</td>
                <td>{{ round(dataAnnee.sup, dec) }}</td>
              </tbody>
            </v-simple-table>

            <v-simple-table dense class="in">
              <thead>
                <tr>
                  <th>
                    <v-btn
                      v-if="$store.getters.droitMax >= 5"
                      icon
                      color="primary"
                      @click="reload()"
                    >
                      <v-icon v-if="loading">mdi-reload fa-spin</v-icon>
                      <v-icon v-else>mdi-reload</v-icon>
                    </v-btn>
                  </th>
                  <th>Série</th>
                  <th>Validé</th>
                  <th>Date</th>
                  <th>N° Circuit</th>
                  <th>Nom circuit</th>
                  <th>Nb grp.</th>
                  <th>Km</th>
                  <th>Nb ind.</th>
                  <th>Nb ind. / km</th>
                  <th>Moy. circuits</th>
                </tr>
              </thead>
              <tbody>
                <template
                  v-for="([numeroSerie, serie], indexSerie) in Object.entries(
                    dataAnnee.series
                  )"
                >
                  <tr
                    :class="{ serie: indexCircuit == 0 }"
                    v-for="(circuit, indexCircuit) of Object.values(
                      serie.id_circuits
                    ).sort((a, b) => {
                      return a.numero_circuit - b.numero_circuit;
                    })"
                    :key="`${numeroSerie}-${circuit.id_circuit}`"
                  >
                    <td
                      :class="{ gris: indexSerie % 2 }"
                      v-if="indexCircuit == 0"
                      :rowSpan="Object.entries(serie.id_circuits).length"
                    ></td>
                    <td
                      :class="{ gris: indexSerie % 2 }"
                      v-if="indexCircuit == 0"
                      :rowSpan="Object.entries(serie.id_circuits).length"
                    >
                      {{ numeroSerie }}
                    </td>
                    <td :class="{ gris: indexCircuit % 2 }">
                      <input
                        v-if="$store.getters.droitMax >= 5"
                        type="checkbox"
                        v-model="circuit.valid"
                        :disabled="freezeValid"
                        @change="validChange(circuit)"
                      />
                      <template v-else>
                        {{ `${circuit.valid ? "Oui" : "Non"}` }}
                      </template>
                    </td>

                    <td :class="{ gris: indexCircuit % 2 }">
                      {{ circuit.date }}
                    </td>
                    <td :class="{ gris: indexCircuit % 2 }">
                      {{ circuit.numero_circuit }}
                    </td>
                    <td :class="{ gris: indexCircuit % 2 }">
                      {{ circuit.nom_circuit }}
                    </td>
                    <td :class="{ gris: indexCircuit % 2 }">
                      {{ circuit.groupes }}
                    </td>
                    <td :class="{ gris: indexCircuit % 2 }">
                      {{ circuit.km }}
                    </td>
                    <td :class="{ gris: indexCircuit % 2 }">
                      {{ circuit.nb }}
                    </td>
                    <td :class="{ gris: indexCircuit % 2 }">
                      {{ round(circuit.nb / circuit.km, dec) }}
                    </td>
                    <td
                      :class="{ gris: indexSerie % 2, serie: true }"
                      v-if="indexCircuit == 0"
                      :rowSpan="Object.entries(serie.id_circuits).length"
                    >
                      {{ round(serie.moy, dec) }}
                    </td>
                  </tr>
                </template>
              </tbody>
            </v-simple-table>
          </v-tab-item>
        </v-tabs>
      </div>
    </div>
  </div>
</template>

<script>
import listForm from "@/components/form/list-form";
import dynamicForm from "@/components/form/dynamic-form";
import { apiRequest } from "@/core/js/data/api.js";
import "./table.css";

export default {
  name: "in-table",
  props: ["graphOnly", "commentaires"],
  components: {
    listForm,
    "in-graph": () => import("./in-graph.vue"),
    dynamicForm
  },
  data: () => ({
    dataIn: null,
    configChoix: {},
    ready: false,
    loading: true,
    settings: { nom_espece: "Cerf", ug: "Causse-Gorges", displayReg: true },
    dataAnnee: null,
    dataUg: null,
    dec: 4,
    freezeValid: false,
    configSwitchReg: {
      type: "bool_switch",
      label: "Régression linéaire",
      name: "displayReg"
    }
  }),
  methods: {
    resNbCircuits() {
      const res = [];
      if (!this.dataUg) return [];
      for (const [annee, dataAnnee] of Object.entries(
        this.dataUg.annees || {}
      )) {
        let nbCircuitsMin = 1e10;
        let nbCircuitsMax = -1e10;
        let nbSeries = 0;
        for (const serie of Object.values(dataAnnee.series)) {
          nbSeries += 1;
          nbCircuitsMax = Math.max(
            nbCircuitsMax,
            Object.keys(serie.id_circuits).length
          );
          nbCircuitsMin = Math.min(
            nbCircuitsMin,
            Object.keys(serie.id_circuits).length
          );
        }
        res.push({ annee, nbCircuitsMin, nbCircuitsMax, nbSeries });
      }
      return res;
    },
    round(x, dec) {
      if (x == 0) return 0;
      if (x == null) return "";
      const e = 10 ** dec;
      return Math.round(x * e) / e;
    },
    validChange(circuit) {
      this.freezeValid = true;
      const postData = {};
      postData.id_tag = circuit.id_tag;
      postData.id_realisation = circuit.id_realisation;
      postData.valid = circuit.valid;
      apiRequest("PATCH", "api/in/valid_realisation/", {
        postData
      }).then(() => {
        // this.dataIn = data;
        this.initInTable();
        this.freezeValid = false;
      });
    },
    initInTable() {
      this.dataAnnee = null;
      this.dataUg = null;

      if (!(this.settings.ug && this.settings.nom_espece && this.ready)) {
        return null;
      }
      const nom_especes = this.dataIn.nom_especes;
      const ugs = nom_especes[this.settings.nom_espece].ugs;
      this.dataUg = ugs[this.settings.ug];
    },

    nbCircuits(nom_espece, ug, annee) {
      if (!(nom_espece && ug && annee)) return 0;

      const nom_especes = this.dataIn.nom_especes;
      const ugs = nom_especes[nom_espece].ugs;
      const annees = ugs[ug].annees;

      var nbCircuits = 0;
      for (const serie of Object.values(annees[annee].series)) {
        nbCircuits += Object.keys(serie.id_circuits).length;
      }
      return nbCircuits;
    },

    settingsChange() {
      if (!this.ready) {
        return;
      }
      if (!this.items("ug").includes(this.settings.ug)) {
        this.settings.ug = null;
      }

      this.configChoix.ug.items = this.items("ug");

      this.initInTable();
    },

    items(type) {
      const nom_especes = this.dataIn.nom_especes;
      if (type == "nom_espece") {
        return Object.keys(nom_especes);
      }

      if (!this.settings.nom_espece) {
        return [];
      }

      const ugs = nom_especes[this.settings.nom_espece].ugs;

      if (type == "ug") {
        return Object.keys(ugs);
      }

      if (!this.settings.ug) {
        return [];
      }
    },
    reload() {
      this.loading = true;
      
      this.$store.dispatch("inResults", {forceReload: true}).then(data => {
        
        this.ready = false;
        this.dataAnnee = false;
        this.dataIn = data;
        this.configChoix.nom_espece = {
          name: "nom_espece",
          label: "Espèce",
          items: this.items("nom_espece"),
          change: this.settingsChange,
          display: "button"
        };
        this.configChoix.ug = {
          name: "ug",
          label: "Secteur",
          items: this.items("ug"),
          change: this.settingsChange,
          display: "button"
        };

        this.ready = true;
        this.loading = false;

        this.initInTable();
      });
    }
  },

  mounted() {
    this.reload();
  }
};
</script>

<style lang="css">
.in-table {
  width: 100%;
  margin: 0 100px;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to, .fade-leave-active  /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
.graph-chained {
  margin-bottom: 100px;
}
</style>
