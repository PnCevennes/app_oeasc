<template>
  <div class="form-declaration">
    <div v-if="initialized">
      <h1 v-if="!idDeclaration">{{ config.title }}</h1>
      <h1 v-else>{{ `Éditer la déclaration ${idDeclaration}` }}</h1>
      <p>Besoin d'aide <help code="declaration_help"></help></p>
      <fil-arianne
        :config="config"
        :keySession="keySession"
        :validForms="validForms"
      >
      </fil-arianne>
      <div
        v-for="[keySessionGroup, sessionGroup] in Object.entries(config.groups)"
        :key="keySessionGroup"
      >
        <div v-if="showGroupSession(keySessionGroup)">
          <h2>{{ sessionGroup.title }}</h2>
        </div>
        <div
          v-for="[keySessionCur, configSession] in Object.entries(
            sessionGroup.sessions
          )"
          :key="keySessionCur"
        >
          <form-session
          class="session"
            v-if="showSession(keySessionCur)"
            :baseModel="declaration"
            :config="configSession"
            :validForms="validForms"
            :keySession="keySession"
          ></form-session>
        </div>
      </div>
    </div>

    <div v-else>
      Chargement en cours
    </div>
  </div>
</template>

<script>
import { configDeclaration } from "./config";
import filArianne from "./fil-ariane";
import formSession from "@/components/form/session.vue";
import help from "@/components/form/help";
import "@/components/form/form.css";
import "./declaration.css";

// import Declaration from "./declaration.js";

export default {
  name: "declarationForm",

  components: {
    formSession,
    filArianne,
    help
  },

  watch: {
    $route() {
      // this.keySession = this.getKeySesion();

      if (this.idDeclaration != this.declaration.id_declaration) {
        this.initDeclarationForm();
      }
    }
  },

  data: () => ({
    config: configDeclaration.config(),
    declaration: null,
    validForms: {},
    initialized: false
  }),

  computed: {
    idDeclaration() {
      return this.$route.params.idDeclaration || null;
    },

    keySession: function() {
      return this.$route.query.keySession || "foret_statut";
    },

    declarationNotNull: function() {
      const declarationNotNull = {};

      for (const key in this.declaration) {
        if (
          this.declaration[key] &&
          (!Array.isArray(this.declaration[key]) ||
            this.declaration[key].length)
        ) {
          declarationNotNull[key] = this.declaration[key];
        }
      }

      return declarationNotNull;
    }
  },

  methods: {
    initDeclarationForm() {
      // this.keySession = this.getKeySesion();
      // this.idDeclaration = this.getIdDeclatation();      this.$store.commit("configDeclaration", configDeclaration);
      this.$store.commit("declarationForm", {});

      this.$store.commit("configDeclaration", configDeclaration);

      const promises = [
        this.$store.dispatch("nomenclatures"),
        this.idDeclaration &&
          this.$store.dispatch("declarationForm", this.idDeclaration)
      ];

      Promise.all(promises).then(() => {
        let declaration = this.idDeclaration
          ? this.$store.getters.declarationForm
          : {};

        declaration = { ...declaration.foret, ...declaration };
        this.declaration = configDeclaration.initModel(declaration);
        configDeclaration.initValidForms({baseModel: this.declaration, $store: this.$store}, this.validForms);
        this.initialized = true;
        this.declaration.id_declarant =
          this.declaration.id_declarant || this.$store.getters.user.id_role;
      });
    },

    showSession: function(keySession) {
      return this.keySession === "all" || this.keySession == keySession;
    },

    showGroupSession: function(keySessionGroup) {
      return (
        this.keySession === "all" ||
        this.keySession in this.config.groups[keySessionGroup].sessions
      );
    }
  },
  created: function() {
    this.initDeclarationForm();
  }
};
</script>
