<template>
  <div>
    <div :class="containerClass">
      <div class="buttons">
        <md-button
          v-if="!bEditContent && $store.getters.droit_max >= 5"
          class="md-icon-button"
          @click="bEditContent = true"
        >
          <md-icon>edit</md-icon>
        </md-button>
        <md-button
          v-if="bEditContent"
          class="md-icon-button"
          @click="bEditContent = false"
        >
          <md-icon>cancel</md-icon>
        </md-button>

        <md-button
          v-if="bEditContent"
          class="md-icon-button"
          @click="updateContent()"
        >
          <md-icon>check</md-icon>
        </md-button>
      </div>

      <!-- <div v-if="!bEditContent" class="content" v-html="contentHTML"></div> -->
      <v-runtime-template v-if="!bEditContent" class="content" :template="contentHTML"></v-runtime-template>

      <div v-if="bEditContent" class="editor">
        <md-field>
          <label>Textarea</label>
          <md-textarea
            v-model="contentMD"
            :rows="20"
            :md-autogrow="true"
          ></md-textarea>
        </md-field>
      </div>
    </div>
  </div>
</template>

<script>
// load content
import { apiRequest } from "@/core/js/data/api.js";
import { config } from "@/config/config.js";
import { MapService } from "@/modules/map";
import faqDeclaration from "./faq-declaration"
import "./content.css";
// import Vue from "vue";
import VRuntimeTemplate from "v-runtime-template";

export default {
  name: "oeasc-content",
  props: ["code", "containerClassIn"],
  watch: {
    $route() {
      // react to route changes...
      this.initContent();
    }
  },
  components: {
    VRuntimeTemplate,
    faqDeclaration // eslint-disable-line
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
      // const cs = Vue.component("contentView", {
      //   render: function(h) {
      //     const div = document.createElement("div");
      //     div.innerHTML = data.html;
      //     return Vue.compile(h(div.outerHTML));
      //   }
      // });
      // this.component = cs;
      // console.log(cs, data.html);
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
    if (this.containerClassIn) {
      this.containerClass[this.containerClassIn] = true;
    } else {
      this.containerClass = { "content-containter": true };
    }
    this.initContent();
  }
};
</script>
