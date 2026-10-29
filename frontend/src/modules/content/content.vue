<template>
  <div
    :class="{ 'content-page': isPage, 'content-appercu': this.nbLines }"
    v-if="bInitialized"
  >
    <!-- @mouseover="onMouseOver()" @mouseout="onMouseOut()" -->
    <div>
      <!-- si on n'est pas en mode édition et que le contenu est défini -->
      <div v-if="!bEditContents && content">
        <div>
          <!-- bouton pour éditer le contenu -->
          <v-btn
            icon
            variant="text"
            v-if="!bEditContents && $store.getters.droitMax >= 5"
            @click="bEditContents = true"
            :ref="`btn-edit-content_${getCode()}`"
          >
            <v-icon>edit</v-icon>
          </v-btn>
        </div>

        <!-- affichage de la date de création et de modification pour les actu -->
        <div v-if="displayContentDate">
          <i>Le {{ formatDateFr(content.meta_create_date) }}</i>
        </div>

        <!-- affichage du contenu -->
        <!-- evite la propagation des événements de clavier vers les élements parents pour éviter les conflits raccourcis clavier -->
        <v-runtime-template
          v-if="!renderError"
          class="content"
          @keydown="$event.stopPropagation()"
          @keyup="$event.stopPropagation()"
          :template="content.html"
        ></v-runtime-template>
      </div>
      <div>
        <!-- si on est en mode édition -->
        <div
          v-if="bEditContents && content"
          class="edit-content"
        >
          <div>
            <v-btn
              icon
              variant="text"
              v-if="bEditContents"
              @click="bEditContents = false"
            >
              <v-icon>cancel</v-icon>
            </v-btn>
            <v-btn
              icon
              variant="text"
              v-if="bEditContents"
              @click="
                configImgForm.value = { position: 'center' };
                dialogImg = true;
              "
            >
              <v-icon>image</v-icon>
            </v-btn>
            <v-btn
              icon
              variant="text"
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
              variant="text"
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
          ></generic-form>

          <v-dialog
            max-width="1400px"
            v-model="dialogImg"
          >
            <v-card v-if="dialogImg">
              <genericForm
                class="edit-dialog"
                :config="configImgForm"
                @onSuccess="getImg($event)"
              ></genericForm>
            </v-card>
          </v-dialog>

          <v-dialog
            max-width="1400px"
            v-model="dialogDoc"
          >
            <v-card v-if="dialogDoc">
              <genericForm
                class="edit-dialog"
                :config="configDocForm"
                @onSuccess="getDoc($event)"
              ></genericForm>
            </v-card>
          </v-dialog>
          <v-snackbar
            color="success"
            v-model="bSnack"
            :timeout="2000"
          >
            {{ msgSnack }}
          </v-snackbar>
        </div>

        <!-- fin -->
      </div>
    </div>
    <val />
  </div>
</template>

<script>
// Chargement des contenu pour les type = "page" défini dans le index.js

import { defineAsyncComponent } from 'vue';
import { config } from '@/config/config.js';
import components from './config/components';

import './content.css';
import configContentForm from './config/form-content';
import configImgForm from './config/form-img';
import configDocForm from './config/form-doc';
import marked from 'marked';
import { escapeHtml, formatDateFr } from '@/core/js/util/util.js';

import VRuntimeTemplate from 'vue3-runtime-template'; // pour l'affichage du contenu markdown dynamique

// formulaire de modification de page : chargé à la demande. content.vue est monté pour CHAQUE
// page CMS vue par TOUS les visiteurs (pas seulement les admins) ; le formulaire lui-même n'est
// affiché que derrière v-if="bEditContents" (voir template), mais un import statique aurait quand
// même fait télécharger tout son arbre (generic-form -> dynamic-form-group -> dynamic-form, qui
// utilise une bonne partie des composants de saisie Vuetify) à chaque visiteur, admin ou non.
const genericForm = defineAsyncComponent(() => import('@/components/form/generic-form'));

export default {
  name: 'oeasc-content',
  components: {
    ...components,
    VRuntimeTemplate,
    genericForm,
  },
  // un échec de compilation/rendu du template d'un contenu (HTML invalide issu de la BDD,
  // variable absente comme `meta`) ne doit pas faire planter toute la page
  errorCaptured(err) {
    console.error(`Contenu CMS "${this.getCode()}" non affichable :`, err);
    this.renderError = true;
    return false;
  },
  props: [
    'code',
    'containerClassIn',
    'meta',
    'nbLines',
    'displayContentDate',
    'link',
    'page',
    'tagNames',
  ],
  watch: {
    // Navigation entre deux pages /actualite/:code qui réutilisent ce composant.
    // Ne rien faire quand le code vient d'une prop (liste d'actualités) ou quand on QUITTE la
    // page (code absent de la route) : sinon setContent({}) basculait le composant en mode
    // édition pendant son démontage, d'où des erreurs de patch Vue (« C is null », « parentNode »).
    '$route.params.code'(newCode) {
      if (this.code || !newCode) return;
      this.initContent();
    },
    'content.html'() {
      this.renderError = false;
    },
  },
  computed: {
    configForm() {
      const configForm = {
        ...this.configContentForm,
        value: this.content,
      };
      return configForm;
    },
    docPath() {
      return this.$store.getters.mediaDocPath;
    },
    isPage() {
      return this.page !== 'undefined';
    },
  },
  data: () => ({
    mouseIn: true,
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
    renderError: false,
    contentValues: {
      id_espece: null,
      espece: null,
      id_zone_indicative: [],
      id_zone_cynegetique: [],
      id_secteur: [],
      id_saison: null,
    },
  }),
  methods: {
    formatDateFr,
    // onMouseOver() { // non utilisé

    getImg(event) {
      // attributs toujours entre guillemets et échappés : le snippet est ensuite compilé comme template Vue
      const attr = (name, val) => (val ? ` ${name}="${escapeHtml(val)}"` : '');
      let str_img = '<content-img';
      str_img += !event.position
        ? ''
        : event.position == 'center'
          ? ' center'
          : attr('float', event.position);
      str_img += attr('src', event.src);
      str_img += attr('source', event.source);
      str_img += attr('author', event.author);
      str_img += attr('title', event.title);
      str_img += attr('height', event.height);
      str_img += attr('width', event.width);
      str_img += ' ></content-img>';
      navigator.clipboard.writeText(str_img).then(() => {
        this.dialogImg = false;
        this.bSnack = true;
        this.msgSnack = `Le code de l'image à été copié dans le presse-papier`;
      });
    },
    getDoc(event) {
      // src est inséré dans une chaîne JS d'une expression Vue, elle-même dans un attribut HTML :
      // on échappe d'abord pour JS (\ et '), puis pour HTML. Le texte du lien ne doit pas
      // pouvoir ouvrir une interpolation Vue ({{ }}).
      const srcJs = String(event.src ?? '').replace(/\\/g, '\\\\').replace(/'/g, "\\'");
      const txt = escapeHtml(event.txt || event.src).replace(/\{/g, '&#123;');
      const str_doc = `<a :href="docPath + '${escapeHtml(srcJs)}'" target="_blank" rel="noopener noreferrer">${txt}</a>`;
      navigator.clipboard.writeText(str_doc).then(() => {
        this.dialogDoc = false;
        this.bSnack = true;
        this.msgSnack = `Le code du lien à été copié dans le presse-papier`;
      });
    },

    // getFormData(ref, key) { // non utilisé

    //     return out
    //   }, 1000)

    setContent(data) {
      // recupère le contenu est le transforme en html. Place ce contenu dans content.html qui sera ensuite intégré au template
      this.content = data;

      this.configContentForm.value = this.content;
      let html = marked(data.md || '');
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
          const configStoreTag = this.$store.getters.configStore('commonsTag');
          content.tags = this.$store.getters[configStoreTag.storeNames].filter((t) => {
            return this.tagNames.includes(t.nom_tag);
          });
        }
        this.setContent(content);
        return;
      }

      const configStore = this.$store.getters.configStore('commonsContent');
      const code = this.getCode();
      this.$store.dispatch(configStore.get, { value: code, fieldName: 'code' }).then(
        (data) => {
          // réponse périmée (navigation entre-temps) ou composant démonté : on ignore
          if (this.$.isUnmounted || code !== this.getCode()) return;
          this.setContent(data);
        },
        // si erreur => content vide (comportement prod != dev)
        (error) => {
          error;
          if (this.$.isUnmounted || code !== this.getCode()) return;
          this.setContent({ code: this.getCode() });
        }
      );
    },


    triggerValidForm() {
      const btnValidFormContent =
        this.$refs[`content-form_${this.getCode()}`] &&
        this.$refs[`content-form_${this.getCode()}`].$refs[`btn-valid-form`];
      if (btnValidFormContent) {
        btnValidFormContent.click({});
      }
    },

  },
  mounted() {
    // load Tags

    const configStoreTag = this.$store.getters.configStore('commonsTag');

    this.$store.dispatch(configStoreTag.getAll).then(() => {
      this.bInitialized = true;
      this.initContent();
    });

  },
};
</script>
