<!--
    Formulaire pour choisir les options des restituions
    - choix des paramètres (placés dans settings)
    - création d'une liste de filtres
      - le choix des filtres est placé dans le dictionnaire : settings.filters
-->

<template>
  <div>
    <div v-if="configFormRestition">

      <!-- choix des paramètres -->
      <dynamic-form-group
        :config="configFormRestition"
        :baseModel="settings"
      ></dynamic-form-group>

      <!-- choix des filtres -->
      <div class="filters" v-for="filter of filterForms" :key="filter.name">
        <dynamic-form
          :config="filter"
          :baseModel="settings.filters"
        ></dynamic-form>
      </div>
    </div>
  </div>
</template>

<script>

import dynamicFormGroup from "@/components/form/dynamic-form-group";
import dynamicForm from "@/components/form/dynamic-form";
import configFormRestition from "./config/form-restitution.js"; // definition du formulaire
import restitutions from "./config/restitutions"; // dictionaires contenant les options des restituions pour chaque type de donnée (dataType)


export default {
  name: "restitution-form",
  components: { dynamicFormGroup, dynamicForm },
  props: ["dataType"],
  watch: {
    settings: {
      deep: true,
      handler() {
        this.emitSettings();
      }
    }
  },
  data: () => ({
    filterForms: [],
    settings: {},
    configFormRestition: null,
    restitution: null,
    n: 0
  }),
  mounted() {
    this.initConfig();
  },
  methods: {
    /**
     * gère la configuration du formulaire
     */
    initConfig() {

      // configuration de la restitution en fonction du type de données
      this.restitution = restitutions[this.dataType];

      // on donne à settings des valeurs par defaut (si définies)
      this.settings = this.restitution.default || {dataType: this.dataType};

      // on initialise settings.filters (si non défini dans default)
      this.settings.filters = this.settings.filters || {};

      // chaque changement dans le formulaire entraine un emmitSettings
      for (const formDef of Object.values(configFormRestition.formDefs)) {
        formDef.change = () => {
          this.emitSettings()
        }; // ideal newChange
      }


      // items pour les choix de fieldName et filterList
      const items = Object.keys(this.restitution.items)
      .map(name => ({
        text: this.restitution.items[name].text,
        value: name
      }));
      for (const keyForm of ["fieldName", "filterList"]) {
        configFormRestition.formDefs[keyForm].items = items;
      }

      // action quand on change filterList
      configFormRestition.formDefs.filterList.change = this.filterSelectChange;

      this.configFormRestition = configFormRestition;

      // gère la liste des filtres
      this.processFilterForms();

      this.emitSettings();
    },

    /**
     * gère la liste des definitions des composants filtres
     */
    processFilterForms() {
        this.filterForms = (this.settings.filterList || [])
        .map(name => {
            return {
              type: "list_form",
              name,
              label: `Filtre : ${this.restitution.items[name].text}`,
              list_type: "autocomplete",
              multiple: true,
              url: 'api/resultat/custom/',
              params: {
                fieldName: name,
                dataType: this.settings.dataType,
              },
              change: () => {
                  this.filterFormsChange();
              }
        };
      });
    },

    /**
     * action effectuée lors d'un changement dans les formulaire de la liste de filtre
     */
    filterFormsChange() {
      this.n = this.n + 1;
      this.emitSettings();
    },

    /**
     * action effectuée quand on ajoute ou l'on retire un filtre de la liste
     */
    filterSelectChange() {

      this.processFilterForms();
      this.n = this.n + 1;

      // test pour savoir si un filtre à été retiré
      for (const key of Object.keys({ ...this.settings.filters })) {
        if (!this.settings.filterList.includes(key)) {
          delete this.settings.filters[key];
        }
      }
      setTimeout(() => {
        this.emitSettings();
      }, 100);
    },

    options() {
      return JSON.parse(JSON.stringify(this.settings));
    },

    /**
     * Output : pour faire passer 'settings' aux composants parents
     */
    emitSettings() {
      const settings = this.options();
      settings.n = this.n;
      this.$emit("updateSettings", settings);
    }
  }
};
</script>
