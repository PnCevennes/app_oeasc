<template>
  <div>
    <div>
      <!-- {{ validForms[config.name] }} -->
      <h3>{{ config.title }}</h3>

      <v-form v-model="validForms[config.name]" :ref="config.name">
        <dynamic-form-group
          v-for="[keyFormGroup, configFormGroup] in Object.entries(
            config.groups
          )"
          :key="keyFormGroup"
          :config="configFormGroup"
          :baseModel="baseModel"
        >
        </dynamic-form-group>

        <v-btn color="success" @click="action()">
          {{ (this.config.action && this.config.action.label) || "Suivant" }}
        </v-btn>
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
      </v-row>
    </div>
  </div>
</template>

<script>
import dynamicFormGroup from "@/components/form/dynamic-form-group";

export default {
  name: "formSession",
  components: {
    dynamicFormGroup
  },
  data: () => ({
    // affichage modal quand la requete post est lancée
    bModalPost: false
  }),
  watch: {},
  props: ["config", "baseModel", "validForms"],
  methods: {
    action: function() {
      // si le formulaire n'est pas valide on ne fait rien
      // les erreurs seront affichées
      if (!this.validate()) {
        return;
      }

      // action definie dans la config (par exemple: envoyer un post du formulaire)
      if (this.config.action) {
        // this.bModalPost = true;
        this.config.action
          .process({ baseModel: this.baseModel })
          .then(response => {
            console.log("post ok", response);
            this.bModalPost = false;
          });

        // action par defaut aller à la section suivante
      } else {
        const nextSession = this.$store.getters.configDeclaration.nextSession(
          this.config.name
        );
        if (nextSession) {
          this.$router.push({query:{keySession: nextSession}});
        }
      }
    },

    validate: function() {
      this.$refs[this.config.name].validate();
      return this.validForms[this.config.name];
    }
  }
};
</script>
