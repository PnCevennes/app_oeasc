<!-- Affiche le formulaire en fonction de sa configuration.
dynamic-form est un composant de dynamic-form-group qui lui meme est un composant de generic-form.vue.
 -->

<template>
  <div
    v-show="!configForm.hidden"
    :ref="config.name"
    class="dynamic-form"
  >
    <template v-if="configForm.displayValue && configForm.displayLabel">
      <b>{{ configForm.label }} :</b>
    </template>

    <!-- test config -->
    <template v-if="!configForm.valid">
      <label>{{ configForm.label }}</label>
      Problème avec la config de form
      {{ config }}
    </template>

    <!-- test cond-->
    <template v-else-if="!configForm.condition"></template>

    <!-- list -->
    <template v-else-if="configForm.type === 'list'">
      <list
        :config="configForm"
        :baseModel="baseModel"
      ></list>
    </template>

    <!-- Boolean radio -->
    <template v-else-if="configForm.type === 'bool_radio'">
      <span v-if="configForm.displayValue">
        <template v-if="baseModel[configForm.name] === true">
          {{ configForm.labels[0] }}
        </template>
        <template v-else-if="baseModel[configForm.name] === false">
          {{ configForm.labels[1] }}
        </template>
        <template v-else>Indéfini</template>
      </span>
      <v-radio-group
        v-else
        v-model="baseModel[configForm.name]"
        :label="configForm.label"
        row
        :rules="configForm.rules"
        @change="configForm.change && configForm.change({ baseModel, config, $store })"
      >
        <span
          v-if="config.required"
          class="required"
        >
          *
        </span>
        <help
          :code="`form-${config.name}`"
          v-if="config.help"
        ></help>

        <v-radio
          :label="configForm.labels[0]"
          :value="true"
        ></v-radio>
        <v-radio
          :label="configForm.labels[1]"
          :value="false"
        ></v-radio>
      </v-radio-group>
    </template>

    <!-- Bolean switch -->
    <template v-else-if="configForm.type === 'bool_switch'">
      <span v-if="configForm.displayValue">
        <template v-if="baseModel[configForm.name] === true">Oui</template>
        <template v-else-if="baseModel[configForm.name] === false">non</template>
        <template v-else>Indéfini</template>
      </span>
      <v-switch
        :id="`form-${config.name}`"
        v-else
        dense
        v-model="baseModel[configForm.name]"
        :label="configForm.label"
        :disabled="configForm.disabled"
        @change="configForm.change && configForm.change({ baseModel, config, $store })"
      ></v-switch>
    </template>

    <!-- text -->
    <template v-else-if="['text', 'number', 'password', 'date', 'email'].includes(configForm.type)">
      <span v-if="configForm.displayValue">{{ baseModel[configForm.name] }}</span>
      <v-text-field
        v-else
        :id="`form-${configForm.name}`"
        :type="
          !show1 && configForm.type === 'password'
            ? 'password'
            : configForm.type == 'date'
              ? configForm.type
              : 'text'
        "
        :append-icon="config.type === 'password' ? (show1 ? 'mdi-eye' : 'mdi-eye-off') : null"
        dense
        v-model="baseModel[configForm.name]"
        :rules="configForm.rules"
        :label="configForm.label"
        :counter="configForm.counter"
        :maxlength="configForm.maxlength"
        :disabled="configForm.disabled"
        @change="inputChange($event)"
      >
        <span slot="label">
          {{ configForm.label }}
          <span
            v-if="configForm.required && config.label"
            class="required"
          >
            *
          </span>
        </span>
        {{ `form-${config.name}` }}

        <span
          slot="append"
          @click="show1 = !!show1"
        >
          <v-btn
            icon
            v-if="config.type === 'password'"
            @click="show1 = !show1"
            tabindex="-1"
          >
            <v-icon>
              {{ config.type === 'password' ? (show1 ? 'mdi-eye' : 'mdi-eye-off') : null }}
            </v-icon>
          </v-btn>
          <help
            tabindex="-1"
            :code="`form-${configForm.name}`"
            v-if="configForm.help"
          ></help>
        </span>
      </v-text-field>
    </template>

    <!-- text area -->
    <template v-else-if="configForm.type === 'text_area'">
      <span v-if="configForm.displayValue">{{ baseModel[configForm.name] }}</span>
      <v-textarea
        v-else
        v-model="baseModel[configForm.name]"
        :label="configForm.label"
        :placeholder="configForm.placeholder"
        :rows="configForm.rows"
      >
        <help
          slot="append"
          :code="`form-${configForm.name}`"
          v-if="configForm.help"
        ></help>
      </v-textarea>
    </template>

    <template v-else-if="configForm.type === 'file'">
      <span v-if="configForm.displayValue">{{ baseModel[configForm.name] }}</span>
      <v-file-input
        v-else
        v-model="baseModel[configForm.name]"
        :label="configForm.label"
        :placeholder="configForm.placeholder"
      >
        <help
          slot="append"
          :code="`form-${configForm.name}`"
          v-if="configForm.help"
        ></help>
      </v-file-input>
    </template>

    <!-- nomenclature -->
    <template v-else-if="configForm.type === 'nomenclature'">
      <nomenclature-form
        :config="configForm"
        :baseModel="baseModel"
      ></nomenclature-form>
    </template>

    <!-- essence -->
    <!-- <template v-else-if="configForm.type === 'essence'">
      <essence-form :config="configForm" :baseModel="baseModel"></essence-form>
    </template> -->

    <!-- select map -->
    <template v-else-if="configForm.type === 'select_map'">
      <select-map
        :config="configForm"
        :baseModel="baseModel"
      ></select-map>
      <!-- <div>##### ConfigForm {{ configForm }}</div> -->
    </template>

    <!-- list form -->
    <template v-else-if="configForm.type === 'list_form'">
      <list-form
        :config="configForm"
        :baseModel="baseModel"
      ></list-form>
    </template>

    <!-- content -->
    <template v-else-if="configForm.type === 'content'">
      <oeasc-content
        :meta="configForm.meta"
        :code="configForm.code"
        :containerClassIn="'content-container-form'"
      ></oeasc-content>
    </template>
    <template v-else-if="configForm.type === 'button'">
      <v-tooltip bottom>
        <template v-slot:activator="{ on }">
          <v-btn
            v-on="on"
            :icon="!!configForm.icon"
            @click="configForm.click({ baseModel })"
          >
            {{ configForm.label }}
            <v-icon v-if="configForm.icon">{{ configForm.icon }}</v-icon>
          </v-btn>
        </template>
        <span>{{ configForm.tooltip }}</span>
      </v-tooltip>
    </template>
  </div>
</template>

<script>
import nomenclatureForm from './nomenclature-form.vue';
import listForm from './list-form.vue';
import selectMap from './select-map.vue';
import help from './help.vue'; // contenu d'aide inscrit dans la bdd. Remplacer après pas static help.vue pour un contenu statique
import list from './list.vue';
import { copy } from '@/core/js/util/util.js';
import { formFunctions } from '@/components/form/functions/form.js';

export default {
  name: 'dynamicForm',

  components: {
    nomenclatureForm,
    selectMap,
    listForm,
    oeascContent: () => import('@/modules/content/content.vue'),
    help,
    list,
  },

  data: () => ({
    show1: false, // Indique si le mot de passe est visible (pour les champs password)
    configTypes: [
      // Liste des types de champs de formulaire pris en charge par le composant
      'input', // Champ de saisie générique
      'bool_radio', // Champ booléen sous forme de boutons radio
      'bool_switch', // Champ booléen sous forme d'interrupteur
      'text', // Champ texte simple
      'email', // Champ de saisie d'email
      'date', // Champ de sélection de date
      'text_area', // Champ de saisie de texte multilignes
      'nomenclature', // Champ de nomenclature (sélection dans une liste de valeurs)
      'number', // Champ de saisie numérique
      'select_map', // Champ de sélection sur une carte
      'essence', // Champ spécifique pour l'essence (commenté dans le template)
      'list_form', // Champ permettant d'afficher un formulaire sous forme de liste
      'degats', // Champ spécifique pour les dégâts (non utilisé ici)
      'content', // Champ affichant du contenu statique ou dynamique
      'password', // Champ de saisie de mot de passe
      'list', // Champ affichant une liste d'éléments
      'button', // Champ affichant un bouton
      'file', // Champ de sélection de fichier
    ],
    configForm: null, // Stocke la configuration résolue du champ de formulaire
  }),

  props: ['config', 'baseModel'],

  // bidouille à voir si on y arrive avec computed
  watch: {
    baseModel: {
      handler() {
        this.configForm = this.getConfigForm();
      },
      deep: true,
    },
    config: {
      handler() {
        this.configForm = this.getConfigForm();
      },
      deep: true,
    },
  },

  methods: {
    /**
     * Gère le changement de valeur d'un champ du formulaire.
     *
     * @param {Event} event - L'événement déclenché lors du changement de valeur.
     *
     * - Pour les champs de type 'number', si la valeur saisie est une chaîne vide,
     *   on la remplace par null afin d'éviter une erreur lors de l'insertion SQL.
     * - Si une fonction 'change' est définie dans la configuration du formulaire,
     *   elle est appelée avec le modèle de base, la configuration et le store.
     */
    inputChange(event) {
      event; // L'événement n'est pas utilisé ici, mais peut servir pour des extensions futures.
      // Vérifie si le champ est de type 'number' et si la valeur est vide
      if (this.configForm.type == 'number' && this.baseModel[this.config.name] == '') {
        // Remplace la valeur vide par null pour éviter les erreurs SQL
        this.baseModel[this.config.name] = null;
      }
      // Appelle la fonction de changement si elle existe dans la configuration
      return (
        this.configForm.change &&
        this.configForm.change({
          baseModel: this.baseModel,
          config: this.config,
          $store: this.$store,
        })
      );
    },

    /**
     * Résout et retourne la configuration finale du formulaire à partir de la configuration passée en props.
     * Cette méthode permet de :
     *  - Fusionner les paramètres de la configuration locale avec ceux du store si nécessaire.
     *  - Résoudre dynamiquement les propriétés qui sont des fonctions (ex : condition, disabled, etc.).
     *  - Copier les autres propriétés pour éviter les effets de bord.
     *  - Vérifier la validité du type de champ.
     *  - Appliquer automatiquement les règles de validation selon le type de champ.
     *  - Initialiser la valeur par défaut si elle existe et n'est pas déjà attribuée.
     *
     * @returns {Object} configResolved - La configuration complète et résolue du champ de formulaire.
     */
    getConfigForm: function () {
      // Initialisation de la configuration résolue avec des valeurs par défaut
      const configResolved = { condition: true, valid: true };

      // Si la configuration possède un storeName, on récupère les paramètres du store
      if (this.config && this.config.storeName) {
        const configStore = this.$store.getters.configStore(this.config.storeName);

        // On complète les propriétés manquantes avec celles du store
        this.config.idFieldName = this.config.idFieldName || configStore.idFieldName;

        this.config.displayFieldName = this.config.displayFieldName || configStore.displayFieldName;
        this.config.api = this.config.api || configStore.apis;
      }

      // Parcours de chaque propriété de la configuration
      for (const key in this.config) {
        if (
          typeof this.config[key] === 'function' &&
          !['change', 'processItems', 'url'].includes(key) // On exclut certaines fonctions spécifiques
        ) {
          // Si la propriété est une fonction, on l'exécute pour obtenir sa valeur dynamique
          configResolved[key] = this.config[key]({
            baseModel: this.baseModel,
            $store: this.$store,
          });
        } else {
          // Sinon, on copie la valeur pour éviter les effets de bord
          configResolved[key] = copy(this.config[key]);
        }
      }

      // Vérifie si le type du champ est valide parmi les types autorisés
      configResolved.valid = this.configTypes.includes(this.config.type);

      // Ajout automatique des règles de validation selon le type de champ
      formFunctions.rules.processRules(configResolved);

      // Si une valeur par défaut existe et n'est pas encore attribuée, on l'initialise
      if (
        configResolved.default &&
        (configResolved.multiple
          ? this.baseModel[this.config.name].length
          : !this.baseModel[this.config.name])
      ) {
        // On gère le cas où la valeur par défaut peut être une Promise
        Promise.resolve(configResolved.default).then((value) => {
          this.baseModel[this.config.name] = value;
        });
      }

      // Retourne la configuration résolue et complète du champ
      return configResolved;
    },
  },

  created: function () {
    this.configForm = this.getConfigForm();
  },
};
</script>

<style scoped>
@import url('./form.css');
</style>
