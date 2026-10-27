<!--
  Page « Données aberrantes » : réalisations de chasse dont le poids ou la longueur des dagues
  sort de la fourchette standard (espèce x classe d'âge x sexe, table oeasc_chasse.t_standards_mesures).
  Les mesures sont modifiables directement dans le tableau ; une ligne corrigée qui rentre dans la
  fourchette disparaît de la liste au rechargement.
-->
<template>
  <div>
    <br />
    <h1>Données aberrantes</h1>
    <p style="max-width: 900px; color: #555">
      Réalisations dont le poids ou la longueur des dagues sort de la fourchette standard définie
      pour l'espèce, la classe d'âge et le sexe (poids en kg, dagues en mm). Corrigez les valeurs
      directement dans le tableau puis enregistrez la ligne. Pour le cerf et le chevreuil, modifier le
      poids entier recalcule le poids vidé, et inversement. Les fourchettes se modifient dans
      <router-link :to="{ name: 'chasse.admin' }">Données chasse → onglet Standards de mesures</router-link>
      .
    </p>

    <!-- FILTRES -->
    <div class="filtres">
      <v-select
        v-model="idSaison"
        :items="saisons"
        item-title="nom_saison"
        item-value="id_saison"
        label="Saison"
        density="compact"
        variant="outlined"
        clearable
        hide-details
        style="max-width: 200px"
      ></v-select>
      <v-select
        v-model="idEspece"
        :items="especes"
        item-title="nom_espece"
        item-value="id_espece"
        label="Espèce"
        density="compact"
        variant="outlined"
        clearable
        hide-details
        style="max-width: 200px"
      ></v-select>
      <v-select
        v-model="typeMesure"
        :items="typesMesure"
        item-title="title"
        item-value="value"
        label="Type de donnée"
        density="compact"
        variant="outlined"
        clearable
        hide-details
        style="max-width: 200px"
      ></v-select>
    </div>

    <div style="margin: 0.8rem 0; color: #555">
      <v-progress-circular
        v-if="loading"
        indeterminate
        size="18"
        width="2"
      ></v-progress-circular>
      <span v-else>{{ rows.length }} réalisation(s) à vérifier</span>
    </div>

    <v-data-table
      :headers="headers"
      :items="rows"
      item-value="id_realisation"
      :items-per-page="25"
      :loading="loading"
      density="compact"
      no-data-text="Aucune donnée aberrante pour ces filtres."
    >
      <template #[`item.date_exacte`]="{ item }">
        {{ formatDate(item.date_exacte) }}
      </template>

      <!-- cellules de mesure : champ numérique, en rouge si la mesure est hors fourchette -->
      <template
        v-for="champ in champsMesure"
        :key="champ"
        #[`item.${champ}`]="{ item }"
      >
        <v-text-field
          v-model="item.edition[champ]"
          type="number"
          min="0"
          step="any"
          density="compact"
          variant="outlined"
          hide-details
          :color="estAberrant(item, champ) ? 'error' : undefined"
          :base-color="estAberrant(item, champ) ? 'error' : undefined"
          :bg-color="estAberrant(item, champ) ? 'red-lighten-5' : undefined"
          class="champ-mesure"
          :disabled="item.enregistrement"
          @update:model-value="recalculerPoids(item, champ)"
          @keyup.enter="enregistrer(item)"
        ></v-text-field>
      </template>

      <template #[`item.fourchette`]="{ item }">
        <div
          v-for="a in item.anomalies"
          :key="a.mesure"
          class="fourchette"
        >
          {{ libelleMesure(a.mesure) }} : {{ a.valeur_min }} – {{ a.valeur_max }}
        </div>
      </template>

      <template #[`item.actions`]="{ item }">
        <v-btn
          icon
          size="small"
          variant="text"
          color="primary"
          title="Enregistrer"
          :disabled="!modifie(item) || item.enregistrement"
          :loading="item.enregistrement"
          @click="enregistrer(item)"
        >
          <v-icon>mdi-content-save</v-icon>
        </v-btn>
        <v-btn
          icon
          size="small"
          variant="text"
          title="Annuler les modifications"
          :disabled="!modifie(item) || item.enregistrement"
          @click="reinitialiser(item)"
        >
          <v-icon>mdi-undo</v-icon>
        </v-btn>
      </template>
    </v-data-table>
  </div>
</template>

<script>
import { apiRequest } from '@/core/js/data/api.js';
import { describeApiError } from '@/core/js/data/api-messages.js';
import { snackbarStore } from '@/store/snackbar';

// champs de t_realisations modifiables dans le tableau
const CHAMPS_MESURE = [
  'poid_entier',
  'poid_vide',
  'poid_c_f_p',
  'long_dagues_droite',
  'long_dagues_gauche',
];

// mesure de t_standards_mesures -> champs de t_realisations concernés
const CHAMPS_PAR_MESURE = {
  poid_entier: ['poid_entier'],
  poid_vide: ['poid_vide'],
  poid_c_f_p: ['poid_c_f_p'],
  long_dagues: ['long_dagues_droite', 'long_dagues_gauche'],
};

// poids vide = exp(exposant) * poids entier ^ puissance, par code espèce (mêmes coefficients que
// oeasc_chasse.fct_poid_vide et backend/.../chasse/poids.py). Autres espèces : pas de conversion.
const COEFFICIENTS_POIDS = {
  CF: { exposant: -0.3948, puissance: 1.0247 },
  CH: { exposant: -0.3572, puissance: 1.023 },
};

const arrondi2 = (valeur) => Math.round(valeur * 100) / 100;

const LIBELLE_MESURE = {
  poid_entier: 'Poids entier (kg)',
  poid_vide: 'Poids vide (kg)',
  poid_c_f_p: 'Poids c.f.p. (kg)',
  long_dagues: 'Dagues (mm)',
};

export default {
  name: 'donnees-aberrantes-chasse',

  data() {
    return {
      saisons: [],
      especes: [],
      typesMesure: [
        { title: 'Poids', value: 'poids' },
        { title: 'Dagues', value: 'dagues' },
      ],
      idSaison: null,
      idEspece: null,
      typeMesure: null,
      rows: [],
      loading: false,
      champsMesure: CHAMPS_MESURE,
      headers: [
        { title: 'Saison', key: 'nom_saison' },
        { title: 'Bracelet', key: 'numero_bracelet' },
        { title: 'Date', key: 'date_exacte' },
        { title: 'Espèce', key: 'nom_espece' },
        { title: 'Sexe', key: 'sexe' },
        { title: 'Âge', key: 'classe_age' },
        { title: 'Poids entier (kg)', key: 'poid_entier', sortable: false },
        { title: 'Poids vide (kg)', key: 'poid_vide', sortable: false },
        { title: 'Poids c.f.p. (kg)', key: 'poid_c_f_p', sortable: false },
        { title: 'Dague D (mm)', key: 'long_dagues_droite', sortable: false },
        { title: 'Dague G (mm)', key: 'long_dagues_gauche', sortable: false },
        { title: 'Fourchette attendue', key: 'fourchette', sortable: false },
        { title: '', key: 'actions', sortable: false },
      ],
    };
  },

  watch: {
    idSaison() {
      this.charger();
    },
    idEspece() {
      this.charger();
    },
    typeMesure() {
      this.charger();
    },
  },

  mounted() {
    this.chargerFiltres();
    this.charger();
  },

  methods: {
    libelleMesure(mesure) {
      return LIBELLE_MESURE[mesure] || mesure;
    },

    formatDate(date) {
      return date ? new Date(date).toLocaleDateString('fr-FR') : '';
    },

    chargerFiltres() {
      apiRequest('GET', 'api/generic/chasse/saisons')
        .then((res) => {
          this.saisons = (res.items || []).sort((a, b) => b.id_saison - a.id_saison);
        })
        .catch((error) => {
          snackbarStore.show(
            describeApiError(error, { fallback: 'Impossible de charger la liste des saisons.' }),
            'error'
          );
        });
      apiRequest('GET', 'api/generic/commons/especes')
        .then((res) => {
          this.especes = res.items || [];
        })
        .catch((error) => {
          snackbarStore.show(
            describeApiError(error, { fallback: 'Impossible de charger la liste des espèces.' }),
            'error'
          );
        });
    },

    /** Charge les réalisations hors fourchette pour les filtres sélectionnés. */
    charger() {
      this.loading = true;
      return apiRequest('GET', 'api/chasse/donnees-aberrantes', {
        params: {
          id_saison: this.idSaison,
          id_espece: this.idEspece,
          type: this.typeMesure,
        },
      })
        .then((res) => {
          this.rows = (res.data || []).map((row) => this.preparerLigne(row));
        })
        .catch((error) => {
          this.rows = [];
          snackbarStore.show(
            describeApiError(error, {
              fallback: 'Les données aberrantes n’ont pas pu être chargées. Merci de réessayer.',
            }),
            'error'
          );
        })
        .finally(() => {
          this.loading = false;
        });
    },

    /** Ajoute à la ligne le tampon d'édition (valeurs saisies) et l'état d'enregistrement. */
    preparerLigne(row) {
      const edition = {};
      CHAMPS_MESURE.forEach((champ) => {
        edition[champ] = row[champ];
      });
      return { ...row, edition, enregistrement: false };
    },

    /**
     * Poids entier et poids vidé se déduisent l'un de l'autre (cerf, chevreuil) : quand l'un est
     * modifié, l'autre est recalculé dans le tableau. Un champ vidé ne recalcule rien.
     */
    recalculerPoids(item, champ) {
      const coef = COEFFICIENTS_POIDS[item.code_espece];
      if (!coef || !['poid_entier', 'poid_vide'].includes(champ)) {
        return;
      }
      const saisi = this.valeurSaisie(item, champ);
      if (saisi === null || Number.isNaN(saisi) || saisi <= 0) {
        return;
      }
      if (champ === 'poid_entier') {
        item.edition.poid_vide = arrondi2(Math.exp(coef.exposant) * saisi ** coef.puissance);
      } else {
        item.edition.poid_entier = arrondi2((saisi / Math.exp(coef.exposant)) ** (1 / coef.puissance));
      }
    },

    /** La mesure de ce champ est-elle hors fourchette (d'après la valeur chargée) ? */
    estAberrant(item, champ) {
      return item.anomalies.some((a) => (CHAMPS_PAR_MESURE[a.mesure] || []).includes(champ));
    },

    /** Valeur du champ telle que saisie, normalisée (null si vide) pour comparaison / envoi. */
    valeurSaisie(item, champ) {
      const valeur = item.edition[champ];
      return valeur === '' || valeur === undefined || valeur === null ? null : Number(valeur);
    },

    champsModifies(item) {
      return CHAMPS_MESURE.filter((champ) => {
        const avant = item[champ] === undefined ? null : item[champ];
        return this.valeurSaisie(item, champ) !== avant;
      });
    },

    modifie(item) {
      return this.champsModifies(item).length > 0;
    },

    reinitialiser(item) {
      CHAMPS_MESURE.forEach((champ) => {
        item.edition[champ] = item[champ];
      });
    },

    /** Envoie uniquement les champs modifiés, puis recharge la liste (la ligne disparaît si corrigée). */
    enregistrer(item) {
      const champs = this.champsModifies(item);
      if (!champs.length || item.enregistrement) {
        return;
      }
      const postData = {};
      champs.forEach((champ) => {
        postData[champ] = this.valeurSaisie(item, champ);
      });

      item.enregistrement = true;
      apiRequest('PATCH', `api/chasse/donnees-aberrantes/${item.id_realisation}`, { postData })
        .then((res) => {
          if (res && res.success === false) {
            throw res;
          }
          snackbarStore.show(
            `Réalisation ${item.numero_bracelet || item.id_realisation} enregistrée.`,
            'success'
          );
          return this.charger();
        })
        .catch((error) => {
          item.enregistrement = false;
          snackbarStore.show(
            describeApiError(error, {
              action: 'modification',
              fallback: 'Les valeurs n’ont pas pu être enregistrées. Merci de réessayer.',
            }),
            'error'
          );
        });
    },
  },
};
</script>

<style scoped>
.filtres {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  margin-top: 1rem;
}
.champ-mesure {
  min-width: 90px;
  max-width: 120px;
}
.fourchette {
  white-space: nowrap;
  color: #b00020;
  font-size: 0.85em;
}
</style>
