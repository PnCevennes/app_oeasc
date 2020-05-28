<template>
  <div>
    <h1>Indices nocturnes (tableau)</h1>

    <div v-if="ready"></div>
    <div v-for="type of ['espece', 'ug', 'annee']" :key="type">
      <list-form
        v-if="ready && configChoix[type]"
        :config="configChoix[type]"
        :baseModel="settings"
      ></list-form>
    </div>

    <div v-if="dataTable">
      <table class="table">
        <thead>
          <tr>
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
            <th>IN</th>
            <th>d. moy.</th>
            <th>(d. moy.) **2</th>
            <th>S</th>
            <th>S/(n*(n-1)</th>
            <th>E</th>
            <th>inf</th>
            <th>sup</th>
          </tr>
        </thead>
        <tbody>
          <template
            v-for="([numeroSerie, serie], indexSerie) in Object.entries(
              dataTable.series
            )"
          >
            <tr
              v-for="([id_circuit, circuit], indexCircuit) of Object.entries(
                serie.id_circuits
              )"
              :key="`${numeroSerie}-${id_circuit}`"
            >
              <td
                v-if="indexCircuit == 0"
                :rowSpan="Object.entries(serie.id_circuits).length"
              >
                {{ numeroSerie }}
              </td>
              <td>
                <input
                  v-if='$store.getters.droitMax >= 5'
                  type="checkbox"
                  v-model="circuit.valid"
                  :disabled='freezeValid'
                  @change="validChange(circuit.id_observation, circuit.valid)"
                />
                <template v-else>{{`${circuit.valid ? 'Oui' : 'Non'}`}}</template>
              </td>
              <td>{{ circuit.date }}</td>
              <td>{{ circuit.numero_circuit }}</td>
              <td>{{ circuit.nom_circuit }}</td>
              <td>{{ circuit.groupes }}</td>
              <td>{{ circuit.km }}</td>
              <td>{{ circuit.nb }}</td>
              <td>{{ round(circuit.nb / circuit.km, dec) }}</td>
              <td
                v-if="indexCircuit == 0"
                :rowSpan="Object.entries(serie.id_circuits).length"
              >
                {{ round(serie.moy, dec) }}
              </td>
              <td
                v-if="indexSerie == 0 && indexCircuit == 0"
                :rowSpan="
                  nbCircuits(settings.espece, settings.ug, settings.annee)
                "
              >
                {{ round(dataTable.moy, dec) }}
              </td>
              <td
                v-if="indexCircuit == 0"
                :rowSpan="Object.entries(serie.id_circuits).length"
              >
                {{ round(serie.e_moy, dec) }}
              </td>
              <td
                v-if="indexCircuit == 0"
                :rowSpan="Object.entries(serie.id_circuits).length"
              >
                {{ round(serie.e_moy_2, dec) }}
              </td>
              <td
                v-if="indexSerie == 0 && indexCircuit == 0"
                :rowSpan="
                  nbCircuits(settings.espece, settings.ug, settings.annee)
                "
              >
                {{ round(dataTable.s_e_moy_2, dec) }}
              </td>
              <td
                v-if="indexSerie == 0 && indexCircuit == 0"
                :rowSpan="
                  nbCircuits(settings.espece, settings.ug, settings.annee)
                "
              >
                {{ round(dataTable.s_e_moy_2_n_nm1, dec) }}
              </td>
              <td
                v-if="indexSerie == 0 && indexCircuit == 0"
                :rowSpan="
                  nbCircuits(settings.espece, settings.ug, settings.annee)
                "
              >
                {{ round(dataTable.E, dec) }}
              </td>
              <td
                v-if="indexSerie == 0 && indexCircuit == 0"
                :rowSpan="
                  nbCircuits(settings.espece, settings.ug, settings.annee)
                "
              >
                {{ round(dataTable.inf, dec) }}
              </td>
              <td
                v-if="indexSerie == 0 && indexCircuit == 0"
                :rowSpan="
                  nbCircuits(settings.espece, settings.ug, settings.annee)
                "
              >
                {{ round(dataTable.sup, dec) }}
              </td>
            </tr>
          </template>
        </tbody>
      </table>
      <pre>
      </pre>
    </div>
  </div>
</template>

<script>
import listForm from "@/components/form/list-form";
import { apiRequest } from "@/core/js/data/api.js";

export default {
  name: "in-table",
  components: { listForm },
  data: () => ({
    dataIn: null,
    configChoix: {},
    ready: false,
    settings: { espece: "Cerf", ug: "Méjean", annee: "2019" },
    dataTable: null,
    dec: 4,
    freezeValid: false,
  }),
  methods: {
    round(x, dec) {
      if (x == 0) return 0;
      if (x == null) return '';
      const e = 10 ** dec;
      return Math.round(x * e) / e;
    },
    validChange(id_observation, valid) {
      this.freezeValid = true;
      console.log("validChange", id_observation, valid);
      apiRequest("PATCH", 'api/in/valid_obs/',{ data: { id_observation, valid } }).then((data)=>{
        // this.dataIn = data;
        data
        setTimeout(()=>{
          this.initInTable();
          this.freezeValid = false;
        console.log("validChange Request ok", id_observation, valid);
        });

        //on fait un petit snack pour le style
      });
    },
    initInTable() {
      this.dataTable = null;
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
      const annees = ugs[this.settings.ug].annees;
      const annee = annees[this.settings.annee];
      this.dataTable = annee;
      console.log("initTable", annee);
      return annee;
    },

    nbCircuits(espece, ug, annee) {
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
      console.log("settingsChange", this.ready);
      if (!this.ready) {
        return;
      }
      if (!this.items("ug").includes(this.settings.ug)) {
        console.log('no ug')
        this.settings.ug = null;
      }

      if (!this.items("annee").includes(this.settings.annee)) {
        console.log('no annee')
        this.settings.annee = null;
      }

      this.configChoix.ug.items = this.items("ug");
      this.configChoix.annee.items = this.items("annee");

      this.configChoix.ug_save = {...this.configChoix.ug}
      this.configChoix.annee_save = {...this.configChoix.annee}

      this.configChoix.ug = this.configChoix.annee =null

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
    }
  },

  mounted() {
    this.$store.dispatch("in_results").then(data => {
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
        label: "Ug",
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
      this.initInTable();
    });
  }
};
</script>

<style lang="css">
th, td {
  font-size: 0.9em;
  border: 1px solid;
  padding: 2px;
}
</style>
