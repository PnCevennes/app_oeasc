<template>
  <div :class="{ 'content-page': isPage }" v-if="bInitialized">
    <div>
      <div v-if="!bEditContents && content">
        <div>
          <v-btn
            icon
            v-if="!bEditContents && $store.getters.droitMax >= 5"
            @click="bEditContents = true"
            ref="btn-edit-content"
          >
            <v-icon>edit</v-icon>
          </v-btn>
        </div>

        <div v-if="displayContentDate">
          <i>Crée le {{ displayDate(content.meta_create_date) }}</i>

          <i
            v-if="
              displayDate(content.meta_create_date) !=
                displayDate(content.meta_update_date)
            "
            >, modifié le {{ displayDate(content.meta_create_date) }}</i
          >
        </div>
        <v-runtime-template
          class="content"
          :template="content.html"
        ></v-runtime-template>
        <div v-if="linkFullContent">
          <a :href="`#/${link}/${content.code}`">Lire la suite</a>
        </div>
      </div>
      <div>
        <div v-if="bEditContents && content" class="edit-content">
          <div>
            <v-btn icon v-if="bEditContents" @click="bEditContents = false">
              <v-icon>cancel</v-icon>
            </v-btn>
            <v-btn
              icon
              v-if="bEditContents"
              @click="
                configImgForm.value = null;
                dialogImg = true;
              "
            >
              <v-icon>image</v-icon>
            </v-btn>
            <v-btn
              icon
              v-if="bEditContents"
              @click="
                configDocForm.value = null;
                dialogDoc = true;
              "
            >
              <v-icon>fa-file-alt</v-icon>
            </v-btn>
          </div>

          <generic-form
            ref="content-form"
            :config="configContentForm"
            @onSuccess="setContent($event)"
          >
          </generic-form>

          <v-dialog max-width="1400px" v-model="dialogImg">
            <v-card v-if="dialogImg">
              <genericForm
                class="edit-dialog"
                :config="configImgForm"
                @onSuccess="getImg($event)"
              ></genericForm>
            </v-card>
          </v-dialog>

          <v-dialog max-width="1400px" v-model="dialogDoc">
            <v-card v-if="dialogDoc">
              <genericForm
                class="edit-dialog"
                :config="configDocForm"
                @onSuccess="getDoc($event)"
              ></genericForm>
            </v-card>
          </v-dialog>
          <v-snackbar color="success" v-model="bSnack" :timeout="2000">
            {{ msgSnack }}
          </v-snackbar>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
// load content
import { config } from "@/config/config.js";
// import { MapService } from "@/modules/map";
import faqDeclaration from "./faq-declaration";
import tableAide from "./table-aide";
import declarationTable from "@/modules/declaration/declaration-table";
import baseMap from "@/modules/map/base-map";
import contentImg from "./content-img";
import listePartenaire from "./liste-partenaire";
import inGraph from "@/modules/in/in-graph.vue";
import inTable from "@/modules/in/in-table.vue";
import restitution from "@/modules/restitution/restitution.vue";

import "./content.css";
// import Vue from "vue";
import VRuntimeTemplate from "v-runtime-template";
import configContentForm from "./config/form-content";
import configImgForm from "./config/form-img";
import configDocForm from "./config/form-doc";
import genericForm from "@/components/form/generic-form";
import marked from "marked";

export default {
  name: "oeasc-content",
  props: [
    "code",
    "containerClassIn",
    "meta",
    "nbLines",
    "displayContentDate",
    "link",
    "page",
    "tagNames"
  ],
  watch: {
    $route() {
      // react to route changes...
      this.initContent();
    }
  },
  computed: {
    docPath() {
      return this.$store.getters.mediaDocPath;
    },
    isPage() {
      return this.page != "undefined";
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
    genericForm
  },
  data: () => ({
    keysPressed: {},
    dp: null,
    content: null,
    bEditContents: false,
    containerClass: {},
    mainConfig: config,
    linkFullContent: null,
    dialogImg: false,
    dialogDoc: false,
    configContentForm,
    configImgForm,
    configDocForm,
    bSnack: false,
    msgSnack: null,
    bInitialized: false
  }),
  methods: {
    displayDate(date) {
      return date && date.split(" ")[0];
    },
    getImg(event) {
      const str_img = `<content-img ${event.center ? "center" : ""}
  src="${event.src || ""}"
  title="${event.title || ""}"
  source="${event.source || ""}"></content-img>`;
      navigator.clipboard.writeText(str_img).then(() => {
        this.dialogImg = false;
        this.bSnack = true;
        this.msgSnack = `Le code de l'image à été copié dans le presse-papier`;
      });
    },
    getDoc(event) {
      const str_doc = `<a :href="docPath + '${
        event.src
      }'" target="_blanck">${event.txt || event.src}</a>`;
      navigator.clipboard.writeText(str_doc).then(() => {
        this.dialogDoc = false;
        this.bSnack = true;
        this.msgSnack = `Le code du lien à été copié dans le presse-papier`;
      });
    },

    setContent(data) {
      this.content = data;
      this.configContentForm.value = this.content;
      let html = marked(data.md || "");
      if (this.nbLines) {
        this.linkFullContent = html.split("\n").length > this.nbLines;
        html = html
          .split("\n")
          .slice(0, this.nbLines)
          .join("\n");
      }
      this.content.html = `<div>${html}</div>`;
      this.bEditContents = !this.content.code;
    },
    getCode() {
      return this.code || this.$route.params.code;
    },

    initContent() {

      if (!this.getCode()) {
        const content = {};
        if (this.tagNames) {
          const configStoreTag = this.$store.getters.configStore("commonsTag");
          content.tags = this.$store.getters[configStoreTag.names].filter(t => {  
            return this.tagNames.includes(t.nom_tag)
          }
          );
        }
        this.setContent(content);
        return;
      }

      const configStore = this.$store.getters.configStore("commonsContent");
      console.log('uuuu')
      this.$store
        .dispatch(configStore.get, { value: this.getCode(), fieldName: "code" })
        .then(
          data => this.setContent(data),
          error => {error; this.setContent({code: this.getCode()})}
        );
    },
    manageKeys() {
      if (
        ["Control", " "].every(key =>
          Object.keys(this.keysPressed).includes(key)
        )
      ) {
        const elem = document.querySelector(
          ".content :is(h1, h2, h3, h4, h5, h6):hover, .content p:hover, .content li:hover"
        );

        if (elem && elem.innerHTML) {
          const preText =
            elem.tagName[0].toLowerCase() == "h"
              ? "# "
              : elem.tagName.toLowerCase() == "li"
              ? "* "
              : "";
          const text = preText + elem.innerHTML;

          let index = this.content.md
            .replace(this.$store.getters.mediaDocPath, "")
            .replace(this.$store.getters.mediaImgPath, "")
            .indexOf(text);
          for (let s = text.length; s >= 5 || index == -1; s--) {
            index = this.content.md.indexOf(text.substring(0, s));
          }
          setTimeout(() => {
            const textAreaContent = this.$refs[
              "content-form"
            ].$el.querySelector("textarea");
            textAreaContent.focus();
            if (index != -1) {
              textAreaContent.setSelectionRange(index, index);
            }
          }, 500);
        }

        // var elementMouseIsOver = document.elementFromPoint(x, y);
        const btnEditContent = this.$refs["btn-edit-content"];
        if (btnEditContent) {
          btnEditContent.click({});
        }
        const btnValidFormContent =
          this.$refs["content-form"] &&
          this.$refs["content-form"].$refs["btn-valid-form"];
        if (btnValidFormContent) {
          btnValidFormContent.click({});
        }
      }
    },
    onKeyUp(event) {
      if (this.$store.getters.droitMax <= 5 || !event) {
        return;
      }
      setTimeout(() => {
        if (this.keysPressed[event.key]) {
          delete this.keysPressed[event.key];
        }
        this.keysPressed = {};
      }, 50);
    },
    onKeyDown(event) {
      if (this.$store.getters.droitMax <= 5 || !event) {
        return;
      }
      if (!Object.keys(this.keysPressed).includes(event.key)) {
        this.keysPressed[event.key] = true;
        this.manageKeys(event);
      }
    }
  },
  mounted() {
    // load Tags

    const configStoreTag = this.$store.getters.configStore("commonsTag");
    
    this.$store.dispatch(configStoreTag.getAll).then(() => {
      this.bInitialized = true;
      this.initContent();
    });
  },
  created() {
    window.removeEventListener("keyup", this.onKeyUp);
    window.addEventListener("keyup", this.onKeyUp);

    window.removeEventListener("keydown", this.onKeyDown);
    window.addEventListener("keydown", this.onKeyDown);
  }
};
</script>
