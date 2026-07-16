<!--
  affiche le tableau correspondant aux données admin de chaques bModalSuccess
  Ce composant générique de tableau affiche les données sous forme de tableau avec des fonctionnalités de recherche, d'édition et de suppression.
  - Il utilise v-data-table pour afficher les données.
  - Les en-têtes du tableau sont définis dans configTable.headers.
  - Les actions possibles sur chaque ligne sont définies dans configTable.headerDefs.actions.
  - La propriété "config" permet de personnaliser le tableau via des props.
  - Le tableau supporte la recherche, l'édition et la suppression de lignes.
  - Les boîtes de dialogue pour l'édition et la confirmation de suppression sont intégrées.

 -->

<template>
  <div>
    <!--
      Ce composant Vue.js affiche une boîte de dialogue de confirmation pour la suppression d'une ligne dans un tableau.
      - <v-dialog> : Fenêtre modale persistante qui s'affiche lorsque la variable 'deleteModal' est vraie.
      - <v-card-title> : Titre de la boîte de dialogue avec une icône d'avertissement et un message de confirmation.
      - <v-checkbox> : Permet à l'utilisateur de choisir de ne plus afficher ce message lors des prochaines suppressions.
        - 'deleteWithoutWarning' : Variable liée au choix de l'utilisateur.
      - <v-btn Oui> : Bouton pour confirmer la suppression.
        - Appelle la méthode 'deleteRow' avec l'identifiant de la ligne à supprimer ('idToDelete'), puis ferme la boîte de dialogue.
      - <v-btn Non> : Bouton pour annuler la suppression et fermer la boîte de dialogue.
      - Les variables 'idToDelete' et 'deleteModal' sont réinitialisées lors de la fermeture de la boîte de dialogue.
    -->
    <v-dialog
      persistent
      max-width="600px"
      v-model="deleteModal"
    >
      <v-card>
        <v-card-title>
          <v-icon large>warning</v-icon>
          Êtes vous sûr de vouloir supprimer la ligne?
        </v-card-title>

        <v-card-text>
          <v-checkbox
            dense
            tiny
            v-model="deleteWithoutWarning"
            label="Ne plus afficher ce message avant la suppression"
          ></v-checkbox>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="green darken-1"
            variant="text"
            @click="
              deleteRow(idToDelete);
              idToDelete = null;
              deleteModal = false;
            "
          >
            Oui
          </v-btn>

          <v-btn
            color="green darken-1"
            variant="text"
            @click="
              idToDelete = null;
              deleteModal = false;
            "
          >
            Non
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>

    <!--
      Ce composant Vue.js représente un tableau générique utilisant Vuetify (v-data-table).
      Il est hautement configurable via la propriété `configTable` qui définit :
        - Le titre du tableau
        - Les classes CSS à appliquer
        - Les en-têtes du tableau (headers)
        - Le mode dense ou non
        - Le mode serveur ou client pour la pagination
        - Le nombre d'éléments côté serveur

      Fonctionnalités principales :
        - Affichage d'un titre dynamique
        - Barre de recherche par colonne (sauf si `noSearch` est défini dans le header)
        - Bouton pour ajouter une nouvelle ligne dans la colonne "actions" avec un tooltip explicatif
        - Affichage des actions (éditer, supprimer, etc.) dans la colonne "actions" selon la configuration
        - Affichage conditionnel d'un bouton d'édition pour chaque cellule (hors colonne "actions") si la fonction `bEditCell` le permet
        - Affichage du contenu de chaque cellule via la fonction `displayCell`
        - Gestion du chargement des données avec un texte personnalisé
        - Support du tri multiple et de la pagination serveur

      Slots et templates :
        - `body.prepend` : Ajoute une ligne de filtres de recherche en haut du tableau
        - Slot dynamique pour chaque cellule du tableau, permettant une personnalisation avancée de l'affichage et des actions

      Points d'attention :
        - Les actions dans la colonne "actions" sont dynamiques et peuvent dépendre de conditions spécifiques
        - L'utilisation de fonctions comme `edit`, `bEditCell`, et `displayCell` permet une grande flexibilité dans la gestion des interactions et de l'affichage

      Ce composant est idéal pour afficher et manipuler des données tabulaires de façon flexible et interactive dans une application Vue.js utilisant Vuetify.
    -->
    <v-card>
      <v-card-title>
        {{ configTable.title }}
        <v-spacer></v-spacer>
      </v-card-title>

      <v-data-table
        :options.sync="options"
        :class="configTable.classes"
        :headers="configTable.headers"
        :items="filteredItems"
        multi-sort
        :dense="configTable.dense"
        :loading="!configTable.items"
        :server-items-length="configTable.serverSide && itemsServerCount"
        loading-text="Chargement en cours... merci de patienter"
        :footer-props="{ 'items-per-page-options': [20, 50, 100] }"
      >
        <template v-slot:body.prepend>
          <tr>
            <td
              v-for="header of configTable.headers"
              :key="header.value"
            >
              <v-text-field
                v-if="!header.noSearch"
                dense
                v-model="searchs[header.value]"
                type="text"
              ></v-text-field>
              <v-tooltip top>
                <template v-slot:activator="{ props: tooltipActivatorProps }">
                  <v-btn
                    v-bind="tooltipActivatorProps"
                    v-if="header.value == 'actions'"
                    color="primary"
                    icon
                    size="x-small"
                    variant="text"
                    @click="edit('actions')"
                  >
                    <v-icon size="16">fa-plus</v-icon>
                  </v-btn>
                </template>
                <span>Ajouter une nouvelle ligne au tableau</span>
              </v-tooltip>
            </td>
          </tr>
        </template>

        <template
          v-for="(value, index) of (configTable.headers || []).map((header) => header.value)"
          #[`item.${value}`]="props"
        >
          <div :key="index">
            <!-- bouton supprimer et editer -->
            <div
              v-if="value == 'actions'"
              class="d-flex flex-nowrap align-center"
            >
              <template
                v-for="(action, indexAction) of props.column.list || []"
                :key="indexAction"
              >
                <v-btn
                  v-if="!action.condition || action.condition({ $store, item: props.item })"
                  icon
                  size="x-small"
                  variant="text"
                  :to="
                    typeof action.to == 'function'
                      ? action.to({ item: props.item, $store })
                      : action.to
                  "
                  :title="action.title"
                  @click="action.click && action.click(props.item[configTable.idFieldName])"
                >
                  <v-icon size="16">{{ action.icon }}</v-icon>
                </v-btn>
              </template>
            </div>

            <div v-if="bEditCell(props)">
              <v-btn
                v-if="value != 'actions'"
                small
                @click="edit(value, props.item[configTable.idFieldName])"
              >
                <span v-html="displayCell(props, value)"></span>
              </v-btn>
            </div>
            <div v-else>
              <!-- si value == true  ou si value == false on affiche un icone -->
              <v-icon
                v-if="displayCell(props, value) === true || displayCell(props, value) === false"
                small
                :color="displayCell(props, value) ? 'success' : 'error'"
              >
                {{ displayCell(props, value) ? 'mdi-check-bold' : 'mdi-close-thick' }}
              </v-icon>
              <span
                v-else
                v-html="displayCell(props, value)"
              ></span>
            </div>
          </div>
        </template>
      </v-data-table>
    </v-card>

    <!--
      Affiche un message d'erreur dans une boîte de dialogue si 'bError' est vrai.
      - Utilise v-snackbar pour afficher le message d'erreur 'msgError'.
      - La boîte de dialogue disparaît après 5 secondes (timeout = 5000).
     -->
    <v-snackbar
      color="error"
      v-model="bError"
      :timeout="5000"
    >
      {{ msgError }}
    </v-snackbar>

    <!--
      Affiche un formulaire générique dans une boîte de dialogue pour l'édition des données.
      - Utilise v-dialog pour afficher le formulaire lorsque 'bEditDialog' est vrai.
      - La largeur maximale de la boîte de dialogue est fixée à 1400px.
      - Le composant 'genericForm' est utilisé pour afficher le formulaire avec la configuration 'configForm'.
     -->
    <v-dialog
      persistent
      max-width="1400px"
      v-model="bEditDialog"
    >
      <v-card>
        <genericForm
          class="edit-dialog"
          v-if="configForm && bEditDialog"
          :config="configForm"
        ></genericForm>
      </v-card>
    </v-dialog>
  </div>
</template>

<script>
import { copy, sortDate } from '@/core/js/util/util.js';
// import { sortDateTable } from './util';
import genericForm from '@/components/form/generic-form.vue';
import './table.css';

export default {
  name: 'generic-table',
  components: { genericForm },
  props: {
    config: {
      type: Object,
    },
  },
  data: () => ({
    options: {}, // Objet contenant les options de configuration du tableau
    configTable: {}, // Configuration spécifique du tableau (colonnes, tri, etc.)
    searchs: {}, // Paramètres de recherche appliqués au tableau
    saveValue: null, // Valeur temporaire pour sauvegarder des données
    msgError: null, // Message d'erreur à afficher à l'utilisateur
    bError: false, // Booléen indiquant la présence d'une erreur
    idToDelete: null, // Identifiant de l'élément à supprimer
    deleteModal: null, // Référence au composant modal de suppression
    deleteWithoutWarning: false, // Indique si la suppression doit se faire sans avertissement
    configForm: null, // Configuration du formulaire associé au tableau
    bEditDialog: false, // Booléen pour afficher ou masquer la boîte de dialogue d'édition
    itemsServerCount: null, // Nombre total d'éléments sur le serveur (pour la pagination)
  }),
  watch: {
    config: {
      handler() {
        this.initConfig();
      },
      deep: true,
    },
    searchs: {
      handler() {
        this.loadData(false);
      },
      deep: true,
    },

    options() {
      this.loadData(false);
    },
  },
  methods: {
    /**
     * Affiche la valeur d'une cellule dans le tableau générique.
     *
     * @param {Object} props - Les propriétés de la cellule, incluant l'élément (item) et l'en-tête (header).
     * @param {String} value - La clé correspondant à la valeur à afficher dans l'item.
     * @returns {*} La valeur à afficher dans la cellule. Si la propriété 'display' de l'en-tête est une fonction,
     *              elle est appelée avec l'item et le store comme paramètres. Sinon, la valeur de l'item correspondant à la clé 'value' est retournée.
     */
    displayCell(props, value) {
      const res =
        props.item &&
        (typeof props.column.display == 'function'
          ? props.column.display(props.item, { $store: this.$store })
          : props.item[value]);
      return res;
    },

    /**
     * Détermine si une cellule du tableau peut être éditée.
     *
     * Cette fonction vérifie d'abord si la propriété 'edit' est définie dans l'en-tête de la colonne.
     * Si une condition d'édition est spécifiée ('edit.condition'), elle l'évalue en lui passant le store Vuex
     * et le modèle de base de la ligne courante. Si aucune condition n'est définie, la cellule est éditable par défaut.
     *
     * @param {Object} props - Les propriétés de la cellule, incluant l'en-tête et l'élément de la ligne.
     * @returns {Boolean} - Retourne vrai si la cellule est éditable, faux sinon.
     */
    bEditCell(props) {
      return (
        props.column.edit &&
        (!props.column.edit.condition ||
          props.column.edit.condition({
            $store: this.$store,
            baseModel: props.item,
          }))
      );
    },

    /**
     * Retourne la configuration du formulaire d'édition pour une cellule spécifique du tableau.
     *
     * @param {string} value - La clé correspondant à la colonne du tableau (ex: nom du champ).
     * @param {any} id - L'identifiant unique de la ligne à éditer.
     * @returns {Object|null} La configuration du formulaire d'édition, ou null si la colonne n'est pas éditable.
     *
     * Étapes principales :
     * 1. Recherche l'élément (ligne) du tableau correspondant à l'id fourni.
     * 2. Recherche la configuration de l'en-tête (colonne) correspondant à la valeur donnée.
     * 3. Vérifie si la colonne est éditable (propriété 'edit' dans l'en-tête).
     * 4. Copie la configuration du formulaire d'édition à partir de l'en-tête.
     * 5. Personnalise le titre et le label du formulaire si ce n'est pas la colonne 'actions'.
     * 6. Définit les propriétés supplémentaires du formulaire (idFieldName, valeur, affichage, etc.).
     * 7. Définit l'action d'annulation pour fermer le dialogue et annuler l'édition.
     * 8. Redéfinit l'action de succès pour mettre à jour l'élément dans le tableau après édition,
     *    en appliquant éventuellement une pré-processing sur les données.
     * 9. Retourne la configuration complète du formulaire d'édition.
     */
    getConfigForm(value, id) {
      const item = this.configTable.items.find((item) => item[this.configTable.idFieldName] === id);
      const header = this.configTable.headers.find((header) => header && header.value == value);
      const label = header.text;
      if (!header.edit) {
        return null;
      }
      const configForm = copy(header.edit);

      if (value != 'actions') {
        configForm.title = `Modifier ${header.text} pour ${
          item[this.configTable.labelFieldName || this.configTable.idFieldName]
        }`;
        configForm.label = label;
      }
      configForm.idFieldName = configForm.idFieldName || this.configTable.idFieldName;
      configForm.value = copy(item) || configForm.value;
      configForm.switchDisplay = false;
      configForm.displayValue = false;
      configForm.cancel = {
        action: () => {
          this.cancel(value, item && item[this.configTable.idFieldName]);
          this.closeDialog();
        },
      };
      if (configForm.action && configForm.action.onSuccess) {
        configForm.action.onSuccess2 = configForm.action.onSuccess;
      } else {
        configForm.action = configForm.action || {};
      }
      configForm.action.onSuccess = ({ data }) => {
        configForm.action.onSuccess2 && configForm.action.onSuccess2({ data });

        let elem = this.configTable.items.find(
          (item) => item[this.configTable.idFieldName] == data[this.configTable.idFieldName]
        );

        if (!elem) {
          elem = {};
          this.configTable.items.push(elem);
        }

        const processedData = this.configTable.preProcess
          ? this.configTable.preProcess({ data: [data] })[0]
          : data;

        for (const key of Object.keys(processedData)) {
          elem[key] = processedData[key];
        }

        this.closeDialog();
      };
      return configForm;
    },

    /**
     * Annule les modifications apportées à un élément spécifique du tableau.
     *
     * @param {any} value - La valeur initiale (non utilisée dans cette fonction).
     * @param {string|number} id - L'identifiant unique de l'élément à restaurer.
     *
     * Si l'identifiant n'est pas fourni, la fonction retourne immédiatement.
     * Recherche l'élément correspondant dans la liste des items du tableau
     * en utilisant le champ d'identifiant défini dans la configuration.
     * Pour chaque clé présente dans l'objet `saveVal` (qui contient les valeurs sauvegardées),
     * la valeur de l'élément est restaurée à sa valeur initiale.
     */
    cancel(value, id) {
      if (!id) {
        return;
      }
      const elem = this.configTable.items.find((item) => item[this.configTable.idFieldName] == id);
      for (const key of Object.keys(this.saveVal)) {
        elem[key] = this.saveVal[key];
      }
    },

    /**
     * Ouvre le formulaire d'édition pour une ligne spécifique du tableau.
     *
     * @param {Object} value - Les données de la ligne à éditer.
     * @param {number|string} id - L'identifiant unique de la ligne à éditer.
     *
     * Étapes :
     * 1. Ferme la boîte de dialogue en cours.
     * 2. Initialise la configuration du formulaire d'édition avec les données de la ligne sélectionnée.
     * 3. Si un identifiant est fourni, copie les données de la ligne correspondante pour permettre l'édition sans altérer l'original.
     * 4. Active la boîte de dialogue d'édition si la configuration du formulaire est correctement initialisée.
     */
    edit(value, id) {
      this.closeDialog();
      this.configForm = this.getConfigForm(value, id);
      this.saveVal = id
        ? copy(this.configTable.items.find((item) => item[this.configTable.idFieldName] == id))
        : null;
      this.bEditDialog = !!this.configForm;
    },

    /**
     * Supprime une ligne du tableau en fonction de son identifiant.
     *
     * @param {any} id - L'identifiant unique de la ligne à supprimer.
     *
     * Étapes :
     * 1. Recherche l'index de la ligne à supprimer dans le tableau `items` en utilisant l'identifiant.
     * 2. Si la ligne existe (index différent de -1) :
     *    a. Si une fonction de suppression (`delete`) est définie dans la configuration du tableau :
     *       - Appelle cette fonction en passant l'identifiant et le store Vuex.
     *       - En cas de succès, retire la ligne du tableau.
     *       - En cas d'erreur, affiche un message d'erreur.
     *    b. Sinon, retire simplement la ligne du tableau localement.
     */
    deleteRow(id) {
      const index = this.configTable.items.findIndex((d) => d[this.configTable.idFieldName] == id);
      if (index !== -1) {
        if (this.configTable.delete) {
          this.configTable.delete(id, { $store: this.$store }).then(
            () => {
              this.configTable.items.splice(index, 1);
            },
            (err) => {
              this.bError = true;
              this.msgError = err;
            }
          );
        } else {
          this.configTabel.items.splice(index, 1);
        }
      }
    },

    /**
     * Ferme la boîte de dialogue d'édition.
     */
    closeDialog() {
      this.bEditDialog = false;
    },

    /**
     * Initialise la configuration du tableau générique.
     *
     * 1. Copie la configuration reçue en props et initialise certains champs (loaded, stores).
     * 2. Si un store est défini, récupère sa configuration depuis le store Vuex :
     *    - Active le mode serveur si nécessaire.
     *    - Définit les champs d'identifiant et d'affichage.
     *    - Fusionne les options du store avec celles du composant.
     *    - Définit la méthode de suppression d'une ligne.
     *    - Ajoute le store à la liste des stores utilisés.
     *    - Ajoute la définition de la colonne "actions" si elle n'existe pas (édition, suppression).
     * 3. Construit la liste des headers du tableau à partir de headerDefs :
     *    - Pour chaque header, adapte l'affichage selon le type (ex : date, store lié).
     *    - Pour les headers liés à un store, définit la méthode d'affichage et de tri.
     *    - Filtre les headers selon leur condition d'affichage.
     * 4. Place la colonne "actions" en début de tableau si elle existe.
     * 5. Définit les classes CSS du tableau selon la configuration.
     * 6. Précharge les données nécessaires via les stores associés :
     *    - Construit les options de recherche et de tri pour chaque store.
     *    - Lance les requêtes asynchrones pour récupérer les données.
     * 7. Si certains headers ont une méthode de pré-traitement, l'applique sur les données chargées.
     * 8. Met à jour la configuration finale du tableau et lance le chargement des données.
     */
    initConfig() {
      const config = copy(this.config);
      config.loaded = false;
      config.stores = {};

      if (config.storeName) {
        const configStore = this.$store.getters.configStore(config.storeName);
        config.serverSide = configStore.serverSide;
        config.idFieldName = configStore.idFieldName;
        this.options = {
          ...this.options,
          ...(configStore.options || {}),
        };
        config.displayFieldName = config.displayFieldName || configStore.displayFieldName;
        config.delete = (id, { $store }) => {
          return $store.dispatch(configStore.delete, { value: id });
        };
        config.stores.items = config.storeName;
        if (!config.headerDefs.actions) {
          config.headerDefs.actions = {
            noSearch: true,
            width: '90px',
            text: 'Actions',
            sortable: false,
            edit: config.configForm,
            list: [
              {
                title: 'Editer la ligne',
                icon: 'mdi-pencil',
                click: (id) => this.edit('actions', id),
              },
              {
                title: 'Supprimer la ligne',
                icon: 'mdi-trash-can',
                click: (id) => {
                  if (!this.deleteWithoutWarning) {
                    this.idToDelete = id;
                    this.deleteModal = true;
                  } else {
                    this.deleteRow(id);
                  }
                },
              },
            ],
          };
        }
      }

      /** contruction de la variable header */
      const headers = [];

      for (const [value, headerDef] of Object.entries(config.headerDefs)) {
        // copie superficielle : config.headerDefs vient d'une prop, la muter directement échoue
        // silencieusement en Vue 3 (proxy readonly)
        const header = { ...headerDef, value };
        // Vuetify 3 lit "title" pour le libellé de colonne (au lieu de "text" en Vuetify 2) ;
        // toutes les configs de tableau du projet utilisent encore "text", donc pont de compat ici
        // plutôt que de renommer "text" en "title" dans chaque fichier de config.
        header.title = header.title ?? header.text;

        // le tri ne fonctionne pas correctement à cause du format de la date. On récupère maintenant le bon format en bdd et on modifie l'affiche avec la fonction display dans le fichier de config de la table
        //  if (header.type == 'date') {
        //   sortDate; // apparemment inutilisé
        //   header.display = (a) =>
        //     a && a[header.value] && a[header.value].includes('-')
        //       ? a[header.value].split('-').reverse().join('/')
        //       : a[header.value];
        // }

        if (header.storeName) {
          const configStore = this.$store.getters.configStore(header.storeName);
          header.displayFieldName = header.displayFieldName || configStore.displayFieldName;

          /** test pour ne pas avoir deux fois le même store name */
          if (!Object.values(config.stores).includes(header.storeName)) {
            // config.stores[value] = header.storeName;
          }
          if (header.displayFieldName) {
            // on change ça
            header.display = (d) => {
              if (!d) {
                return '';
              }

              // case secteur.nom_secteur
              const displayFieldNames = header.displayFieldName.split('.');

              let inter = d[header.value];
              if (!inter) {
                return '';
              }
              return displayFieldNames.map((key) => inter[key]).join(' ');
            };
          }
          header.sort = (a, b) => {
            const aa = header.display ? header.display(a, { $store: this.$store }) : a;
            const bb = header.display ? header.display(b, { $store: this.$store }) : b;
            return aa == bb ? 0 : aa < bb ? -1 : 1;
          };
        }
        if (!header.condition || header.condition({ $store: this.$store })) {
          headers.push(header);
        }
      }

      /** on place actions en début de liste */
      const headerActionsIndex = headers.findIndex((h) => h.value === 'actions');
      if (headerActionsIndex != -1) {
        const headerActions = headers[headerActionsIndex];
        headers.splice(headerActionsIndex, 1);
        headers.unshift(headerActions);
      }

      config.headers = headers;

      config.classes = {
        'small-table': config.small,
        striped: config.striped,
      };

      /** preloadData with promises from storeNames */
      if (Object.keys(config.stores).length) {
        config.preloadData = ({ $store }) => {
          const promises = [];
          for (const storeName of Object.values(config.stores)) {
            const configStore = this.$store.getters.configStore(storeName);

            // on ajoute __like apres les clés de filtres
            // pour pouvoir filtrer en ilike ensuite
            const searchOptions = {};
            for (const [keySearch, valueSearch] of Object.entries(this.searchs || {})) {
              const header = this.configTable.headers.find((h) => h.value === keySearch);
              let key = header.displayFieldName
                ? `${keySearch}.${header.displayFieldName}`
                : keySearch;
              searchOptions[`${key}__ilike`] = valueSearch;
            }

            // on change les clé de tri pour les storeName
            const sortBy = [...this.options.sortBy];
            for (const [index, keySort] of this.options.sortBy.entries()) {
              const header = this.configTable.headers.find((h) => h.value === keySort);
              if (header.displayFieldName) {
                sortBy[index] = `${this.options.sortBy[index]}.${header.displayFieldName}`;
              }
            }

            // construction de l'objet options. Si serverSide est true, on ne stocke pas les données en cache
            // et on ajoute les options de recherche et de tri
            const options =
              storeName == config.storeName && configStore.serverSide
                ? {
                    ...this.options,
                    notCommit: true,
                    ...searchOptions,
                    sortBy,
                    serverSide: true,
                  }
                : {};

            promises.push($store.dispatch(configStore.getAll, options));
          }
          return Promise.all(promises);
        };
      }

      /** preProcess from headerDefs */
      if (config.headers.some((h) => h.preProcess)) {
        config.preProcess = ({ data }) => {
          return data.map((d) => {
            for (const header of this.configTable.headers.filter((h) => h.preProcess)) {
              d[header.value] = header.preProcess(d);
            }
            return d;
          });
        };
      }

      this.configTable = config;
      this.loadData(this.configTable.loaded);
    },

    /**
     * Charge les données pour le tableau générique.
     *
     * Cette méthode vérifie si une fonction de préchargement des données (`preloadData`) est définie dans la configuration du tableau
     * et si les données n'ont pas déjà été chargées (`!loaded`). Si c'est le cas, elle appelle `preloadData` en passant le store Vuex.
     *
     * Une fois les données préchargées :
     * - Elle parcourt les clés des stores définis dans la configuration du tableau.
     * - Si la clé est "items", elle extrait les éléments retournés par la promesse.
     *   - Si les éléments contiennent une propriété `items`, elle met à jour le compteur d'éléments filtrés (`itemsServerCount`)
     *     et récupère la liste des items.
     *   - Sinon, elle met à jour le compteur avec la longueur du tableau.
     * - Les items sont ensuite traités par une éventuelle fonction de pré-traitement (`preProcess`) avant d'être assignés à la configuration.
     * - Enfin, la propriété `loaded` du tableau est mise à jour et la configuration est copiée pour forcer la réactivité.
     *
     * En cas d'erreur lors du chargement, le message d'erreur et le flag d'erreur sont mis à jour.
     */
    loadData(loaded) {
      /** call preloadData */
      if (this.configTable.preloadData && !loaded) {
        this.configTable.preloadData({ $store: this.$store }).then(
          (res) => {
            for (const [index, key] of Object.keys(this.configTable.stores).entries()) {
              if (key == 'items') {
                let items = res[index];

                // sortie du
                if (items && items.items) {
                  this.itemsServerCount = items.total_filtered;
                  items = items.items;
                } else if (items) {
                  this.itemsServerCount = items.length;
                }

                if (items) {
                  this.configTable.items = this.configTable.preProcess
                    ? this.configTable.preProcess({ data: items })
                    : items;
                }
              }
            }
            this.configTable.loaded = true;
            this.configTable = copy(this.configTable);
          },
          (error) => {
            this.msgError = error;
            this.bError = true;
          }
        );
      }
    },
  },
  computed: {
    /**
     * Retourne les éléments filtrés en fonction des critères de recherche.
     *
     * Cette méthode parcourt tous les éléments de la table (configTable.items)
     * et applique les filtres de recherche définis dans l'objet 'searchs' pour chaque colonne.
     *
     * Pour chaque élément :
     *  - On initialise une variable 'cond' à true, qui déterminera si l'élément passe tous les filtres.
     *  - On parcourt chaque colonne (header) de la table :
     *      - Si un critère de recherche existe pour cette colonne, on récupère la valeur à afficher :
     *          - Si la colonne possède une fonction 'display', on l'utilise pour obtenir la valeur affichée.
     *          - Sinon, on prend la valeur brute de l'élément pour cette colonne.
     *      - On vérifie si la valeur affichée contient le texte recherché (insensible à la casse).
     *      - Si le filtrage est côté serveur (serverSide), on ignore le filtre local.
     *  - Si l'élément satisfait tous les critères de recherche, on l'ajoute au tableau 'filteredItems'.
     *
     * La méthode retourne le tableau des éléments filtrés.
     */
    filteredItems() {
      if (!this.configTable.items) {
        return [];
      }
      const filteredItems = [];
      for (const item of this.configTable.items) {
        var cond = true;
        for (const header of this.configTable.headers) {
          const search = this.searchs[header.value];
          if (!search) {
            continue;
          }

          const val = header.display
            ? header.display(item, { $store: this.$store })
            : item[header.value];
          cond =
            this.configTable.serverSide ||
            (cond && String(val).toLowerCase().includes(search.toLowerCase()));
        }
        if (cond) {
          filteredItems.push(item);
        }
      }
      return filteredItems;
    },
  },
  mounted() {
    this.initConfig();
  },
};
</script>
