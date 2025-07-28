<!--
  Composant VueJS pour afficher une liste de choix dans un formulaire.
  Ce composant gère plusieurs types de listes : boutons, combobox, autocomplete, select, checkbox et radio.
  Il utilise les propriétés de configuration passées via "config" pour adapter l'affichage et le comportement.
-->

<template>
  <span>
    <!-- Affiche un message de chargement si les items ne sont pas encore disponibles -->
    <div v-if="!items">{{ info.msg }}</div>

    <!-- Affiche uniquement la valeur sélectionnée si displayValue est activé dans la config -->
    <span v-else-if="config.displayValue">
      <span>{{ valueDisplay }}</span>
    </span>

    <!-- Affichage principal de la liste de choix -->
    <div v-else>
      <div class="list-form">
        <!-- Affichage sous forme de boutons si list_type = 'button' -->
        <div v-if="config.list_type === 'button'">
          <div class="select-list-label">{{ config.label }}</div>
          <v-btn-toggle v-model="baseModel[config.name]" @change="change($event)" dense>
            <v-btn :value="item[config.valueFieldName]" v-for="(item, index) of items" :key="index">
              {{ item[config.displayFieldName] }}
            </v-btn>
          </v-btn-toggle>
        </div>

        <!-- Affichage sous forme de combobox (champ de saisie avec suggestions) -->
        <div v-else-if="config.list_type === 'combobox'">
          <v-combobox ref="autocomplete" :id="`form-${config.name}`" clearable
            v-model="baseModel[config.name]" :items="items" :label="config.label"
            :required="config.required ? true : false" :multiple="config.multiple ? true : false"
            :item-value="config.valueFieldName" :item-text="config.displayFieldName"
            :rules="config.rules" :chips="config.multiple ? true : false" dense
            :small-chips="config.multiple ? true : false"
            :deletable-chips="config.multiple ? true : false" :search-input.sync="search"
            :placeholder="config.placeholder" :filter="config.dataReloadOnSearch && customFilter"
            @change="change($event)" :return-object="config.returnObject ? true : false"
            :disabled="config.disabled" @update:list-index="comboboxUpdateListIndex($event)">
            <!-- Label du champ avec indication si plusieurs réponses sont possibles et si le champ est requis -->
            <span slot="label">
              {{ config.label }}
              <i v-if="config.multiple">(plusieurs réponses possibles)</i>
              <span v-if="config.required" class="required">*</span>
            </span>
          </v-combobox>
        </div>

        <!-- Affichage sous forme d'autocomplete (champ de saisie avec recherche) -->
        <div v-else-if="config.list_type === 'autocomplete'">
          <v-autocomplete ref="autocomplete" :id="`form-${config.name}`" clearable
            v-model="baseModel[config.name]" :items="items" :label="config.label"
            :required="config.required ? true : false" :multiple="config.multiple ? true : false"
            :item-value="config.valueFieldName" :item-text="config.displayFieldName"
            :rules="config.rules" :chips="config.multiple ? true : false" dense
            :small-chips="config.multiple ? true : false"
            :deletable-chips="config.multiple ? true : false" :search-input.sync="search"
            :placeholder="config.placeholder" :filter="config.dataReloadOnSearch && customFilter"
            @change="change($event)" :return-object="config.returnObject ? true : false"
            :disabled="config.disabled" no-data-text="Pas de donnée disponible">
            <span slot="label">
              {{ config.label }}
              <i v-if="config.multiple">(plusieurs réponses possibles)</i>
              <span v-if="config.required" class="required">*</span>
            </span>
            <!-- Affiche l'aide si elle est définie dans la config -->
            <help slot="prepend" :code="`form-${config.name}`" v-if="config.help"></help>
          </v-autocomplete>
        </div>

        <!-- Affichage sous forme de select (liste déroulante) -->
        <div v-else-if="config.list_type === 'select'">
          <v-select :id="`form-${config.name}`" clearable dense v-model="baseModel[config.name]"
            :items="items" :label="config.label" :required="config.required ? true : false"
            :multiple="config.multiple ? true : false" :item-value="config.valueFieldName"
            :item-text="config.displayFieldName" :rules="config.rules"
            :chips="config.multiple ? true : false" :small-chips="config.multiple ? true : false"
            :deletable-chips="config.multiple ? true : false"
            :return-object="config.returnObject ? true : false" :disabled="config.disabled"
            @change="change($event)">
            <span slot="label">
              {{ config.label }}
              <i v-if="config.multiple">(plusieurs réponses possibles)</i>
              <span v-if="config.required" class="required">*</span>
            </span>
            <help slot="prepend" :code="`form-${config.name}`" v-if="config.help"></help>
          </v-select>
        </div>

        <!-- Affichage sous forme de cases à cocher ou boutons radio -->
        <div v-else>
          <!-- Checkbox pour sélection multiple -->
          <div v-if="config.multiple">
            <v-container fluid>
              <div class="select-list-label-container" v-if="!!config.label">
                <span class="select-list-label">{{ config.label }}</span>
                <span v-if="config.required" class="required">*</span>
                <help :code="`form-${config.name}`" v-if="config.help"></help>
                <br />
                <i>(plusieurs réponses possibles)</i>
              </div>
              <!-- Génère une case à cocher pour chaque item -->
              <v-checkbox v-for="(item, index) in items" :key="index"
                v-model="baseModel[config.name]"
                :hide-details="index < items.length - 1 ? true : false" :value="
                  (config.returnObject && item) || item[config.valueFieldName]
                " :label="item[config.displayFieldName]" dense :rules="config.rules"
                :disabled="config.disabled" @change="change($event)"></v-checkbox>
              <!-- Affiche l'aide spécifique à chaque item si définie -->
              <help class="help-radio-item" :code="`item-${item[config.valueFieldName]}`"
                v-if="config.helps"></help>
            </v-container>
          </div>

          <!-- Radio pour sélection unique -->
          <div v-else>
            <v-container fluid>
              <div class="select-list-label-container" v-if="!!config.label">
                <span class="select-list-label">{{ config.label }}</span>
                <span v-if="config.required" class="required">*</span>
                <help :code="`form-${config.name}`" v-if="config.help"></help>
              </div>
              <v-radio-group v-model="baseModel[config.name]" :rules="config.rules">
                <template v-for="item in items">
                  <div :key="item[config.valueFieldName]" style="position: relative">
                    <div class="radio">
                      <v-radio :value="
                        (config.returnObject && item) ||
                          item[config.valueFieldName]
                      " :label="item[config.displayFieldName]" :disabled="config.disabled"
                        @change="change($event)"></v-radio>
                    </div>
                    <!-- Affiche l'aide spécifique à chaque item sauf ceux exclus par la config -->
                    <help class="help-radio-item" :code="`list-${item[config.valueFieldName]}`"
                      v-if="
                        config.helps &&
                          !(
                            config.helps.except &&
                            config.helps.except.includes(item.cd_nomenclature)
                          )
                      "></help>
                  </div>
                </template>
              </v-radio-group>
            </v-container>
          </div>
        </div>
      </div>
    </div>
  </span>
</template>



<script>
import help from "./help.vue";
import { apiRequest } from "@/core/js/data/api.js";

export default {
  name: "lisForm",
  components: { help },
  data: () => ({
    items: null, // Liste des éléments à afficher dans la liste de choix (après traitement et filtrage)
    info: {
      status: "loading", // Statut d'information sur le chargement des données
      msg: "Chargement des données", // Message affiché lors du chargement
      comboBoxIndex: null, // Index de l'élément sélectionné dans le combobox
      comboBoxSelected: null // Objet de l'élément sélectionné dans le combobox
    },
    defaultConfig: {
      valueFieldName: "value", // Nom du champ utilisé pour la valeur des items (par défaut)
      displayFieldName: "text" // Nom du champ utilisé pour l'affichage des items (par défaut)
    },
    search: "", // Texte de recherche saisi par l'utilisateur (pour autocomplete/combobox)
    dataItems: null // Données brutes récupérées avant traitement (API, store, ou config.items)
  }),


  watch: {
    search() {
      if (this.config.dataReloadOnSearch) {
        this.getData();
      }
    },
    baseModel: {
      handler() {

        this.setInitSearch();
      },
      deep: true
    },
    config() {
      this.setDefaultConfig();
    }
  },
  methods: {


    /**
     * Met à jour l'index de la liste sélectionnée dans le combobox.
     * Cette méthode est appelée lors de la sélection d'un élément dans le composant v-combobox.
     * Elle stocke l'index sélectionné dans la propriété comboBoxIndex et l'élément correspondant dans comboBoxSelected.
     * Cela permet ensuite d'utiliser la valeur sélectionnée pour gérer le modèle ou effectuer des traitements spécifiques.
     * @param {Number} event - Index de l'élément sélectionné dans la liste du combobox.
     */
    comboboxUpdateListIndex(event) {
      this.comboBoxIndex = event;
      this.comboBoxSelected = this.items[event];
    },

    /**
     * Méthode appelée lors d'un changement de valeur dans la liste.
     * Elle gère la mise à jour du modèle selon le type de liste et les options de configuration.
     * Pour les listes de type combobox avec returnObject, elle transforme les chaînes en objets selon les champs configurés.
     * Elle évite les doublons dans la sélection et déclenche la fonction de changement personnalisée si définie dans la config.
     * @param {Event} event - L'événement de changement déclenché par le composant.
     */
    change(event) {
      // Pour les listes de type combobox, select ou autocomplete, on déclenche une action pour gérer l'index clearable
      if( ["combobox", "select", "autocomplete"].includes(this.config.list_type)) {
      this.$store.dispatch('setClearableTabIndex', `#form-${this.config.name}`);
      }

      // Cas particulier pour le combobox avec returnObject :
      // Si la valeur sélectionnée est une chaîne, on la transforme en objet avec les bons champs
      if (this.config.list_type == "combobox" && this.config.returnObject) {

      // Si sélection unique et comboBoxSelected existe, on met à jour directement le modèle
      if(!this.config.multiple && this.comboBoxSelected) {
        this.baseModel[this.config.name] = this.comboBoxSelected
      } else {

        // On récupère les valeurs sélectionnées, sous forme de tableau
        let values = this.baseModel[this.config.name];
        values = this.config.multiple ? values : [values];

        // On transforme chaque valeur string en objet, ou on garde l'objet tel quel
        values = values
        .map(value => {
          if (typeof value === "string") {
          const elem = this.items.find(
            item => item[this.config.displayFieldName] == value
          );
          if (elem) {
            return elem;
          }
          // Si aucun élément trouvé, on crée un objet avec la valeur affichée
          const v = {};
          v[this.config.valueFieldName] = null;
          v[this.config.displayFieldName] = value;
          return v;
          }
          return value;
        })
        // On filtre pour éviter les doublons dans la sélection
        .filter((item, pos, self) => {
          const index = self.findIndex(
          e =>
            (e[this.config.valueFieldName] &&
            e[this.config.valueFieldName] ==
              item[this.config.valueFieldName]) ||
            e[this.config.displayFieldName] ==
            item[this.config.displayFieldName]
          );
          return index == pos;
        });
        // Mise à jour du modèle avec la nouvelle sélection
        this.baseModel[this.config.name] = this.config.multiple
        ? values
        : values[0];
      }
      }
      // Si une fonction de changement personnalisée est définie dans la config, on l'appelle
      this.config.change &&
      this.config.change({
        baseModel: this.baseModel,
        config: this.config,
        $store: this.$store,
        $event: event
      });
    },


    /**
     * Filtre personnalisé pour les composants de type autocomplete ou combobox.
     * Cette fonction est utilisée pour filtrer les éléments de la liste selon le texte de recherche saisi par l'utilisateur.
     * Actuellement, elle retourne toujours true (aucun filtrage), mais elle peut être adaptée pour effectuer un filtrage plus précis.
     * @param {Object} item - L'élément de la liste à tester.
     * @param {String} queryText - Le texte de recherche saisi par l'utilisateur.
     * @returns {Boolean} true si l'élément doit être affiché, false sinon.
     */
    customFilter(item, queryText) {
      // Ici, aucun filtrage n'est appliqué : tous les éléments sont affichés.
      // Pour personnaliser le filtrage, comparer item[config.displayFieldName] avec queryText.
      item + queryText;
      return true;
    },

    /**
     * Traite et prépare la liste des items à afficher dans le composant.
     * Cette méthode permet d'appliquer une transformation personnalisée sur les données via config.processItems,
     * puis de filtrer les éléments selon les filtres définis dans config.filters.
     * Enfin, elle met à jour la propriété "items" du composant avec la liste finale.
     */
    processItems: function() {
      // Si une fonction de traitement personnalisée est définie dans la config, on l'utilise pour transformer les données.
      // Sinon, on utilise directement les données récupérées (dataItems).
      let items = this.config.processItems
      ? this.config.processItems({
        dataItems: this.dataItems,
        config: this.config,
        baseModel: this.baseModel
        })
      : this.dataItems;

      // Si des filtres sont définis dans la config, on applique un filtrage sur les items.
      // Chaque filtre est une clé avec un tableau de valeurs autorisées.
      if (this.config.filters) {
      items = items.filter(elem =>
        Object.entries(this.config.filters).every(([key, values]) => {
        // On vérifie que la valeur de chaque clé de l'élément est incluse dans le tableau des valeurs autorisées.
        return values.includes(elem[key]);
        })
      );
      }
      // Mise à jour de la propriété "items" avec la liste filtrée et/ou transformée.
      this.items = items;
    },

    /**
     * Initialise la valeur de recherche pour les composants de type autocomplete ou combobox.
     * Cette méthode vérifie si le champ du formulaire utilise un objet comme valeur (returnObject),
     * et si aucun texte de recherche n'est déjà présent.
     * Si une valeur existe dans le modèle de base (baseModel), elle récupère le champ d'affichage (displayFieldName)
     * et l'utilise pour initialiser le texte de recherche.
     * Cela permet d'afficher correctement la valeur sélectionnée dans le champ de recherche lors du rendu initial.
     */
    setInitSearch() {
      // Récupère la valeur du champ d'affichage à partir du modèle de base
      const value =
      this.baseModel[this.config.name] &&
      this.baseModel[this.config.name][this.config.displayFieldName];

      // Si le composant est un autocomplete ou combobox, utilise un objet comme valeur,
      // qu'aucune recherche n'est en cours et qu'une valeur existe, initialise la recherche
      if (
      ["autocomplete", "combobox"].includes(this.config.list_type) &&
      this.config.returnObject &&
      !this.search &&
      value
      ) {
      this.search = value;
      }
    },

    /**
     * Méthode pour simuler un clic sur le premier chip affiché dans le composant autocomplete.
     * Utile pour déclencher une action ou ouvrir le menu associé au chip sélectionné.
     * La méthode utilise un délai court (setTimeout) pour s'assurer que les chips sont bien rendus dans le DOM
     * avant d'essayer d'accéder à leur élément HTML.
     * Elle récupère la référence du composant autocomplete via $refs, puis cherche les éléments ayant la classe "v-chip".
     * Si au moins un chip est présent, elle déclenche un clic sur le premier chip.
     */
    clickChips() {
      setTimeout(() => {
      const chips =
        this.$refs.autocomplete &&
        this.$refs.autocomplete.$el.getElementsByClassName("v-chip");
      chips && chips.length && chips[0].click();
      }, 10);
    },

    /**
     * Initialise les valeurs par défaut de la configuration du composant.
     * Cette méthode vérifie si une configuration de store est utilisée (storeName),
     * et récupère alors les noms des champs de valeur et d'affichage depuis le store.
     * Elle met à jour la configuration par défaut (defaultConfig) avec ces valeurs si elles ne sont pas déjà définies.
     * Ensuite, elle parcourt chaque clé de la configuration par défaut et l'applique à la config principale
     * si la clé n'est pas déjà présente dans la config passée au composant.
     * Cela garantit que tous les champs nécessaires à l'affichage et au fonctionnement du composant
     * sont correctement initialisés, même si certains paramètres ne sont pas explicitement fournis.
     */
    setDefaultConfig() {
      // Si un store est défini dans la config, on récupère la configuration du store
      if (this.config.storeName) {
      const configStore = this.$store.getters.configStore(
        this.config.storeName
      );
      // On définit le nom du champ valeur par défaut à partir du store si non défini
      this.defaultConfig.valueFieldName =
        this.config.valueFieldName || configStore.idFieldName;
      // On définit le nom du champ d'affichage par défaut à partir du store si non défini
      this.defaultConfig.displayFieldName =
        this.config.displayFieldName || configStore.displayFieldName;
      }

      // Pour chaque clé de la configuration par défaut, on l'applique à la config principale si elle n'est pas définie
      for (const key in this.defaultConfig) {
      this.config[key] = this.config[key] || this.defaultConfig[key];
      }
    },


    /**
     * Récupère les données à afficher dans la liste.
     * Cette méthode gère plusieurs sources de données :
     * - Si les items sont déjà présents et qu'il n'y a pas de rechargement sur la recherche, elle traite directement les items.
     * - Si un store est défini dans la config, elle récupère la configuration du store et lance une requête via le store.
     * - Si une URL est définie dans la config, elle effectue une requête API pour récupérer les données.
     * Les paramètres de tri, de pagination et de recherche sont adaptés selon la configuration.
     * Une fois les données récupérées, elle les traite via processItems.
     * En cas d'erreur, elle met à jour le message d'information.
     */
    getData: function() {
      let promise = null;
      // Si les items sont déjà présents et qu'il n'y a pas de rechargement sur la recherche
      if (this.dataItems && !this.config.dataReloadOnSearch) {
      this.processItems();
      } 
      // Si un store est défini dans la configuration
      else if (this.config.storeName) {
      // Récupération de la configuration du store
      const configStore = this.$store.getters.configStore(
        this.config.storeName
      );
      // Définition du nom du champ valeur et du champ d'affichage
      this.config.valueFieldName =
        this.config.valueFieldName || configStore.idFieldName;
      this.config.displayFieldName =
        this.config.displayFieldName || configStore.displayFieldName;
      // Tri de la colonne d'affichage
      this.config.displayFieldSortDesc =
        this.config.displayFieldSortDesc || false;

      // Préparation des paramètres pour la requête au store
      const params = {
        notCommit: this.config.dataReloadOnSearch,
        sortBy: [this.config.displayFieldName],
        sortDesc: [this.config.displayFieldSortDesc],
        itemsPerPage: this.config.dataReloadOnSearch ? 10 : -1,
        ...this.config.params
      };
      // Ajout du paramètre de recherche si nécessaire
      if (this.config.dataReloadOnSearch && this.search) {
        params[`${this.config.displayFieldName}__ilike`] = this.search || "";
      }
      // Lancement de la requête au store
      promise = this.$store.dispatch(configStore.getAll, params);

      } 
      // Si une URL est définie dans la configuration
      else if (this.config.url) {
      // Construction de l'URL (fonction ou chaîne)
      const url =
        typeof this.config.url === "function"
        ? this.config.url({
          search: this.search || "",
          baseModel: this.baseModel,
          config: this.config
          })
        : this.config.url;
      // Lancement de la requête API
      promise = apiRequest("GET", url, { params: this.config.params || {} });
      }

      // Traitement de la réponse de la requête
      if (promise) {
      promise.then(
        apiData => {
        // Mise à jour des items avec les données reçues
        this.dataItems = apiData.items || apiData;
        this.processItems();
        },
        error => {
        // En cas d'erreur, mise à jour du message d'information
        this.info = {
          status: "error",
          msg: error
        };
        }
      );
      }
    },

    /**
     * Fonction appelée lors d'un changement de valeur dans le composant.
     * Elle est utilisée pour gérer les interactions avec le modèle de données du formulaire.
     * @param {Event} e - L'événement de changement déclenché par le composant.
     */
    autocompleteChange: function(e) {
      e;
    }


  },
  computed: {

    /**
     * Calcule et retourne la valeur affichée pour le champ sélectionné.
     * Cette méthode est utilisée lorsque l'option "displayValue" est activée dans la configuration.
     * Elle récupère la valeur courante du champ dans le modèle de base (baseModel).
     * - Si aucune valeur n'est sélectionnée, elle retourne une chaîne vide.
     * - Si le champ est en mode multiple, elle traite la valeur comme un tableau.
     * - Si les valeurs sont des chaînes, elle les concatène avec une virgule.
     * - Si les valeurs sont des objets, elle filtre les items pour ne garder que ceux sélectionnés,
     *   puis extrait leur champ d'affichage (displayFieldName) et les concatène.
     * Cela permet d'afficher correctement la ou les valeurs sélectionnées, qu'elles soient des chaînes ou des objets.
     * @returns {String} La valeur affichée, concaténée si plusieurs réponses.
     */
    valueDisplay() {
      let values = this.baseModel[this.config.name];
      // Si aucune valeur n'est sélectionnée, retourne une chaîne vide
      if (!(values || (this.config.multiple && values && !values.length))) {
      return "";
      }
      // Si le champ est en mode multiple, traite la valeur comme un tableau
      values = this.config.multiple ? values : [values];

      // Si les valeurs sont des chaînes, les concatène avec une virgule
      if (typeof values[0] == "string") {
      return values.join(", ");
      } else {
      // Si les valeurs sont des objets, filtre les items pour ne garder que ceux sélectionnés
      const textArray = (this.items || [])
        .filter(item => {
        return values.includes(item[this.config.valueFieldName]);
        })
        // Extrait le champ d'affichage et concatène les valeurs
        .map(item => item[this.config.displayFieldName]);
      return textArray.join(", ");
      }
    }

  },
  props: ["config", "baseModel"],
  created() {
    this.setDefaultConfig();
  },
  mounted: function() {


    // Vérifie si la configuration contient déjà une liste d'items
    if (this.config.items) {
      // Si les items sont des chaînes (ex: ["A", "B"]), on les transforme en objets { text, value }
      if (this.config.items.length && typeof this.config.items[0] != "object") {
      this.dataItems = this.config.items.map(item => ({
        text: item,
        value: item
      }));
      } else {
      // Sinon, on utilise directement la liste d'objets fournie
      this.dataItems = this.config.items;
      }
    }
    // Initialise la recherche si besoin (pour autocomplete/combobox)
    this.setInitSearch();

    // Récupère les données à afficher dans la liste (API, store, etc.)
    this.getData();


  } 
};
</script>

<style lang="scss" scoped>
.md-checkbox,
.md-radio {
  display: flex;
}
.radio {
  display: inline-block;
}
</style>
