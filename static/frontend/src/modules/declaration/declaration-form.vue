<template>
  <div>
    <div v-if="initialized">
      <h1>{{ config.title }}</h1>
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
          v-for="[keySession, configSession] in Object.entries(
            sessionGroup.sessions
          )"
          :key="keySession"
        >
          <form-session
            v-if="showSession(keySession)"
            :baseModel="declaration"
            :config="configSession"
            :validForms="validForms"
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
import "@/components/form/form.css";

// import Declaration from "./declaration.js";

export default {
  name: "declarationForm",

  watch: {
    $route() {
      this.keySession = this.getKeySesion();

      if (this.idDeclaration != this.getIdDeclatation()) {
        this.initDeclarationForm();
      }
    }
  },

  data: () => ({
    config: configDeclaration.config(),
    declaration: null,
    validForms: {},
    keySession: null,
    idDeclaration: null,
    initialized: false
  }),

  components: {
    formSession,
    filArianne
  },

  computed: {
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
      console.log("initDeclarationForm");
      this.keySession = this.getKeySesion();
      this.idDeclaration = this.getIdDeclatation();
      this.$store.commit("configDeclaration", configDeclaration);

      const promises = [
        this.$store.dispatch("nomenclatures"),
        this.idDeclaration && this.$store.dispatch("declarationForm", this.idDeclaration)
      ];

      Promise.all(promises).then(() => {
        let declaration = this.$store.getters.declarationForm;
        declaration = { ...declaration, ...declaration.foret };
        this.declaration = configDeclaration.initModel(declaration);
        this.initialized = true;
        this.declaration.id_declarant = this.declaration.id_declarant || this.$store.getters.user.id_role;
      });
    },

    getKeySesion: function() {
      return this.$route.query.keySession || "foret_statut";
    },

    getIdDeclatation: function() {
      return this.$route.params.idDeclaration || null;
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
