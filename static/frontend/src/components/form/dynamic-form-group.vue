<template>
  <div>
    <div
      v-if="config.forms && hasForms(config)"
      :class="{
        'form-group': true,
        border: config.class && config.class.includes('border'),
        margin: config.class && config.class.includes('margin'),
        padding: config.class && config.class.includes('padding')
      }"
    >
      <h4>
        {{ config.title }}
        <help :code="`group-form-${config.name}`" v-if="config.help"></help>
      </h4>

      <v-container>
        <template v-if="config.direction === 'row'">
          <v-row>
            <v-col
              v-for="[keyForm, configForm] in Object.entries(config.forms)"
              :key="keyForm"
            >
              <dynamic-form
                :config="{
                  ...{ name: keyForm },
                  ...configForm,
                  displayValue: config.displayValue,
                  displayLabel: config.displayLabel
                }"
                :baseModel="baseModel"
              ></dynamic-form>
            </v-col>
          </v-row>
        </template>
        <template v-else>
          <v-row
            v-for="[keyForm, configForm] in Object.entries(config.forms)"
            :key="keyForm"
          >
            <dynamic-form
              :config="{
                ...{ name: keyForm },
                ...configForm,
                displayValue: config.displayValue,
                displayLabel: config.displayLabel
              }"
              :baseModel="baseModel"
            ></dynamic-form>
          </v-row>
        </template>
      </v-container>

      <!-- 
      <div
        :class="{
          'flex-container': true,
          'flex-row': config.direction === 'row'
        }"
      >
        <dynamic-form
          v-for="[keyForm, configForm] in Object.entries(config.forms)"
          :key="keyForm"
          :config="{
            ...{ name: keyForm },
            ...configForm,
            displayValue: config.displayValue,
            displayLabel: config.displayLabel
          }"
          :baseModel="baseModel"
        ></dynamic-form>
      </div> -->
    </div>
    <div
      v-else-if="config.groups"
    >
      <v-container>
        <template v-if="config.direction === 'row'">
          <v-row>
            <v-col
              v-for="[keyFormGroup, configFormGroup] in Object.entries(
                config.groups
              )"
              :key="keyFormGroup"
            >
              <dynamic-form-group
                :baseModel="baseModel"
                :config="{
                  ...configFormGroup,
                  displayValue: config.displayValue,
                  displayLabel: config.displayValue
                }"
              ></dynamic-form-group>
            </v-col>
          </v-row>
        </template>
        <template v-else>
          <v-row
            v-for="[keyFormGroup, configFormGroup] in Object.entries(
              config.groups
            )"
            :key="keyFormGroup"
          >
            <dynamic-form-group
              :baseModel="baseModel"
              :config="{
                ...configFormGroup,
                displayValue: config.displayValue,
                displayLabel: config.displayValue
              }"
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
  methods: {
    hasForms() {
      let cond = false;
      if (this.config.forms) {
        for (const form of Object.values(this.config.forms)) {
          cond =
            cond ||
            !form.condition ||
            form.condition({ baseModel: this.baseModel, $store: this.$store });
        }
      }
      if (this.config.groups) {
        cond = this.hasForms(this.config.groups);
      }

      return cond;
    }
  }
};
</script>
