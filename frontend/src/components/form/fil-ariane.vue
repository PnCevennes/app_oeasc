<template>
  <div v-if="keySession != 'all'">
    <v-row dense class="fil-arianne-container">
      <v-col
        v-for="([keySessionGroup, sessionGroup], indexGroup) in Object.entries(
          config.sessionGroups
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
      >{{ indexGroup + 1 }}. {{ sessionGroup.title }}</v-col>
    </v-row>
    <v-row
      dense
      v-for="([keySessionGroup, sessionGroup], indexGroup) in Object.entries(
        config.sessionGroups
      )"
      :key="keySessionGroup"
      class="fil-arianne-container"
    >
      <template v-if="condSessions(keySessionGroup)">
        <v-col
          v-for="(keySession, indexSession) in 
            sessionGroup.sessions
          "
          :key="keySession"
          @click="condValidSession(keySession) && onSessionClick(keySession)"
          :class="{
            'current-session': condCurrentSession(keySession),
            'valid-session': condValidSession(keySession)
          }"
        >
          {{ indexGroup + 1 }}.{{ indexSession + 1 }} -
          {{ config.sessionDefs[keySession].title }}
        </v-col>
      </template>
    </v-row>
  </div>
</template>
<script>
import { sessionFunctions } from "@/components/form/functions/session";
// import "./declaration.css";
export default {
  name: "fil-arianne",
  props: ["config", "keySession", "baseModel"],
  data: () => ({}),
  watch: {
    baseModel: {
      handler() {
    }},
    deep: true,
  },
  computed: {
    freeze() {
      return this.baseModel.freeze;
    },
  },
  methods: {
    onSessionGroupClick(keySessionGroup) {
      const keySession = sessionFunctions.firstSession(this.config, keySessionGroup);
      this.onSessionClick(keySession);
    },

    onSessionClick(keySession) {
      this.$router.push({ query: { keySession } });
    },

    condSessions(keySessionGroup) {
      return (
        keySessionGroup == sessionFunctions.group(this.config, this.keySession)
      );
    },

    condValidSession(keySession) {
      return (
        sessionFunctions.condValidSession(
          {
            config: this.config,
            $store: this.$store,
            baseModel: this.baseModel,
          },
          keySession
        ) && !this.baseModel.freeze
      );
    },

    condValidSessionGroup(keySessionGroup) {
      const keySession = sessionFunctions.firstSession(
        this.config,
        keySessionGroup
      );
      return this.condValidSession(keySession) && !this.baseModel.freeze;
    },

    condCurrentSession(keySession) {
      return this.keySession == keySession;
    },

    condCurrentGroup(keySessionGroup) {
      const keySession = sessionFunctions.firstSession(
        this.config,
        keySessionGroup
      );
      return this.condCurrentSession(keySession);
    },
  },
};
</script>

<style scoped>
.fil-arianne-container > div {
  /* flex-grow: 1; */
  text-align: center;
  margin: 1px;
  background-color: lightgrey;
}

.fil-arianne-container > div.current-group,
.fil-arianne-container > div.current-session {
  font-weight: bold;
}

.fil-arianne-container > div.valid-session,
.fil-arianne-container > div.valid-group {
  background-color: lightgoldenrodyellow;
  cursor: pointer;
}
</style>
