<!-- Contient tous les textes d'aide du formulaire de déclaration.  -->

<template>
  <div v-if="localShow">
    <v-dialog
      v-model="localShow"
      max-width="600"
      width="600"
    >
      <v-card>
        <v-card-title
          style="
            justify-content: center;
            white-space: normal;
            overflow-wrap: anywhere;
            word-break: break-word;
            text-align: center;
          "
        >
          Êtes-vous sûr de vouloir envoyer une relance à {{ declaration_data.declarant }} ?
        </v-card-title>
        <v-card-text
          style="
            white-space: normal;
            overflow-wrap: anywhere;
            word-break: break-word;
            text-align: center;
          "
        >
          L'email sera envoyé à : {{ declaration_data.email }}
        </v-card-text>
        <v-card-actions style="justify-content: center">
          <v-btn
            style="margin-right: 10px"
            color="green lighten-2"
            @click="sendRelanceMail"
            :loading="processing"
            :disabled="processing"
          >
            Oui
          </v-btn>
          <v-btn
            color="red lighten-2"
            @click="closePopup"
            :disabled="processing"
          >
            Non
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { apiRequest } from '@/core/js/data/api';
import { snackbarStore } from '@/store/snackbar';
export default {
  compatConfig: { MODE: 3 }, // verrouille les acquis Phase 4 (composant testé sans warning au 2026-07-10)
  name: 'confirmRelanceMail',
  components: {},
  props: {
    declaration_data: {
      type: Object,
      required: true,
    },
    show_popup_relance: {
      type: Boolean,
      required: true,
    },
  },
  watch: {
    show_popup_relance(newVal) {
      this.localShow = newVal;
    },
    localShow(newVal) {
      if (!newVal) {
        this.$emit('close-relance-popup');
      }
    },
  },
  data() {
    return {
      localShow: this.show_popup_relance,
      processing: false,
    };
  },
  methods: {
    closePopup() {
      this.localShow = false;
    },

    sendRelanceMail() {
      this.processing = true;
      apiRequest(
        'GET',
        `api/declaration/send_mail_renouvellement?id_declaration=${this.declaration_data.id_declaration}`
      )
        .then((response) => {
          console.log('Relance envoyée avec succès :', response);
          // this.$emit('show-snackbar', 'Relance envoyée avec succès');
          snackbarStore.show('Relance envoyée avec succès', 'success');
        })
        .catch((error) => {
          console.error("Erreur lors de l'envoi de la relance :", error);
          // this.$emit('show-snackbar', 'Erreur lors de l\'envoi de la relance');
          snackbarStore.show("Erreur lors de l'envoi de la relance", 'error');
          this.processing = false;
        })
        .finally(() => {
          this.processing = false;
          this.closePopup();
        });
    },
  },
};
</script>
