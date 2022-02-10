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
        <div>
          <restitution2 v-bind="settings"></restitution2>
        </div>
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

import restitutionForm from "./restitution-form";
import restitution2 from './restitution.vue';
// import deepEqual from "fast-deep-equal";

export default {

  name: "restitution-dashboard",

  components: {
    restitutionForm,
    restitution2
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

      /**
       * propStr pour lister toutes les propriétés du widget
       */
      let propsStr = "";

      // liste des propriétés de settings utiles pour le code du widget
      const propList = Object.keys(this.settings)
        // filtre sur les clé
        .filter( prop =>
          !["n", "filterList"].includes(prop)
          &&  (
            ["dataType", "fieldName", "fieldName2", "display", "height"].includes(prop)
            // clés spéciales graph
            || this.settings.display == "graph" && ["typeGraph", "stacking"].includes(prop)
          )
        )

      // boucle sur la liste de clé pour faire les propriétés
      for (const prop of propList) {
      const propValue = this.settings[prop];
        propsStr += propValue
          ? typeof propValue == "object"
            ? ` :${prop}='${JSON.stringify(propValue)}'`
            : ` ${prop}=${propValue}`
          : ` :${prop}="null"`;
      }

      // code du widget
      return `<div><restitution2 ${propsStr} ></restitution2></div>`;
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
