<template>
  <div>
    <div
      v-if="config.forms && hasForms(config)"
      :class="{
        'form-group': true
      }"
    >
      <h4>{{ config.title }}</h4>
      <div
        :class="{
          'flex-container': true,
          'flex-row': config.direction === 'row'
        }"
      >
        <dynamic-form
          v-for="[keyForm, configForm] in Object.entries(config.forms)"
          :key="keyForm"
          :config="{ ...{ name: keyForm }, ...configForm }"
          :baseModel="baseModel"
        ></dynamic-form>
      </div>
    </div>
    <div
      v-else-if="config.groups"
      :class="{
        'flex-container': true,
        'flex-row': config.direction === 'row'
      }"
    >
      <dynamic-form-group
        v-for="[keyFormGroup, configFormGroup] in Object.entries(config.groups)"
        :key="keyFormGroup"
        :baseModel="baseModel"
        :config="configFormGroup"
      ></dynamic-form-group>
    </div>
  </div>
</template>

<script>
import dynamicForm from "@/components/form/dynamic-form";
import "./form.css";

export default {
  name: "dynamic-form-group",
  components: {
    dynamicForm
  },
  data: () => ({}),
  props: ["config", "baseModel"],
  methods: {
    hasForms() {
      console.log('test', this.config.name, this.config);

        let cond = false
        if(this.config.forms) {
          console.log('forms')

          for (const form of Object.values(this.config.forms)) {
            cond = cond || !form.condition || form.condition({baseModel: this.baseModel})
          }
        }
        if (this.config.groups) {
          console.log('groups')
          cond =  this.hasForms(this.config.groups)
        }

      console.log('cond', cond);
      return cond;
    }
  }
};
</script>
