<template>
  <div>
    <!-- les groupes -->
    <div v-if="groupList && groupList.length">
      <!-- <v-container> -->
      <template v-if="config.direction === 'row'">
        <v-row dense>
          <v-col v-for="(configGroup, index) of groupList" :key="index">
            <dynamic-form-group
              :baseModel="baseModel"
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
              :config="configGroup"
            ></dynamic-form-group>
          </v-col>
        </v-row>
      </template>
      <!-- </v-container> -->
    </div>

    <!-- les forms -->
    <div v-else-if="formList && formList.length">
      <h4>
        {{ config.title }}
        <help :code="`${config.help}`" v-if="config.help"></help>
      </h4>

      <!-- <v-container style="background-color:green; width:100%"> -->
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
      <!-- </v-container> -->
    </div>
  </div>
</template>

<script>
import dynamicForm from "@/components/form/dynamic-form";
import help from "./help";
import "./form.css";

export default {
  name: "dynamic-form-group",
  components: {
    dynamicForm,
    help
  },
  data: () => ({}),
  props: ["config", "baseModel"],
  computed: {
    formList() {
      return this.computeFormList(this.config);
    },
    hasForms() {
      return this.computeHasForms(this.config);
    },
    groupList() {
      return this.computeGroupList(this.config);
    }
  },
  methods: {
    // renvoie la liste des formulaires filtrée par condition
    computeFormList(config) {
      // si config.forms n'est pas défini, on prend tous les form de formDefs
      console.log(config);
      const forms = config.forms || Object.keys(config.formDefs || {});

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
