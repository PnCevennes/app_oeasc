<template>
  <div class="page-restitution">
    <h2>Restitution test</h2>
    {{ toContent() }}

    <div class="container-restitution">
      <div class="result">
        {{settings}}
        <restitution v-bind="settings"> </restitution>
      </div>
      <div class="config">
        <config-restitution
          @updateSettings="settings = $event"
        >
        </config-restitution>
        
      </div>
    </div>
  </div>
</template>

<script>
import restitution from "./restitution.vue";
import configRestitution from './config-restitution';
import "./restitution.css";

export default {
  name: "test-restitution",
  components: {
    restitution,
    configRestitution
  },
  methods: {
toContent() {
      let content = "<restitution";
      for (const prop of Object.keys(this.settings)) {
        const propValue = this.settings[prop];
        content += propValue
          ? typeof propValue == "object"
            ? ` :${prop}='${JSON.stringify(propValue)}' `
            : ` ${prop}=${propValue} `
          : null;
      }
      content += "></restitution>";
      return content;
    },
  },
  data: () => ({
    settings: {display: 'map', dataType: 'declaration'},
    declarations: null,
    // configDeclaration,
    results: null,
    display: 'table',
  }),
};
</script>
