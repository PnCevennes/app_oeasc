<template>
  <div>
    <div
      v-if="config.forms"
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
};
</script>
