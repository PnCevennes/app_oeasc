<template>
  <div>
    <div class="content-containter">
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
      <div v-if="!bEditContent" class="content" v-html="contentHTML"></div>
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
// import Vue from 'vue';

import "./content.css";
// import { baseMap } from "../../components/map";

// let contentHTML = "";
// let contentMD = "";
// let bEditContent = false;

export default {
  name: "oeasc-content",
  props: ["code"],
  watch: {
    $route() {
      // react to route changes...
      this.initContent();
    }
  },
  data: () => ({
    contentHTML: "",
    contentMD: "",
    bEditContent: false,
  }),
  methods: {
    setContent: function(data) {
      this.contentHTML = data.html;
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
      console.log('init content', this.code, this.getCode())
      apiRequest("GET", `api/commons/content/${this.getCode()}`).then(
        (data) => this.setContent(data)
      );
    },
    updateContent: function() {

      let data = {
        md: this.contentMD,
        code: this.getCode()
      };

      apiRequest("PATCH", `api/commons/content/${this.getCode()}`, { data }).then(
        (data) => this.setContent(data)
      );
    }
  },

  mounted: function() {
    this.initContent()
  }
};
</script>
