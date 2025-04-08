

<template>
  <!-- formulaire de modification de page -->

  <div >
    <h2>affichage formAttribution</h2>
  </div>
</template>

<script>
import dynamicForm from "./dynamic-form.vue";
// import help from "./help";

export default {
  name: "formRealisation",
  components: {
    //dynamicForm,
    // help
  },
  data: () => ({}),
  props: ["config", "baseModel", "depthIn"],
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
    }
  },
  methods: {
    computeDisplayGroup(config) {
      return (
        !config.condition ||
        config.condition({ baseModel: this.baseModel, $store: this.$store })
      );
    },

    // renvoie la liste des formulaires filtrée par condition
    computeFormList(config) {
      // si config.forms n'est pas défini, on prend tous les form de formDefs
      const forms =
        config.forms ||
        (!config.groups && Object.keys(config.formDefs || {})) ||
        [];

      return forms
        .filter(keyForm => {
          const formDef = config.formDefs[keyForm];
          return (
            !formDef.condition ||
            formDef.condition({
              baseModel: this.baseModel,
              $store: this.$store
            })
          );
        })
        .map(keyForm => {
          const formDef = config.formDefs[keyForm];
          return {
            ...formDef,
            formDefs: config.formDefs,
            name: keyForm,
            displayValue: this.config.displayValue,
            displayLabel: this.config.displayLabel
          };
        });
    },

    // renvoie la liste des groupes
    computeGroupList(config) {
      return (config.groups || []).map(group => ({
        ...group,
        formDefs: config.formDefs,
        displayLabel: this.config.displayLabel,
        displayValue: this.config.displayValue
      }));
    },

    // renvoie si la config possède au moins un formulaire
    computeHasForms(config) {
      if (config.forms) {
        return this.computeFormList(config).length;
      }
      if (this.config.groups) {
        return this.config.groups.some(group => this.computeHasForms(group));
      }
    }
  }
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
