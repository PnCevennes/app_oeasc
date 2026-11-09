<!--
  Page publique « Dégâts agricoles » (menu Résultats des suivis) : graphiques par
  saison, répartition par type de culture (ou par culture) et carte des communes.
  Données : indemnisations de dégâts agricoles, zone OEASC (schéma oeasc_agricole).
  Chaque section a sa case « Uniquement l'OEASC » (cochée par défaut) : ne compter que
  les déclarations dont l'unité de gestion agricole est dans l'OEASC.
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

      <v-checkbox
        v-model="oeascSaisons"
        :label="LIBELLE_OEASC"
        density="compact"
        hide-details
      ></v-checkbox>

      <filtres-graphiques
        v-if="optionsFiltres"
        v-model="filtres"
        :options="optionsFiltres"
      ></filtres-graphiques>

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
          title="Nombre de parcelles endommagées par saison"
          :categories="categories"
          :series="[{ name: 'Parcelles endommagées', data: valeurs('nb_declarations'), color: '#f7a35c' }]"
          yTitle="Nombre de parcelles endommagées"
        ></graph_colonnes_saisons>

        <graph_colonnes_saisons
          title="Nombre de dossiers expertisés par saison"
          :categories="categories"
          :series="[{ name: 'Dossiers expertisés', data: valeurs('nb_dossiers'), color: '#8085e9' }]"
          yTitle="Nombre de dossiers expertisés"
        ></graph_colonnes_saisons>

        <div class="bloc-graphique">
          <graph_colonnes_saisons
            :title="
              enVolume
                ? 'Volume détruit par saison'
                : 'Surface détruite et surface remise en état par saison'
            "
            :categories="categories"
            :series="seriesSurfaceVolume"
            :yTitle="enVolume ? 'Volume (qtx)' : 'Surface (ha)'"
            :unite="enVolume ? 'qtx' : 'ha'"
            :decimales="1"
          ></graph_colonnes_saisons>
          <v-checkbox
            v-model="enVolume"
            class="case-volume"
            label="Afficher en volume"
            density="compact"
            hide-details
          ></v-checkbox>
        </div>
      </div>

      <p class="note">
        Les surfaces ne comptent que les déclarations exprimées en hectares : celles évaluées en
        nombre de plants ou en kilogrammes (arbres fruitiers, maraîchage…) sont exclues des surfaces
        mais comptées dans les montants, les déclarations et les dossiers.
      </p>

      <h2>{{ libelleCultures }}</h2>

      <selecteur-saison
        v-model="idSaisonCultures"
        :saisons="saisons"
        :disabled="toutesSaisonsCultures"
      >
        <v-checkbox
          v-model="toutesSaisonsCultures"
          label="Cumuler toutes les saisons"
          density="compact"
          hide-details
        ></v-checkbox>
        <v-checkbox
          v-model="parCulture"
          label="Afficher par culture"
          density="compact"
          hide-details
        ></v-checkbox>
        <v-checkbox
          v-model="oeascCultures"
          :label="LIBELLE_OEASC"
          density="compact"
          hide-details
        ></v-checkbox>
      </selecteur-saison>

      <filtres-graphiques
        v-if="optionsFiltres"
        v-model="filtresCultures"
        sansTypesCulture
        :options="optionsFiltres"
      ></filtres-graphiques>

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
        fieldName="nom"
        fieldValue="valeur"
        :title="titreCamembert"
        :unite="mesure.unite"
        :code_couleurs="couleursCultures"
        :ordre="ordreCultures"
        height="500px"
      ></camembert>
      <div
        v-else-if="toutesSaisonsCultures || idSaisonCultures"
        class="note"
      >
        Aucune valeur à afficher{{ toutesSaisonsCultures ? '' : ' pour cette saison' }}.
      </div>

      <h2>Carte des communes</h2>

      <selecteur-saison
        v-model="idSaisonCarte"
        :saisons="saisons"
        :disabled="toutesSaisonsCarte"
        :loading="chargementCarte"
      >
        <v-checkbox
          v-model="toutesSaisonsCarte"
          :disabled="chargementCarte"
          label="Toutes les années cumulées"
          density="compact"
          hide-details
        ></v-checkbox>
        <v-checkbox
          v-model="oeascCarte"
          :disabled="chargementCarte"
          :label="LIBELLE_OEASC"
          density="compact"
          hide-details
        ></v-checkbox>
      </selecteur-saison>

      <v-tabs
        v-model="mesureCarte"
        color="primary"
        bg-color="grey-lighten-3"
        grow
        class="onglets-mesure"
      >
        <v-tab
          v-for="m of ONGLETS_MESURE"
          :key="m.cle"
          :value="m.cle"
        >
          {{ m.onglet }}
        </v-tab>
      </v-tabs>

      <filtres-graphiques
        v-if="optionsFiltres"
        v-model="filtresCarte"
        sansCommunes
        :options="optionsFiltres"
      ></filtres-graphiques>

      <map_degats_communes
        :geojson="geojsonCommunes"
        :mesure="mesureCarte"
        :loading="chargementCarte"
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
import filtresGraphiques from './filtres-graphiques.vue';

// onglets de la carte des communes, dans l'ordre d'affichage
const ONGLETS_MESURE = [
  { cle: 'montant', onglet: 'Par montant' },
  { cle: 'surface', onglet: 'Par surface' },
  { cle: 'volume', onglet: 'Par volume' },
  { cle: 'remise', onglet: 'Par surface remise en état' },
];

// part (en %) en dessous de laquelle une culture est regroupée dans « Autres cultures »
// (affichage par culture uniquement : les types de culture, peu nombreux, restent séparés)
const SEUIL_AUTRES = 2;

// couleurs des parts du camembert, attribuées aux cultures (ou aux types) par ordre d'importance
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
// libellés renvoyés par l'API pour une déclaration sans culture / une culture sans type
const NOMS_NON_RENSEIGNES = ['Non renseignée', 'Non renseigné'];
const MESURES_SOMMEES = ['nb_declarations', 'montant_total', 'surface_detruite'];

// au-delà de la palette, teintes réparties par l'angle d'or pour rester distinctes
const couleurCulture = (rang) =>
  rang < PALETTE_CULTURES.length
    ? PALETTE_CULTURES[rang]
    : `hsl(${Math.round((rang * 137.508) % 360)}, 55%, 55%)`;

// famille de couleur selon le type de culture ; teinte null => couleur de la palette
const FAMILLES_COULEURS = [
  { nom: 'prairies', motif: 'PRAIRIE', teinte: 120, saturation: 55 },
  { nom: 'cereales', motif: 'CEREALE', teinte: 48, saturation: 90, eclaircie: 7 },
  { nom: 'fruits', motif: 'FRUIT', teinte: 0, saturation: 70 },
];
const FAMILLE_AUTRE = { nom: 'autre', teinte: null };
const familleCouleur = (nomType) => {
  const nom = (nomType || '').normalize('NFD').replace(/[\u0300-\u036f]/g, '').toUpperCase();
  return FAMILLES_COULEURS.find((f) => nom.includes(f.motif)) || FAMILLE_AUTRE;
};

const arrondi = (valeur, decimales) => Number(valeur.toFixed(decimales));

// case « uniquement les unités de gestion agricole de l'OEASC » de chaque section
const LIBELLE_OEASC = "Uniquement l'OEASC";

export default {
  name: 'pageDegatsAgricoles',
  components: {
    camembert,
    filtresGraphiques,
    graph_colonnes_saisons,
    map_degats_communes,
    selecteurSaison,
  },
  data: () => ({
    chargement: true,
    erreur: null,
    saisons: [], // indicateurs par saison, de la plus ancienne à la plus récente
    idSaisonCultures: null,
    idSaisonCarte: null,
    ONGLETS_MESURE,
    mesureCarte: 'montant', // onglet de la carte : montant, surface, volume ou remise
    cultures: [], // indicateurs par culture pour idSaisonCultures
    // idem cumulés sur toutes les saisons : référence des couleurs, et données du camembert
    // quand toutesSaisonsCultures est coché
    culturesToutesSaisons: [],
    toutesSaisonsCultures: false, // camembert : cumul de toutes les saisons
    parCulture: false, // camembert : détail par culture au lieu des types de culture
    toutesSaisonsCarte: false, // carte : cumul de toutes les saisons au lieu de idSaisonCarte
    // par section : uniquement les déclarations des unités de gestion agricole de l'OEASC
    oeascSaisons: true,
    // filtres des 4 graphiques par saison : options proposées et identifiants sélectionnés
    // (tout est sélectionné par défaut, une fois les options chargées)
    optionsFiltres: null,
    cleSaisons: null, // paramètres de la dernière requête des saisons (ignore les réponses périmées)
    filtres: { communes: [], typesCulture: [], especes: [] },
    // idem pour le camembert (sélection indépendante de celle des graphiques par saison)
    filtresCultures: { communes: [], typesCulture: [], especes: [] },
    // idem pour la carte (types de culture et espèces uniquement)
    filtresCarte: { communes: [], typesCulture: [], especes: [] },
    enVolume: false, // 4e graphique : volume détruit (qtx) au lieu des surfaces
    oeascCultures: true,
    oeascCarte: true,
    LIBELLE_OEASC,
    chargementCarte: false, // true pendant le chargement des communes de la carte
    geojsonCommunes: null, // communes + indicateurs pour idSaisonCarte (ou cumulés)
    mesureCultures: 'nb_declarations',
    mesures: [
      { value: 'nb_declarations', label: 'Nombre de parcelles endommagées', decimales: 0, unite: '' },
      { value: 'surface_detruite', label: 'Surface détruite (ha)', decimales: 2, unite: 'Ha' },
      { value: 'montant_total', label: 'Montant indemnisé (€)', decimales: 0, unite: '€' },
    ],
  }),
  computed: {
    categories() {
      return this.saisons.map((s) => s.nom_saison);
    },
    seriesSurfaceVolume() {
      if (this.enVolume) {
        return [{ name: 'Volume détruit', data: this.valeurs('volume_detruit'), color: '#e4572e' }];
      }
      return [
        { name: 'Surface détruite', data: this.valeurs('surface_detruite'), color: '#e4572e' },
        {
          name: 'Surface remise en état (ressemis)',
          data: this.valeurs('surface_ressemis'),
          color: '#76b041',
        },
      ];
    },
    mesure() {
      return this.mesures.find((m) => m.value === this.mesureCultures);
    },
    nomSaisonCultures() {
      const saison = this.saisons.find((s) => s.id_saison === this.idSaisonCultures);
      return saison ? saison.nom_saison : '';
    },
    libelleCultures() {
      return this.parCulture ? 'Cultures touchées' : 'Types de culture touchés';
    },
    titreCamembert() {
      const periode = this.toutesSaisonsCultures
        ? 'toutes saisons cumulées'
        : `saison ${this.nomSaisonCultures}`;
      return `${this.libelleCultures} — ${this.mesure.label} — ${periode}`;
    },
    // parts de référence (toutes saisons confondues, par ordre d'importance) : fixent l'ordre
    // et les couleurs des parts, identiques d'une saison et d'une mesure à l'autre
    partsToutesSaisons() {
      return this.regrouper(this.culturesToutesSaisons);
    },
    // parts affichées : saison choisie ou cumul, par culture ou par type de culture
    partsCultures() {
      return this.toutesSaisonsCultures ? this.partsToutesSaisons : this.regrouper(this.cultures);
    },
    // le regroupement « Autres cultures (n) », absent de la liste, est placé à la fin
    // Par type de culture, les parts partent du haut dans le sens horaire, du moins au plus
    // important, sauf le plus petit type (MÉLANGE) placé en dernier : les deux petites parts
    // se retrouvent de part et d'autre du sommet, et le libellé de la plus petite s'affiche
    // à gauche, du côté opposé aux autres, au lieu de les chevaucher
    ordreCultures() {
      const noms = this.partsToutesSaisons.map((c) => c.nom);
      if (this.parCulture || noms.length < 3) {
        return noms;
      }
      const [plusPetit, ...autres] = noms.reverse();
      return [...autres, plusPetit];
    },
    // nom de culture -> nom de son type de culture (pour colorer chaque culture selon son type)
    typeParCulture() {
      const types = {};
      for (const c of [...this.culturesToutesSaisons, ...this.cultures]) {
        types[c.nom_culture] = c.nom_type_culture;
      }
      return types;
    },
    // { nom de la part: couleur } : une part garde la même couleur dans tous les camemberts.
    // Teinte par type de culture (prairies : verts, céréales : jaunes, fruits et légumes :
    // rouges) ; par culture, dégradé de clair à foncé au sein de la teinte de son type
    couleursCultures() {
      const couleurs = {};
      const noms = [];
      // les parts absentes du cumul (réponse pas encore arrivée) sont ajoutées à la suite
      for (const { nom } of [...this.partsToutesSaisons, ...this.partsCultures]) {
        if (!noms.includes(nom)) {
          noms.push(nom);
        }
      }
      const typeDe = (nom) => (this.parCulture ? this.typeParCulture[nom] : nom);
      // effectif de chaque famille de couleur, pour répartir le dégradé
      const effectifs = {};
      for (const nom of noms) {
        const famille = familleCouleur(typeDe(nom));
        effectifs[famille.nom] = (effectifs[famille.nom] || 0) + 1;
      }
      const rangs = {};
      let rangAutre = 0;
      for (const nom of noms) {
        if (NOMS_NON_RENSEIGNES.includes(nom)) {
          couleurs[nom] = COULEUR_NON_RENSEIGNEE;
          continue;
        }
        const famille = familleCouleur(typeDe(nom));
        if (famille.teinte === null) {
          couleurs[nom] = couleurCulture(rangAutre++);
          continue;
        }
        const rang = rangs[famille.nom] || 0;
        rangs[famille.nom] = rang + 1;
        // un type seul garde sa teinte de base ; sinon dégradé du plus foncé au plus clair
        couleurs[nom] =
          this.parCulture && effectifs[famille.nom] > 1
            ? `hsl(${famille.teinte}, ${famille.saturation}%, ${
                35 + (famille.eclaircie || 0) + (rang * 35) / (effectifs[famille.nom] - 1)
              }%)`
            : `hsl(${famille.teinte}, ${famille.saturation}%, ${48 + (famille.eclaircie || 0)}%)`;
      }
      for (const { nom } of this.dataCamembert) {
        if (!(nom in couleurs)) {
          couleurs[nom] = COULEUR_AUTRES; // regroupement « Autres cultures (n) »
        }
      }
      return couleurs;
    },
    // parts du camembert ; par culture, les petites parts sont regroupées pour rester lisible
    dataCamembert() {
      const { value, decimales } = this.mesure;
      const lignes = this.partsCultures
        .map((c) => ({ nom: c.nom, valeur: c[value] }))
        .filter((c) => c.valeur > 0)
        .sort((a, b) => b.valeur - a.valeur);
      const total = lignes.reduce((somme, c) => somme + c.valeur, 0);
      if (!total) {
        return [];
      }
      const seuil = this.parCulture ? SEUIL_AUTRES : 0;
      const principales = lignes.filter((c) => (c.valeur / total) * 100 >= seuil);
      const autres = lignes.filter((c) => (c.valeur / total) * 100 < seuil);
      if (autres.length > 1) {
        principales.push({
          nom: `Autres cultures (${autres.length})`,
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
    oeascSaisons() {
      this.chargerSaisons();
    },
    filtres: {
      deep: true,
      handler() {
        this.chargerSaisons();
      },
    },
    filtresCultures: {
      deep: true,
      handler() {
        this.chargerCulturesToutesSaisons();
        this.chargerCultures(this.idSaisonCultures);
      },
    },
    oeascCultures() {
      this.chargerCulturesToutesSaisons();
      this.chargerCultures(this.idSaisonCultures);
    },
    idSaisonCarte() {
      this.chargerCommunes();
    },
    toutesSaisonsCarte() {
      this.chargerCommunes();
    },
    oeascCarte() {
      this.chargerCommunes();
    },
    filtresCarte: {
      deep: true,
      handler() {
        this.chargerCommunes();
      },
    },
  },
  methods: {
    valeurs(champ) {
      return this.saisons.map((s) => s[champ]);
    },
    // lignes de l'API (une par culture) -> parts { nom, mesures } : une par culture si
    // parCulture, sinon une par type de culture (mesures sommées) ; par nombre de
    // déclarations décroissant
    regrouper(cultures) {
      const parts = {};
      for (const c of cultures) {
        const nom = this.parCulture ? c.nom_culture : c.nom_type_culture;
        parts[nom] = parts[nom] || {
          nom,
          nb_declarations: 0,
          montant_total: 0,
          surface_detruite: 0,
        };
        for (const champ of MESURES_SOMMEES) {
          parts[nom][champ] += c[champ];
        }
      }
      return Object.values(parts).sort(
        (a, b) => b.nb_declarations - a.nb_declarations || a.nom.localeCompare(b.nom)
      );
    },
    // toutes les saisons sont renvoyées (à 0 si besoin) : la liste sert aussi aux sélecteurs
    // un filtre complètement coché n'est pas envoyé (pas de filtre : les déclarations sans
    // culture ou sans espèce restent comptées) ; un filtre vide est envoyé vide (rien retenu)
    paramFiltre(selection, options) {
      return selection.length === options.length ? undefined : selection.join(',');
    },
    // paramètres de requête correspondant à une sélection de filtres
    paramsFiltres(f) {
      const o = this.optionsFiltres;
      if (!o) {
        return {};
      }
      return {
        communes: this.paramFiltre(f.communes, o.communes),
        types_culture: this.paramFiltre(f.typesCulture, o.types_culture),
        especes: this.paramFiltre(f.especes, o.especes),
      };
    },
    chargerSaisons() {
      const uniquement_oeasc = this.oeascSaisons;
      const params = { uniquement_oeasc, ...this.paramsFiltres(this.filtres) };
      const cle = JSON.stringify(params);
      this.cleSaisons = cle;
      return apiRequest('GET', 'api/agricole/results/saisons', { params }).then((res) => {
        // ignore une réponse arrivée après un nouveau changement de la case ou des filtres
        if (cle === this.cleSaisons) {
          this.saisons = res.items || [];
        }
      });
    },
    chargerCulturesToutesSaisons() {
      const uniquement_oeasc = this.oeascCultures;
      const cle = JSON.stringify(this.filtresCultures);
      apiRequest('GET', 'api/agricole/results/cultures', {
        params: {
          toutes_saisons: true,
          uniquement_oeasc,
          ...this.paramsFiltres(this.filtresCultures),
        },
      }).then((res) => {
        if (uniquement_oeasc === this.oeascCultures && cle === JSON.stringify(this.filtresCultures)) {
          this.culturesToutesSaisons = res.items || [];
        }
      });
    },
    chargerCultures(id_saison) {
      if (!id_saison) {
        this.cultures = [];
        return;
      }
      const uniquement_oeasc = this.oeascCultures;
      const cle = JSON.stringify(this.filtresCultures);
      apiRequest('GET', 'api/agricole/results/cultures', {
        params: { id_saison, uniquement_oeasc, ...this.paramsFiltres(this.filtresCultures) },
      }).then((res) => {
        // ignore une réponse arrivée après un nouveau changement de saison, de case ou de filtre
        if (
          id_saison === this.idSaisonCultures &&
          uniquement_oeasc === this.oeascCultures &&
          cle === JSON.stringify(this.filtresCultures)
        ) {
          this.cultures = res.items || [];
        }
      });
    },
    requeteCarteCourante(id_saison, toutes_saisons, uniquement_oeasc, cle) {
      return (
        cle === JSON.stringify(this.filtresCarte) &&
        id_saison === this.idSaisonCarte &&
        toutes_saisons === this.toutesSaisonsCarte &&
        uniquement_oeasc === this.oeascCarte
      );
    },
    chargerCommunes() {
      const id_saison = this.idSaisonCarte;
      const toutes_saisons = this.toutesSaisonsCarte;
      const uniquement_oeasc = this.oeascCarte;
      if (!toutes_saisons && !id_saison) {
        this.geojsonCommunes = null;
        this.chargementCarte = false;
        return;
      }
      this.chargementCarte = true;
      const cle = JSON.stringify(this.filtresCarte);
      const { types_culture, especes } = this.paramsFiltres(this.filtresCarte);
      const params = {
        ...(toutes_saisons ? { toutes_saisons: true } : { id_saison }),
        uniquement_oeasc,
        types_culture,
        especes,
      };
      apiRequest('GET', 'api/agricole/results/communes', { params })
        .then((res) => {
          // ignore une réponse arrivée après un nouveau changement de saison, de cumul ou de case
          if (this.requeteCarteCourante(id_saison, toutes_saisons, uniquement_oeasc, cle)) {
            this.geojsonCommunes = res;
          }
        })
        .finally(() => {
          if (this.requeteCarteCourante(id_saison, toutes_saisons, uniquement_oeasc, cle)) {
            this.chargementCarte = false;
          }
        });
    },
  },
  mounted() {
    // options des filtres : tout est sélectionné par défaut (sans déclencher de rechargement
    // superflu : le watcher ne s'applique qu'après le premier chargement des saisons)
    const chargementFiltres = apiRequest('GET', 'api/agricole/results/filtres')
      .then((res) => {
        this.optionsFiltres = {
          communes: res.communes || [],
          types_culture: res.types_culture || [],
          especes: res.especes || [],
        };
        const toutSelectionne = () => ({
          communes: this.optionsFiltres.communes.map((c) => c.id),
          typesCulture: this.optionsFiltres.types_culture.map((t) => t.id),
          especes: this.optionsFiltres.especes.map((e) => e.id),
        });
        this.filtres = toutSelectionne();
        this.filtresCultures = toutSelectionne();
        this.filtresCarte = toutSelectionne();
      })
      .catch((err) => console.error('dégâts agricoles (filtres) :', err));
    chargementFiltres
      .then(() => this.chargerSaisons())
      .then(() => {
        this.chargerCulturesToutesSaisons();
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
/* case superposée au bas du graphique, à droite, sur la ligne de la légende */
.bloc-graphique {
  position: relative;
}
.onglets-mesure {
  margin: 8px 0;
  border: 1px solid #bdbdbd;
  border-radius: 4px;
}
.onglets-mesure :deep(.v-tab) {
  font-size: 0.95rem;
  font-weight: 600;
  text-transform: none;
}
.onglets-mesure :deep(.v-tab--selected) {
  background-color: #bbdefb;
}
.case-volume {
  position: absolute;
  right: 8px;
  bottom: 6px;
}
.note {
  font-style: italic;
  color: #555;
  margin: 8px 0;
}
</style>
