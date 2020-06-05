<template>
  <div>
    <div v-if="ready" class="settings">
      <div class="flex-list">
        <div v-for="type of ['espece', 'ug', 'annee']" :key="type">
          <list-form
            v-if="ready && configChoix[type]"
            :config="configChoix[type]"
            :baseModel="settings"
          ></list-form>
        </div>
      </div>
    </div>
    <div>
      <in-graph
        v-if="settings.espece"
        :displayReg="settings.displayReg"
        :dataIn="dataIn"
        :espece="settings.espece"
        :ug="settings.ug"
        width="100%"
        height="400px"
        @clickPoint="setAnnee"
      ></in-graph>
    </div>
    <div class="flex-list2">
      <div>
        <dynamic-form
          v-if="ready"
          :config="configSwitchReg"
          :baseModel="settings"
        ></dynamic-form>
      </div>
      <div>
        <transition name="fade">
          <div v-if="dataUg && this.settings.displayReg">
            <v-simple-table dense class="stats">
              <thead>
                <tr>
                  <th>y = ax + b</th>
                  <th>a</th>
                  <th>b</th>
                  <th>R<sup>2</sup></th>
                  <th>p-val a</th>
                  <th>p-val b</th>
                </tr>
              </thead>
              <tbody>
                <td></td>
                <td>
                  {{ round(dataUg.reg_lin.params[0], dec) }}
                </td>
                <td>
                  {{ round(dataUg.reg_lin.params[1], dec) }}
                </td>
                <td>
                  {{ round(dataUg.reg_lin.R2, dec) }}
                </td>
                <td>
                  {{ round(dataUg.reg_lin.pvalues[0], dec) }}
                </td>
                <td>
                  {{ round(dataUg.reg_lin.pvalues[1], dec) }}
                </td>
              </tbody>
            </v-simple-table>
          </div>
        </transition>
      </div>
    </div>

    <div v-if="dataAnnee">
      <h4>
        Indices nocturnes {{ settings.espece }} {{ settings.ug }}
        {{ settings.annee }}
      </h4>

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
          <td>
            {{ round(dataAnnee.moy, dec) }}
          </td>
          <td>
            {{ round(dataAnnee.E, dec) }}
          </td>
          <td>
            {{ round(dataAnnee.inf, dec) }}
          </td>
          <td>
            {{ round(dataAnnee.sup, dec) }}
          </td>
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
                <v-icon v-if="loading">
                  mdi-reload fa-spin
                </v-icon>
                <v-icon v-else>
                  mdi-reload
                </v-icon>
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
              >
              </td>
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
                  @change="validChange(circuit.id_observation, circuit.valid)"
                />
                <template v-else>{{
                  `${circuit.valid ? "Oui" : "Non"}`
                }}</template>
              </td>
              <!-- <td :class="{ gris: indexCircuit % 2 }">
                {{ circuit.id_observation }}
              </td> -->
              <td :class="{ gris: indexCircuit % 2 }">{{ circuit.date }}</td>
              <td :class="{ gris: indexCircuit % 2 }">
                {{ circuit.numero_circuit }}
              </td>
              <td :class="{ gris: indexCircuit % 2 }">
                {{ circuit.nom_circuit }}
              </td>
              <td :class="{ gris: indexCircuit % 2 }">{{ circuit.groupes }}</td>
              <td :class="{ gris: indexCircuit % 2 }">{{ circuit.km }}</td>
              <td :class="{ gris: indexCircuit % 2 }">{{ circuit.nb }}</td>
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
              <!-- <td
                v-if="indexSerie == 0 && indexCircuit == 0"
                :rowSpan="
                  nbCircuits(settings.espece, settings.ug, settings.annee)
                "
              >
                {{ round(dataAnnee.moy, dec) }}
              </td>
              <td
                v-if="indexSerie == 0 && indexCircuit == 0"
                :rowSpan="
                  nbCircuits(settings.espece, settings.ug, settings.annee)
                "
              >
                {{ round(dataAnnee.E, dec) }}
              </td>
              <td
                v-if="indexSerie == 0 && indexCircuit == 0"
                :rowSpan="
                  nbCircuits(settings.espece, settings.ug, settings.annee)
                "
              >
                {{ round(dataAnnee.inf, dec) }}
              </td>
              <td
                v-if="indexSerie == 0 && indexCircuit == 0"
                :rowSpan="
                  nbCircuits(settings.espece, settings.ug, settings.annee)
                "
              >
                {{ round(dataAnnee.sup, dec) }}
              </td> -->
            </tr>
          </template>
        </tbody>
      </v-simple-table>
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
    settings: { espece: "Cerf", ug: "Méjean", annee: "2019", displayReg: true },
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
    setAnnee(annee) {
      this.settings.annee = String(annee);
      this.settingsChange();
    },
    round(x, dec) {
      if (x == 0) return 0;
      if (x == null) return "";
      const e = 10 ** dec;
      return Math.round(x * e) / e;
    },
    validChange(id_observation, valid) {
      this.freezeValid = true;
      apiRequest("PATCH", "api/in/valid_obs/", {
        data: { id_observation, valid }
      }).then(() => {
        // this.dataIn = data;
        this.initInTable();
        this.freezeValid = false;
      });
    },
    initInTable() {
      this.dataAnnee = null;
      this.dataUg = null;

      if (
        !(
          this.settings.annee &&
          this.settings.ug &&
          this.settings.espece &&
          this.ready
        )
      ) {
        return null;
      }
      const especes = this.dataIn.especes;
      const ugs = especes[this.settings.espece].ugs;
      this.dataUg = ugs[this.settings.ug];
      const annees = ugs[this.settings.ug].annees;
      const annee = annees[this.settings.annee];
      this.dataAnnee = annee;
      return annee;
    },

    nbCircuits(espece, ug, annee) {
      if (!(espece && ug && annee)) return 0;

      const especes = this.dataIn.especes;
      const ugs = especes[espece].ugs;
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
        console.log("no ug");
        this.settings.ug = null;
      }

      if (!this.items("annee").includes(this.settings.annee)) {
        console.log("no annee");
        this.settings.annee = null;
      }

      this.configChoix.ug.items = this.items("ug");
      this.configChoix.annee.items = this.items("annee");

      this.configChoix.ug_save = { ...this.configChoix.ug };
      this.configChoix.annee_save = { ...this.configChoix.annee };

      this.configChoix.ug = this.configChoix.annee = null;

      setTimeout(() => {
        this.configChoix.ug = this.configChoix.ug_save;
        this.configChoix.annee = this.configChoix.annee_save;
        this.initInTable();
      }, 10);
    },

    items(type) {
      const especes = this.dataIn.especes;
      if (type == "espece") {
        return Object.keys(especes);
      }

      if (!this.settings.espece) {
        return [];
      }

      const ugs = especes[this.settings.espece].ugs;

      if (type == "ug") {
        return Object.keys(ugs);
      }

      if (!this.settings.ug) {
        return [];
      }

      const annees = ugs[this.settings.ug].annees;

      return Object.keys(annees);
    },
    reload() {
      this.loading = true;
      this.$store.dispatch("in_results").then(data => {
        this.ready = false;
        this.dataAnnee = false;
        this.dataIn = data;
        this.configChoix.espece = {
          name: "espece",
          label: "Espèce",
          items: this.items("espece"),
          change: this.settingsChange,
          display: "select"
        };
        this.configChoix.ug = {
          name: "ug",
          label: "Secteur",
          items: this.items("ug"),
          change: this.settingsChange,
          display: "select"
        };
        this.configChoix.annee = {
          name: "annee",
          label: "Année",
          items: this.items("annee"),
          change: this.settingsChange,
          display: "select"
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
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to, .fade-leave-active  /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
</style>
