<!--
  Éditeur de texte visuel (WYSIWYG, Tiptap) pour les contenus : pages et actualités.

  Le texte est mis en forme directement, comme dans un traitement de texte ; la valeur (v-model)
  est le HTML correspondant, précédé d'une marque (voir wysiwyg-extensions.js). Les anciens
  contenus en markdown sont convertis à l'ouverture, sans être réécrits tant qu'on ne les modifie pas.

  Les composants Vue présents dans un contenu (<restitution>, <content-img>, <v-icon>…) sont
  conservés tels quels et affichés comme des pastilles ; double-clic pour en modifier le code, bouton
  « Composant » pour en insérer un.

  Insertion depuis l'extérieur (images / documents de content.vue) : le parent fournit
  `editorBridge` ({ insert: null }) ; l'éditeur y place sa fonction d'insertion.
-->
<template>
  <div
    v-if="editor"
    class="wysiwyg"
  >
    <div
      class="wysiwyg-outils"
      role="toolbar"
      aria-label="Mise en forme"
    >
      <v-select
        :model-value="style"
        :items="styles"
        item-title="titre"
        item-value="valeur"
        density="compact"
        variant="outlined"
        hide-details
        label="Style"
        class="wysiwyg-select"
        @update:model-value="setStyle"
      ></v-select>
      <v-select
        :model-value="taille"
        :items="tailles"
        item-title="titre"
        item-value="valeur"
        density="compact"
        variant="outlined"
        hide-details
        label="Taille"
        class="wysiwyg-select"
        @update:model-value="setTaille"
      ></v-select>

      <div
        v-for="(groupe, rang) of groupes"
        :key="rang"
        class="wysiwyg-groupe"
      >
        <v-btn
          v-for="outil of groupe"
          :key="outil.titre"
          :title="outil.titre"
          :aria-label="outil.titre"
          :aria-pressed="outil.actif ? outil.actif() : undefined"
          :variant="outil.actif && outil.actif() ? 'tonal' : 'text'"
          :disabled="outil.inactif ? outil.inactif() : false"
          :icon="outil.icone"
          size="small"
          density="comfortable"
          @mousedown.prevent
          @click="outil.action"
        ></v-btn>
      </div>

      <!-- couleur du texte -->
      <v-menu :close-on-content-click="false">
        <template v-slot:activator="{ props }">
          <v-btn
            v-bind="props"
            title="Couleur du texte"
            aria-label="Couleur du texte"
            :variant="couleurActuelle ? 'tonal' : 'text'"
            icon="mdi-palette"
            size="small"
            density="comfortable"
          ></v-btn>
        </template>
        <v-card class="pa-2 wysiwyg-couleurs">
          <div class="wysiwyg-grille-couleurs">
            <button
              v-for="couleur of COULEURS"
              :key="couleur"
              type="button"
              :style="{ backgroundColor: couleur }"
              :class="{ choisie: couleur === couleurActuelle }"
              :aria-label="`Couleur ${couleur}`"
              @click="appliqueCouleur(couleur)"
            ></button>
          </div>
          <label class="wysiwyg-couleur-libre">
            Autre couleur
            <input
              type="color"
              :value="couleurActuelle || '#000000'"
              @input="appliqueCouleur($event.target.value)"
            />
          </label>
          <v-btn
            size="small"
            variant="text"
            block
            @click="appliqueCouleur(null)"
          >
            Couleur par défaut
          </v-btn>
        </v-card>
      </v-menu>

      <!-- smileys -->
      <v-menu :close-on-content-click="false">
        <template v-slot:activator="{ props }">
          <v-btn
            v-bind="props"
            title="Insérer un smiley"
            aria-label="Insérer un smiley"
            variant="text"
            icon="mdi-emoticon-outline"
            size="small"
            density="comfortable"
          ></v-btn>
        </template>
        <v-card class="pa-2 wysiwyg-emojis">
          <section
            v-for="categorie of EMOJIS"
            :key="categorie.titre"
          >
            <h4>{{ categorie.titre }}</h4>
            <div class="wysiwyg-grille-emojis">
              <button
                v-for="emoji of categorie.liste"
                :key="emoji"
                type="button"
                :aria-label="`Insérer ${emoji}`"
                @click="insereEmoji(emoji)"
              >
                {{ emoji }}
              </button>
            </div>
          </section>
        </v-card>
      </v-menu>

      <!-- outils du tableau, quand le curseur y est -->
      <div
        v-if="isActive('table')"
        class="wysiwyg-groupe wysiwyg-tableau"
      >
        <v-btn
          v-for="outil of outilsTableau"
          :key="outil.titre"
          :title="outil.titre"
          size="small"
          variant="text"
          @mousedown.prevent
          @click="outil.action"
        >
          {{ outil.libelle }}
        </v-btn>
      </div>
    </div>

    <editor-content
      :editor="editor"
      class="wysiwyg-zone content"
    ></editor-content>

    <!-- lien -->
    <v-dialog
      v-model="lienOuvert"
      max-width="520px"
    >
      <v-card>
        <v-card-title>Lien</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="adresse"
            label="Adresse"
            placeholder="https://… ou /nom_de_page"
            autofocus
            @keyup.enter="appliqueLien"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            v-if="isActive('link')"
            variant="text"
            @click="retireLien"
          >
            Retirer le lien
          </v-btn>
          <v-btn
            color="success"
            variant="flat"
            @click="appliqueLien"
          >
            Appliquer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- image : lien ou envoi d'un fichier -->
    <v-dialog
      v-model="imageOuverte"
      max-width="520px"
      scrollable
    >
      <v-card>
        <v-card-title>Image</v-card-title>
        <v-card-text>
          <v-text-field
            v-model="imageAdresse"
            label="Adresse de l'image (nom de fichier du serveur ou https://…)"
            placeholder="https://…"
            autofocus
            @keyup.enter="appliqueImage"
          ></v-text-field>
          <v-file-input
            v-model="imageFichier"
            label="… ou envoyer une image depuis l'ordinateur"
            accept="image/*"
            prepend-icon=""
            prepend-inner-icon="mdi-upload"
            :loading="imageEnvoiEnCours"
            :disabled="imageEnvoiEnCours"
            @update:model-value="envoieImage"
          ></v-file-input>
          <v-alert
            v-if="imageErreur"
            type="error"
            density="compact"
            class="mb-2"
          >
            {{ imageErreur }}
          </v-alert>
          <img
            v-if="imageAdresse.trim()"
            :src="apercuImage(imageAdresse.trim())"
            alt=""
            class="wysiwyg-apercu"
          />
          <v-text-field
            v-model="imageAlt"
            label="Description (lue à la place de l'image)"
          ></v-text-field>
          <v-text-field
            v-model="imageTitre"
            label="Légende"
          ></v-text-field>
          <v-text-field
            v-model="imageSource"
            label="Auteur / source"
          ></v-text-field>
          <v-select
            v-model="imagePosition"
            :items="POSITIONS_IMAGE"
            item-title="titre"
            item-value="valeur"
            label="Position"
          ></v-select>
          <v-checkbox
            v-model="imageTitreSurImage"
            label="Afficher la légende sur l'image"
            density="compact"
            hide-details
          ></v-checkbox>
          <v-text-field
            v-model="imageLien"
            label="Lien au clic (image agrandie, optionnel)"
            placeholder="nom_de_fichier.jpg ou https://…"
          ></v-text-field>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="imageOuverte = false"
          >
            Annuler
          </v-btn>
          <v-btn
            color="success"
            variant="flat"
            :disabled="!imageAdresse.trim() || imageEnvoiEnCours"
            @click="appliqueImage"
          >
            Insérer
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!-- document : choix d'un document existant ou envoi, inséré sous forme de lien -->
    <v-dialog
      v-model="documentOuvert"
      max-width="1400px"
    >
      <v-card v-if="documentOuvert">
        <generic-form
          class="edit-dialog"
          :config="configDocForm"
          @onSuccess="appliqueDocument"
        ></generic-form>
      </v-card>
    </v-dialog>

    <!-- code d'un composant -->
    <v-dialog
      v-model="composantOuvert"
      max-width="800px"
    >
      <v-card>
        <v-card-title>Composant</v-card-title>
        <v-card-text>
          <p class="mb-2">
            Code du composant (ex. <code>&lt;v-icon&gt;fa-file-pdf&lt;/v-icon&gt;</code>,
            <code>&lt;restitution …&gt;&lt;/restitution&gt;</code>). Il est affiché tel quel sur la page.
          </p>
          <v-textarea
            v-model="composantCode"
            label="Code"
            rows="6"
            auto-grow
            autofocus
            style="font-family: monospace"
          ></v-textarea>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            variant="text"
            @click="composantOuvert = false"
          >
            Annuler
          </v-btn>
          <v-btn
            color="success"
            variant="flat"
            :disabled="!composantCode.trim()"
            @click="appliqueComposant"
          >
            {{ composantPosition === null ? 'Insérer' : 'Modifier' }}
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { defineAsyncComponent, markRaw } from 'vue';
import { Editor, EditorContent } from '@tiptap/vue-3';
import StarterKit from '@tiptap/starter-kit';
import { Extension } from '@tiptap/core';
import TextAlign from '@tiptap/extension-text-align';
import { Color, FontSize, TextStyle } from '@tiptap/extension-text-style';
import { TableKit } from '@tiptap/extension-table';
import { apiRequest } from '@/core/js/data/api.js';
import { escapeHtml } from '@/core/js/util/util.js';
import configDocForm from '@/modules/content/config/form-doc';
import {
  ComposantBloc,
  ComposantEnLigne,
  ImageLegende,
  adresseImage,
  attributsComposant,
  contenuVersEditeur,
  editeurVersContenu,
  estEnLigne,
} from './wysiwyg-extensions.js';

// chargé à la demande (arbre generic-form -> dynamic-form volumineux)
const genericForm = defineAsyncComponent(() => import('@/components/form/generic-form'));

const COULEURS = [
  '#000000', '#4d4d4d', '#808080', '#b3b3b3',
  '#c0392b', '#e74c3c', '#e67e22', '#f39c12',
  '#f1c40f', '#27ae60', '#16a085', '#2ecc71',
  '#2980b9', '#3498db', '#8e44ad', '#d81b60',
];

const EMOJIS = [
  { titre: 'Visages', liste: '😀 😃 😄 😁 😆 😅 😂 🙂 😉 😊 😇 🥰 😍 😋 😎 🤓 🥳 🤔 😐 🙄 😬 😴 😢 😭 😱 😡 🤗' },
  { titre: 'Gestes', liste: '👍 👎 👌 ✌️ 🤝 👏 🙌 🙏 💪 👋 👉 👈 👆 👇 ✋ 👀 💡 ❤️' },
  { titre: 'Nature', liste: '🌲 🌳 🌿 🍀 🍁 🍂 🌸 🍄 🦋 🐝 🐦 🦅 🦉 🐺 🦊 🐻 🐗 🦌 🐑 🐄 🐴 ⛰️ 🏔️ ☀️ ⛅ 🌧️ ❄️ 🌈 💧 🔥' },
  { titre: 'Objets', liste: '📅 📌 📎 📝 📄 📁 📊 📢 📞 📧 💻 📷 🔍 ⏰ 🎁 🎉 ☕ 🚗 🥾 🏠' },
  { titre: 'Symboles', liste: '✅ ✔️ ❌ ❗ ❓ ⚠️ ⛔ ℹ️ ⭐ ✨ ➡️ ⬅️ ⬆️ ⬇️ 🔴 🟠 🟡 🟢 🔵' },
].map(({ titre, liste }) => ({ titre, liste: liste.split(' ') }));

// Touche Tab : insère une tabulation (dans une liste : change le niveau d'indentation) au lieu de
// faire perdre le focus à l'éditeur
const Tabulation = Extension.create({
  name: 'tabulation',
  addKeyboardShortcuts() {
    return {
      Tab: ({ editor }) => {
        if (editor.isActive('listItem')) return editor.commands.sinkListItem('listItem') || true;
        if (editor.isActive('tableCell') || editor.isActive('tableHeader')) return false;
        return editor.commands.insertContent('\t');
      },
      'Shift-Tab': ({ editor }) => {
        if (editor.isActive('listItem')) return editor.commands.liftListItem('listItem') || true;
        return false;
      },
    };
  },
});

export default {
  name: 'wysiwygEditor',
  components: { EditorContent, genericForm },
  props: {
    modelValue: { type: String, default: '' },
  },
  emits: ['update:modelValue'],
  inject: {
    editorBridge: { from: 'editorBridge', default: null },
  },
  data: () => ({
    editor: null,
    tick: 0, // incrémenté à chaque transaction : fait recalculer l'état des boutons
    derniere: null, // dernière valeur émise (pour ne pas recharger l'éditeur avec sa propre valeur)
    COULEURS,
    EMOJIS,
    lienOuvert: false,
    documentOuvert: false,
    configDocForm,
    adresse: '',
    composantOuvert: false,
    composantCode: '',
    composantPosition: null, // position du composant modifié ; null = insertion
    imageOuverte: false,
    imageAdresse: '',
    imageAlt: '',
    imageTitre: '', // légende
    imageSource: '', // auteur
    imagePosition: 'left',
    imageTitreSurImage: false,
    imageLien: '',
    imageFichier: null,
    POSITIONS_IMAGE: [
      { titre: 'Gauche', valeur: 'left' },
      { titre: 'Centre', valeur: 'center' },
      { titre: 'Droite', valeur: 'right' },
      { titre: 'Flottante à gauche (texte autour)', valeur: 'float-left' },
      { titre: 'Flottante à droite (texte autour)', valeur: 'float-right' },
    ],
    imageEnvoiEnCours: false,
    imageErreur: '',
  }),
  computed: {
    // adresse des images du serveur : aperçu des <content-img> dans le texte
    cheminImages() {
      return (this.$store && this.$store.getters.mediaImgPath) || '';
    },
    styles() {
      return [
        { titre: 'Paragraphe', valeur: 0 },
        { titre: 'Titre 1', valeur: 1 },
        { titre: 'Titre 2', valeur: 2 },
        { titre: 'Titre 3', valeur: 3 },
      ];
    },
    tailles() {
      return [
        { titre: 'Petit', valeur: '0.85em' },
        { titre: 'Normal', valeur: null },
        { titre: 'Grand', valeur: '1.25em' },
        { titre: 'Très grand', valeur: '1.5em' },
        { titre: 'Énorme', valeur: '2em' },
      ];
    },
    style() {
      this.tick; // eslint-disable-line no-unused-expressions
      if (!this.editor) return null;
      if (this.editor.isActive('paragraph')) return 0;
      return [1, 2, 3].find((niveau) => this.editor.isActive('heading', { level: niveau })) ?? null;
    },
    taille() {
      this.tick; // eslint-disable-line no-unused-expressions
      return this.editor ? this.editor.getAttributes('textStyle').fontSize ?? null : null;
    },
    couleurActuelle() {
      this.tick; // eslint-disable-line no-unused-expressions
      return this.editor ? this.editor.getAttributes('textStyle').color || null : null;
    },
    groupes() {
      const ed = () => this.editor.chain().focus();
      const actif = (...args) => this.isActive(...args);
      return [
        [
          { titre: 'Annuler', icone: 'mdi-undo', action: () => ed().undo().run(), inactif: () => !this.editor.can().undo() },
          { titre: 'Rétablir', icone: 'mdi-redo', action: () => ed().redo().run(), inactif: () => !this.editor.can().redo() },
        ],
        [
          { titre: 'Gras', icone: 'mdi-format-bold', actif: () => actif('bold'), action: () => ed().toggleBold().run() },
          { titre: 'Italique', icone: 'mdi-format-italic', actif: () => actif('italic'), action: () => ed().toggleItalic().run() },
          { titre: 'Souligné', icone: 'mdi-format-underline', actif: () => actif('underline'), action: () => ed().toggleUnderline().run() },
          { titre: 'Barré', icone: 'mdi-format-strikethrough', actif: () => actif('strike'), action: () => ed().toggleStrike().run() },
          { titre: 'Effacer la mise en forme', icone: 'mdi-format-clear', action: () => ed().unsetAllMarks().run() },
        ],
        [
          { titre: 'Liste à puces', icone: 'mdi-format-list-bulleted', actif: () => actif('bulletList'), action: () => ed().toggleBulletList().run() },
          { titre: 'Liste numérotée', icone: 'mdi-format-list-numbered', actif: () => actif('orderedList'), action: () => ed().toggleOrderedList().run() },
          { titre: 'Citation', icone: 'mdi-format-quote-close', actif: () => actif('blockquote'), action: () => ed().toggleBlockquote().run() },
          { titre: 'Ligne de séparation', icone: 'mdi-minus', action: () => ed().setHorizontalRule().run() },
        ],
        [
          { titre: 'Aligner à gauche', icone: 'mdi-format-align-left', actif: () => this.alignementActif('left'), action: () => this.aligne('left') },
          { titre: 'Centrer', icone: 'mdi-format-align-center', actif: () => this.alignementActif('center'), action: () => this.aligne('center') },
          { titre: 'Aligner à droite', icone: 'mdi-format-align-right', actif: () => this.alignementActif('right'), action: () => this.aligne('right') },
          { titre: 'Justifier', icone: 'mdi-format-align-justify', actif: () => actif({ textAlign: 'justify' }), action: () => ed().setTextAlign('justify').run() },
        ],
        [
          { titre: 'Lien', icone: 'mdi-link', actif: () => actif('link'), action: this.ouvreLien },
          { titre: 'Insérer un document', icone: 'mdi-file-document-outline', action: this.ouvreDocument },
          { titre: 'Insérer une image', icone: 'mdi-image-outline', actif: () => actif('image'), action: this.ouvreImage },
          {
            titre: 'Insérer un tableau',
            icone: 'mdi-table',
            action: () => ed().insertTable({ rows: 3, cols: 3, withHeaderRow: true }).run(),
            inactif: () => actif('table'),
          },
          { titre: 'Composant (code Vue / HTML)', icone: 'mdi-puzzle-outline', action: () => this.ouvreComposant() },
        ],
      ];
    },
    outilsTableau() {
      const ed = () => this.editor.chain().focus();
      return [
        { libelle: '+ Ligne', titre: 'Ajouter une ligne en dessous', action: () => ed().addRowAfter().run() },
        { libelle: '+ Colonne', titre: 'Ajouter une colonne à droite', action: () => ed().addColumnAfter().run() },
        { libelle: '− Ligne', titre: 'Supprimer la ligne', action: () => ed().deleteRow().run() },
        { libelle: '− Colonne', titre: 'Supprimer la colonne', action: () => ed().deleteColumn().run() },
        { libelle: 'Ligne de titre', titre: 'Mettre ou retirer la ligne de titre', action: () => ed().toggleHeaderRow().run() },
        { libelle: 'Supprimer le tableau', titre: 'Supprimer le tableau', action: () => ed().deleteTable().run() },
      ];
    },
  },
  watch: {
    // contenu remplacé par le parent (chargement d'un autre texte)
    modelValue(valeur) {
      if (!this.editor || valeur === this.derniere) return;
      this.derniere = valeur;
      this.editor.commands.setContent(contenuVersEditeur(valeur), { emitUpdate: false });
    },
  },
  mounted() {
    this.derniere = this.modelValue;
    this.editor = markRaw(
      new Editor({
        content: contenuVersEditeur(this.modelValue),
        extensions: [
          StarterKit.configure({ link: { openOnClick: false, HTMLAttributes: { target: null, rel: null } } }),
          ImageLegende.configure({ cheminImages: this.cheminImages }),
          ComposantBloc.configure({ cheminImages: this.cheminImages }),
          ComposantEnLigne.configure({ cheminImages: this.cheminImages }),
          TextAlign.configure({ types: ['heading', 'paragraph'] }),
          Tabulation,
          TextStyle,
          FontSize,
          Color,
          TableKit.configure({ table: { resizable: true } }),
        ],
        editorProps: {
          attributes: { role: 'textbox', 'aria-multiline': 'true', lang: 'fr', spellcheck: 'true' },
          // double-clic sur un composant : modification de son code
          handleDoubleClickOn: (view, pos, node, nodePos) => {
            if (node.type.name === 'image') {
              this.ouvreImage();
              return true;
            }
            if (!node.type.name.startsWith('composant')) return false;
            this.ouvreComposant(nodePos, node.attrs.brut);
            return true;
          },
        },
        onTransaction: () => {
          this.tick++;
        },
        // le contenu n'est réécrit (markdown -> html) que si l'utilisateur le modifie
        onUpdate: ({ editor }) => {
          this.derniere = editeurVersContenu(editor);
          this.$emit('update:modelValue', this.derniere);
        },
      })
    );
    if (this.editorBridge) this.editorBridge.insert = this.insereBrut;
  },
  beforeUnmount() {
    if (this.editorBridge && this.editorBridge.insert === this.insereBrut) this.editorBridge.insert = null;
    if (this.editor) this.editor.destroy();
  },
  methods: {
    isActive(...args) {
      this.tick; // eslint-disable-line no-unused-expressions
      return this.editor ? this.editor.isActive(...args) : false;
    },
    commande() {
      return this.editor.chain().focus();
    },
    setStyle(valeur) {
      if (valeur) this.commande().setHeading({ level: valeur }).run();
      else this.commande().setParagraph().run();
    },
    setTaille(valeur) {
      if (valeur) this.commande().setFontSize(valeur).run();
      else this.commande().unsetFontSize().run();
    },
    appliqueCouleur(couleur) {
      if (couleur) this.commande().setColor(couleur).run();
      else this.commande().unsetColor().run();
    },
    // alignement : celui de l'image si une image est sélectionnée, sinon celui du paragraphe
    aligne(valeur) {
      if (this.editor.isActive('image')) {
        this.commande().updateAttributes('image', { alignement: valeur === 'left' ? null : valeur }).run();
      } else {
        this.commande().setTextAlign(valeur).run();
      }
    },
    alignementActif(valeur) {
      if (this.isActive('image')) {
        return (this.editor.getAttributes('image').alignement || 'left') === valeur;
      }
      return this.isActive({ textAlign: valeur });
    },
    insereEmoji(emoji) {
      this.commande().insertContent(emoji).run();
    },

    // --- lien ---
    ouvreLien() {
      this.adresse = this.editor.getAttributes('link').href || '';
      this.lienOuvert = true;
    },
    appliqueLien() {
      let href = this.adresse.trim();
      this.lienOuvert = false;
      if (!href) return this.retireLien();
      // « www.exemple.fr » : adresse externe saisie sans son protocole
      if (!/^([a-z][a-z0-9+.-]*:|\/|#)/i.test(href)) href = 'https://' + href;
      if (this.editor.state.selection.empty && !this.editor.isActive('link')) {
        // rien de sélectionné : l'adresse elle-même sert de texte au lien
        this.commande()
          .insertContent({ type: 'text', text: this.adresse.trim(), marks: [{ type: 'link', attrs: { href } }] })
          .run();
        return;
      }
      this.commande().extendMarkRange('link').setLink({ href }).run();
    },
    retireLien() {
      this.lienOuvert = false;
      this.commande().extendMarkRange('link').unsetLink().run();
    },

    // --- image (fichier du serveur, envoyé depuis l'ordinateur, ou adresse) ---
    // une image sélectionnée est reprise par la fenêtre et mise à jour à la validation
    ouvreImage() {
      const image = this.editor.isActive('image') ? this.editor.getAttributes('image') : {};
      this.imageAdresse = image.src || '';
      this.imageAlt = image.alt || '';
      this.imageTitre = image.titre || '';
      this.imageSource = image.source || '';
      this.imagePosition = image.alignement || 'left';
      this.imageTitreSurImage = !!image.titreSurImage;
      this.imageLien = image.lien || '';
      this.imageFichier = null;
      this.imageErreur = '';
      this.imageOuverte = true;
    },
    // aperçu : un nom de fichier du serveur est précédé du chemin des images
    apercuImage(src) {
      return adresseImage(src, this.cheminImages);
    },
    // fichier choisi : envoyé tout de suite, son nom remplit le champ (insertion à la validation)
    async envoieImage(fichier) {
      const choisi = Array.isArray(fichier) ? fichier[0] : fichier;
      if (!choisi) return;
      this.imageEnvoiEnCours = true;
      this.imageErreur = '';
      try {
        const reponse = await apiRequest('POST', 'api/commons/add_file/img', { postData: { file: choisi } });
        if (!reponse || !reponse.src) throw new Error('Envoi refusé');
        this.imageAdresse = reponse.src;
        if (!this.imageAlt) this.imageAlt = reponse.src.replace(/\.[^.]+$/, '').replace(/_/g, ' ');
      } catch (err) {
        this.imageErreur = (err && err.message) || "L'image n'a pas pu être envoyée.";
      } finally {
        this.imageEnvoiEnCours = false;
      }
    },
    appliqueImage() {
      const src = this.imageAdresse.trim();
      if (!src || this.imageEnvoiEnCours) return;
      this.imageOuverte = false;
      const attrs = {
        src,
        alt: this.imageAlt.trim() || null,
        titre: this.imageTitre.trim() || null,
        source: this.imageSource.trim() || null,
        lien: this.imageLien.trim() || null,
        alignement: this.imagePosition === 'left' ? null : this.imagePosition,
        titreSurImage: this.imageTitreSurImage,
      };
      if (this.editor.isActive('image')) this.commande().updateAttributes('image', attrs).run();
      else this.commande().insertContent({ type: 'image', attrs }).run();
    },

    // --- composants (code Vue / HTML conservé tel quel) ---
    ouvreComposant(position = null, code = '') {
      this.composantPosition = position;
      this.composantCode = code;
      this.composantOuvert = true;
    },
    appliqueComposant() {
      const brut = this.composantCode.trim();
      this.composantOuvert = false;
      if (!brut) return;
      if (this.composantPosition === null) return this.insereBrut(brut);
      const { state, view } = this.editor;
      const noeud = state.doc.nodeAt(this.composantPosition);
      if (noeud && noeud.type.name.startsWith('composant')) {
        view.dispatch(state.tr.setNodeMarkup(this.composantPosition, undefined, attributsComposant(brut)));
      }
    },
    // --- document (lien vers un fichier du serveur) ---
    ouvreDocument() {
      this.configDocForm.value = null;
      this.documentOuvert = true;
    },
    appliqueDocument(event) {
      this.documentOuvert = false;
      // src est inséré dans une chaîne JS d'une expression Vue, elle-même dans un attribut HTML :
      // échappement JS (\ et ') puis HTML. Le texte du lien ne doit pas ouvrir d'interpolation Vue.
      const srcJs = String(event.src ?? '').replace(/\\/g, '\\\\').replace(/'/g, "\\'");
      const txt = escapeHtml(event.txt || event.src).replace(/\{/g, '&#123;');
      this.insereBrut(
        `<a :href="docPath + '${escapeHtml(srcJs)}'" target="_blank" rel="noopener noreferrer">${txt}</a>`,
      );
    },
    // insère un composant (ou tout code HTML/Vue) à la position du curseur
    insereBrut(brut) {
      this.commande()
        .insertContent({
          type: estEnLigne(brut) ? 'composantEnLigne' : 'composantBloc',
          attrs: attributsComposant(brut),
        })
        .run();
    },
  },
};
</script>

<style scoped>
.wysiwyg {
  border: 1px solid rgba(0, 0, 0, 0.3);
  border-radius: 6px;
}

.wysiwyg:focus-within {
  border-color: rgb(var(--v-theme-primary));
}

.wysiwyg-outils {
  position: sticky;
  top: 0;
  z-index: 2;
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  align-items: center;
  padding: 4px 6px;
  border-bottom: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 6px 6px 0 0;
  background-color: rgb(var(--v-theme-surface));
}

.wysiwyg-select {
  flex: 0 0 140px;
}

.wysiwyg-groupe {
  display: flex;
  align-items: center;
  padding-left: 4px;
  border-left: 1px solid rgba(0, 0, 0, 0.2);
}

.wysiwyg-tableau {
  flex-basis: 100%;
  padding-left: 0;
  border-left: 0;
}

.wysiwyg-zone :deep(.tiptap) {
  min-height: 22em;
  padding: 8px 24px;
  outline: none;
  text-align: left;
}

.wysiwyg-zone :deep(.tiptap table) {
  border-collapse: collapse;
}

.wysiwyg-zone :deep(.tiptap td),
.wysiwyg-zone :deep(.tiptap th) {
  position: relative;
  min-width: 3em;
  padding: 4px 8px;
  border: 1px solid rgba(0, 0, 0, 0.3);
  vertical-align: top;
}

.wysiwyg-zone :deep(.selectedCell) {
  background-color: rgba(var(--v-theme-primary), 0.15);
}

.wysiwyg-zone :deep(.column-resize-handle) {
  position: absolute;
  top: 0;
  right: -2px;
  bottom: -2px;
  width: 4px;
  background-color: rgb(var(--v-theme-primary));
  pointer-events: none;
}

.wysiwyg-zone :deep(.tiptap.resize-cursor) {
  cursor: col-resize;
}

/* image (div.img-content, mêmes styles que sur le site) : poignées d'angle visibles au survol et
   quand l'image est sélectionnée */
.wysiwyg-zone :deep(.img-wysiwyg) {
  position: relative;
  max-width: 100%;
  cursor: pointer;
}

.wysiwyg-zone :deep(.img-wysiwyg img) {
  max-width: 100%;
}

.wysiwyg-zone :deep(.poignee-img) {
  position: absolute;
  display: none;
  width: 12px;
  height: 12px;
  background-color: rgb(var(--v-theme-primary));
  border: 2px solid #fff;
  border-radius: 3px;
  z-index: 2;
  touch-action: none;
}

.wysiwyg-zone :deep(.img-wysiwyg:hover .poignee-img),
.wysiwyg-zone :deep(.img-wysiwyg.ProseMirror-selectednode .poignee-img) {
  display: block;
}

.wysiwyg-zone :deep(.poignee-img[data-coin='hg']) { top: -6px; left: -6px; cursor: nwse-resize; }
.wysiwyg-zone :deep(.poignee-img[data-coin='hd']) { top: -6px; right: -6px; cursor: nesw-resize; }
.wysiwyg-zone :deep(.poignee-img[data-coin='bg']) { bottom: -6px; left: -6px; cursor: nesw-resize; }
.wysiwyg-zone :deep(.poignee-img[data-coin='bd']) { bottom: -6px; right: -6px; cursor: nwse-resize; }

.wysiwyg-zone :deep(.img-wysiwyg.ProseMirror-selectednode) {
  outline: 2px solid rgb(var(--v-theme-primary));
}

.wysiwyg-apercu {
  max-width: 100%;
  max-height: 240px;
  border: 1px solid rgba(0, 0, 0, 0.2);
  border-radius: 4px;
}

/* composant Vue conservé tel quel : pastille avec son nom */
.wysiwyg-zone :deep(.composant-cms:not(.composant-img)) {
  display: inline-block;
  max-width: 100%;
  margin: 2px 0;
  padding: 2px 10px;
  border: 1px dashed rgb(var(--v-theme-primary));
  border-radius: 12px;
  background-color: rgba(var(--v-theme-primary), 0.08);
  font-size: 0.85rem;
  line-height: 1.6;
  cursor: pointer;
  user-select: none;
}

.wysiwyg-zone :deep(.composant-cms:not(.composant-img))::before {
  content: '⚙ ' attr(data-label);
}

/* <content-img> : affiché comme l'image réelle (styles .img-content de content.css) */
.wysiwyg-zone :deep(.composant-img) {
  max-width: 100%;
  cursor: pointer;
  user-select: none;
}

.wysiwyg-zone :deep(.composant-img img) {
  max-width: 100%;
  pointer-events: none;
}

.wysiwyg-zone :deep(.composant-cms.ProseMirror-selectednode) {
  outline: 2px solid rgb(var(--v-theme-primary));
}

/* couleur du texte */
.wysiwyg-couleurs {
  width: 220px;
}

.wysiwyg-grille-couleurs {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 6px;
}

.wysiwyg-grille-couleurs button {
  aspect-ratio: 1;
  border: 1px solid rgba(0, 0, 0, 0.3);
  border-radius: 6px;
  cursor: pointer;
}

.wysiwyg-grille-couleurs button.choisie,
.wysiwyg-grille-couleurs button:hover {
  outline: 2px solid rgb(var(--v-theme-primary));
  outline-offset: 1px;
}

.wysiwyg-couleur-libre {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin: 8px 0 4px;
  font-size: 0.9rem;
}

/* smileys */
.wysiwyg-emojis {
  width: min(360px, 85vw);
  max-height: 340px;
  overflow-y: auto;
}

.wysiwyg-emojis h4 {
  margin: 6px 0 2px;
  font-size: 0.85rem;
  opacity: 0.7;
}

.wysiwyg-grille-emojis {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(36px, 1fr));
}

.wysiwyg-grille-emojis button {
  padding: 2px;
  border-radius: 6px;
  font-size: 1.4rem;
  line-height: 1.4;
  cursor: pointer;
}

.wysiwyg-grille-emojis button:hover {
  background-color: rgba(var(--v-theme-primary), 0.15);
}
</style>
