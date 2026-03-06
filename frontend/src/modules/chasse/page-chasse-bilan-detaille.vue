<template>
  <div>
    <!--
      Formulaire générique pour sélectionner les paramètres de filtre du bilan.
      Utilisé pour permettre à l'utilisateur de choisir l'espèce, la saison, la zone, etc.
      Les valeurs sélectionnées sont stockées dans bilanParams.
    -->
    <generic-form :config="{
      ...$store.getters.configFormContentChasse(),
      value: bilanParams
    }"></generic-form>

    <!-- Titre principal de la page -->
    <h1>Bilan synthétique et analyse des plans de chasse</h1>

    <!-- Affiche un loader tant que les infos ne sont pas chargées -->
    <div v-if="!infos.nom_saison">
      <v-progress-linear indeterminate color="yellow darken-2"></v-progress-linear>
    </div>

    <!-- Affiche les informations du bilan une fois chargées -->
    <div v-else>
      <ul>
        <li><b>Saison</b> : {{ infos.nom_saison }}</li>
        <li><b>Echelle</b> : {{ infos.echelle }}</li>
        <li><b>Espèce</b> : {{ infos.nom_espece }}</li>
        <li><b>Nombre d'attributions</b> : {{ infos.nb_attribution }}</li>
        <li><b>Nombre de réalisations</b> : {{ infos.nb_realisation }}</li>
        <li><b>Taux de réalisation</b> : {{ infos.taux_realisation }}%</li>
        <li><b>Nombre de transfert vers la/les zc</b> : {{ infos.transfert_zc }}</li>
        <li><b>Nombre de transfert vers la/les zi</b> : {{ infos.transfert_zi }}</li>
      </ul>

      <!--
        Graphique principal du bilan de chasse.
        Utilise les paramètres sélectionnés dans bilanParams.
      -->
      <!-- <graph-chasse v-bind="bilanParams" type="bilan"> </graph-chasse> -->
      <graph_bilan_evolution :bilanParams="bilanParams"> </graph_bilan_evolution>




      <!-- Graphiques complémentaires -->


      <!--
        Graphiques circulaires pour la répartition par sexe, classe d'âge et mode de chasse.
        Utilisés pour analyser la structure des prélèvements.
      -->
      <v-row style="min-height: 400px;">

        <v-col style="width: 70%">
          <camembert :data_db="data_cam_sexe_age" fieldName="text" fieldValue="count" :code_couleurs="code_couleurs_repartition_sexe_age"
            title="Répartition par sexe et âge"></camembert>
        </v-col>
        <v-col style="width: 70%">
          <camembert :data_db="data_part_mode_chasse" fieldName="text" fieldValue="count"
            title="Répartition par mode de chasse"></camembert>
        </v-col>

      </v-row>

      <!--
        Graphiques linéaires pour la chronologie des prélèvements.
        Premier graphique : chronologie pour la saison sélectionnée.
        Deuxième graphique : chronologie sur les 5 dernières saisons.
      -->

      <v-row>
        <v-col>
          <graph_lignes_multiples :data_db="data_chronologie_prelevement" field_x="mois" field_y="nb_realisations" fields_line="nom_saison" 
            :title="`Chronologie des prélèvements (${nb_saison_chronologie} dernières saisons)`"
            ></graph_lignes_multiples>
        </v-col>
        <!-- ajout d'un mini formulaire pour modifier nb_saison_chronologie  -->
        <v-col style="max-width: 300px; min-width: 200px;">
          <v-text-field v-model="nb_saison_chronologie" label="Nombre de saisons à afficher" type="number" min="1" max="10"></v-text-field>
        </v-col>
      </v-row>

      <!--
        Section spécifique pour l'espèce "Cerf".
        Affiche des graphiques supplémentaires par catégorie de bracelet.
      -->
      <!-- <div v-if="infos.nom_espece == 'Cerf'"> -->
      <div>
        <!-- <h2>Résultats par catégories</h2> -->
        <v-row>
          
          <v-col style="width: 70%">
            <camembert :data_db="data_count_realisations_par_type_de_bracelet" fieldName="type_bracelet" fieldValue="nb_bracelet"
              title="Prélèvements par type de bracelet"></camembert>
          </v-col>
          <v-col>
            <histogramme_comparatif :data_db="data_nbRealisations_vs_nbAttributions"
              fieldReference="nb_attributions"
              nameReference="attributions"
              fieldGroup="type_bracelet" :listfieldValues="['nb_realisations']"
              nameGroup=" Type de bracelets" :listNameValues="['nb Réalisations']"
              title="Comparatif des prélèvements par type de bracelet"></histogramme_comparatif>
          </v-col>
        </v-row>
        <v-row>
          <!--
            Affiche un graphique pour chaque type de bracelet (CEM, CEFF, CEFFD).
            Permet d'analyser les attributions par catégorie.
          -->
          <!-- <v-col v-for="bracelet in ['CEM', 'CEFF', 'CEFFD']" :key="bracelet">
            <graph-chasse v-bind="bilanParams" :bracelet="bracelet" type="attribution_bracelet">
            </graph-chasse>
          </v-col> -->
        </v-row>


        <v-row>
          <v-col>
            <restitution2 display="graph" fieldName2="bracelet" fieldName="mois_txt"
              dataType="chasse" typeGraph="column" :stacking="true"
              :title="`Chronologie des prélèvements par catégorie`" :filters="{ ...bilanParams }">
            </restitution2>
          </v-col>

          <v-col>
            <restitution2 display="graph" fieldName2="bracelet" fieldName="label_mode_chasse"
              dataType="chasse" typeGraph="column" :stacking="true"
              :title="`Répartition par mode de chasse  et par catégorie`"
              :filters="{ ...bilanParams }"></restitution2>
          </v-col>
        </v-row>

        <v-row>
          <!--
            Graphiques circulaires pour la répartition par classe d'âge,
            séparés pour chaque type de bracelet (CEM et CEFF).
          -->
          <!-- <v-col>
            <restitution2 display="graph" fieldName="label_classe_age" dataType="chasse"
              typeGraph="pie" :title="`Part des classes d'âge (CEM)`"
              :filters="{ ...bilanParams, bracelet: ['CEM'] }"></restitution2>
          </v-col>
          <v-col>
            <restitution2 display="graph" fieldName="label_classe_age" dataType="chasse"
              typeGraph="pie" :title="`Part des classes d'âge (CEFF)`"
              :filters="{ ...bilanParams, bracelet: ['CEFF'] }"></restitution2>
          </v-col> -->
        </v-row>

      </div>
    </div>
  </div>
</template>

<script>
import Highcharts from "highcharts";
import exportingInit from "highcharts/modules/exporting";
import offlineExporting from "highcharts/modules/offline-exporting";
import genericForm from "@/components/form/generic-form.vue";
import graphChasse from "./graph-chasse.vue";
import restitution2 from "@/modules/restitution2/restitution.vue";
import camembert from "../../components/graph/camembert.vue";
import graph_lignes_multiples from "../../components/graph/graph_lignes_multiples.vue";
import graph_bilan_evolution from "./graph/graph_bilan_evolution.vue";
import { apiRequest } from "@/core/js/data/api.js";
import histogramme_comparatif from "../../components/graph/histogramme_comparatif.vue";


// Modification de highcharts pour permettre l'export des graphiques
exportingInit(Highcharts); // initialise le module export, doit être fait après l'import de highcharts
offlineExporting(Highcharts); // initialise l'export coté client, doit être fait après l'import de highcharts




export default {
  name: "pageChasseBilanDetaille",
  components: { genericForm, graphChasse, restitution2, camembert, graph_bilan_evolution, graph_lignes_multiples, histogramme_comparatif },

  // Déclaration des données réactives du composant
  data: () => ({
    // Paramètres de filtre pour les requêtes. Correspond au formulaire en haut de page (saison, espèce, secteur, zone, etc.)
    bilanParams: {
      id_espece: null,             // Identifiant de l'espèce sélectionnée
      espece: null,                // Nom de l'espèce (optionnel, parfois utilisé pour affichage)
      id_zone_indicative: [],      // Liste des zones indicatives sélectionnées
      id_zone_cynegetique: [],     // Liste des zones cynégétiques sélectionnées
      id_secteur: [],              // Liste des secteurs sélectionnés
      id_saison: null              // Identifiant de la saison sélectionnée
    },
    nb_saison_chronologie: 5, // Nombre de saisons à afficher dans le graphique de chronologie des prélèvements
    // Informations détaillées du bilan, récupérées depuis l'API après sélection des filtres
    infos: {},
    data_bilan_principal: null, // histogramme bilan principal
    data_cam_sexe_age: null, // camembert sexe/age
    data_part_mode_chasse: null, // camembert part mode de chasse
    data_chronologie_prelevement: null, // graph multi-lignes chronologie des prélèvements
    data_count_realisations_par_type_de_bracelet: null, // graph multi-lignes chronologie des prélèvements par type de bracelet
    data_nbRealisations_vs_nbAttributions: null, // histogramme comparatif nb réalisations vs nb attributions

    code_couleurs_repartition_sexe_age: {
      // Mâles (tons bleus) — plus jeune = ton plus clair
      "Mâle - Adulte": "#528adf",        // bleu foncé
      "Mâle - Sub-adulte": "#5cabeb",    // bleu moyen
      "Mâle - Juvénile": "#90CAF9",        // bleu clair
      "Mâle - Inconnu": "#a9cdeb",   // cas particulier, ton intermédiaire

      // Femelles (tons rose) — plus jeune = ton plus clair
      "Femelle - Adulte": "#e470a2",     // rose foncé
      "Femelle - Sub-adulte": "#d86d91", // rose moyen
      "Femelle - Juvénile": "#F8BBD0",   // rose clair
      "Femelle - Inconnu": "#e6cad5",// ton intermédiaire

      // Indéterminés (tons gris) — plus jeune = ton plus clair
      "Indéterminé - Adulte": "#424242",      // gris foncé
      "Indéterminé - Sub-adulte": "#9E9E9E",  // gris moyen
      "Indéterminé - Juvénile": "#E0E0E0",    // gris clair
      "Indéterminé - Indéterminé": "#9E9E9E", // ton intermédiaire
    }

  
  
  }),

  watch: {
    bilanParams: {
      deep: true,
      handler() {
        this.recuperation_data(this.bilanParams);
      }
    },
      nb_saison_chronologie() {
        apiRequest("GET", 'api/chasse/realisations_par_mois_sur_dernieres_saisons/',  { params: { ...this.bilanParams, nb_saison: this.nb_saison_chronologie } }) 
        .then(result => {
          this.data_chronologie_prelevement = result;
        });
      
      }
  },
  methods: {
    /**
     * Traite les paramètres du bilan pour récupérer les informations associées.
     *
     * Cette fonction initialise l'objet `infos` à vide, puis vérifie la validité des paramètres du bilan.
     * Si l'identifiant de saison (`id_saison`) n'est pas défini mais que l'identifiant d'espèce (`id_espece`) l'est,
     * la fonction retourne immédiatement sans effectuer d'action supplémentaire.
     * 
     * Sinon, elle déclenche l'action Vuex `getAnalyseBilanInfos` avec les paramètres du bilan (`bilanParams`).
     * Lorsque la promesse est résolue, elle met à jour l'objet `infos` avec les données reçues.
     *
     * Cas d'utilisation :
     * - Cette fonction est utilisée lorsqu'on souhaite afficher ou mettre à jour les informations détaillées
     *   d'un bilan de chasse, en fonction des paramètres sélectionnés (saison, espèce, etc.).
     * - Elle permet de s'assurer que seules les requêtes valides sont envoyées au store.
     */
    recuperation_data(bilanParams) {
      // this.infos = {};
      // si il manque la saison et l'espece on annule.
      if (!this.bilanParams.id_saison && this.bilanParams.id_espece) {
        return;
      }

      // console.log("bilanParams", bilanParams);
      // this.graph_categories = apiRequest("GET", 'api/chasse/results/infos',  { params });

      apiRequest("GET", 'api/chasse/results/infos',  { params: bilanParams }).then(infos => {
          this.infos = infos;
        });

      apiRequest("GET", 'api/chasse/count_categorie_realisations/',  { params: bilanParams }) 
        .then(result => {
          this.data_cam_sexe_age = result;
        });
      apiRequest("GET", 'api/chasse/count_mode_chasse_realisations/',  { params: bilanParams }) 
        .then(result => {
          this.data_part_mode_chasse = result;
        });
      apiRequest("GET", 'api/chasse/realisations_par_mois_sur_dernieres_saisons/',  { params: { ...bilanParams, nb_saison: this.nb_saison_chronologie } }) 
        .then(result => {
          this.data_chronologie_prelevement = result;
        });
      
      apiRequest("GET", 'api/chasse/count_realisations_par_type_de_bracelet/',  { params: { ...bilanParams, nb_saison: this.nb_saison_chronologie } }) 
        .then(result => {
          this.data_count_realisations_par_type_de_bracelet = result;
          // console.log("data_count_realisations_par_type_de_bracelet", this.data_count_realisations_par_type_de_bracelet);
        });
      apiRequest("GET", 'api/chasse/difference_nbRealisations_nbAttributions/',  { params: { ...bilanParams, nb_saison: this.nb_saison_chronologie } }) 
        .then(result => {
          this.data_nbRealisations_vs_nbAttributions = result;
          // console.log("data_nbRealisations_vs_nbAttributions", this.data_nbRealisations_vs_nbAttributions);
        });


    }
  }

  
};
</script>
