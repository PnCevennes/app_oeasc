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
        <v-col style="width: 70%">
          <camembert
            :data_db="data_cam_sexe_age"
            fieldName="text"
            fieldValue="count"
            :code_couleurs="code_couleurs_repartition_sexe_age"
            title="Répartition par sexe et âge"
          ></camembert>
        </v-col>
        <v-col style="width: 70%">
          <camembert
            :data_db="data_part_mode_chasse"
            fieldName="text"
            fieldValue="count"
            :code_couleurs="code_couleurs_mode_chasse"
            title="Répartition par mode de chasse"
          ></camembert>
        </v-col>
      </v-row>

      <!--
        Graphiques linéaires pour la chronologie des prélèvements.
        Premier graphique : chronologie pour la saison sélectionnée.
        Deuxième graphique : chronologie sur les 5 dernières saisons.
      -->

      <v-row>
        <v-col>
          <graph_lignes_multiples
            :data_db="data_chronologie_prelevement"
            field_x="mois"
            field_y="nb_realisations"
            fields_line="nom_saison"
            :title="`Chronologie des prélèvements (${nb_saison_chronologie} dernières saisons)`"
          ></graph_lignes_multiples>
        </v-col>
        <!-- ajout d'un mini formulaire pour modifier nb_saison_chronologie  -->
        <v-col style="max-width: 300px; min-width: 200px">
          <v-text-field
            v-model="nb_saison_chronologie"
            label="Nombre de saisons à afficher"
            type="number"
            min="1"
            max="10"
          ></v-text-field>
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
            <camembert
              :data_db="data_count_realisations_par_type_de_bracelet"
              fieldName="type_bracelet"
              fieldValue="nb_bracelet"
              :code_couleurs="code_couleurs_type_bracelet"
              title="Prélèvements par type de bracelet"
            ></camembert>
          </v-col>
          <v-col>
            <histogramme_comparatif
              :data_db="data_nbRealisations_vs_nbAttributions"
              fieldReference="nb_attributions"
              nameReference="attributions"
              fieldGroup="type_bracelet"
              :listfieldValues="['nb_realisations']"
              nameGroup=" Type de bracelets"
              :listNameValues="['nb Réalisations']"
              :code_couleurs_categorie="code_couleurs_comparatif_type_bracelet"
              couleur_reste="#e0e0e0"
              title="Comparatif des prélèvements par type de bracelet"
            ></histogramme_comparatif>
          </v-col>
        </v-row>

        <v-row>
          <v-col>
            <colonnes_empilees
              :data_db="data_nb_type_bracelet_par_mois"
              fieldGroup="mois"
              :values_field="['type de bracelet', 'réalisations']"
              :code_couleurs="code_couleurs_type_bracelet"
              :title="`Chronologie des prélèvements par catégorie`"
            ></colonnes_empilees>
          </v-col>

          <v-col>
            <colonnes_empilees
              :data_db="data_repartition_mode_chasse_par_type_bracelet"
              fieldGroup="mode_chasse"
              :values_field="['type de bracelet', 'réalisations']"
              :code_couleurs="code_couleurs_type_bracelet"
              :title="`Réalisation par mode de chasse et par type de bracelet`"
            ></colonnes_empilees>
          </v-col>
        </v-row>

        <v-row>
          <!--
            Graphiques circulaires pour la répartition par classe d'âge,
            séparés pour chaque type de bracelet (CEM et CEFF).
          -->
          <v-col>
            <colonnes_empilees
              :data_db="data_nbrealisation_par_age_par_type_bracelet"
              fieldGroup="type_bracelet"
              :values_field="['classe_age', 'réalisations']"
              :code_couleurs_categorie="code_couleurs_age_par_type_bracelet"
              :title="`Prélèvements par classe d'âge et par catégorie`"
            ></colonnes_empilees>
          </v-col>
          <v-col></v-col>
        </v-row>
      </div>
    </div>
  </div>
</template>

<script>
import Highcharts from 'highcharts';
import exportingInit from 'highcharts/modules/exporting';
import offlineExporting from 'highcharts/modules/offline-exporting';
import genericForm from '@/components/form/generic-form.vue';
import camembert from '../../components/graph/camembert.vue';
import graph_lignes_multiples from '../../components/graph/graph_lignes_multiples.vue';
import graph_bilan_evolution from './graph/graph_bilan_evolution.vue';
import { apiRequest } from '@/core/js/data/api.js';
import histogramme_comparatif from '../../components/graph/histogramme_comparatif.vue';
import colonnes_empilees from '../../components/graph/colonnes_empilees.vue';

// Modification de highcharts pour permettre l'export des graphiques
exportingInit(Highcharts); // initialise le module export, doit être fait après l'import de highcharts
offlineExporting(Highcharts); // initialise l'export coté client, doit être fait après l'import de highcharts

export default {
  name: 'pageChasseBilanDetaille',
  components: {
    genericForm,
    camembert,
    graph_bilan_evolution,
    graph_lignes_multiples,
    histogramme_comparatif,
    colonnes_empilees,
  },

  // Déclaration des données réactives du composant
  data() {
    // ------------------------------------------------------------------
    // Rampes de couleur communes aux graphiques "sexe / classe d'âge".
    // Principe :
    //   - la TEINTE indique le sexe   : bleu = Mâle, orange/jaune = Femelle, violet = Indéterminé
    //     (repris des couleurs par défaut de Highcharts : #7cb5ec / #f7a35c / #8085e9)
    //   - la CLARTÉ indique l'âge      : plus l'animal est jeune, plus la couleur est claire
    //     (Adulte le plus foncé -> Sub-adulte -> Juvénile -> Inconnu / Indéterminé le plus clair)
    // ------------------------------------------------------------------
    const rampe_male = {
      Adulte: '#1f5c99',
      'Sub-adulte': '#4a90d9',
      Juvénile: '#8fc1ec',
      Inconnu: '#c6e0f7',
      Indéterminé: '#c6e0f7',
    };
    const rampe_femelle = {
      Adulte: '#f7b264', // orange foncé
      'Sub-adulte': '#fad090',
      Juvénile: '#fff3af',
      Inconnu: '#fffbea', // jaune très clair
      Indéterminé: '#fffbea',
    };
    const rampe_indetermine = {
      Adulte: '#3f3f9e',
      'Sub-adulte': '#7076d6',
      Juvénile: '#a6aae8',
      Inconnu: '#d2d4f5',
      Indéterminé: '#d2d4f5',
    };

    return {
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
      data_cam_sexe_age: null, // camembert sexe/age
      data_part_mode_chasse: null, // camembert part mode de chasse
      data_chronologie_prelevement: null, // graph multi-lignes chronologie des prélèvements
      data_count_realisations_par_type_de_bracelet: null, // graph multi-lignes chronologie des prélèvements par type de bracelet
      data_nbRealisations_vs_nbAttributions: null, // histogramme comparatif nb réalisations vs nb attributions
      data_nb_type_bracelet_par_mois: null, // graph multi-lignes chronologie des prélèvements par type de bracelet
      data_repartition_mode_chasse_par_type_bracelet: null, // graph multi-lignes chronologie des prélèvements par type de bracelet et par mode de chasse
      data_nbrealisation_par_age_par_type_bracelet: null, // graph multi-lignes chronologie des prélèvements par type de bracelet et par classe d'âge

      // Camembert "Répartition par sexe et âge".
      // Teinte = sexe (bleu / orange-jaune / violet), clarté = âge (plus jeune = plus clair).
      code_couleurs_repartition_sexe_age: {
        'Mâle - Adulte': rampe_male['Adulte'],
        'Mâle - Sub-adulte': rampe_male['Sub-adulte'],
        'Mâle - Juvénile': rampe_male['Juvénile'],
        'Mâle - Inconnu': rampe_male['Inconnu'],
        'Mâle - Indéterminé': rampe_male['Indéterminé'],

        'Femelle - Adulte': rampe_femelle['Adulte'],
        'Femelle - Sub-adulte': rampe_femelle['Sub-adulte'],
        'Femelle - Juvénile': rampe_femelle['Juvénile'],
        'Femelle - Inconnu': rampe_femelle['Inconnu'],
        'Femelle - Indéterminé': rampe_femelle['Indéterminé'],

        'Indéterminé - Adulte': rampe_indetermine['Adulte'],
        'Indéterminé - Sub-adulte': rampe_indetermine['Sub-adulte'],
        'Indéterminé - Juvénile': rampe_indetermine['Juvénile'],
        'Indéterminé - Inconnu': rampe_indetermine['Inconnu'],
        'Indéterminé - Indéterminé': rampe_indetermine['Indéterminé'],
      },

      // Camembert "Répartition par mode de chasse" — couleur par mode de chasse
      // (palette par défaut de Highcharts, une teinte distincte par mode)
      code_couleurs_mode_chasse: {
        'Battue': '#7cb5ec',
        'Individuel': '#434348',
        'Affut': '#90ed7d',
        'Approche': '#f7a35c',
        'Poussée silencieuse': '#e4d354',
        'Indéterminé': '#8085e9',
      },

      // Couleur par type de bracelet. Utilisé pour :
      //  - le camembert "Prélèvements par type de bracelet"
      //  - les colonnes empilées "Chronologie des prélèvements par catégorie"
      //  - les colonnes empilées "Réalisation par mode de chasse et par type de bracelet"
      // Même logique de teinte que ci-dessus : bleu = catégories mâles, orange-jaune = femelles, violet = chevreuil.
      code_couleurs_type_bracelet: {
        CEM: '#1f5c99', // bleu foncé
        CEFFD: '#3f82c4', // bleu moyen
        MOM: '#6aa9e0', // bleu clair
        MOM1: '#a8ccef', // bleu très clair
        CEFF: '#f7b264', // orange foncé
        MOF: '#fad090', // orange moyen
        MOIJ: '#fff3af', // jaune clair
        CHI: '#7076d6', // violet
      },

      // Histogramme comparatif "Comparatif des prélèvements par type de bracelet"
      // -> couleur de la partie gauche (réalisations) de chaque ligne selon le type de bracelet.
      //    La partie droite (restant) est en gris clair (voir prop couleur_reste du composant).
      code_couleurs_comparatif_type_bracelet: {
        CEM: '#1f5c99',
        CEFFD: '#3f82c4',
        MOM: '#6aa9e0',
        MOM1: '#a8ccef',
        CEFF: '#f7b264', // orange foncé
        MOF: '#fad090', // orange moyen
        MOIJ: '#fff3af', // jaune clair
        CHI: '#7076d6',
      },

      // Colonnes empilées "Prélèvements par classe d'âge et par catégorie"
      // -> couleur qui dépend à la fois de la colonne (type de bracelet) et de la série (classe d'âge).
      //    Teinte = groupe du bracelet (bleu = mâles, orange-jaune = femelles, violet = chevreuil),
      //    clarté = classe d'âge (plus jeune = plus clair). "Inconnu" = même couleur que "Indéterminé".
      code_couleurs_age_par_type_bracelet: {
        CEM: { ...rampe_male },
        CEFFD: { ...rampe_male },
        MOM1: { ...rampe_male },
        MOM: { ...rampe_male },
        CEFF: { ...rampe_femelle },
        MOF: { ...rampe_femelle },
        MOIJ: { ...rampe_femelle },
        CHI: { ...rampe_indetermine },
      },
    };
  },

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
      // si il manque la saison ou l'espece on annule.
      if (!this.bilanParams.id_saison || !this.bilanParams.id_espece) {
        return;
      }

      // console.log("bilanParams", bilanParams);
      // this.graph_categories = apiRequest("GET", 'api/chasse/results/infos',  { params });

      apiRequest('GET', 'api/chasse/results/infos', { params: bilanParams }).then((infos) => {
        this.infos = infos;
      });

      apiRequest('GET', 'api/chasse/count_categorie_realisations', { params: bilanParams }).then(
        (result) => {
          this.data_cam_sexe_age = result;
        }
      );
      apiRequest('GET', 'api/chasse/count_mode_chasse_realisations', { params: bilanParams }).then(
        (result) => {
          this.data_part_mode_chasse = result;
        }
      );
      apiRequest('GET', 'api/chasse/realisations_par_mois_sur_dernieres_saisons', {
        params: { ...bilanParams, nb_saison: this.nb_saison_chronologie },
      }).then((result) => {
        this.data_chronologie_prelevement = result;
      });

      apiRequest('GET', 'api/chasse/count_realisations_par_type_de_bracelet', {
        params: { ...bilanParams, nb_saison: this.nb_saison_chronologie },
      }).then((result) => {
        this.data_count_realisations_par_type_de_bracelet = result;
        // console.log("data_count_realisations_par_type_de_bracelet", this.data_count_realisations_par_type_de_bracelet);
      });
      apiRequest('GET', 'api/chasse/difference_nbRealisations_nbAttributions', {
        params: { ...bilanParams, nb_saison: this.nb_saison_chronologie },
      }).then((result) => {
        this.data_nbRealisations_vs_nbAttributions = result;
        // console.log("data_nbRealisations_vs_nbAttributions", this.data_nbRealisations_vs_nbAttributions);
      });
      apiRequest('GET', 'api/chasse/count_realisations_par_par_mois_par_type_bracelet', {
        params: { ...bilanParams, nb_saison: this.nb_saison_chronologie },
      }).then((result) => {
        this.data_nb_type_bracelet_par_mois = result;
      });

      apiRequest('GET', 'api/chasse/count_mode_chasse_par_type_bracelet', {
        params: { ...bilanParams, nb_saison: this.nb_saison_chronologie },
      }).then((result) => {
        this.data_repartition_mode_chasse_par_type_bracelet = result;
      });
      apiRequest('GET', 'api/chasse/count_realisations_par_age_par_type_bracelet', {
        params: { ...bilanParams, nb_saison: this.nb_saison_chronologie },
      }).then((result) => {
        this.data_nbrealisation_par_age_par_type_bracelet = result;
      });
    },
  },
};
</script>
