<template>
  <div>
    <div v-if="initialized">
      <h1>{{ config.title }}</h1>
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
      <!-- {{ declarationNotNull }} -->

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
import formSession from "@/components/form/session.vue";
import "@/components/form/form.css";

// import Declaration from "./declaration.js";

export default {
  name: "declarationForm",

  watch: {
    $route() {
      this.keySession = this.getKeySesion();
    }
  },

  data: () => ({
    config: configDeclaration.config(),
    declaration: configDeclaration.initModel(),
    validForms: {},
    keySession: null,
    initialized: false
  }),

  components: {
    formSession
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
    getKeySesion: function() {
      return this.$route.params.keySession || "all";
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
    this.keySession = this.getKeySesion();
    this.$store.commit("configDeclaration", configDeclaration);
    this.$store.dispatch("nomenclatures").then(() => {
      this.initialized = true;
    });
  }
};
</script>
