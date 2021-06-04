<template>
  <div class="chained-form">
    <div>
      <h2>{{ title }}</h2>

      <div v-if="initialized">
        <p v-if="config.help">
          Besoin d'aide
          <help :code="config.help"></help>
        </p>

        <fil-arianne :config="config" :keySession="keySession" :baseModel="config.value"></fil-arianne>
      
    {{config.value}}
        <generic-form :config="configSession(keySession)">
          <div slot="success">
            <slot name="success"></slot>
          </div>
        </generic-form>
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
  props: ["config"],
  components: {
    filArianne,
    help,
    genericForm,
  },

  data: () => ({
    declaration: null,
    validForms: {},
    initialized: false,
    freeze: null,
  }),

  computed: {
    id() {
      return this.$route.params.id;
    },
    title() {
      return typeof this.config.title == "function"
        ? this.config.title({ id: this.id, $store: this.$store })
        : this.config.title;
    },
    firstSession() {
      return sessionFunctions.firstSession(this.config);
    },

    // retourne la clé de session courrante
    keySession() {
      return this.$route.query.keySession || this.firstSession;
    },
  },

  methods: {
    configSession(keySession) {
      let sessionDef = {};
      if (keySession == "all") {
        // on renvoie toutes les sessions
        sessionDef.groups = sessionFunctions.groups(this.config);
        sessionDef.action = this.config.action;
      } else {
        sessionDef = this.config.sessionDefs[keySession];

        // si c'est la dernière session validation = requete
        if (sessionFunctions.lastSession(this.config) == keySession) {

          sessionDef.action = this.config.action;

          // sinon on passe au formulaire suivant
        } else {
          sessionDef.bChained = true;
          sessionDef.action = {
            label: "Suivant",
            process: ({ $router, config }) => {
              return new Promise((resolve) => {
                const nextSession = sessionFunctions.nextSession(
                  config,
                  config.keySession
                );
                if (nextSession) {
                  // ici indispensable sinon bug et valide à l'avant dernière !!!!!
                  setTimeout(() => {
                    $router.push({ query: { keySession: nextSession } });
                  }, 200)
                }
                resolve();
              });
            },
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
      if (this.config.preloadData) {
        this.config
          .preloadData({
            $store: this.$store,
            id: this.id,
            config: this.config,
          })
          .then(() => {
            this.initialized = true;
          });
      } else {
        this.initialized = true;
      }
    },

    showSession: function (keySession) {
      return this.keySession === "all" || this.keySession == keySession;
    },

    showGroupSession: function (keySessionGroup) {
      return (
        this.keySession === "all" ||
        this.keySession in this.config.sessionGroups[keySessionGroup].sessions
      );
    },
  },
  created: function () {
    this.initChainedForm();
  },
};
</script>

<style>
.chained-form {
  width: 100%;
  margin: 50px;
}
</style>
