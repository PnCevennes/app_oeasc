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
      <graph-chasse v-bind="bilanParams" type="bilan"> </graph-chasse>

      <!-- Graphiques complémentaires -->

      <!--
        Graphiques circulaires pour la répartition par sexe, classe d'âge et mode de chasse.
        Utilisés pour analyser la structure des prélèvements.
      -->
      <v-row>
        <v-col>
          <restitution2 display="graph" fieldName="label_sexe" dataType="chasse" typeGraph="pie"
            title="Part des sexes" :filters="{ ...bilanParams }"></restitution2>
        </v-col>
        <v-col>
          <restitution2 display="graph" fieldName="label_classe_age" dataType="chasse"
            typeGraph="pie" title="Part des classes d'âge" :filters="{ ...bilanParams }">
          </restitution2>
        </v-col>
        <v-col>
          <restitution2 display="graph" fieldName="label_mode_chasse" dataType="chasse"
            typeGraph="pie" title="Part des modes de chasse" :filters="{ ...bilanParams }">
          </restitution2>
        </v-col>
      </v-row>

      <!--
        Graphiques linéaires pour la chronologie des prélèvements.
        Premier graphique : chronologie pour la saison sélectionnée.
        Deuxième graphique : chronologie sur les 5 dernières saisons.
      -->
      <v-row>
        <v-col>
          <restitution2 display="graph" fieldName="mois_txt" dataType="chasse" typeGraph="line"
            :title="`Chronologie des prélèvements (Saison ${infos.nom_saison})`"
            :filters="{ ...bilanParams }"></restitution2>
        </v-col>
        <v-col>
          <restitution2 display="graph" fieldName2="nom_saison" fieldName="mois_txt"
            dataType="chasse" typeGraph="line"
            :title="`Chronologie des prélèvements (5 dernières saisons)`"
            :filters="{ ...bilanParams, id_saison: infos.last_5_id_saison }"></restitution2>
        </v-col>
      </v-row>

      <!--
        Section spécifique pour l'espèce "Cerf".
        Affiche des graphiques supplémentaires par catégorie de bracelet.
      -->
      <div v-if="infos.nom_espece == 'Cerf'">
        <h2>Résultats par catégories</h2>
        <v-row>
          <v-col>
            <restitution2 display="graph" fieldName="bracelet" dataType="chasse" typeGraph="pie"
              :title="`Prélèvements par type de bracelet`" :filters="{ ...bilanParams }">
            </restitution2>
          </v-col>
        </v-row>
        <v-row>
          <!--
            Affiche un graphique pour chaque type de bracelet (CEM, CEFF, CEFFD).
            Permet d'analyser les attributions par catégorie.
          -->
          <v-col v-for="bracelet in ['CEM', 'CEFF', 'CEFFD']" :key="bracelet">
            <graph-chasse v-bind="bilanParams" :bracelet="bracelet" type="attribution_bracelet">
            </graph-chasse>
          </v-col>
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
          <v-col>
            <restitution2 display="graph" fieldName="label_classe_age" dataType="chasse"
              typeGraph="pie" :title="`Part des classes d'âge (CEM)`"
              :filters="{ ...bilanParams, bracelet: ['CEM'] }"></restitution2>
          </v-col>
          <v-col>
            <restitution2 display="graph" fieldName="label_classe_age" dataType="chasse"
              typeGraph="pie" :title="`Part des classes d'âge (CEFF)`"
              :filters="{ ...bilanParams, bracelet: ['CEFF'] }"></restitution2>
          </v-col>
        </v-row>

      </div>
    </div>
  </div>
</template>

<script>
import genericForm from "@/components/form/generic-form.vue";
import graphChasse from "./graph-chasse.vue";
import restitution2 from "@/modules/restitution2/restitution.vue";

export default {
  name: "pageChasseBilanDetaille",
  components: { genericForm, graphChasse, restitution2 },

  // Déclaration des données réactives du composant
  data: () => ({
    // Paramètres de filtre pour le bilan, liés au formulaire générique
    bilanParams: {
      id_espece: null,             // Identifiant de l'espèce sélectionnée
      espece: null,                // Nom de l'espèce (optionnel, parfois utilisé pour affichage)
      id_zone_indicative: [],      // Liste des zones indicatives sélectionnées
      id_zone_cynegetique: [],     // Liste des zones cynégétiques sélectionnées
      id_secteur: [],              // Liste des secteurs sélectionnés
      id_saison: null              // Identifiant de la saison sélectionnée
    },
    // Informations détaillées du bilan, récupérées depuis l'API après sélection des filtres
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
    processBilanParams() {
      this.infos = {};
      if (!this.bilanParams.id_saison && this.bilanParams.id_espece) {
        return;
      }
      // console.log("getBilanParams");
      this.$store
        .dispatch("getAnalyseBilanInfos", this.bilanParams)
        .then(infos => {
          this.infos = infos;
        });
    }
  }
};
</script>
