<template>
  <div>
    <!-- les forms -->
    <div
      v-if="config.forms && hasForms"
      :class="{
        'form-group': true,
        border: config.class && config.class.includes('border'),
        margin: config.class && config.class.includes('margin'),
        padding: config.class && config.class.includes('padding')
      }"
    >
      <h4>
        {{ config.title }}
        <help :code="`${config.help}`" v-if="config.help"></help>
      </h4>

      <v-container>
        <template v-if="config.direction === 'row'">
          <v-row>
            <v-col v-for="(configForm, index) of formList" :key="index">
              <dynamic-form
                :config="configForm"
                :baseModel="baseModel"
              ></dynamic-form>
            </v-col>
          </v-row>
        </template>
        <template v-else>
          <v-row v-for="(configForm, index) of formList" :key="index">
            <dynamic-form
              :config="configForm"
              :baseModel="baseModel"
            ></dynamic-form>
          </v-row>
        </template>
      </v-container>
    </div>

    <!-- les groupes -->
    <div v-else-if="config.groups">
      <v-container>
        <template v-if="config.direction === 'row'">
          <v-row>
            <v-col v-for="(configGroup, index) of groupList" :key="index">
              <dynamic-form-group
                :baseModel="baseModel"
                :config="configGroup"
              ></dynamic-form-group>
            </v-col>
          </v-row>
        </template>
        <template v-else>
          <v-row v-for="(configGroup, index) of groupList" :key="index">
            <dynamic-form-group
              :baseModel="baseModel"
              :config="configFormGroup"
            ></dynamic-form-group>
          </v-row>
        </template>
      </v-container>
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
      return Object.keys(config.forms || {})
        .filter(keyForm => {
          const form = config.forms[keyForm];
          return (
            !form.condition ||
            form.condition({ baseModel: this.baseModel, $store: this.$store })
          );
        })
        .map(keyForm => {
          return {
            ...config.forms[keyForm],
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
