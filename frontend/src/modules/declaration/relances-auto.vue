<!--
  Page d'administration « Relances automatiques » (menu Administration, droit >= 5).
  - bouton en haut : active / désactive l'envoi automatique des relances (flask send-relance) ;
  - tableau : une ligne par déclaration relancée (automatiquement ou manuellement), avec date et numéro de la dernière relance
    (entre parenthèses : relances restantes avant la clôture automatique), renouvelée / clôturée.
  Données : GET api/declaration/relances_auto, POST api/declaration/relances_auto/actif.
-->
<template>
  <div>
    <br />
    <h1>Relances automatiques</h1>

    <v-card
      class="mb-4"
      variant="flat"
      border
    >
      <v-card-text class="d-flex align-center flex-wrap ga-4">
        <v-btn
          :color="actif ? 'error' : 'success'"
          :prepend-icon="actif ? 'mdi-pause-circle' : 'mdi-play-circle'"
          :loading="saving"
          :disabled="loading || saving"
          @click="toggleActif"
        >
          {{ actif ? 'Désactiver les relances automatiques' : 'Activer les relances automatiques' }}
        </v-btn>
        <span v-if="!loading">
          Les relances automatiques sont
          <strong :class="actif ? 'text-success' : 'text-error'">
            {{ actif ? 'activées' : 'désactivées' }}
          </strong>
          .
        </span>
      </v-card-text>
    </v-card>

    <v-data-table
      :headers="headers"
      :items="relances"
      :loading="loading"
      :items-per-page="25"
      item-value="id_declaration"
      loading-text="Chargement..."
      no-data-text="Aucune relance n'a encore été envoyée."
      items-per-page-text="Lignes par page"
    >
      <template #item.id_declaration="{ item }">
        <router-link
          :to="{ name: 'voir_declaration', params: { id: item.id_declaration } }"
        >
          {{ item.id_declaration }}
        </router-link>
      </template>
      <template #item.renouvelee="{ item }">
        <v-icon
          v-if="item.renouvelee"
          color="green"
          aria-label="Renouvelée"
        >
          mdi-check-circle
        </v-icon>
      </template>
      <template #item.cloturee="{ item }">
        <v-icon
          v-if="item.cloturee"
          color="green"
          aria-label="Clôturée"
        >
          mdi-check-circle
        </v-icon>
      </template>
    </v-data-table>
  </div>
</template>

<script>
import { apiRequest } from '@/core/js/data/api.js';
import { describeApiError } from '@/core/js/data/api-messages.js';
import { snackbarStore } from '@/store/snackbar';

export default {
  name: 'relances-auto',
  data() {
    return {
      actif: true,
      relances: [],
      loading: true,
      saving: false,
      headers: [
        { title: 'Déclaration', key: 'id_declaration' },
        { title: 'Forêt', key: 'label_foret' },
        { title: 'Déclarant', key: 'declarant' },
        { title: 'Dernière relance', key: 'date_derniere_relance', sortable: false },
        // numéro de la relance (relances restantes avant la clôture automatique)
        { title: 'N° relance (restantes)', key: 'numero_relance' },
        { title: 'Relances manuelles', key: 'nb_manuelles', align: 'center' },
        { title: 'Renouvelée', key: 'renouvelee', align: 'center' },
        { title: 'Clôturée', key: 'cloturee', align: 'center' },
      ],
    };
  },
  created() {
    this.charger();
  },
  methods: {
    async charger() {
      this.loading = true;
      try {
        const res = await apiRequest('GET', 'api/declaration/relances_auto');
        this.actif = res.actif;
        // le numéro est affiché avec les relances restantes entre parenthèses
        this.relances = res.relances.map((r) => ({ ...r, numero_relance: r.libelle_relance }));
      } catch (err) {
        console.error('relances-auto charger', err);
        snackbarStore.show(describeApiError(err, { action: 'chargement' }), 'error');
      } finally {
        this.loading = false;
      }
    },

    async toggleActif() {
      this.saving = true;
      try {
        const res = await apiRequest('POST', 'api/declaration/relances_auto/actif', {
          postData: { actif: !this.actif },
        });
        if (!res || res.success === false) {
          throw new Error('échec');
        }
        this.actif = res.data.actif;
        snackbarStore.show(
          this.actif ? 'Relances automatiques activées' : 'Relances automatiques désactivées',
          'success'
        );
      } catch (err) {
        console.error('relances-auto toggleActif', err);
        snackbarStore.show(describeApiError(err, { action: 'enregistrement' }), 'error');
      } finally {
        this.saving = false;
      }
    },
  },
};
</script>
