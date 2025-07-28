<!--
  Composant Vue.js : session.vue

  Ce composant gère l'affichage et la soumission d'un formulaire dynamique pour la déclaration de session.
  Il utilise Vuetify pour la mise en page et les composants d'interface utilisateur.

  Structure principale :
  - Affiche le titre du formulaire à partir de la configuration passée en props.
  - Utilise <v-form> pour encapsuler le formulaire et gérer sa validation.
  - Génère dynamiquement les groupes de champs du formulaire via <dynamic-form-group> en fonction de la configuration.
  - Affiche un bouton d'action ("Suivant" ou personnalisé) pour soumettre le formulaire, désactivé si l'état 'freeze' est actif.
  - Indique la présence de champs obligatoires avec une étoile rouge.
  - Affiche un dialogue de progression (<v-dialog>) lors de l'envoi de la déclaration, informant l'utilisateur que le processus est en cours.
  - Affiche un dialogue de succès (<v-dialog>) lorsque la déclaration a été enregistrée, proposant des liens pour poursuivre ou revenir à l'accueil.

  Principales propriétés et variables utilisées :
  - config : objet de configuration du formulaire (titre, groupes de champs, action, etc.).
  - validForms : objet de suivi de la validité des différents formulaires.
  - baseModel : modèle de données de base pour le formulaire.
  - bModalPost : booléen contrôlant l'affichage du dialogue de progression.
  - bModalSuccess : booléen contrôlant l'affichage du dialogue de succès.
  - freeze : booléen indiquant si le formulaire est en état "gelé" (désactivé).
  - keySession : clé de session utilisée pour déterminer l'affichage du bouton d'action.

  Points d'attention :
  - Les groupes de champs sont générés dynamiquement à partir de la configuration, permettant une grande flexibilité.
  - Les dialogues modaux améliorent l'expérience utilisateur lors de la soumission et après le succès.
  - Les liens proposés après la réussite permettent à l'utilisateur de poursuivre son parcours facilement.

  Ce composant est conçu pour être réutilisable et adaptable à différents types de formulaires de session.
-->
<template>
  <div>
    <div>
      <h3>{{ config.title }}</h3>

      <v-form
        v-model="validForms[config.name]"
        :ref="config.name"
        v-if="!bModalSuccess"
      >
        <dynamic-form-group
          v-for="[keyFormGroup, configFormGroup] in Object.entries(
            config.groups
          )"
          :key="keyFormGroup"
          :config="{
          ...configFormGroup, class: 'border margin padding'}"
          :baseModel="baseModel"
        >
        </dynamic-form-group>
      <v-row>

        <v-btn
          right
          absolute
          color="success"
          @click="action()"
          :disabled='freeze'
          v-if="this.config.action || this.keySession != 'all'"
        >
          {{ (this.config.action && this.config.action.label) || "Suivant" }}
        </v-btn>
      </v-row>
      <span style="color:red">*</span> <i>champs obligatoires.</i>
      </v-form>
    </div>
    <div>
      <v-row>
        <v-dialog v-model="bModalPost" persistent max-width="500">
          <v-card>
            <v-card-title class="headline"
              >Envoi de votre déclaration</v-card-title
            >
            <v-card-text class="text-center">
              <v-progress-circular
                indeterminate
                color="primary"
              ></v-progress-circular>
            </v-card-text>
            <v-card-text
              >Veuillez patienter, le processus peut prendre quelques
              instants.</v-card-text
            >
          </v-card>
        </v-dialog>
        <v-dialog v-model="bModalSuccess" persistent max-width="600">
          <v-card>
            <v-card-title class="headline"
              >Votre déclaration à bien été enregistrée</v-card-title
            >
            <v-card-text>
              <p>Vous pouvez désormais</p>
              <ul>
                <li>
                  <a href="#/declaration/declarer_en_ligne"
                    >Déclarer de nouveaux dégâts en forêt</a
                  >
                </li>
                <li>
                  <a Voir href="#/declaration/liste"
                    >Voir la liste des dégâts déclarés</a
                  >
                </li>
                <li><a href="#/">Retourner à l'accueil</a></li>
              </ul>
            </v-card-text>
          </v-card>
        </v-dialog>
      </v-row>
    </div>
  </div>
</template>

<script>
import dynamicFormGroup from "@/components/form/dynamic-form-group.vue";

export default {
  name: "formSession",
  components: {
    dynamicFormGroup
  },
  data: () => ({
    bModalPost: false, // Indique si la fenêtre modale de publication est affichée ou non  // bModalPost: false
    bModalSuccess: false, // Indique si la fenêtre modale de succès est affichée ou non  // bModalSuccess: false
    freeze: false, // Détermine si le formulaire est gelé (désactivé) ou non  // freeze: false
  }),
  watch: {
    baseModel: {
      deep:true,
      handler() {
        this.freeze = this.baseModel.freeze;
      }
    }
  },
  props: ["config", "baseModel", "validForms", "keySession"],
  methods: {

    /**
     * Méthode principale d'action du formulaire.
     * Elle gère la soumission du formulaire, la validation, l'affichage des dialogues de progression et de succès,
     * et l'enchaînement vers la prochaine étape si nécessaire.
     */
    action: function() {
      // Vérifie la validité du formulaire via la méthode validate().
      // Si le formulaire n'est pas valide, on arrête ici (les erreurs sont affichées automatiquement).
      if (!this.validate()) {
      return;
      }

      // Si une action personnalisée est définie dans la configuration (ex: envoi POST du formulaire)
      if (this.config.action) {
      // Affiche le dialogue de progression (spinner) pendant le traitement.
      this.bModalPost = true;
      // Exécute la fonction process définie dans la config, généralement une requête asynchrone.
      this.config.action
        .process({ baseModel: this.baseModel })
        .then(response => {
        // Après la réussite, masque le dialogue de progression et affiche le dialogue de succès.
        setTimeout(() => {
          this.bModalPost = false;
          this.bModalSuccess = true;
        }, 1000); // délai pour laisser le spinner visible un court instant
        });

      // Si aucune action personnalisée n'est définie, on passe à la session suivante (navigation interne)
      } else {
      // Récupère la prochaine session à afficher via le store Vuex.
      const nextSession = this.$store.getters.configDeclaration.nextSession(
        this.config.name
      );
      // Si une prochaine session existe, on navigue vers celle-ci en modifiant la query de l'URL.
      if (nextSession) {
        this.$router.push({ query: { keySession: nextSession } });
      }
      }
    },


    /**
     * Valide le formulaire référencé par le nom spécifié dans la configuration.
     * Utilise la référence du formulaire (`$refs`) pour déclencher la validation.
     * Retourne l'état de validité du formulaire correspondant depuis `validForms`.
     * @returns {Boolean} - Indique si le formulaire est valide ou non.
     */
    validate: function() {
      this.$refs[this.config.name].validate();
      return this.validForms[this.config.name];
    }


  },
};
</script>
