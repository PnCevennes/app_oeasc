<!-- Formulaire de modification de page. Structure globale avec les boutons d'action
 le contenu du formulaire est plutot dans dynamic-form-group-->
<!-- est appelé dans content/content.vue -->

<template>
  <div
    v-if="config"
    class="form-container"
  >
    <div
      class="debug"
      v-if="debug && Object.keys(debug).length"
    >
      <h3>Debug</h3>
      <pre>{{ debug }}</pre>
    </div>
    <h2 v-if="title">{{ title }}</h2>
    <div v-if="bRequestSuccess">
      <slot name="success"></slot>
    </div>
    <div v-else-if="baseModel">
      <slot name="prependForm"></slot>
      <v-form
        v-model="bValidForm"
        ref="form"
        v-if="bInit"
      >
        <div>
          <dynamic-form-group
            :config="configDynamicGroupForm"
            :baseModel="baseModel"
          ></dynamic-form-group>
          <div>
            <span style="color: red">*</span>
            <i>champs obligatoires.</i>
          </div>
        </div>

        <template v-if="!displayValue">
          <v-btn
            v-if="config.action"
            absolute
            right
            ref="btn-valid-form"
            color="success"
            @click="processAction()"
            :disabled="bSending || baseModel.freeze"
          >
            {{ config.action.label || 'Valider' }}
          </v-btn>
        </template>

        <v-btn
          v-if="switchDisplay"
          color="primary"
          @click="processAnnulerModifier()"
        >
          {{ displayValue ? 'Modifier' : 'Annuler' }}
        </v-btn>

        <v-btn
          v-if="config.cancel"
          color="primary"
          @click="config.cancel.action({ baseModel })"
        >
          Annuler
        </v-btn>

        <v-progress-linear
          indeterminate
          color="green"
          v-if="bSending"
        ></v-progress-linear>

        <slot name="appendForm"></slot>
      </v-form>
    </div>
    <v-snackbar
      color="error"
      v-model="bError"
      :timeout="5000"
    >
      {{ msgError }}
    </v-snackbar>
    <v-snackbar
      color="success"
      v-model="bSuccess"
      :timeout="2000"
    >
      {{ msgSuccess }}
    </v-snackbar>
  </div>
</template>

<script>
import { apiRequest } from '@/core/js/data/api.js';
import dynamicFormGroup from '@/components/form/dynamic-form-group.vue';
import { config as globalConfig } from '@/config/config.js';
import { copy } from '@/core/js/util/util.js';

export default {
  name: 'generic-form',
  components: {
    dynamicFormGroup,
  },
  props: ['config'],
  computed: {
    idModel() {
      return (
        (this.baseModel && this.baseModel[this.config.idFieldName]) ||
        (this.config.value && this.config.value[this.config.idFieldName])
      );
    },

    configDynamicGroupForm() {
      return {
        groups: this.config.groups,
        forms: this.config.forms,
        formDefs: this.config.formDefs,
        displayValue: this.displayValue,
        displayLabel: this.config.displayLabel,
      };
    },
    method() {
      return typeof this.config.action.request.method === 'function'
        ? this.config.action.request.method({ id: this.idModel })
        : this.config.action.request.method;
    },
    debug() {
      const debug = {};
      for (const key of this.config.debug || []) {
        let val;
        for (const subkey of key.split('.')) {
          val = val == undefined ? (this.baseModel || {})[subkey] : val[subkey];
        }
        debug[key] = val;
      }
      return debug;
    },
    url() {
      return typeof this.config.action.request.url === 'function'
        ? this.config.action.request.url({ id: this.idModel })
        : this.config.action.request.url;
    },
    switchDisplay() {
      return typeof this.config.switchDisplay == 'function'
        ? this.config.switchDisplay({ id: this.idModel })
        : this.config.switchDisplay;
    },
    title() {
      return typeof this.config.title == 'function'
        ? this.config.title({ id: this.idModel })
        : this.config.title;
    },
  },
  watch: {
    config() {
      this.initConfig();
    },
  },
  mounted() {
    this.initConfig();
  },

  methods: {
    /**
     * Gère le clic sur le bouton "Annuler/Modifier".
     *
     * Cette méthode est appelée lorsqu'un utilisateur clique sur le bouton
     * "Annuler/Modifier". Elle permet de basculer entre les modes d'affichage
     * (lecture ou édition du formulaire) et de réinitialiser le modèle de données si nécessaire.
     *
     * Fonctionnement détaillé :
     * - Si le formulaire est en mode édition (displayValue = false), on restaure
     *   le modèle de base (baseModel) à partir de la sauvegarde (baseModelSave).
     *   Cela permet d'annuler toutes les modifications non validées par l'utilisateur.
     * - On inverse la valeur de displayValue pour basculer entre les modes
     *   (affichage des valeurs ou édition du formulaire).
     * - Le setTimeout avec 100ms permet de laisser le temps à l'interface
     *   de se mettre à jour correctement avant d'effectuer la bascule.
     */
    processAnnulerModifier() {
      setTimeout(() => {
        // Si on annule la modification, on restaure le modèle initial
        if (!this.displayValue) {
          this.baseModel = copy(this.baseModelSave);
        }
        // On inverse le mode d'affichage/édition
        this.displayValue = !this.displayValue;
      }, 100);
    },

    /**
     * Initialise la configuration du formulaire générique.
     *
     * Cette méthode prépare le formulaire en fonction de la configuration passée en props.
     * Elle gère notamment l'affichage en mode lecture/édition, l'initialisation des données,
     * la récupération des définitions de formulaire depuis le store, et la préparation des actions.
     *
     * Fonctionnement détaillé :
     * - Détermine le mode d'affichage (lecture ou édition) selon la config.
     * - Si un store est associé (storeName), récupère la configuration du store
     *   et complète la config du formulaire si besoin (formDefs, etc.).
     * - Prépare les méthodes de préchargement des données et d'envoi (process, preProcess).
     * - Si une méthode de préchargement existe, la lance pour récupérer les données
     *   (utile pour l'édition d'un objet existant).
     * - Initialise le modèle de base (baseModel) et active le formulaire (bInit).
     */
    initConfig() {
      // Détermine le mode d'affichage (lecture ou édition)
      this.displayValue =
        typeof this.config.displayValue == 'function'
          ? this.config.displayValue({ id: this.idModel })
          : this.config.displayValue;

      if (!this.config) return;

      // Désactive temporairement le formulaire le temps de l'initialisation
      this.bInit = false;

      // Si un store est associé au formulaire
      const storeName = this.config.storeName;
      if (storeName) {
        // Récupère la configuration du store
        const configStore = this.$store.getters.configStore(storeName);

        // Si les définitions de formulaire ne sont pas présentes, les récupère depuis le store
        if (!this.config.formDefs) {
          for (const [key, value] of Object.entries(configStore.configForm)) {
            this.config[key] = value;
          }
        }

        // Prépare la méthode de préchargement des données (pour édition d'un objet existant)
        this.config.preloadData = ({ $store, id, config }) => {
          return new Promise((resolve) => {
            if (!id) {
              // Si pas d'id, rien à précharger
              resolve();
            } else {
              // Récupère les données depuis le store
              $store.dispatch(configStore.get, { value: id }).then((data) => {
                config.value = data;
                this.baseModel = null;
                resolve();
              });
            }
          });
        };

        // Définit le nom du champ identifiant si absent
        this.config.idFieldName = this.config.idFieldName || configStore.idFieldName;

        // Prépare l'action d'envoi (process) selon si on crée ou modifie (post/patch)
        this.config.action = this.config.action || {};
        this.config.action.process = ({ id, $store, postData }) => {
          return $store.dispatch(id ? configStore.patch : configStore.post, {
            value: id,
            postData,
          });
        };

        // Prépare la méthode de prétraitement des données avant envoi
        this.config.action.preProcess = configStore.preProcess;
      }

      // Si une méthode de préchargement existe, la lance pour récupérer les données
      if (
        this.config.preloadData
        //  && !this.config.value
      ) {
        this.config
          .preloadData({
            $store: this.$store,
            config: this.config,
            id: this.idModel,
          })
          .then(() => {
            // Réinitialise le modèle de base
            this.baseModel = null;

            // Initialise le modèle de base à partir des données récupérées
            this.initBaseModel();
            // Active le formulaire
            this.bInit = true;
          });
      } else {
        // Si pas de préchargement, initialise directement le modèle de base
        this.initBaseModel();
        this.bInit = true;
      }
    },

    /**
     * Initialise le modèle de base du formulaire.
     * Cette méthode prépare l'objet `baseModel` qui servira à stocker les valeurs des champs du formulaire,
     * en tenant compte de la configuration (`config.formDefs`) et des valeurs existantes (`config.value`).
     */
    initBaseModel() {
      const baseModel = this.config.value || {};
      const value = this.config.value || {};

      for (const [keyForm, formDef] of Object.entries(this.config.formDefs)) {
        baseModel[keyForm] =
          value[keyForm] != undefined ? value[keyForm] : formDef.multiple ? [] : null;
      }
      baseModel.freeze = false;
      this.baseModel = baseModel;
      this.baseModelSave = copy(baseModel);
    },

    /**
     * Prépare les données à envoyer lors de la soumission du formulaire.
     * Si une fonction de prétraitement (preProcess) est définie dans la configuration d'action,
     * elle est utilisée pour transformer les données du modèle de base avant l'envoi.
     * Sinon, le modèle de base est envoyé tel quel.
     *
     * @returns {Object} Données prêtes à être envoyées à l'API ou au store.
     */
    postData() {
      return this.config.action.preProcess
        ? this.config.action.preProcess({
            baseModel: this.baseModel,
            globalConfig,
            config: this.config,
          })
        : this.baseModel;
    },

    /**
     * Gère la soumission du formulaire lors du clic sur le bouton d'action principal.
     *
     * Fonctionnement détaillé :
     * - Valide le formulaire via la méthode validate() de Vuetify.
     * - Si le formulaire n'est pas valide, la fonction s'arrête.
     * - Prépare la promesse de requête selon la configuration :
     *   - Si une requête API est définie (config.action.request), utilise la méthode request().
     *   - Sinon, utilise la méthode process du store si elle existe.
     * - Si aucune promesse n'est générée, déclenche l'événement "onSuccess" avec les données à envoyer.
     * - Active l'indicateur d'envoi (bSending).
     * - Vérifie s'il existe des stores à mettre à jour (cas des combobox avec returnObject).
     *   - Pour chaque champ concerné, si une valeur n'a pas d'identifiant, ajoute le store à la liste à mettre à jour.
     * - Exécute la promesse :
     *   - En cas de succès :
     *     - Désactive l'indicateur d'envoi.
     *     - Déclenche l'événement "onSuccess" avec les données retournées.
     *     - Affiche un message de succès si le formulaire n'est pas enchaîné (bChained).
     *     - Exécute la fonction onSuccess personnalisée si elle existe dans la config.
     *     - Met à jour les stores concernés via commit.
     *     - Si le mode switchDisplay est actif, repasse en mode affichage des valeurs.
     *     - Sinon, affiche le slot de succès si le formulaire n'est pas enchaîné.
     *   - En cas d'erreur :
     *     - Désactive l'indicateur d'envoi.
     *     - Affiche un message d'erreur dans le snackbar.
     */
    processAction() {
      setTimeout(() => {
        // Validation du formulaire
        this.bValidForm = this.$refs.form.validate();
        if (!this.bValidForm) {
          return;
        }

        // Préparation de la promesse selon la config
        let promise = this.config.action.request
          ? this.request()
          : this.config.action.process &&
            this.config.action.process({
              postData: this.postData(),
              $store: this.$store,
              $router: this.$router,
              config: this.config,
              id: this.idModel,
            });

        // Si aucune promesse, on déclenche l'événement de succès et on quitte
        if (!promise) {
          this.$emit('onSuccess', this.postData());
          return;
        }

        this.bSending = true;

        // Vérification des stores à mettre à jour (cas des combobox avec returnObject)
        const updateStores = [];
        for (const [key, formDef] of Object.entries(this.config.formDefs)) {
          if (
            formDef.storeName &&
            formDef.returnObject &&
            formDef.list_type == 'combobox' // uniquement pour les combobox avec returnObject
          ) {
            let values = this.baseModel[key];
            values = formDef.multiple ? values : [values];
            const configStore = this.$store.getters.configStore(formDef.storeName);
            const idFieldName = configStore.idFieldName;
            const condReload = values.some((v) => v && !v[idFieldName]);
            if (condReload) {
              updateStores.push({ storeName: formDef.storeName, key });
            }
          }
        }

        // Exécution de la promesse (requête ou action store)
        promise.then(
          (data) => {
            this.bSending = false;
            this.$emit('onSuccess', data);

            // Affichage du message de succès si le formulaire n'est pas enchaîné
            if (!this.config.bChained) {
              this.bSuccess = true;
              this.msgSuccess = 'La requête à été effectuée avec succès';
            }

            // Exécution de la fonction personnalisée onSuccess si définie
            if (this.config.action.onSuccess) {
              this.config.action.onSuccess({
                data,
                $session: this.$session,
                $store: this.$store,
                $router: this.$router,
                $route: this.$route,
                id: this.idModel,
              });
            }

            // Mise à jour des stores concernés
            for (const updateStore of updateStores) {
              let values = this.baseModel[updateStore.key];
              values = this.config.formDefs[updateStore.key].multiple ? values : [values];
              const configStore = this.$store.getters.configStore(updateStore.storeName);
              this.$store.commit(configStore.storeNames, values);
            }

            // Gestion du mode d'affichage après succès
            if (this.switchDisplay) {
              this.displayValue = true;
            } else if (!this.config.bChained) {
              this.bRequestSuccess = true;
            }
          },
          (error) => {
            this.bSending = false;
            this.bError = true;
            this.msgError = `Erreur avec la requête : ${error.msg}`;
          }
        );
      }, 100);
    },

    /**
     * Met à jour le modèle de base du formulaire (`baseModel`) avec de nouvelles valeurs.
     *
     * Cette méthode permet de modifier dynamiquement les champs du modèle de base en fonction
     * d'un objet passé en paramètre. Elle est utile pour synchroniser le modèle avec des données
     * externes ou des modifications partielles.
     *
     * Fonctionnement détaillé :
     * - Utilise un `setTimeout` de 100ms pour laisser le temps à l'interface de se mettre à jour.
     * - À l'intérieur du timeout, utilise `$nextTick` pour s'assurer que la modification du DOM est terminée.
     * - Vérifie que `baseModel` existe avant de procéder.
     * - Parcourt chaque clé/valeur de l'objet `baseModel` passé en paramètre.
     * - Met à jour la valeur correspondante dans le modèle de base du composant.
     *
     * @param {Object} baseModel - Objet contenant les nouvelles valeurs à appliquer au modèle de base.
     */
    updateBaseModel(baseModel) {
      setTimeout(() => {
        this.$nextTick(() => {
          if (this.baseModel) {
            for (const [key, value] of Object.entries(baseModel || {})) {
              this.baseModel[key] = value;
            }
          }
        });
      }, 100);
    },

    /**
     * Retourne le modèle de base du formulaire.
     *
     * Cette méthode permet d'accéder au modèle de base utilisé par le formulaire,
     * utile pour récupérer les données saisies ou modifiées par l'utilisateur.
     *
     * @returns {Object} Le modèle de base du formulaire.
     */
    getBaseModel() {
      return this.baseModel;
    },

    /**
     * Effectue une requête API en utilisant la méthode et l'URL définies dans la configuration.
     *
     * Cette méthode est utilisée pour envoyer des données au serveur ou récupérer des informations
     * via une requête HTTP. Elle utilise la fonction `apiRequest` pour gérer la requête.
     *
     * @returns {Promise} La promesse de la requête API.
     */
    request() {
      return apiRequest(
        this.method,
        this.url,
        {
          postData: this.postData(),
        },
        this.$store
      );
    },
  },
  data: () => ({
    bValidForm: null, // Indique si le formulaire est valide (utilisé par Vuetify)
    bInit: false, // Indique si le formulaire est initialisé et prêt à être affiché
    baseModel: null, // Modèle de base contenant les valeurs des champs du formulaire
    baseModelSave: null, // Sauvegarde du modèle de base pour annuler les modifications
    msgError: null, // Message d'erreur à afficher dans le snackbar
    bError: false, // Indique si une erreur est survenue (affiche le snackbar d'erreur)
    msgSuccess: null, // Message de succès à afficher dans le snackbar
    bSuccess: false, // Indique si l'action a réussi (affiche le snackbar de succès)
    bRequestSuccess: false, // Indique si la requête a été effectuée avec succès (affiche le slot de succès)
    bSending: false, // Indique si une requête est en cours d'envoi (affiche le loader)
    recompConfig: true, // Permet de forcer la recompilation de la config si besoin
    displayValue: null, // Indique si le formulaire est en mode affichage des valeurs (lecture) ou édition
  }),
};
</script>

<style>
.form-container {
  min-width: 800px;
  position: relative;
}
.debug {
  font-style: italic;
  background-color: lightgray;
}
</style>
