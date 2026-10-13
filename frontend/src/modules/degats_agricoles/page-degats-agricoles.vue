<!--
  Page publique « Dégâts agricoles » (menu Résultats des suivis) : graphiques par
  saison, répartition par type de culture et carte des communes.
  Données : indemnisations de dégâts agricoles, zone OEASC (schéma oeasc_agricole).
-->
<template>
  <div class="page-degats-agricoles">
    <h1>Dégâts agricoles</h1>
    <p>
      Indemnisations des dégâts de grand gibier sur les cultures, pour les communes du périmètre de
      l'Observatoire. Une saison s'étend du 1er juillet au 30 juin.
    </p>

    <v-progress-linear
      v-if="chargement"
      indeterminate
      color="primary"
    ></v-progress-linear>

    <div
      v-else-if="erreur"
      style="color: crimson"
    >
      {{ erreur }}
    </div>

    <div v-else-if="!saisons.length">Aucune donnée de dégâts agricoles n'est disponible.</div>

    <div v-else>
      <h2>Évolution par saison</h2>

      <div class="grille-graphiques">
        <graph_colonnes_saisons
          title="Montant total indemnisé par saison"
          :categories="categories"
          :series="[
            { name: 'Montant indemnisé', data: valeurs('montant_total'), color: '#7cb5ec' },
          ]"
          yTitle="Montant indemnisé (€)"
          unite="€"
        ></graph_colonnes_saisons>

        <graph_colonnes_saisons
          title="Nombre de déclarations par saison"
          :categories="categories"
          :series="[{ name: 'Déclarations', data: valeurs('nb_declarations'), color: '#f7a35c' }]"
          yTitle="Nombre de déclarations"
        ></graph_colonnes_saisons>

        <graph_colonnes_saisons
          title="Nombre de dossiers par saison"
          :categories="categories"
          :series="[{ name: 'Dossiers', data: valeurs('nb_dossiers'), color: '#8085e9' }]"
          yTitle="Nombre de dossiers"
        ></graph_colonnes_saisons>

        <graph_colonnes_saisons
          title="Surface détruite et surface remise en état par saison"
          :categories="categories"
          :series="[
            { name: 'Surface détruite', data: valeurs('surface_detruite'), color: '#e4572e' },
            {
              name: 'Surface remise en état (ressemis)',
              data: valeurs('surface_ressemis'),
              color: '#76b041',
            },
          ]"
          yTitle="Surface (ha)"
          unite="ha"
          :decimales="1"
        ></graph_colonnes_saisons>

        <graph_colonnes_saisons
          title="Surface détruite cumulée"
          :categories="categories"
          :series="[{ name: 'Surface détruite cumulée', data: surfaceCumulee, color: '#a23b72' }]"
          yTitle="Surface cumulée (ha)"
          unite="ha"
          :decimales="1"
        ></graph_colonnes_saisons>
      </div>

      <p class="note">
        Les surfaces ne comptent que les déclarations exprimées en hectares : celles évaluées en
        nombre de plants ou en kilogrammes (arbres fruitiers, maraîchage…) sont exclues des surfaces
        mais comptées dans les montants, les déclarations et les dossiers.
      </p>

      <h2>Types de culture touchés</h2>

      <selecteur-saison
        v-model="idSaisonCultures"
        :saisons="saisons"
      ></selecteur-saison>

      <v-btn-toggle
        v-model="mesureCultures"
        mandatory
        density="compact"
        color="primary"
        variant="outlined"
        divided
      >
        <v-btn
          v-for="mesure of mesures"
          :key="mesure.value"
          :value="mesure.value"
        >
          {{ mesure.label }}
        </v-btn>
      </v-btn-toggle>

      <camembert
        v-if="dataCamembert.length"
        :data_db="dataCamembert"
        fieldName="nom_culture"
        fieldValue="valeur"
        :title="titreCamembert"
        :unite="mesure.unite"
        :code_couleurs="couleursCultures"
        :ordre="ordreCultures"
        height="500px"
      ></camembert>
      <div
        v-else-if="idSaisonCultures"
        class="note"
      >
        Aucune valeur à afficher pour cette saison.
      </div>

      <h2>Carte des communes</h2>

      <selecteur-saison
        v-model="idSaisonCarte"
        :saisons="saisons"
        :disabled="toutesSaisonsCarte"
      >
        <v-checkbox
          v-model="toutesSaisonsCarte"
          label="Toutes les années cumulées"
          density="compact"
          hide-details
        ></v-checkbox>
      </selecteur-saison>

      <map_degats_communes
        :geojson="geojsonCommunes"
        :cumul="!!(geojsonCommunes && geojsonCommunes.toutes_saisons)"
      ></map_degats_communes>
    </div>
  </div>
</template>

<script>
import { apiRequest } from '@/core/js/data/api.js';
import camembert from '@/components/graph/camembert.vue';
import graph_colonnes_saisons from './graph/graph_colonnes_saisons.vue';
import map_degats_communes from './map/map_degats_communes.vue';
import selecteurSaison from './selecteur-saison.vue';

// part (en %) en dessous de laquelle une culture est regroupée dans « Autres cultures »
const SEUIL_AUTRES = 2;

// couleurs des parts du camembert, attribuées aux cultures par ordre d'importance
// (toutes saisons confondues) pour rester identiques d'une saison et d'une mesure à l'autre
const PALETTE_CULTURES = [
  '#4e79a7',
  '#f28e2b',
  '#59a14f',
  '#e15759',
  '#b07aa1',
  '#edc948',
  '#76b7b2',
  '#9c755f',
  '#ff9da7',
  '#1b9e77',
  '#a6761d',
  '#7570b3',
  '#e7298a',
  '#66a61e',
  '#86bcb6',
  '#d37295',
  '#a0cbe8',
  '#ffbe7d',
  '#8cd17d',
  '#d4a6c8',
];
const COULEUR_AUTRES = '#b0b0b0';
const COULEUR_NON_RENSEIGNEE = '#dcdcdc';
const NOM_NON_RENSEIGNEE = 'Non renseignée';

// au-delà de la palette, teintes réparties par l'angle d'or pour rester distinctes
const couleurCulture = (rang) =>
  rang < PALETTE_CULTURES.length
    ? PALETTE_CULTURES[rang]
    : `hsl(${Math.round((rang * 137.508) % 360)}, 55%, 55%)`;

const arrondi = (valeur, decimales) => Number(valeur.toFixed(decimales));

export default {
  name: 'pageDegatsAgricoles',
  components: { camembert, graph_colonnes_saisons, map_degats_communes, selecteurSaison },
  data: () => ({
    chargement: true,
    erreur: null,
    saisons: [], // indicateurs par saison, de la plus ancienne à la plus récente
    idSaisonCultures: null,
    idSaisonCarte: null,
    cultures: [], // indicateurs par type de culture pour idSaisonCultures
    culturesToutesSaisons: [], // idem cumulés sur toutes les saisons (référence des couleurs)
    toutesSaisonsCarte: false, // carte : cumul de toutes les saisons au lieu de idSaisonCarte
    geojsonCommunes: null, // communes + indicateurs pour idSaisonCarte (ou cumulés)
    mesureCultures: 'nb_declarations',
    mesures: [
      { value: 'nb_declarations', label: 'Nombre de déclarations', decimales: 0, unite: '' },
      { value: 'surface_detruite', label: 'Surface détruite (ha)', decimales: 2, unite: 'Ha' },
      { value: 'montant_total', label: 'Montant indemnisé (€)', decimales: 0, unite: '€' },
    ],
  }),
  computed: {
    categories() {
      return this.saisons.map((s) => s.nom_saison);
    },
    surfaceCumulee() {
      let cumul = 0;
      return this.saisons.map((s) => {
        cumul += s.surface_detruite;
        return arrondi(cumul, 2);
      });
    },
    mesure() {
      return this.mesures.find((m) => m.value === this.mesureCultures);
    },
    nomSaisonCultures() {
      const saison = this.saisons.find((s) => s.id_saison === this.idSaisonCultures);
      return saison ? saison.nom_saison : '';
    },
    titreCamembert() {
      return `Types de culture touchés — ${this.mesure.label} — saison ${this.nomSaisonCultures}`;
    },
    // ordre des parts, identique dans tous les camemberts : cultures par ordre d'importance
    // toutes saisons confondues ; le regroupement « Autres cultures (n) », absent de la liste,
    // est placé à la fin
    ordreCultures() {
      return this.culturesToutesSaisons.map((c) => c.nom_culture);
    },
    // { nom de la part: couleur } : une culture garde la même couleur dans tous les camemberts
    couleursCultures() {
      const couleurs = {};
      let rang = 0;
      // les cultures absentes du cumul (réponse pas encore arrivée) sont ajoutées à la suite
      for (const { nom_culture } of [...this.culturesToutesSaisons, ...this.cultures]) {
        if (nom_culture in couleurs) {
          continue;
        }
        couleurs[nom_culture] =
          nom_culture === NOM_NON_RENSEIGNEE ? COULEUR_NON_RENSEIGNEE : couleurCulture(rang++);
      }
      for (const { nom_culture } of this.dataCamembert) {
        if (!(nom_culture in couleurs)) {
          couleurs[nom_culture] = COULEUR_AUTRES; // regroupement « Autres cultures (n) »
        }
      }
      return couleurs;
    },
    // parts du camembert : les petites cultures sont regroupées pour rester lisible
    dataCamembert() {
      const { value, decimales } = this.mesure;
      const lignes = this.cultures
        .map((c) => ({ nom_culture: c.nom_culture, valeur: c[value] }))
        .filter((c) => c.valeur > 0)
        .sort((a, b) => b.valeur - a.valeur);
      const total = lignes.reduce((somme, c) => somme + c.valeur, 0);
      if (!total) {
        return [];
      }
      const principales = lignes.filter((c) => (c.valeur / total) * 100 >= SEUIL_AUTRES);
      const autres = lignes.filter((c) => (c.valeur / total) * 100 < SEUIL_AUTRES);
      if (autres.length > 1) {
        principales.push({
          nom_culture: `Autres cultures (${autres.length})`,
          valeur: autres.reduce((somme, c) => somme + c.valeur, 0),
        });
      } else {
        principales.push(...autres);
      }
      return principales.map((c) => ({ ...c, valeur: arrondi(c.valeur, decimales) }));
    },
  },
  watch: {
    idSaisonCultures(id_saison) {
      this.chargerCultures(id_saison);
    },
    idSaisonCarte() {
      this.chargerCommunes();
    },
    toutesSaisonsCarte() {
      this.chargerCommunes();
    },
  },
  methods: {
    valeurs(champ) {
      return this.saisons.map((s) => s[champ]);
    },
    chargerCultures(id_saison) {
      if (!id_saison) {
        this.cultures = [];
        return;
      }
      apiRequest('GET', 'api/agricole/results/cultures', { params: { id_saison } }).then((res) => {
        // ignore une réponse arrivée après un nouveau changement de saison
        if (id_saison === this.idSaisonCultures) {
          this.cultures = res.items || [];
        }
      });
    },
    chargerCommunes() {
      const id_saison = this.idSaisonCarte;
      const toutes_saisons = this.toutesSaisonsCarte;
      if (!toutes_saisons && !id_saison) {
        this.geojsonCommunes = null;
        return;
      }
      const params = toutes_saisons ? { toutes_saisons: true } : { id_saison };
      apiRequest('GET', 'api/agricole/results/communes', { params }).then((res) => {
        // ignore une réponse arrivée après un nouveau changement de saison ou de cumul
        if (id_saison === this.idSaisonCarte && toutes_saisons === this.toutesSaisonsCarte) {
          this.geojsonCommunes = res;
        }
      });
    },
  },
  mounted() {
    apiRequest('GET', 'api/agricole/results/saisons')
      .then((res) => {
        this.saisons = res.items || [];
        apiRequest('GET', 'api/agricole/results/cultures', {
          params: { toutes_saisons: true },
        }).then((r) => {
          this.culturesToutesSaisons = r.items || [];
        });
        // saison la plus récente par défaut
        const derniere = this.saisons[this.saisons.length - 1];
        if (derniere) {
          this.idSaisonCultures = derniere.id_saison;
          this.idSaisonCarte = derniere.id_saison;
        }
      })
      .catch((err) => {
        console.error('dégâts agricoles :', err);
        this.erreur = 'Impossible de charger les données de dégâts agricoles.';
      })
      .finally(() => {
        this.chargement = false;
      });
  },
};
</script>

<style scoped>
.page-degats-agricoles {
  width: 100%;
  max-width: 1200px;
}
.page-degats-agricoles h2 {
  margin-top: 32px;
  margin-bottom: 8px;
}
.grille-graphiques {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 16px;
}
/* une seule colonne sur petit écran, sinon les graphiques sont illisibles */
@media (max-width: 900px) {
  .grille-graphiques {
    grid-template-columns: minmax(0, 1fr);
  }
}
.note {
  font-style: italic;
  color: #555;
  margin: 8px 0;
}
</style>
