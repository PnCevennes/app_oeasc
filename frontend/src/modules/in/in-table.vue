<!-- ensemble de tableau et de graphiques dans la page d'administration des indices nocturnes. -->

<template>
  <div class="in-table">
    <div>
      <!-- Affichage des filtres de sélection (Espèce, Secteur) -->
      <v-row
        dense
        v-if="ready"
      >
        <v-col
          v-for="[type, config] of Object.entries(configChoix)"
          :key="type"
        >
          <!-- listForm : composant pour afficher les boutons de sélection des filtres -->
          <list-form
            v-if="ready && config && config.items.length"
            :config="config"
            :baseModel="settings"
          ></list-form>
        </v-col>
      </v-row>

      <!-- Tableau récapitulatif du nombre de séries et de circuits par année -->
      <v-row v-if="dataUg && graphOnly === undefined">
        <v-col>
          <v-table
            density="compact"
            class="stats"
            v-if="dataUg"
          >
            <thead>
              <tr>
                <th>Année</th>
                <th>Nb Séries</th>
                <th>Nb Circuits(min)</th>
                <th>Nb Circuits(max)</th>
              </tr>
            </thead>
            <tbody>
              <!-- resNbCircuits() : méthode qui calcule les stats par année -->
              <tr
                v-for="(row, index) of resNbCircuits()"
                :key="index"
              >
                <td>{{ row.annee }}</td>
                <td>{{ row.nbSeries }}</td>
                <td>{{ row.nbCircuitsMin }}</td>
                <td>{{ row.nbCircuitsMax }}</td>
              </tr>
            </tbody>
          </v-table>
        </v-col>
      </v-row>

      <!-- Affichage du graphique pour le secteur sélectionné -->
      <v-row
        v-for="ug in [settings.ug]"
        :key="ug"
      >
        <v-col>
          <!-- in-graph : composant graphique des indices nocturnes -->
          <in-graph
            :class="{ 'graph-chained': graphOnly !== undefined }"
            v-if="settings.nom_espece"
            :displayReg="settings.displayReg"
            :dataIn="dataIn"
            :nom_espece="settings.nom_espece"
            :ug="ug"
            width="100%"
            height="400px"
            :commentaires="
              commentaires &&
              commentaires[settings.nom_espece] &&
              commentaires[settings.nom_espece][ug]
            "
          ></in-graph>
        </v-col>
      </v-row>

      <!-- Switch pour afficher ou non la régression linéaire -->
      <v-row v-if="graphOnly === undefined">
        <v-col
          cols="2"
          class="col-switch"
        >
          <!-- dynamicForm : composant pour le switch de la régression -->
          <dynamic-form
            v-if="ready"
            :config="configSwitchReg"
            :baseModel="settings"
          ></dynamic-form>
        </v-col>
        <v-col>
          <transition name="fade">
            <!-- Tableau des paramètres de la régression linéaire -->
            <div v-if="dataUg && this.settings.displayReg">
              <v-table
                density="compact"
                class="stats"
              >
                <thead>
                  <tr>
                    <th>y = ax + b</th>
                    <th>a</th>
                    <th>b</th>
                    <!-- <th>R<sup>2</sup></th> -->
                    <th>p-val</th>
                    <!-- <th>p-val b</th> -->
                  </tr>
                </thead>
                <tbody>
                  <tr>
                    <td></td>
                    <!-- round() : méthode pour arrondir les valeurs -->
                    <td>{{ round(dataUg.reg_lin.params[0], dec) }}</td>
                    <td>{{ round(dataUg.reg_lin.params[1], dec) }}</td>
                    <!-- <td>
                    {{ round(dataUg.reg_lin.R2, dec) }}
                    </td>-->
                    <td>{{ round(dataUg.reg_lin.pvalues[0], dec) }}</td>
                    <!-- <td>
                    {{ round(dataUg.reg_lin.pvalues[1], dec) }}
                    </td>-->
                  </tr>
                </tbody>
              </v-table>
            </div>
          </transition>
        </v-col>
      </v-row>

      <!-- Tableau principal des indices nocturnes par année et série -->
      <div v-if="dataUg && graphOnly == undefined">
        <h4>Indices nocturnes {{ settings.nom_espece }} {{ settings.ug }}</h4>

        <v-tabs
          v-model="activeAnneeTab"
          center-active
          dark
        >
          <!-- Onglets pour chaque année disponible -->
          <v-tab
            v-for="annee of Object.keys(dataUg.annees)"
            :key="annee"
            :value="'tab-' + annee"
          >
            {{ annee }}
          </v-tab>
        </v-tabs>

        <v-window
          v-model="activeAnneeTab"
          eager
        >
          <!-- Contenu de chaque onglet année -->
          <!-- eager : force le rendu de tous les onglets dès le montage, plutôt que d'attendre
               qu'ils soient activés une première fois. Sans ça, quand dataUg est remplacé (reload
               après validation d'un circuit), Vuetify perd le suivi des onglets déjà "visités" et
               leur contenu (lignes du tableau, onglet actif) peut disparaître. -->
          <v-window-item
            v-for="[annee, dataAnnee] of Object.entries(dataUg.annees)"
            :key="annee"
            :value="'tab-' + annee"
          >
            <!-- Tableau des statistiques globales de l'année -->
            <v-table
              density="compact"
              class="stats"
            >
              <thead>
                <tr>
                  <th>IN</th>
                  <th>E</th>
                  <th>inf</th>
                  <th>sup</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>{{ round(dataAnnee.moy, dec) }}</td>
                  <td>{{ round(dataAnnee.E, dec) }}</td>
                  <td>{{ round(dataAnnee.inf, dec) }}</td>
                  <td>{{ round(dataAnnee.sup, dec) }}</td>
                </tr>
              </tbody>
            </v-table>

            <!-- Tableau détaillé des circuits par série -->
            <v-table
              density="compact"
              class="in"
            >
              <thead>
                <tr>
                  <th>
                    <!-- Bouton pour recharger les données (admin uniquement) -->
                    <v-btn
                      v-if="$store.getters.droitMax >= 5"
                      icon
                      color="primary"
                      @click="reload()"
                    >
                      <v-icon v-if="loading">mdi-reload fa-spin</v-icon>
                      <v-icon v-else>mdi-reload</v-icon>
                    </v-btn>
                  </th>
                  <th>Série</th>
                  <th>Validé</th>
                  <th>Date</th>
                  <th>N° Circuit</th>
                  <th>Nom circuit</th>
                  <th>Nb grp.</th>
                  <th>Km</th>
                  <th>Nb ind.</th>
                  <th>Nb ind. / km</th>
                  <th>Moy. circuits</th>
                </tr>
              </thead>
              <tbody>
                <!-- Boucle sur chaque série et chaque circuit de la série -->
                <template
                  v-for="([numeroSerie, serie], indexSerie) in Object.entries(dataAnnee.series)"
                >
                  <tr
                    :class="{ serie: indexCircuit == 0 }"
                    v-for="(circuit, indexCircuit) of Object.values(serie.id_circuits).sort(
                      (a, b) => {
                        return a.numero_circuit - b.numero_circuit;
                      }
                    )"
                    :key="`${numeroSerie}-${circuit.id_circuit}`"
                  >
                    <!-- Première colonne vide pour l'affichage -->
                    <td
                      :class="{ gris: indexSerie % 2 }"
                      v-if="indexCircuit == 0"
                      :rowSpan="Object.entries(serie.id_circuits).length"
                    ></td>
                    <!-- Affichage du numéro de série (fusionné sur les lignes de la série) -->
                    <td
                      :class="{ gris: indexSerie % 2 }"
                      v-if="indexCircuit == 0"
                      :rowSpan="Object.entries(serie.id_circuits).length"
                    >
                      {{ numeroSerie }}
                    </td>
                    <!-- Checkbox pour valider le circuit (admin uniquement) -->
                    <td
                      v-if="settings.ug != 'Causse-Gorges_coeur'"
                      :class="{ gris: indexCircuit % 2 }"
                    >
                      <input
                        v-if="$store.getters.droitMax >= 5"
                        type="checkbox"
                        v-model="circuit.valide_PNC"
                        :disabled="freezeValid"
                        @change="validChange(circuit)"
                      />
                      <template v-else>
                        {{ `${circuit.valide_PNC ? 'Oui' : 'Non'}` }}
                      </template>
                      pnc
                    </td>
                    <td v-else>
                      <input
                        v-if="$store.getters.droitMax >= 5"
                        type="checkbox"
                        v-model="circuit.valide_ZC"
                        :disabled="freezeValid"
                        @change="validChange(circuit)"
                      />
                      <template v-else>
                        {{ `${circuit.valide_ZC ? 'Oui' : 'Non'}` }}
                      </template>
                      zc
                    </td>

                    <!-- Affichage des informations du circuit -->
                    <td :class="{ gris: indexCircuit % 2 }">
                      {{ circuit.date }}
                    </td>
                    <td :class="{ gris: indexCircuit % 2 }">
                      {{ circuit.numero_circuit }}
                    </td>
                    <td :class="{ gris: indexCircuit % 2 }">
                      {{ circuit.nom_circuit }}
                    </td>
                    <td :class="{ gris: indexCircuit % 2 }">
                      {{ circuit.groupes }}
                    </td>
                    <td :class="{ gris: indexCircuit % 2 }">
                      {{ circuit.km }}
                    </td>
                    <td :class="{ gris: indexCircuit % 2 }">
                      {{ circuit.nb }}
                    </td>
                    <td :class="{ gris: indexCircuit % 2 }">
                      {{ round(circuit.nb / circuit.km, dec) }}
                    </td>
                    <!-- Moyenne de la série (fusionné sur les lignes de la série) -->
                    <td
                      :class="{ gris: indexSerie % 2, serie: true }"
                      v-if="indexCircuit == 0"
                      :rowSpan="Object.entries(serie.id_circuits).length"
                    >
                      {{ round(serie.moy, dec) }}
                    </td>
                  </tr>
                </template>
              </tbody>
            </v-table>
          </v-window-item>
        </v-window>
      </div>
    </div>
  </div>
</template>

<script>
import listForm from '@/components/form/list-form';
import dynamicForm from '@/components/form/dynamic-form';
import { apiRequest } from '@/core/js/data/api.js';
import inGraph from './in-graph.vue';
import './table.css';

export default {
  name: 'in-table',
  props: ['graphOnly', 'commentaires'],
  components: {
    listForm,
    inGraph,
    dynamicForm,
  },
  // Données réactives du composant
  data: () => ({
    // Données principales récupérées depuis l'API (toutes les espèces, secteurs, années, etc.)
    dataIn: null,
    // Configuration des filtres de sélection (Espèce, Secteur)
    configChoix: {},
    // Indique si les données sont prêtes à être affichées
    ready: false,
    // Indique si le chargement des données est en cours
    loading: true,
    // Paramètres sélectionnés par l'utilisateur (espèce, secteur, affichage régression)
    // Valeurs par défaut : Cerf et Causse-Gorges, régression affichée
    settings: { nom_espece: 'Cerf', ug: 'Causse-Gorges', displayReg: true },
    // Données de l'année sélectionnée (non utilisé directement ici, mais peut servir pour des extensions)
    dataAnnee: null,
    // Données du secteur sélectionné (utilisé pour afficher les tableaux et graphiques)
    dataUg: null,
    // Nombre de décimales pour l'affichage des valeurs numériques
    dec: 4,
    // Empêche la modification de la validation pendant une requête API
    freezeValid: false,
    // Onglet année actif dans le tableau des indices nocturnes (v-tabs/v-window liés par value)
    activeAnneeTab: null,
    // Configuration du switch pour afficher ou non la régression linéaire
    configSwitchReg: {
      type: 'bool_switch', // Type du champ : interrupteur booléen
      label: 'Régression linéaire', // Libellé affiché
      name: 'displayReg', // Nom du champ lié à settings
    },
  }),
  methods: {
    /**
     * Calcule les statistiques du nombre de séries et de circuits par année pour le secteur sélectionné.
     *
     * Utilisation :
     * - Cette méthode est appelée dans le template pour afficher le tableau récapitulatif du nombre de séries et de circuits par année.
     *
     * Fonctionnement :
     * - Parcourt chaque année disponible dans le secteur sélectionné (dataUg).
     * - Pour chaque année, parcourt toutes les séries et calcule :
     *    - nbSeries : nombre total de séries pour l'année.
     *    - nbCircuitsMin : nombre minimum de circuits dans une série pour l'année.
     *    - nbCircuitsMax : nombre maximum de circuits dans une série pour l'année.
     * - Retourne un tableau d'objets contenant ces statistiques pour chaque année.
     */
    resNbCircuits() {
      const res = [];
      // Si aucune donnée n'est disponible pour le secteur, retourne un tableau vide
      if (!this.dataUg) return [];
      // Parcourt chaque année du secteur sélectionné
      for (const [annee, dataAnnee] of Object.entries(this.dataUg.annees || {})) {
        // Initialise les valeurs min et max à des extrêmes pour le calcul
        let nbCircuitsMin = 1e10;
        let nbCircuitsMax = -1e10;
        let nbSeries = 0;
        // Parcourt chaque série de l'année
        for (const serie of Object.values(dataAnnee.series)) {
          nbSeries += 1; // Incrémente le nombre de séries
          // Met à jour le maximum de circuits trouvés dans une série
          nbCircuitsMax = Math.max(nbCircuitsMax, Object.keys(serie.id_circuits).length);
          // Met à jour le minimum de circuits trouvés dans une série
          nbCircuitsMin = Math.min(nbCircuitsMin, Object.keys(serie.id_circuits).length);
        }
        // Ajoute les statistiques de l'année au résultat
        res.push({ annee, nbCircuitsMin, nbCircuitsMax, nbSeries });
      }
      // Retourne le tableau des statistiques par année
      return res;
    },

    round(x, dec) {
      if (x == 0) return 0;
      if (x == null) return '';
      const e = 10 ** dec;
      return Math.round(x * e) / e;
    },

    /**
     * Met à jour la validation d'un circuit (case à cocher dans le tableau).
     *
     * Fonctionnement :
     * - Cette méthode est appelée lorsqu'un administrateur modifie la case à cocher "Validé" d'un circuit dans le tableau détaillé.
     * - Elle empêche toute modification supplémentaire pendant la requête API (freezeValid).
     * - Prépare les données à envoyer à l'API (id_tag, id_realisation, valide_PNC, valide_ZC).
     * - Envoie une requête PATCH à l'API pour mettre à jour la validation du circuit.
     * - Une fois la requête terminée, elle recharge les données du secteur sélectionné (initInTable) et réactive la modification.
     *
     * Utilisation :
     * - Appelée lors du changement de la case à cocher "Validé" dans le tableau des circuits (événement @change sur l'input).
     */
    validChange(circuit) {
      // Empêche la modification pendant la requête API
      this.freezeValid = true;
      const postData = {};
      // Prépare les données à envoyer à l'API
      // postData.id_tag = circuit.id_tag;
      postData.id_realisation = circuit.id_realisation;
      postData.valide_PNC = circuit.valide_PNC;
      postData.valide_ZC = circuit.valide_ZC;
      // Envoie la requête PATCH à l'API pour mettre à jour la validation
      apiRequest('PATCH', 'api/in/valid_realisation/', {
        postData,
      }).then(() => {
        // Recharge les données du secteur sélectionné pour mettre à jour l'affichage,
        // puis seulement réactive la modification (sinon les checkboxes se réactivaient
        // avant que les nouvelles données soient arrivées, permettant de relancer une
        // validation pendant que le reload précédent était encore en cours).
        this.reload().then(() => {
          this.freezeValid = false;
        });
      });
    },

    /**
     * Initialise les données du tableau "In".
     *
     * Cette fonction réinitialise les variables `dataAnnee` et `dataUg` à null.
     * Elle vérifie ensuite que les paramètres essentiels (`ug`, `nom_espece` dans `settings`, et `ready`) sont bien définis.
     * Si l'un de ces paramètres manque, la fonction retourne immédiatement `null` et n'effectue aucune opération supplémentaire.
     *
     * Si tous les paramètres sont présents, la fonction récupère la liste des espèces (`nom_especes`) depuis `dataIn`,
     * puis extrait les unités de gestion (`ugs`) associées à l'espèce sélectionnée (`settings.nom_espece`).
     * Enfin, elle assigne à `dataUg` l'unité de gestion correspondant à l'identifiant `settings.ug`.
     *
     * Cette fonction est généralement appelée lors de l'initialisation ou de la mise à jour du tableau "In",
     * par exemple lors d'un changement de sélection d'espèce ou d'unité de gestion par l'utilisateur.
     */
    initInTable() {
      this.dataAnnee = null;
      this.dataUg = null;

      if (!(this.settings.ug && this.settings.nom_espece && this.ready)) {
        return null;
      }
      const nom_especes = this.dataIn.nom_especes;
      const ugs = nom_especes[this.settings.nom_espece].ugs;
      this.dataUg = ugs[this.settings.ug];

      // dataUg est remplacé par un nouvel objet à chaque reload (nouvelle requête API) : si l'onglet
      // année actif ne correspond plus à une année de ce nouvel objet (ou n'a jamais été initialisé),
      // on le fait pointer vers une année valide pour éviter que v-tabs/v-window perdent leur sélection.
      const anneesTab = Object.keys(this.dataUg.annees || {}).map((annee) => `tab-${annee}`);
      if (!anneesTab.includes(this.activeAnneeTab)) {
        this.activeAnneeTab = anneesTab[0] || null;
      }
    },

    /**
     * Calcule le nombre total de circuits pour une espèce, un secteur et une année donnés.
     *
     * Fonctionnement :
     * - Vérifie que les paramètres essentiels (nom_espece, ug, annee) sont définis.
     * - Récupère la liste des espèces depuis les données principales (dataIn).
     * - Accède à l'unité de gestion (ug) et à la liste des années disponibles pour cette espèce et ce secteur.
     * - Parcourt chaque série de l'année sélectionnée et additionne le nombre de circuits présents dans chaque série.
     * - Retourne le nombre total de circuits pour l'année, l'espèce et le secteur donnés.
     *
     * Utilisation :
     * - Cette méthode peut être utilisée dans le template pour afficher le nombre total de circuits d'une année,
     *   ou dans des calculs statistiques liés à l'affichage des tableaux ou graphiques.
     */
    nbCircuits(nom_espece, ug, annee) {
      // Vérifie que tous les paramètres sont définis
      if (!(nom_espece && ug && annee)) return 0;

      // Récupère la liste des espèces depuis les données principales
      const nom_especes = this.dataIn.nom_especes;
      // Accède à l'unité de gestion (secteur) pour l'espèce sélectionnée
      const ugs = nom_especes[nom_espece].ugs;
      // Récupère la liste des années pour ce secteur
      const annees = ugs[ug].annees;

      var nbCircuits = 0;
      // Parcourt chaque série de l'année sélectionnée
      for (const serie of Object.values(annees[annee].series)) {
        // Additionne le nombre de circuits présents dans la série
        nbCircuits += Object.keys(serie.id_circuits).length;
      }
      // Retourne le nombre total de circuits
      return nbCircuits;
    },

    /**
     * Met à jour les paramètres de configuration lorsque les paramètres changent.
     *
     * Cette fonction est généralement appelée lors d'un changement dans les paramètres utilisateur,
     * par exemple lors de la modification d'une sélection dans l'interface.
     *
     * - Vérifie si le composant est prêt avant d'effectuer des modifications.
     * - Si la valeur actuelle de 'ug' dans les paramètres n'est plus valide (n'existe pas dans la liste des items),
     *   elle est réinitialisée à null.
     * - Met à jour la liste des items 'ug' dans la configuration de choix.
     * - Réinitialise le tableau en appelant 'initInTable'.
     */
    settingsChange() {
      if (!this.ready) {
        return;
      }
      if (!this.items('ug').includes(this.settings.ug)) {
        this.settings.ug = null;
      }

      this.configChoix.ug.items = this.items('ug');

      this.initInTable();
    },

    /**
     * Retourne la liste des items disponibles pour un type donné ("nom_espece" ou "ug").
     *
     * Utilisation :
     * - Cette méthode est utilisée pour alimenter les listes de sélection des filtres (espèce, secteur).
     * - Elle est appelée lors de l'initialisation des filtres et lors des changements de sélection.
     *
     * Fonctionnement :
     * - Si le type demandé est "nom_espece", retourne la liste des noms d'espèces disponibles.
     * - Si le type demandé est "ug", retourne la liste des secteurs (unités de gestion) pour l'espèce sélectionnée.
     * - Si les paramètres nécessaires ne sont pas définis, retourne un tableau vide.
     */
    items(type) {
      // Récupère la liste des espèces depuis les données principales
      const nom_especes = this.dataIn.nom_especes;
      // Si le type est "nom_espece", retourne la liste des espèces
      if (type == 'nom_espece') {
        return Object.keys(nom_especes);
      }

      // Si aucune espèce n'est sélectionnée, retourne un tableau vide
      if (!this.settings.nom_espece) {
        return [];
      }

      // Récupère la liste des secteurs (ugs) pour l'espèce sélectionnée
      const ugs = nom_especes[this.settings.nom_espece].ugs;

      // Si le type est "ug", retourne la liste des secteurs
      if (type == 'ug') {
        return Object.keys(ugs);
      }

      // Si aucun secteur n'est sélectionné, retourne un tableau vide
      if (!this.settings.ug) {
        return [];
      }
    },

    /**
     * Recharge les données principales du module "In" depuis le store Vuex.
     *
     * Fonctionnement :
     * - Met l'état de chargement à true pour afficher un indicateur de chargement dans l'interface.
     * - Utilise la méthode Vuex "inResults" pour récupérer les données, avec l'option forceReload pour forcer la mise à jour.
     * - Une fois les données reçues :
     *    - Désactive l'état "ready" pour éviter l'affichage prématuré des composants dépendants.
     *    - Réinitialise la donnée "dataAnnee" (non utilisée directement ici, mais utile pour des extensions).
     *    - Met à jour "dataIn" avec les nouvelles données reçues.
     *    - Initialise la configuration des filtres de sélection :
     *        - "nom_espece" : liste des espèces disponibles, bouton de sélection, déclenche settingsChange lors d'un changement.
     *        - "ug" : liste des secteurs disponibles, bouton de sélection, déclenche settingsChange lors d'un changement.
     *    - Réactive l'état "ready" pour permettre l'affichage des composants dépendants.
     *    - Désactive l'indicateur de chargement.
     *    - Appelle "initInTable" pour initialiser les données du tableau principal selon les nouveaux paramètres.
     *
     * Utilisation :
     * - Cette fonction est appelée lors du montage du composant (mounted), ou lorsqu'un administrateur clique sur le bouton de rechargement dans le tableau détaillé.
     */
    reload() {
      this.loading = true;

      // Récupère les données depuis le store Vuex, en forçant le rechargement
      return this.$store.dispatch('inResults', { forceReload: true }).then((data) => {
        this.ready = false; // Désactive l'affichage des composants dépendants
        this.dataAnnee = false; // Réinitialise la donnée d'année
        this.dataIn = data; // Met à jour les données principales

        // Initialise la configuration du filtre "Espèce"
        this.configChoix.nom_espece = {
          name: 'nom_espece',
          label: 'Espèce',
          items: this.items('nom_espece'), // Liste des espèces disponibles
          change: this.settingsChange, // Fonction appelée lors d'un changement de sélection
          list_type: 'button', // Type d'affichage : boutons
        };
        // Initialise la configuration du filtre "Secteur"
        this.configChoix.ug = {
          name: 'ug',
          label: 'Secteur',
          items: this.items('ug'), // Liste des secteurs disponibles
          change: this.settingsChange, // Fonction appelée lors d'un changement de sélection
          list_type: 'button', // Type d'affichage : boutons
        };

        this.ready = true; // Réactive l'affichage des composants dépendants
        this.loading = false; // Désactive l'indicateur de chargement

        // Initialise les données du tableau principal selon les nouveaux paramètres
        this.initInTable();
      });
    },
  },

  mounted() {
    this.reload();
  },
};
</script>

<style lang="css">
.in-table {
  width: 100%;
  padding: 0 50px;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.5s;
}
.fade-enter, .fade-leave-to, .fade-leave-active  /* .fade-leave-active below version 2.1.8 */ {
  opacity: 0;
}
.graph-chained {
  margin-bottom: 100px;
}
</style>
