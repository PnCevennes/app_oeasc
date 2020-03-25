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
        <md-button v-if="bEditContent" class="md-icon-button" @click="bEditContent = false">
          <md-icon>cancel</md-icon>
        </md-button>

        <md-button v-if="bEditContent" class="md-icon-button" @click="updateContent()">
          <md-icon>check</md-icon>
        </md-button>
      </div>
      <div v-if="!bEditContent" class="content" v-html="contentHTML"></div>
      <div v-if="bEditContent" class="editor">
        <md-field>
          <label>Textarea</label>
          <md-textarea v-model="contentMD" :rows="20" :md-autogrow="true"></md-textarea>
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

let contentHTML = "";
let contentMD = "";
let bEditContent = false;

let setContent = function(data) {
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
};

let initContent = function() {
  let code = this.$route.params.code || config.defaultContent;

  apiRequest("GET", `api/commons/content/${code}`).then(setContent.bind(this));
};

let updateContent = function() {
  let code = this.$route.params.code || config.defaultContent;

  let data = {
    md: this.contentMD,
    code
  };

  apiRequest("PATCH", `api/commons/content/${code}`, { data }).then(
    setContent.bind(this)
  );
};

export default {
  name: "oeasc-content",
  watch: {
    $route() {
      // react to route changes...
      initContent.bind(this)();
    }
  },
  data: () => ({
    contentHTML,
    contentMD,
    bEditContent,
    updateContent
  }),
  created: initContent
};
</script>
