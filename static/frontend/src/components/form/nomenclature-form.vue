<template>
  <list-form
    v-if="configList"
    :config="configList"
    :baseModel="baseModel"
    :data="data"
  ></list-form>
</template>

<script>
import listForm from "./list-form";

export default {
  name: "nomenclatureForm",
  components: { listForm },
  props: ["config", "baseModel", "data"],
  data: () => ({
    configList: null
  }),
  created: function() {
    const { nomenclatureType } = this.config;
    this.config.url = `api/oeasc/nomenclatures/${nomenclatureType}`;
    this.config.valueFieldName = "id_nomenclature";
    this.config.textFieldName = "label_fr";
    this.config.returnObject = true;
    this.configList = this.config;
  }
};
</script>

<style lang="scss" scoped>
.md-checkbox,
.md-radio {
  display: flex;
}
</style>
