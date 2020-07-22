<template>
  <div class="chained-form">
cf {{config.value}}
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
          :validForms="validForms"
          :freeze="config.freeze"
        ></fil-arianne>

        <div
          v-for="[keySessionGroup, sessionGroup] in Object.entries(config.sessionGroups)"
          :key="keySessionGroup"
        >
          <div v-if="showGroupSession(keySessionGroup)">
            <h2>{{ sessionGroup.title }}</h2>
          </div>
          <div v-for="keySessionCur of sessionGroup.sessions" :key="keySessionCur">
            <div
              :class="{
              'form-session-container': true,
              isSession: keySession != 'all'
            }"
              v-if="showSession(keySessionCur)"
            >
              <generic-form :config="configSession(keySessionCur)"></generic-form>
              <!-- <form-session
              class="session"
              :baseModel="declaration"
              :config="configSession"
              :validForms="validForms"
              :keySession="keySession"
              ></form-session>-->
            </div>
          </div>
        </div>
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
import "@/components/form/form.css";
// import "./declaration.css";
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
    freeze: null, 
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
            process: ({ $router, config}) => {
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

        sessionDef.keySession = keySession;
        sessionDef.formDefs = this.config.formDefs;
        sessionDef.sessionGroups = this.config.sessionGroups;
        sessionDef.value = this.config.value;
        console.log('niit session', sessionDef.value)

        return sessionDef;
        // sinon passer au suivant ? redirect ou changer key
      }
    },
    initChainedForm() {
        console.log('init cf')
      if (this.config.preLoadData) {
        this.config
          .preLoadData({
            $store: this.$store,
            meta: this.meta,
            config: this.config
          })
          .then(() => {
        console.log('init cf preload', this.config.value)

            this.initialized = true;
          });
      } else {
          console.log('init cf no preload')
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
  }
};
</script>

<style scoped>
.chained-form {
  width: 100%;
  margin-bottom: 50px;
}
</style>
