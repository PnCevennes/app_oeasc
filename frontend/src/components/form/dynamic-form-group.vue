<template>
  <div v-if="displayGroup">
    <div>
      <!-- titre -->
      <h2 v-if="depth == 0">
        {{ config.title }}
        <help :code="`${config.help}`" v-if="config.help"></help>
      </h2>

      <h3 v-if="depth == 1">
        {{ config.title }}
        <help :code="`${config.help}`" v-if="config.help"></help>
      </h3>

      <h4 v-if="depth >= 2">
        {{ config.title }}
        <help :code="`${config.help}`" v-if="config.help"></help>
      </h4>

      <div>
        <!-- les forms -->
        <div v-if="formList && formList.length">
          <template v-if="config.direction === 'row'">
            <v-row dense>
              <v-col v-for="(configForm, index) of formList" :key="index">
                <dynamic-form
                  :config="configForm"
                  :baseModel="baseModel"
                ></dynamic-form>
              </v-col>
            </v-row>
          </template>
          <template v-else>
            <v-row dense v-for="(configForm, index) of formList" :key="index">
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
              <v-col v-for="(configGroup, index) of groupList" :key="index">
                <dynamic-form-group
                  :baseModel="baseModel"
                  :depthIn="depth + 1"
                  :config="configGroup"
                ></dynamic-form-group>
              </v-col>
            </v-row>
          </template>
          <template v-else>
            <v-row dense v-for="(configGroup, index) of groupList" :key="index">
              <v-col>
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
import dynamicForm from "@/components/form/dynamic-form";
import help from "./help";

export default {
  name: "dynamic-form-group",
  components: {
    dynamicForm,
    help
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
