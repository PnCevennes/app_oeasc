<template>
  <div
    :class="{ 'content-page': isPage, 'content-appercu': this.nbLines }"
    v-if="bInitialized"
  >
    <!-- @mouseover="onMouseOver()" @mouseout="onMouseOut()" -->
    <div>
      <div v-if="!bEditContents && content">
        <div>
          <v-btn
            icon
            v-if="!bEditContents && $store.getters.droitMax >= 5"
            @click="bEditContents = true"
            :ref="`btn-edit-content_${getCode()}`"
          >
            <v-icon>edit</v-icon>
          </v-btn>
        </div>

        <div v-if="displayContentDate">
          <i>Le {{ displayDate(content.meta_create_date) }}</i>

          <i
            v-if="
              displayDate(content.meta_create_date) !=
                displayDate(content.meta_update_date) && false
            "
            >, modifié le {{ displayDate(content.meta_create_date) }}</i
          >
        </div>
        <v-runtime-template
          class="content"
          @keydown="$event.stopPropagation()"
          @keyup="$event.stopPropagation()"
          :template="content.html"
        ></v-runtime-template>
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
                configImgForm.value = {position: 'center'};
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
            <v-btn
              icon
              v-if="bEditContents"
              @click="triggerValidForm()"
            >
              <v-icon>fa-check</v-icon>
            </v-btn>

          </div>
          <generic-form
            :ref="`content-form_${getCode()}`"
            :config="configForm"
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
import components from "./config/components"

import "./content.css";
// import Vue from "vue";
import configContentForm from "./config/form-content";
import configImgForm from "./config/form-img";
import configDocForm from "./config/form-doc";
import marked from "marked";

import genericForm from "@/components/form/generic-form";
import VRuntimeTemplate from "v-runtime-template";

export default {
  name: "oeasc-content",
  components: {
    ...components,
    VRuntimeTemplate,
    genericForm
  },

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
    },
    content: {
      handler() {
      },
      deep: true
    }
  },
  computed: {
    configForm() {
      const configForm = {
        ...this.configContentForm,
        value: this.content
      };
      return configForm;
    },
    docPath() {
      return this.$store.getters.mediaDocPath;
    },
    isPage() {
      return this.page !== "undefined";
    }
  },
  data: () => ({
    mouseIn: true,
    keysPressed: {},
    dp: null,
    content: null,
    bEditContents: false,
    containerClass: {},
    mainConfig: config,
    dialogImg: false,
    dialogDoc: false,
    configContentForm,
    configImgForm,
    configDocForm,
    bSnack: false,
    msgSnack: null,
    bInitialized: false,
    contentValues: {espece: null, zi: null, zc: null}
  }),
  methods: {
    onMouseOver() {
      this.mouseIn = true;
    },
    onMouseOut() {
      this.mouseIn = false;
    },

    displayDate(date) {
      return date && date.split(" ")[0];
    },
    getImg(event) {
      let str_img = '<content-img '
     str_img += !event.position ? '' : event.position=='center' ? " center" : ` float=${event.position}`;
     str_img += !event.src ? '' : ` src=${event.src}`;
     str_img += !event.source ? '' : ` source=${event.source}`;
     str_img += !event.author ? '' : ` author=${event.author}`;
     str_img += !event.title ? '' : ` title=${event.title}`;
     str_img += !event.height ? '' : ` height=${event.height}`;
     str_img += !event.width ? '' : ` width=${event.width}`;
      str_img += ' ></content-img>';
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
    getFormData(ref, key) {
      setTimeout(() => {

        var out = this.$refs && this.$refs[ref] && this.$refs[ref].baseModel;
        console.log(this.$refs, ref, out)
        for (const k of key.split('.')) {
          if (!out) {
            break;
          }
          out = out[k]
        }
        return out
      }, 1000)
    },
    setContent(data) {
      this.content = data;

      this.configContentForm.value = this.content;
      let html = marked(data.md || "");
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
          content.tags = this.$store.getters[configStoreTag.storeNames].filter(t => {
            return this.tagNames.includes(t.nom_tag)
          }
          );
        }
        this.setContent(content);
        return;
      }

      const configStore = this.$store.getters.configStore("commonsContent");
      this.$store
        .dispatch(configStore.get, { value: this.getCode(), fieldName: "code" })
        .then(
          data => this.setContent(data),
          // si erreur => content vide (comportement prod != dev)
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
              `content-form_${this.getCode()}`
            ].$el.querySelector("textarea");
            textAreaContent.focus();
            if (index != -1) {
              textAreaContent.setSelectionRange(index, index);
            }
          }, 500);
        }

        // var elementMouseIsOver = document.elementFromPoint(x, y);
        const btnEditContent = this.$refs[`btn-edit-content_${this.getCode()}`];
        if (btnEditContent) {
          btnEditContent.click({});
        }
        const btnValidFormContent =
          this.$refs[`content-form_${this.getCode()}`] &&
          this.$refs[`content-form_${this.getCode()}`].$refs[`btn-valid-form`];
        if (btnValidFormContent) {
          btnValidFormContent.click({});
        }
      }
    },
    triggerValidForm() {
        const btnValidFormContent =
          this.$refs[`content-form_${this.getCode()}`] &&
          this.$refs[`content-form_${this.getCode()}`].$refs[`btn-valid-form`];
        if (btnValidFormContent) {
          btnValidFormContent.click({});
        }
    },
    onKeyUp(event) {
      if (this.$store.getters.droitMax <= 5 || !event || !this.mouseIn) {
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

      if (this.$store.getters.droitMax <= 5 || !event || !this.mouseIn) {
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

    // document.removeEventListener("keyup", this.onKeyUp);
    // document.addEventListener("keyup", this.onKeyUp);

    // document.removeEventListener("keydown", this.onKeyDown);
    // document.addEventListener("keydown", this.onKeyDown);

  },
  created() {
  }
};
</script>
