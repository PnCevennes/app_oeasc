<template>
  <div>
    <!-- Choix des paramètres pour le bilan -->
    <generic-form
      :config="{
        ...$store.getters.configFormContentChasse,
        value: bilanParams
      }"
    ></generic-form>

    <!-- Titre et infos -->
    <h1>Bilan synthétique et analyse des plans de chasse</h1>

    <div v-if="!infos.nom_saison">
      <v-progress-linear
        indeterminate
        color="yellow darken-2"
      ></v-progress-linear>
    </div>

    <div v-else>
      <ul>
        <li><b>Saison</b> : {{ infos.nom_saison }}</li>
        <li><b>Echelle</b> : {{ infos.echelle }}</li>
        <li><b>Espèce</b> : {{ infos.nom_espece }}</li>
        <li><b>Nombre d'attributions</b> : {{ infos.nb_attribution }}</li>
        <li><b>Nombre de réalisations</b> : {{ infos.nb_realisation }}</li>
        <li><b>Taux de réalisation</b> : {{ infos.taux_realisation }}%</li>
      </ul>

      <!-- Bilan chasse -->
      <graph-chasse v-bind="bilanParams" type="bilan"> </graph-chasse>

      <!-- Graphiques -->

      <!-- Sexe age mode chasse -->
      <v-row>
        <v-col>
          <restitution2
            display="graph"
            fieldName="label_sexe"
            dataType="chasse"
            typeGraph="pie"
            title="Part des sexes"
            :filters="{ ...bilanParams }"
          ></restitution2>
        </v-col>
        <v-col>
          <restitution2
            display="graph"
            fieldName="label_classe_age"
            dataType="chasse"
            typeGraph="pie"
            title="Part des classes d'âge"
            :filters="{ ...bilanParams }"
          ></restitution2>
        </v-col>
        <v-col>
          <restitution2
            display="graph"
            fieldName="label_mode_chasse"
            dataType="chasse"
            typeGraph="pie"
            title="Part des modes de chasse"
            :filters="{ ...bilanParams }"
          ></restitution2>
        </v-col>
      </v-row>

      <!-- Chronologie des prélèvements -->
      <v-row>
        <v-col>
          <restitution2
            display="graph"
            fieldName="mois_txt"
            dataType="chasse"
            typeGraph="line"
            :title="`Chronologie des prélèvements (Saison ${infos.nom_saison})`"
            :filters="{ ...bilanParams }"
          ></restitution2>
        </v-col>
        <v-col>
          <restitution2
            display="graph"
            fieldName2="nom_saison"
            fieldName="mois_txt"
            dataType="chasse"
            typeGraph="line"
            :title="`Chronologie des prélèvements (5 dernières saisons)`"
            :filters="{ ...bilanParams, id_saison: infos.last_5_id_saison }"
          ></restitution2>
        </v-col>
      </v-row>

      <div v-if="infos.nom_espece == 'Cerf'">
        <h2>Résultats par catégories</h2>
        <v-row>
          <v-col>
            <restitution2
            display="graph"
            fieldName="bracelet"
            dataType="chasse"
            typeGraph="pie"
            :title="`Prélèvements par type de bracelet`"
            :filters="{ ...bilanParams }"
          ></restitution2>
          </v-col>
        </v-row>
        <v-row>
          <v-col v-for="bracelet in ['CEM', 'CEFF', 'CEFFD']" :key="bracelet">
            <graph-chasse
              v-bind="bilanParams"
              :bracelet="bracelet"
              type="attribution_bracelet"
            >
            </graph-chasse>
          </v-col>
        </v-row>
        <v-row>
          <v-col>
            <restitution2
              display="graph"
              fieldName2="bracelet"
              fieldName="mois_txt"
              dataType="chasse"
              typeGraph="column"
              :stacking="true"
              :title="`Chronologie des prélèvements par catégorie`"
              :filters="{ ...bilanParams }"
            ></restitution2>
          </v-col>

          <v-col>
            <restitution2
              display="graph"
              fieldName2="bracelet"
              fieldName="label_mode_chasse"
              dataType="chasse"
              typeGraph="column"
              :stacking="true"
              :title="`Répartition par mode de chasse  et par catégorie`"
              :filters="{ ...bilanParams }"
            ></restitution2>
          </v-col>
        </v-row>

        <v-row>
          <v-col>
            <restitution2
              display="graph"
              fieldName="label_classe_age"
              dataType="chasse"
              typeGraph="pie"
              :title="`Part des classes d'âge (CEM)`"
              :filters="{ ...bilanParams, bracelet: ['CEM'] }"
            ></restitution2>
          </v-col>
          <v-col>
            <restitution2
              display="graph"
              fieldName="label_classe_age"
              dataType="chasse"
              typeGraph="pie"
              :title="`Part des classes d'âge (CEFF)`"
              :filters="{ ...bilanParams, bracelet: ['CEFF'] }"
            ></restitution2>
          </v-col>
        </v-row>
      </div>
    </div>
  </div>
</template>

<script>
import genericForm from "@/components/form/generic-form";
import graphChasse from "./graph-chasse.vue";
import restitution2 from "@/modules/restitution2/restitution";

export default {
  name: "pageTypeChasse",
  components: { genericForm, graphChasse, restitution2 },
  data: () => ({
    bilanParams: {
      id_espece: null,
      espece: null,
      id_zone_indicative: [],
      id_zone_cynegetique: [],
      id_secteur: [],
      id_saison: null
    },
    infos: {}
  }),
  watch: {
    bilanParams: {
      deep: true,
      handler() {
        this.processBilanParams();
      }
    }
  },
  methods: {
    processBilanParams() {
      this.infos = {};
      if (!this.bilanParams.id_saison && this.bilanParams.id_espece) {
        return;
      }
      console.log("getBilanParams");
      this.$store
        .dispatch("getAnalyseBilanInfos", this.bilanParams)
        .then(infos => {
          this.infos = infos;
        });
    }
  }
};
</script>
