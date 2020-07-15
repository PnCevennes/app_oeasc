<template>
  <div v-if="keySession != 'all'">
    <div class="fil-arianne-container">
      <div
        v-for="([keySessionGroup, sessionGroup], indexGroup) in Object.entries(
          config.groups
        )"
        :key="keySessionGroup"
        @click="
          condValidSessionGroup(keySessionGroup) &&
            onSessionGroupClick(keySessionGroup)
        "
        :class="{
          'current-group': condCurrentGroup(keySessionGroup),
          'valid-group': condValidSessionGroup(keySessionGroup)
        }"
      >
        {{ indexGroup + 1 }}. {{ sessionGroup.title }}
      </div>
    </div>
    <div
      v-for="([keySessionGroup, sessionGroup], indexGroup) in Object.entries(
        config.groups
      )"
      :key="keySessionGroup"
      class="fil-arianne-container"
    >
      <template v-if="condSessions(keySessionGroup)">
        <div
          v-for="([keySession, configSession], indexSession) in Object.entries(
            sessionGroup.sessions
          )"
          :key="keySession"
          @click="condValidSession(keySession) && onSessionClick(keySession)"
          :class="{
            'current-session': condCurrentSession(keySession),
            'valid-session': condValidSession(keySession)
          }"
        >
          {{ indexGroup + 1 }}.{{ indexSession + 1 }} -
          {{ configSession.title }}
        </div>
      </template>
    </div>
  </div>
</template>
<script>
import "./declaration.css";
export default {
  name: "fil-arianne",
  props: ["config", "keySession", "validForms", "freeze"],
  data: () => ({}),
  watch: {
    freeze() {
      console.log('watch freeze')
    }
  },
  methods: {
    onSessionGroupClick(keySessionGroup) {
      const keySession = this.$store.getters.configDeclaration.firstSession(
        keySessionGroup
      );
      this.onSessionClick(keySession);
    },

    onSessionClick(keySession) {
      this.$router.push({ query: { keySession } });
    },

    condSessions(keySessionGroup) {
      return (
        keySessionGroup ==
        this.$store.getters.configDeclaration.group(this.keySession)
      );
    },

    condValidSession(keySession) {
      return this.$store.getters.configDeclaration.condValidSession(keySession, this.validForms) && !this.freeze;
      // return this.validForms[keySession];
    },

    condValidSessionGroup(keySessionGroup) {
      const keySession = this.$store.getters.configDeclaration.firstSession(
        keySessionGroup
      );
      return this.condValidSession(keySession)  && !this.freeze;
    },

    condCurrentSession(keySession) {
      return this.keySession == keySession;
    },

    condCurrentGroup(keySessionGroup) {
      const keySession = this.$store.getters.configDeclaration.firstSession(
        keySessionGroup
      );
      return this.condCurrentSession(keySession);
    }
  }
};
</script>
