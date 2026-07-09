<template>
  <!-- formulaire de modification de page
  dynamic-form est un composant de dynamic-form-group qui lui meme est un composant de generic-form.vue.
  -->

  <div v-if="displayGroup">
    <div>
      <!-- titre -->

      <h2 v-if="depth == 0">
        {{ config.title }}
        <help
          :code="`${config.help}`"
          v-if="config.help"
        ></help>
      </h2>

      <h3 v-if="depth == 1">
        {{ config.title }}
        <help
          :code="`${config.help}`"
          v-if="config.help"
        ></help>
      </h3>

      <h4 v-if="depth >= 2">
        {{ config.title }}
        <help
          :code="`${config.help}`"
          v-if="config.help"
        ></help>
      </h4>

      <div>
        <!-- les forms -->

        <!-- represente une ligne -->
        <div v-if="formList && formList.length">
          <template v-if="config.direction === 'row'">
            <v-row dense>
              <v-col
                v-for="(configForm, index) of formList"
                :key="index"
              >
                <dynamic-form
                  :config="configForm"
                  :baseModel="baseModel"
                ></dynamic-form>
              </v-col>
            </v-row>
          </template>

          <!--represente une colonne -->
          <template v-else>
            <v-row
              dense
              v-for="(configForm, index) of formList"
              :key="index"
            >
              <v-col>
                <dynamic-form
                  :config="configForm"
                  :baseModel="baseModel"
                ></dynamic-form>
              </v-col>
            </v-row>
          </template>
        </div>

        <!-- les groupes -->
        <div v-else-if="groupList && groupList.length">
          <template v-if="config.direction === 'row'">
            <v-row dense>
              <v-col
                v-for="(configGroup, index) of groupList"
                :key="index"
              >
                <dynamic-form-group
                  :baseModel="baseModel"
                  :depthIn="depth + 1"
                  :config="configGroup"
                ></dynamic-form-group>
              </v-col>
            </v-row>
          </template>
          <template v-else>
            <v-row
              dense
              v-for="(configGroup, index) of groupList"
              :key="index"
            >
              <v-col>
                <!-- <h3>retest retest</h3> -->
                <dynamic-form-group
                  :baseModel="baseModel"
                  :depthIn="depth + 1"
                  :config="configGroup"
                ></dynamic-form-group>
              </v-col>
            </v-row>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import dynamicForm from '@/components/form/dynamic-form.vue';
import help from './help.vue'; // contenu d'aide inscrit dans la bdd. A remplacer par static help.vue pour un contenu statique

export default {
  compatConfig: { MODE: 3 }, // verrouille les acquis Phase 4 (composant testé sans warning au 2026-07-10)
  name: 'dynamic-form-group',
  components: {
    dynamicForm,
    help,
  },
  data: () => ({}),
  props: ['config', 'baseModel', 'depthIn'],
  computed: {
    depth() {
      return this.depthIn || 0;
    },
    formList() {
      return this.computeFormList(this.config);
    },
    hasForms() {
      return this.computeHasForms(this.config);
    },
    displayGroup() {
      return this.computeDisplayGroup(this.config);
    },
    groupList() {
      return this.computeGroupList(this.config);
    },
  },
  methods: {
    /**
     * Détermine si le groupe doit être affiché en fonction de la présence ou non d'une condition.
     *
     * @param {Object} config - La configuration du groupe, pouvant contenir une propriété "condition".
     * @returns {boolean} - Retourne true si aucune condition n'est définie ou si la condition est satisfaite,
     *                      sinon retourne false.
     *
     * Détails :
     * - Si la propriété "condition" n'existe pas dans la configuration, le groupe est affiché (true).
     * - Si une condition est définie, elle est évaluée en lui passant le baseModel et le $store.
     *   Si la condition retourne true, le groupe est affiché ; sinon, il ne l'est pas.
     */
    computeDisplayGroup(config) {
      return (
        !config.condition || config.condition({ baseModel: this.baseModel, $store: this.$store })
      );
    },

    /**
     * Génère la liste des formulaires à afficher pour un groupe donné.
     *
     * @param {Object} config - La configuration du groupe, pouvant contenir "forms", "groups" et "formDefs".
     * @returns {Array} - Retourne un tableau d'objets de configuration de formulaires filtrés et enrichis.
     *
     * Détails :
     * - Si la propriété "forms" existe dans la configuration, on l'utilise comme liste de formulaires à afficher.
     * - Si "forms" n'est pas défini et qu'il n'y a pas de groupes, on prend tous les formulaires définis dans "formDefs".
     * - Si aucune de ces propriétés n'est présente, on retourne un tableau vide.
     * - Pour chaque formulaire, on vérifie s'il doit être affiché en fonction de sa condition (si elle existe).
     * - On enrichit chaque formulaire avec des propriétés supplémentaires (formDefs, name, displayValue, displayLabel).
     */
    computeFormList(config) {
      // Détermine la liste des formulaires à afficher
      const forms = config.forms || (!config.groups && Object.keys(config.formDefs || {})) || [];

      // Filtre les formulaires selon leur condition et enrichit leur configuration
      return forms
        .filter((keyForm) => {
          const formDef = config.formDefs[keyForm];
          // Affiche le formulaire si aucune condition ou si la condition est satisfaite
          return (
            !formDef.condition ||
            formDef.condition({
              baseModel: this.baseModel,
              $store: this.$store,
            })
          );
        })
        .map((keyForm) => {
          const formDef = config.formDefs[keyForm];
          // Enrichit la configuration du formulaire avec des propriétés utiles
          return {
            ...formDef,
            formDefs: config.formDefs,
            name: keyForm,
            displayValue: this.config.displayValue,
            displayLabel: this.config.displayLabel,
          };
        });
    },

    /**
     * Génère la liste des groupes à afficher pour une configuration donnée.
     *
     * @param {Object} config - La configuration du groupe, pouvant contenir une propriété "groups".
     * @returns {Array} - Retourne un tableau d'objets de configuration de groupes enrichis.
     *
     * Détails :
     * - Si la propriété "groups" existe dans la configuration, on l'utilise comme liste de groupes à afficher.
     * - Pour chaque groupe, on enrichit la configuration avec les propriétés "formDefs", "displayLabel" et "displayValue"
     *   provenant du groupe parent, afin de faciliter l'accès à ces informations dans les groupes enfants.
     * - Si aucune propriété "groups" n'est présente, on retourne un tableau vide.
     */
    computeGroupList(config) {
      return (config.groups || []).map((group) => ({
        ...group,
        formDefs: config.formDefs,
        displayLabel: this.config.displayLabel,
        displayValue: this.config.displayValue,
      }));
    },

    /**
     * Vérifie récursivement si la configuration ou l'un de ses groupes contient au moins un formulaire affichable.
     *
     * @param {Object} config - La configuration à analyser, pouvant contenir des formulaires ou des groupes.
     * @returns {number|boolean|undefined} - Retourne le nombre de formulaires affichables si présents,
     *                                       true si au moins un groupe contient un formulaire affichable,
     *                                       ou undefined si aucun formulaire ni groupe n'est trouvé.
     *
     * Détails :
     * - Si la propriété "forms" existe dans la configuration, on retourne le nombre de formulaires affichables
     *   après filtrage par condition via la méthode computeFormList.
     * - Si la configuration contient des groupes, on vérifie récursivement pour chaque groupe s'il possède
     *   au moins un formulaire affichable.
     * - Si aucun formulaire ni groupe n'est présent, la fonction retourne undefined.
     */
    computeHasForms(config) {
      // Vérifie si la propriété "forms" existe dans la configuration
      if (config.forms) {
        // Retourne le nombre de formulaires affichables (après filtrage par condition)
        return this.computeFormList(config).length;
      }
      // Vérifie si la configuration contient des groupes
      if (this.config.groups) {
        // Parcourt chaque groupe et vérifie récursivement s'il possède au moins un formulaire affichable
        return this.config.groups.some((group) => this.computeHasForms(group));
      }
      // Si aucun formulaire ni groupe, retourne undefined
    },
  },
};
</script>

<style scoped>
.form-group.border {
  border: 1px solid lightgrey;
  border-radius: 10px;
}

.form-group.margin {
  margin: 10px;
}

.form-group.padding {
  padding: 10px;
}
</style>
