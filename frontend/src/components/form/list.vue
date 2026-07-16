<template>
  <div>
    <!-- Affiche le label principal si displayValue n'est pas activé -->
    <b v-if="!config.displayValue">{{ config.label }}</b>
    <!-- Ligne d'en-tête du tableau -->
    <v-row dense>
      <!-- Colonne pour les boutons d'action -->
      <v-col class="col-btn"></v-col>
      <!-- Colonnes pour chaque champ du formulaire, sauf ceux cachés -->
      <v-col
        v-for="keyForm of config.forms.filter((keyForm) => !config.formDefs[keyForm].hidden)"
        :key="keyForm"
      >
        <!-- Affiche le label du champ si le champ n'est pas caché -->
        <b v-if="!config.formDefs[keyForm].hidden">{{ config.formDefs[keyForm].label }}</b>
      </v-col>
    </v-row>

    <!-- Affichage des lignes du tableau, une par élément du modèle -->
    <v-row
      dense
      v-for="(lineModel, indexLine) of lines"
      :key="indexLine"
    >
      <!-- Colonne pour le bouton de suppression -->
      <v-col class="col-btn">
        <v-btn
          icon
          color="red"
          @click="deleteItem(indexLine)"
          v-if="!config.displayValue"
        >
          <v-icon>mdi-close-circle</v-icon>
        </v-btn>
      </v-col>

      <!-- Colonnes pour chaque champ du formulaire, sauf ceux cachés -->
      <v-col
        v-for="keyForm of config.forms.filter((keyForm) => !config.formDefs[keyForm].hidden)"
        :key="keyForm"
      >
        <!-- Utilisation du composant dynamic-form pour chaque champ -->
        <dynamic-form
          :config="{
            ...config.formDefs[keyForm],
            name: keyForm,
            change: newChange(config.formDefs[keyForm].change),
            displayValue: config.displayValue,
          }"
          :baseModel="lineModel"
        ></dynamic-form>
      </v-col>
    </v-row>

    <!-- Ligne pour le bouton d'ajout d'un nouvel élément -->
    <v-row dense>
      <v-col class="col-btn">
        <v-btn
          color="green"
          icon
          v-if="!config.displayValue"
        >
          <!-- Bouton d'ajout, désactivé si le formulaire n'est pas valide -->
          <v-icon
            @click="addItem"
            :disabled="!bValidForm"
          >
            mdi-plus-circle
          </v-icon>
        </v-btn>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import { defineAsyncComponent } from 'vue';
import { formFunctions } from '@/components/form/functions/form.js';
export default {
  name: 'list',
  props: ['config', 'baseModel'],
  methods: {
    /**
     * Supprime un élément de la liste à l'index donné.
     * Cette méthode retire l'élément correspondant dans le tableau du modèle de base
     * associé au nom du formulaire (this.config.name).
     * Après la suppression, la propriété 'refresh' est modifiée pour forcer la mise à jour
     * de l'affichage du composant.
     *
     * @param {number} index - L'index de l'élément à supprimer dans la liste.
     */
    deleteItem(index) {
      // Retire l'élément à l'index spécifié du tableau
      this.baseModel[this.config.name].splice(index, 1);
      // Déclenche une mise à jour du composant en modifiant 'refresh'
      this.refresh = !this.refresh;
    },

    /**
     * Ajoute un nouvel élément à la liste.
     * Cette méthode crée un nouvel objet modèle basé sur la configuration par défaut
     * (this.config.default) et l'ajoute au tableau du modèle de base associé au nom du formulaire.
     * Après l'ajout, la propriété 'refresh' est modifiée pour forcer la mise à jour
     * de l'affichage du composant.
     */
    addItem() {
      // Crée un nouveau modèle de ligne à partir de la configuration par défaut
      let lineModel = this.config.default || {};
      // Ajoute le nouveau modèle à la liste du modèle de base
      this.baseModel[this.config.name].push(lineModel);
      // Déclenche une mise à jour du composant en modifiant 'refresh'
      this.refresh = !this.refresh;
    },

    /**
     * Méthode qui retourne une fonction de gestion de changement.
     * Cette fonction prend en paramètre un ancien gestionnaire de changement (oldChange).
     * Lorsqu'elle est appelée, elle inverse la valeur de la propriété 'refresh' du composant,
     * ce qui peut déclencher une mise à jour ou un rechargement de la vue.
     * Ensuite, si un ancien gestionnaire de changement est fourni, il est appelé avec les mêmes paramètres
     * ($store, config, baseModel) pour assurer la continuité du traitement.
     *
     * @param {Function} oldChange - Ancienne fonction de gestion du changement à exécuter après la mise à jour.
     * @returns {Function} Fonction qui gère le changement et appelle éventuellement l'ancien gestionnaire.
     */
    newChange(oldChange) {
      return ({ $store, config, baseModel }) => {
        this.refresh = !this.refresh;
        oldChange && oldChange({ $store, config, baseModel });
      };
    },
  },
  watch: {
    baseModel: {
      handler() {},
    },
  },
  computed: {
    /**
     * Vérifie la validité du formulaire principal.
     *
     * Cette méthode parcourt les définitions de formulaires secondaires (forms) associées à la configuration.
     * Pour chaque formulaire :
     *  - Elle copie la définition du formulaire et ajoute le nom du formulaire.
     *  - Si une condition d'affichage est définie, elle l'évalue avec le modèle de base (baseModel).
     *    Si la condition n'est pas remplie, le formulaire est ignoré.
     *  - Les règles de validation sont récupérées et évaluées si elles sont définies comme fonction.
     *  - Les règles sont ensuite traitées via la fonction utilitaire `formFunctions.rules.processRules`.
     *  - Pour chaque ligne du formulaire principal, elle vérifie si la valeur du champ ne respecte pas au moins une règle.
     *
     * Si au moins une règle n'est pas respectée dans un des formulaires secondaires, la méthode retourne `false`.
     * Sinon, elle retourne `true` pour indiquer que le formulaire est valide.
     *
     * @returns {boolean} - Retourne `true` si le formulaire principal est valide, sinon `false`.
     */
    bValidForm() {
      this.refresh;
      if (!this.baseModel[this.config.name]) return true;
      return !this.config.forms.some((keyForm) => {
        const formDef = { ...this.config.formDefs[keyForm], name: keyForm }; // copy ??
        if (formDef.condition && !formDef.condition({ baseModel: this.baseModel })) return false;
        formDef.rules =
          typeof formDef.rules == 'function'
            ? formDef.rules({ baseModel: this.baseModel })
            : formDef.rules;
        formFunctions.rules.processRules(formDef);

        return this.baseModel[this.config.name].some((line) => {
          const val = line[formDef.name];
          return formDef.rules && formDef.rules.some((rule) => rule(val) != true);
        });
      });
    },

    /**
     * Cette méthode retourne les lignes associées au modèle de base selon la configuration actuelle.
     * Elle appelle la méthode 'refresh' (bien que l'appel semble incorrect ici, il manque les parenthèses pour exécuter la fonction).
     * Ensuite, elle retourne la propriété du modèle de base correspondant au nom spécifié dans la configuration.
     * 'baseModel' est supposé être un objet contenant différentes collections de données.
     * 'config.name' permet d'accéder dynamiquement à la collection souhaitée.Retourne les lignes associées au modèle de base selon la configuration actuelle.
     */
    lines() {
      this.refresh;
      return this.baseModel[this.config.name];
    },

    /**
     * Génère une liste de configurations d'affichage pour chaque élément du modèle de base.
     *
     * Cette méthode parcourt les éléments associés à la clé `config.name` dans l'objet `baseModel`.
     * Pour chaque élément, elle crée un nouvel objet de configuration en copiant les propriétés de `config`,
     * puis en ajoutant ou en modifiant les propriétés suivantes :
     * - `displayValue` : défini à `true` pour indiquer que la valeur doit être affichée.
     * - `display` : défini à `"table"` pour spécifier le type d'affichage.
     * - `value` : contient l'élément courant du modèle de base.
     *
     * @returns {Array<Object>} Un tableau d'objets de configuration pour l'affichage des éléments.
     */
    configDisplays() {
      return (this.baseModel[this.config.name] || []).map((item) => {
        return {
          ...this.config,
          displayValue: true,
          display: 'table',
          value: item,
        };
      });
    },
  },
  components: { dynamicForm: defineAsyncComponent(() => import('./dynamic-form')) },
  data: () => ({
    configForm: null, // Stocke la configuration du formulaire principal
    localModel: {}, // Modèle local pour manipuler les données du formulaire
    refresh: null, // Permet de forcer le rafraîchissement du composant
  }),
  mounted() {
    this.baseModel[this.config.name] = this.baseModel[this.config.name] || [];
  },
};
</script>

<style scoped>
.col-btn {
  max-width: 50px;
}
</style>
