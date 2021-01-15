<template>
  <div class="page-restitution">
    <h2>Tableau de bord - restitution</h2>
    {{ toContent() }}
    <v-tooltip bottom>
      <template v-slot:activator="{ on }">
        <v-btn v-on="on" icon @click="contentToClipboard()">
          <v-icon>mdi-clipboard-text</v-icon>
        </v-btn>
      </template>
      <span>Copier le code du widget dans le presse papier</span>
    </v-tooltip>
    <div class="container-restitution">
      <div class="result">
        <restitution ref="restitution" v-bind="settings"></restitution>
      </div>
      <div class="config">
        <restitution-settings
          @updateSettings="updateSettings($event)"
          :dataType="dataType"
        ></restitution-settings>
      </div>
    </div>
    <v-snackbar color="success" v-model="bContentCopied" :timeout="1000">
      Le code du widget à été copié dans le presse-papier
    </v-snackbar>
  </div>
</template>

<script>
import restitution from "./restitution.vue";
import restitutionSettings from "./restitution-settings";
import "./restitution.css";
import deepEqual from "fast-deep-equal";
export default {
  name: "restitution-dashboard",
  components: {
    restitution,
    restitutionSettings
  },
  methods: {
    updateSettings(settings) {
      this.settings = settings;
    },
    toContent() {
      let content = "<div><restitution \n";
      for (const prop of Object.keys(this.settings).filter(
        prop => prop != "default"
      )) {
        const propValue = this.settings[prop];
        if (
          !["n", "filterList"].includes(prop) &&
          (["dataType", "choix1", "display", "height"].includes(prop) ||
            (this.settings.display == "graph" &&
              ["typeGraph", "stacking"].includes(prop)) ||
            !deepEqual(propValue, this.settings.default[prop]))
        ) {
          content += propValue
            ? typeof propValue == "object"
              ? ` :${prop}='${JSON.stringify(propValue)}'`
              : ` ${prop}=${propValue}`
            : ` :${prop}="null"`;
        }
      }
      content += "></restitution></div>";
      return content;
    },
    contentToClipboard() {
      navigator.clipboard.writeText(this.toContent()).then(() => {
        this.bContentCopied = true;
      });
    }
  },
  data: () => ({
    settings: {},
    declarations: null,
    // configDeclaration,
    results: null,
    display: "table",
    bContentCopied: false,
    dataType: "declaration"
  })
};
</script>
