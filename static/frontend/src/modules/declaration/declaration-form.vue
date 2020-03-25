<template>
  <div>
    <pre></pre>
    <h1>{{ config.title }}</h1>
    <div
      v-for="[keySessionGroup, sessionGroup] in Object.entries(config.groups)"
      :key="keySessionGroup"
    >
      <h2>{{ sessionGroup.title }}</h2>
      <form-session
        v-for="[keySession, configSession] in Object.entries(
          sessionGroup.sessions
        )"
        :key="keySession"
        :baseModel="declaration"
        :config="configSession"
        :validForms="validForms"
      ></form-session>
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
  data: () => ({
    config: configDeclaration.config(),
    declaration: configDeclaration.initModel(),
    validForms: {}
  }),
  components: {
    formSession
  }
};
</script>
