<template>
  <div>
      {{validForms[config.name]}}
    <h3>{{ config.title }}</h3>

    <v-form v-model="validForms[config.name]" :ref="config.name">
      <dynamic-form-group
        v-for="[keyFormGroup, configFormGroup] in Object.entries(config.groups)"
        :key="keyFormGroup"
        :config="configFormGroup"
        :baseModel="baseModel"
      >
      </dynamic-form-group>
      <v-btn color="success" @click="validate">
        Suivant
      </v-btn>
    </v-form>
  </div>
</template>

<script>
import dynamicFormGroup from "@/components/form/dynamic-form-group";

export default {
  name: "formSession",
  components: {
    dynamicFormGroup
  },
  data: () => ({}),
  watch: {},
  props: ["config", "baseModel", "validForms"],
  methods: {
    validate: function() {
      this.$refs[this.config.name].validate();
      if(this.validForms[this.config.name]) {
          console.log('actions')
      }
    }
  },
  created: function() {}
};
</script>
