<template>
  <div style="width: 1200px">
    <!--
      Formulaire générique pour sélectionner les paramètres de filtre du bilan.
      Utilisé pour permettre à l'utilisateur de choisir l'espèce, la saison, la zone, etc.
      Les valeurs sélectionnées sont stockées dans bilanParams.
    -->
    <generic-form
      :config="{
        ...$store.getters.configFormContentChasse(),
        value: bilanParams,
      }"
    ></generic-form>

    <!-- Titre principal de la page -->
    <h1>Bilan synthétique et analyse des plans de chasse</h1>

    <!-- Affiche un loader tant que les infos ne sont pas chargées -->
    <div v-if="!infos.nom_saison">
      <v-progress-linear
        indeterminate
        color="yellow darken-2"
      ></v-progress-linear>
    </div>

    <!-- Affiche les informations du bilan une fois chargées -->
    <div v-else>
      <ul>
        <li>
          <b>Saison</b>
          : {{ infos.nom_saison }}
        </li>
        <li>
          <b>Echelle</b>
          : {{ infos.echelle }}
        </li>
        <li>
          <b>Superficie en ha</b>
          : {{ infos.superficie }}
        </li>
        <li>
          <b>Espèce</b>
          : {{ infos.nom_espece }}
        </li>
        <li>
          <b>Nombre d'attributions</b>
          : {{ infos.nb_attribution }}
        </li>
        <li>
          <b>Nombre de réalisations</b>
          : {{ infos.nb_realisation }}
        </li>
        <li>
          <b>Taux de réalisation</b>
          : {{ infos.taux_realisation }}%
        </li>
        <li>
          <b>Nombre de transfert vers la/les zc</b>
          : {{ infos.transfert_zc }}
        </li>
        <li>
          <b>Nombre de transfert vers la/les zi</b>
          : {{ infos.transfert_zi }}
        </li>
      </ul>

      <!--
        Graphique principal du bilan de chasse.
        Utilise les paramètres sélectionnés dans bilanParams.
      -->
      <graph_bilan_evolution :bilanParams="bilanParams"></graph_bilan_evolution>

      <!-- Graphiques complémentaires -->

      <!--
        Graphiques circulaires pour la répartition par sexe, classe d'âge et mode de chasse.
        Utilisés pour analyser la structure des prélèvements.
      -->
      <v-row style="min-height: 400px">
        <v-col>
          <graphChasseIce
            :data_db="data_ice_masse_corporelle"
            :filterParams="bilanParams"
            poids_ou_dagues="true"
            height="450px"
          ></graphChasseIce>
        </v-col>
      </v-row>
      <v-row style="min-height: 400px">
        <v-col>
          <graphChasseIcePoints
            :data_db="data_ice_masse_corporelle"
            :filterParams="bilanParams"
          ></graphChasseIcePoints>
        </v-col>
      </v-row>

      <v-row style="min-height: 400px">
        <v-col>
          <graphChasseIce
            :data_db="data_ice_dagues"
            :filterParams="bilanParams"
            poids_ou_dagues="false"
          ></graphChasseIce>
        </v-col>
      </v-row>
      <v-row style="min-height: 400px">
        <v-col>
          <graphChasseIcePoints
            :data_db="data_ice_dagues"
            :filterParams="bilanParams"
          ></graphChasseIcePoints>
        </v-col>
      </v-row>
    </div>
  </div>
</template>

<script>
import Highcharts from 'highcharts';
import exportingInit from 'highcharts/modules/exporting';
import offlineExporting from 'highcharts/modules/offline-exporting';
import genericForm from '@/components/form/generic-form.vue';
import graph_bilan_evolution from './graph/graph_bilan_evolution.vue';
import { apiRequest } from '@/core/js/data/api.js';
import graphChasseIce from './graph/graph_ice.vue';
import graphChasseIcePoints from './graph/graph_ice_points.vue';

// Modification de highcharts pour permettre l'export des graphiques
exportingInit(Highcharts); // initialise le module export, doit être fait après l'import de highcharts
offlineExporting(Highcharts); // initialise l'export coté client, doit être fait après l'import de highcharts

export default {
  name: 'pageBilanDonneeChasse',
  components: {
    genericForm,
    graph_bilan_evolution,
    graphChasseIce,
    graphChasseIcePoints,
  },

  // Déclaration des données réactives du composant
  data: () => ({
    // Paramètres de filtre pour les requêtes. Correspond au formulaire en haut de page (saison, espèce, secteur, zone, etc.)
    bilanParams: {
      id_espece: null, // Identifiant de l'espèce sélectionnée
      espece: null, // Nom de l'espèce (optionnel, parfois utilisé pour affichage)
      id_zone_indicative: [], // Liste des zones indicatives sélectionnées
      id_zone_cynegetique: [], // Liste des zones cynégétiques sélectionnées
      id_secteur: [], // Liste des secteurs sélectionnés
      id_saison: null, // Identifiant de la saison sélectionnée
    },
    nb_saison_chronologie: 5, // Nombre de saisons à afficher dans le graphique de chronologie des prélèvements
    // Informations détaillées du bilan, récupérées depuis l'API après sélection des filtres
    infos: {},
    data_bilan_principal: null, // histogramme bilan principal
    data_ice_masse_corporelle: null, // graphique ice poids ou dagues
    data_ice_dagues: null, // graphique ice poids ou dagues
  }),

  watch: {
    bilanParams: {
      deep: true,
      handler() {
        this.recuperation_data(this.bilanParams);
      },
    },
    nb_saison_chronologie() {
      apiRequest('GET', 'api/chasse/realisations_par_mois_sur_dernieres_saisons', {
        params: { ...this.bilanParams, nb_saison: this.nb_saison_chronologie },
      }).then((result) => {
        this.data_chronologie_prelevement = result;
      });
    },
  },
  methods: {
    /**
     * Récupère les données du bilan depuis l'API en fonction des paramètres sélectionnés dans le formulaire.
     * Les données récupérées sont ensuite stockées dans les variables d'état du composant (infos, data_cam_sexe_age, data_ice_masse_corporelle, data_ice_dagues) pour être utilisées dans les graphiques.
     */
    recuperation_data(bilanParams) {
      // this.infos = {};
      // si il manque la saison ou l'espece on annule.
      if (!this.bilanParams.id_saison || !this.bilanParams.id_espece) {
        return;
      }

      apiRequest('GET', 'api/chasse/results/infos', { params: bilanParams }).then((infos) => {
        this.infos = infos;
      });

      apiRequest('GET', 'api/chasse/count_categorie_realisations', { params: bilanParams }).then(
        (result) => {
          this.data_cam_sexe_age = result;
        }
      );

      apiRequest('GET', 'api/chasse/results/ice', {
        params: { ...bilanParams, poids_ou_dagues: true },
      }).then((result) => {
        this.data_ice_masse_corporelle = result;
      });

      apiRequest('GET', 'api/chasse/results/ice', {
        params: { ...bilanParams, poids_ou_dagues: false },
      }).then((result) => {
        this.data_ice_dagues = result;
      });
    },
  },
};
</script>
