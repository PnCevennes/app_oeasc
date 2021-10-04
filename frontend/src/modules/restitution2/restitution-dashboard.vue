<!--

  Tableau de bord pour la restitution générique

 -->
<template>
  <div class="page-restitution">

    <h2>Tableau de bord - restitution</h2>

    <div>

        <!-- boutton pour copier le code du widget dans le presse papier -->
        <v-tooltip bottom>
        <template v-slot:activator="{ on }">
            <v-btn v-on="on" icon @click="contentToClipboard()">
            <v-icon>mdi-clipboard-text</v-icon>
            </v-btn>
        </template>
        <span>Copier le code du widget dans le presse papier</span>
        </v-tooltip>

        <!-- message pour indiquer que le code est bien collé dans le presse-papier -->
        <v-snackbar color="success" v-model="bContentCopied" :timeout="1000">
            Le code du widget à été copié dans le presse-papier
        </v-snackbar>


        <!-- affichage du code HTML du widget (DEBUG) -->
        {{ toContent() }}

    </div>

    <div class="container-restitution">

      <!-- Composant de rendu (tableau, graphique, carte)-->
      <div class="result">

        <!-- Affichage des graphes -->
        <div v-if="this.settings.display == 'graph'">
            <restitution-graph v-bind="settings"></restitution-graph>
        </div>

        <!-- TODO ajouter rendus tableau et carte -->

      </div>

      <!-- Composant formulaire pour les choix des paramètres de restitution -->
      <div class="config">
        <restitution-form
          @updateSettings="updateSettings($event)"
          :dataType="dataType"
        ></restitution-form>
      </div>

    </div>
  </div>
</template>

<script>

import restitutionGraph from "./restitution-graph.vue";
import restitutionForm from "./restitution-form";
// import deepEqual from "fast-deep-equal";

export default {

  name: "restitution-dashboard",

  components: {
    restitutionForm,
    restitutionGraph
  },

  data: () => ({
    settings: {}, // données depuis le formulaire de settings
    bContentCopied: false, // pour le snackbar 'pressepapier'
    dataType: "chasse", // type de données ici chasse pour tester mais possibilité de choisir par la suite
  }),

  methods: {

    /**
     * Met à jour les settings
     *  - ?? pour s'assurer de la bonne synchronisation des composants
     */
    updateSettings(settings) {
      this.settings = settings;
    },

    /**
     * Fonction qui génère le code html du widget à insérer dans les contenus
     * en fonction des données contenus dans settings
     */
    toContent() {
      let content = "<div><restitution \n";
      for (const prop of Object.keys(this.settings).filter(
        prop => prop != "default"
      )) {
        const propValue = this.settings[prop];
        if (
          !["n", "filterList"].includes(prop) &&
          (["dataType", "fieldName", "display", "height", 'groupByKey'].includes(prop) ||
            (this.settings.display == "graph" &&
              ["typeGraph", "stacking"].includes(prop)) //
              // ||!deepEqual(propValue, this.settings.default[prop])
            )
        ) {
          content += propValue
            ? typeof propValue == "object"
              ? ` :${prop}='${JSON.stringify(propValue)}'`
              : ` ${prop}=${propValue}`
            : ` :${prop}="null"`;
        }
      }
      content += "></restitution></div>";
      return content;
    },

    /**
     * Copie le code du widget dans le presse papier
     */
    contentToClipboard() {
      navigator.clipboard.writeText(this.toContent()).then(() => {
        this.bContentCopied = true;
      });
    }
  },
};
</script>
