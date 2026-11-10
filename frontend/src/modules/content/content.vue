<template>
  <div
    :class="{ 'content-page': isPage }"
    v-if="bInitialized"
  >
    <!-- @mouseover="onMouseOver()" @mouseout="onMouseOut()" -->
    <div>
      <!-- contenu affiché (reste visible derrière la fenêtre d'édition) -->
      <div v-if="content">
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
        <!-- mode édition (création ou modification) : fenêtre modale -->
        <v-dialog
          :model-value="bEditContents && !!content"
          max-width="1200px"
          scrollable
          persistent
        >
          <v-card
            v-if="bEditContents && content"
            class="edit-content-modal"
          >
            <v-card-title class="d-flex align-center">
              <span>{{ content.code ? `Modifier « ${content.code} »` : 'Nouveau contenu' }}</span>
            </v-card-title>
            <v-card-text>
          <generic-form
            :ref="`content-form_${getCode()}`"
            :config="configForm"
            @onSuccess="onSaved($event)"
          ></generic-form>

          <v-snackbar
            color="success"
            v-model="bSnack"
            :timeout="2000"
          >
            {{ msgSnack }}
          </v-snackbar>
            </v-card-text>
            <v-card-actions>
              <v-spacer></v-spacer>
              <v-btn
                variant="text"
                @click="cancelEdit()"
              >
                Annuler
              </v-btn>
              <v-btn
                color="success"
                variant="flat"
                @click="triggerValidForm()"
              >
                <v-icon start>fa-check</v-icon>
                Enregistrer
              </v-btn>
            </v-card-actions>
          </v-card>
        </v-dialog>
      </div>
    </div>
    <val />
  </div>
</template>

<script>
// Chargement des contenu pour les type = "page" défini dans le index.js

import { defineAsyncComponent } from 'vue';
import components from './config/components';

import './content.css';
import configContentForm from './config/form-content';
import { marked } from 'marked';
import { estContenuHtml, MARQUE_HTML } from '@/components/form/wysiwyg/wysiwyg-marque.js';
import { formatDateFr } from '@/core/js/util/util.js';

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
  props: ['code', 'meta', 'displayContentDate', 'page', 'typePage'],
  // pont vers l'éditeur visuel (wysiwyg-editor.vue) : il y place sa fonction d'insertion, utilisée
  // par les boutons image / document pour insérer directement dans le texte
  provide() {
    return { editorBridge: this.editorBridge };
  },
  watch: {
    // Navigation entre deux pages /actualite/:code qui réutilisent ce composant.
    // Ne rien faire quand le code vient d'une prop (liste d'actualités) ou quand on QUITTE la
    // page (code absent de la route) : sinon setContent({}) basculait le composant en mode
    // édition pendant son démontage, d'où des erreurs de patch Vue (« C is null », « parentNode »).
    '$route.params.code'(newCode) {
      if (this.code || !newCode) return;
      this.initContent();
    },
    // Navigation entre deux pages CMS (page.vue) : le routeur réutilise le même composant, seul le
    // code passé en prop change. Sans ce watcher, le contenu de la première page restait affiché.
    code(newCode, oldCode) {
      if (!this.bInitialized || newCode === oldCode) return;
      this.bEditContents = false;
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
    // chemin des images du serveur : utilisé par les images de l'éditeur visuel dans les textes
    // (`<img :src="imgPath + 'nom.jpg'">`, voir wysiwyg-extensions.js)
    imgPath() {
      return this.$store.getters.mediaImgPath;
    },
    isPage() {
      return this.page !== 'undefined';
    },
  },
  data: () => ({
    content: null,
    bEditContents: false,
    configContentForm,
    bSnack: false,
    msgSnack: null,
    bInitialized: false,
    renderError: false,
    editorBridge: { insert: null },
    // Utilisé par les gabarits CMS (html des contenus) : formulaires de sélection espèce/secteur/saison...
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

    // getFormData(ref, key) { // non utilisé

    //     return out
    //   }, 1000)

    setContent(data) {
      // recupère le contenu est le transforme en html. Place ce contenu dans content.html qui sera ensuite intégré au template
      this.content = data;

      this.configContentForm.value = this.content;
      // contenu enregistré par l'éditeur visuel : déjà du HTML ; anciens contenus : markdown
      let html = estContenuHtml(data.md) ? data.md.slice(MARQUE_HTML.length) : marked(data.md || '');
      this.content.html = `<div>${html}</div>`;
      this.bEditContents = !this.content.code;
    },

    getCode() {
      return this.code || this.$route.params.code;
    },

    // contenu enregistré : la fenêtre se ferme ; après une création, on va sur la page du contenu
    onSaved(data) {
      this.setContent(data);
      if (this.$route.name === 'actualite.new' && data && data.code) {
        this.$router.push(`/actualite/${data.code}`);
      }
    },

    // fermeture de la fenêtre d'édition sans enregistrer ; une création abandonnée n'a pas de
    // page à afficher : retour à la liste des actualités
    cancelEdit() {
      this.bEditContents = false;
      if (this.content && !this.content.code) {
        this.$router.push('/actualites');
      }
    },

    initContent() {
      if (!this.getCode()) {
        // création : type posé automatiquement (« actualite » via la route actualité, sinon « page »)
        this.setContent({ type_page: this.typePage || 'page' });
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


    // enregistre le formulaire d'édition (bouton « Enregistrer » de la modale) : on appelle
    // directement l'action du generic-form ; avec Vuetify 3 la ref d'un v-btn est une instance de
    // composant (sans .click()), pas un élément DOM
    triggerValidForm() {
      const form = this.$refs[`content-form_${this.getCode()}`];
      if (form && typeof form.processAction === 'function') {
        form.processAction();
      }
    },

  },
  mounted() {
    this.bInitialized = true;
    this.initContent();
  },
};
</script>
