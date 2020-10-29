<template>
  <div>
    <div>
      <div>
        <v-btn
          icon
          v-if="!bEdiTContents && $store.getters.droitMax >= 5"
          @click="bEdiTContents = true"
        >
          <v-icon>edit</v-icon>
        </v-btn>
        <v-btn icon v-if="bEdiTContents" @click="bEdiTContents = false">
          <v-icon>cancel</v-icon>
        </v-btn>

        <v-btn icon v-if="bEdiTContents" @click="updateContent()">
          <v-icon>check</v-icon>
        </v-btn>
      </div>

      <v-runtime-template
        v-if="!bEdiTContents"
        class="content"
        :template="contentHTML"
      ></v-runtime-template>
      <div v-if="bEdiTContents" class="edit-content">
        <v-textarea
          :label="`Content ${getCode()}`"
          v-model="contentMD"
          :rows="20"
          large
          outlined
          color="cyan"
          class="edit-content"
        ></v-textarea>
      </div>
    </div>
  </div>
</template>

<script>
// load content
import { apiRequest } from "@/core/js/data/api.js";
import { config } from "@/config/config.js";
// import { MapService } from "@/modules/map";
import faqDeclaration from "./faq-declaration";
import tableAide from "./table-aide";
import declarationTable from "@/modules/declaration/declaration-table";
import baseMap from "@/modules/map/base-map";
import contentImg from './content-img'
import listePartenaire from './liste-partenaire'
import inGraph from '@/modules/in/in-graph.vue'
import inTable from '@/modules/in/in-table.vue'
import restitution from '@/modules/restitution/restitution.vue'

import "./content.css";
// import Vue from "vue";
import VRuntimeTemplate from "v-runtime-template";

export default {
  name: "oeasc-content",
  props: ["code", "containerClassIn", "meta"],
  watch: {
    $route() {
      // react to route changes...
      this.iniTContents();
    }
  },
  computed: {
    dp() {
      return this.$store.getters.distPath;
    }
  },
  components: {
    VRuntimeTemplate,
    faqDeclaration, // eslint-disable-line
    tableAide, // eslint-disable-line
    declarationTable, // eslint-disable-line
    baseMap, // eslint-disable-line
    contentImg, // eslint-disable-line
    listePartenaire, // eslint-disable-line
    inGraph, // eslint-disable-line
    inTable, // eslint-disable-line
    restitution, // eslint-disable-line
  },
  data: () => ({
    // component: null,
    contentHTML: "",
    contentMD: "",
    bEdiTContents: false,
    containerClass: {},
    mainConfig: config,
  }),
  methods: {
    seTContents: function(data) {
      this.contentHTML = `<div>${data.html}</div>`;
      this.contentMD = data.md;
      this.bEdiTContents = false;
    },
    getCode: function() {
      return this.code || this.$route.params.code || config.defaulTContents;
    },

    iniTContents: function() {
      apiRequest("GET", `api/commons/content/${this.getCode()}`).then(data =>
        this.seTContents(data)
      );
    },

    updateContent: function() {
      let postData = {
        md: this.contentMD,
        code: this.getCode()
      };

      apiRequest("PATCH", `api/commons/content/${this.getCode()}`, {
        postData
      }).then(data => this.seTContents(data));
    }
  },

  mounted: function() {
    this.iniTContents();
  },
};
</script>
