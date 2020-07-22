<template>
  <div class="chained-form">
    <div>
      <h2>{{ title }}</h2>

      <div v-if="initialized">
        <p v-if="config.help">
          Besoin d'aide
          <help :code="config.help"></help>
        </p>

        <fil-arianne
          :config="config"
          :keySession="keySession"
          :baseModel="config.value"
          :freeze="config.freeze"
        ></fil-arianne>

        <generic-form :config="configSession(keySession)"></generic-form>
      </div>

      <div v-else>
        Chargement en cours
        <v-progress-linear active indeterminate></v-progress-linear>
      </div>
    </div>
  </div>
</template>

<script>
import filArianne from "./fil-ariane";
import help from "@/components/form/help";
import genericForm from "@/components/form/generic-form";
import { sessionFunctions } from "@/components/form/functions/session";

export default {
  name: "declarationForm",
  props: ["config", "meta"],
  components: {
    filArianne,
    help,
    genericForm
  },

  watch: {
    // $route() {
    //   // this.keySession = this.getKeySesion();
    //   if (this.idDeclaration != this.declaration.id_declaration) {
    //     this.initDeclarationForm();
    //   }
    // },
    // declaration: {
    //   deep: true,
    //   handler() {
    //     console.log("dec watch freeze", this.declaration.freeze);
    //     this.freeze = this.declaration.freeze;
    //   }
    // }
  },

  data: () => ({
    declaration: null,
    validForms: {},
    initialized: false,
    freeze: null
  }),

  computed: {
    title() {
      return typeof this.config.title == "function"
        ? this.config.title({ meta: this.meta, $store: this.$store })
        : this.config.title;
    },
    firstSession() {
      return sessionFunctions.firstSession(this.config);
    },

    // retourne la clé de session courrante
    keySession() {
      return this.$route.query.keySession || this.firstSession;
    }
  },

  methods: {
    configSession(keySession) {
      let sessionDef = {};
      if (keySession == "all") {
        // on renvoie toutes les sessions
        sessionDef.groups = sessionFunctions.groups(this.config);
        sessionDef.request = this.config.request;
      } else {
        sessionDef = this.config.sessionDefs[keySession];

        // si c'est la dernière session validation = requete
        if (sessionFunctions.lastSession(this.config) == keySession) {
          sessionDef.request = this.config.request;

          // sinon on passe au formulaire suivant
        } else {
          sessionDef.action = {
            label: "Suivant",
            process: ({ $router, config }) => {
              const nextSession = sessionFunctions.nextSession(
                config,
                config.keySession
              );
              if (nextSession) {
                $router.push({ query: { keySession: nextSession } });
              }
            }
          };
        }
      }
      sessionDef.keySession = keySession;
      sessionDef.formDefs = this.config.formDefs;
      sessionDef.sessionGroups = this.config.sessionGroups;
      sessionDef.value = this.config.value;

      return sessionDef;
    },
    initChainedForm() {
      if (this.config.preLoadData) {
        this.config
          .preLoadData({
            $store: this.$store,
            meta: this.meta,
            config: this.config
          })
          .then(() => {
            this.initialized = true;
          });
      } else {
        this.initialized = true;
      }
    },

    showSession: function(keySession) {
      return this.keySession === "all" || this.keySession == keySession;
    },

    showGroupSession: function(keySessionGroup) {
      return (
        this.keySession === "all" ||
        this.keySession in this.config.sessionGroups[keySessionGroup].sessions
      );
    }
  },
  created: function() {
    this.initChainedForm();
    console.log(this.config);
  }
};
</script>

<style>

.chained-form {
  width: 100%;
  margin: 50px;
}

</style>
