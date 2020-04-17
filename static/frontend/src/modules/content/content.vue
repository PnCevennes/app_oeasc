<template>
  <div>
    <div>
      <div>
        <v-btn
          icon
          v-if="!bEditContent && $store.getters.droitMax >= 5"
          @click="bEditContent = true"
        >
          <v-icon>edit</v-icon>
        </v-btn>
        <v-btn icon v-if="bEditContent" @click="bEditContent = false">
          <v-icon>cancel</v-icon>
        </v-btn>

        <v-btn icon v-if="bEditContent" @click="updateContent()">
          <v-icon>check</v-icon>
        </v-btn>
      </div>

      <!-- <div v-if="!bEditContent" class="content" v-html="contentHTML"></div> -->
      <v-runtime-template
        v-if="!bEditContent"
        class="content"
        :template="contentHTML"
      ></v-runtime-template>

      <div v-if="bEditContent" class="edit-content">
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
import { MapService } from "@/modules/map";
import faqDeclaration from "./faq-declaration";
import tableAide from "./table-aide";
import declarationTable from "@/modules/declaration/declaration-table";
import "./content.css";
// import Vue from "vue";
import VRuntimeTemplate from "v-runtime-template";

export default {
  name: "oeasc-content",
  props: ["code", "containerClassIn", "meta"],
  watch: {
    $route() {
      // react to route changes...
      this.initContent();
    }
  },
  components: {
    VRuntimeTemplate,
    faqDeclaration, // eslint-disable-line
    tableAide, // eslint-disable-line
    declarationTable // eslint-disable-line
  },
  data: () => ({
    // component: null,
    contentHTML: "",
    contentMD: "",
    bEditContent: false,
    containerClass: {}
  }),
  methods: {
    setContent: function(data) {
      this.contentHTML = `<div>${data.html}</div>`;
      this.contentMD = data.md;
      this.bEditContent = false;
      setTimeout(() => {
        document.body.style.zIndex = 1;
        for (const elem of document.getElementsByClassName("map")) {
          const preConfigName = elem.getAttribute("config");
          const mapConfig = MapService.getPreConfigMap(preConfigName);
          const mapContainerId = elem.getAttribute("id");

          const mapService = new MapService(mapContainerId, mapConfig);

          mapService.init();
        }
      }, 100);
    },
    getCode: function() {
      return this.code || this.$route.params.code || config.defaultContent;
    },

    initContent: function() {
      apiRequest("GET", `api/commons/content/${this.getCode()}`).then(data =>
        this.setContent(data)
      );
    },

    updateContent: function() {
      let data = {
        md: this.contentMD,
        code: this.getCode()
      };

      apiRequest("PATCH", `api/commons/content/${this.getCode()}`, {
        data
      }).then(data => this.setContent(data));
    }
  },

  mounted: function() {
    this.initContent();
  }
};
</script>
