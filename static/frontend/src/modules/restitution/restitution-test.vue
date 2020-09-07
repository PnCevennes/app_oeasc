<template>
  <div class="page-restitution">
    {{settings}}
    <h2>Tableau de bord - restitution</h2>
    <v-tooltip bottom>
      <template v-slot:activator="{ on }">
        <v-btn v-on="on" icon @click="contentToClipboard()">
          <v-icon>mdi-clipboard-text</v-icon>
        </v-btn>
      </template>
      <span>Copier le code du widget dans le presse papier</span>
    </v-tooltip>
    <!-- {{settings}} -->
    <div class="container-restitution">
      <div class="result">
        <restitution v-bind="settings"></restitution>
      </div>
      <div class="config">
        <config-restitution @updateSettings="settings = $event"></config-restitution>
      </div>
    </div>
    <v-snackbar color="success" v-model="bContentCopied" :timeout="1000">
      Le code du widget à été copié dans le presse-papier
    </v-snackbar>
  </div>
</template>

<script>
import restitution from "./restitution.vue";
import configRestitution from "./config-restitution";
import "./restitution.css";

export default {
  name: "test-restitution",
  components: {
    restitution,
    configRestitution,
  },
  methods: {
    toContent() {
      let content = "<div><restitution \n";
      for (const prop of Object.keys(this.settings)) {
        const propValue = this.settings[prop];
        content += propValue
          ? typeof propValue == "object"
            ? ` :${prop}='${JSON.stringify(propValue)}' \n`
            : ` ${prop}=${propValue} \n`
          : null;
      }
      content += "></restitution></div>";
      return content;
    },
    contentToClipboard() {
      navigator.clipboard.writeText(this.toContent()).then(() => {console.log('aa');this.bContentCopied = true});
    }
  },
  data: () => ({
    settings: { display: "map", dataType: "declaration" },
    declarations: null,
    // configDeclaration,
    results: null,
    display: "table",
    bContentCopied: false,
  }),
};
</script>
