<template>
  <!--
    Un bloc « formulaire d'import + journal + tableau d'exemple » de la page
    d'import du plan de chasse (imports-attributions-chasse.vue).
    Grisé et verrouillé tant que `active` est faux.
  -->
  <v-card
    class="etape"
    variant="flat"
    border
    :style="active ? '' : 'opacity:0.55'"
  >
    <v-card-title class="etape-titre">
      <v-icon :color="active ? 'primary' : 'grey'">
        {{ active ? 'mdi-upload' : 'mdi-lock' }}
      </v-icon>
      {{ titre }}
    </v-card-title>

    <v-card-text>
      <div
        v-if="!active"
        style="color: #8a6d3b"
      >
        <v-icon
          left
          color="grey"
        >
          mdi-information-outline
        </v-icon>
        {{ inactifMessage }}
      </div>

      <template v-else>
        <p
          v-if="texteAide"
          style="font-size: 0.85rem; color: #666; max-width: 850px"
        >
          {{ texteAide }}
        </p>

        <div style="max-width: 560px">
          <v-file-input
            v-model="file"
            label="Sélectionner un fichier CSV"
            accept=".csv"
            variant="outlined"
            density="compact"
            prepend-icon="mdi-file-delimited"
            :disabled="uploading"
            hide-details
          ></v-file-input>
        </div>

        <div
          class="mt-2"
          style="display: flex; gap: 12px"
        >
          <v-btn
            :disabled="!file || uploading"
            :loading="enCours"
            color="primary"
            @click="importer"
          >
            <v-icon left>mdi-upload</v-icon>
            Importer
          </v-btn>
          <v-btn
            variant="text"
            :disabled="uploading"
            @click="file = null"
          >
            Effacer
          </v-btn>
        </div>

        <div
          v-if="enCours"
          class="mt-3"
        >
          <v-progress-linear
            indeterminate
            color="primary"
          ></v-progress-linear>
          <div
            v-if="etapeMessage"
            style="margin-top: 0.35rem; font-size: 0.9rem; color: #555"
          >
            {{ etapeMessage }}
          </div>
          <div style="margin-top: 0.15rem; font-size: 0.8rem; color: #888">
            Le traitement s'exécute sur le serveur. Merci de patienter sans fermer la page.
          </div>
        </div>

        <div
          v-if="journal.length"
          class="journal mt-3"
        >
          <div
            v-for="(l, i) in journal"
            :key="i"
            class="journal-ligne"
          >
            <v-icon
              v-if="l.type === 'error'"
              color="error"
              size="small"
            >
              mdi-close-circle
            </v-icon>
            <v-icon
              v-else-if="l.type === 'warning'"
              color="orange"
              size="small"
            >
              mdi-alert
            </v-icon>
            <v-icon
              v-else
              color="green"
              size="small"
            >
              mdi-check-circle
            </v-icon>
            <span>{{ l.message }}</span>
          </div>
        </div>

        <div
          v-if="exemple.colonnes && exemple.colonnes.length"
          class="mt-4"
        >
          <div style="font-size: 0.8rem; color: #888; margin-bottom: 0.25rem">
            Exemple de fichier attendu :
          </div>
          <div style="overflow-x: auto">
            <table class="exemple">
              <thead>
                <tr>
                  <th
                    v-for="c in exemple.colonnes"
                    :key="c"
                  >
                    {{ c }}
                  </th>
                </tr>
              </thead>
              <tbody>
                <tr
                  v-for="(ligne, i) in exemple.lignes"
                  :key="i"
                >
                  <td
                    v-for="(v, j) in ligne"
                    :key="j"
                  >
                    {{ v }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </template>
    </v-card-text>
  </v-card>
</template>

<script>
/**
 * Bloc réutilisable d'une étape d'import du plan de chasse, utilisé 3 fois par
 * `imports-attributions-chasse.vue` (parent). Purement présentation + choix de
 * fichier : le parent gère l'appel réseau et le polling.
 *
 * C'est un composant séparé (et non un template chaîne inline dans le parent)
 * parce que Vuetify est configuré en `autoImport` par SFC (vite.config.js) :
 * les `<v-…>` ne sont pas enregistrés globalement.
 */
export default {
  name: 'ImportSectionAttributions',
  props: {
    titre: { type: String, required: true },
    active: { type: Boolean, default: false }, // false => bloc grisé + verrouillé
    inactifMessage: { type: String, default: '' }, // raison du verrouillage
    texteAide: { type: String, default: '' }, // consignes affichées au-dessus du champ
    uploading: { type: Boolean, default: false }, // un import (n'importe lequel) est en cours
    enCours: { type: Boolean, default: false }, // CET import est en cours -> barre de progression
    etapeMessage: { type: String, default: '' }, // libellé d'étape du suivi backend
    journal: { type: Array, default: () => [] }, // [{ type, message }]
    exemple: {
      type: Object,
      default: () => ({ colonnes: [], lignes: [] }), // tableau d'exemple affiché sous le champ
    },
  },
  emits: ['importer'], // émis avec le File choisi quand l'utilisateur clique « Importer »
  data() {
    return { file: null };
  },
  methods: {
    importer() {
      if (!this.file) return;
      this.$emit('importer', this.file);
    },
  },
};
</script>

<style scoped>
.etape {
  max-width: 1000px;
  margin: 0 0 1.25rem 0;
  padding-bottom: 0.5rem;
}
.etape-titre {
  font-size: 1.05rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}
.mt-2 {
  margin-top: 0.5rem;
}
.mt-3 {
  margin-top: 1rem;
}
.mt-4 {
  margin-top: 1.5rem;
}
.journal {
  background: #fafafa;
  border: 1px solid #eee;
  border-radius: 4px;
  padding: 0.5rem 0.75rem;
  max-height: 320px;
  overflow-y: auto;
  font-size: 0.85rem;
}
.journal-ligne {
  display: flex;
  align-items: flex-start;
  gap: 0.4rem;
  padding: 0.1rem 0;
}
table.exemple {
  border-collapse: collapse;
  font-size: 0.8rem;
}
table.exemple th,
table.exemple td {
  border: 1px solid #ddd;
  padding: 0.25rem 0.5rem;
  white-space: nowrap;
}
table.exemple th {
  background: #f0f0f0;
}
</style>
