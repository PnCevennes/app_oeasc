<template>
  <list-form
    v-if="configList"
    :config="configList"
    :baseModel="baseModel"
    :dataItemsIn="dataItems"
  ></list-form>
</template>

<script>
import listForm from "./list-form";

export default {
  name: "nomenclatureForm",
  components: { listForm },
  props: ["config", "baseModel"],
  data: () => ({
    configList: null,
    dataItems: null
  }),
  created: function() {
    this.config.url = `api/oeasc/nomenclatures/${this.config.nomenclatureType}`;
    this.config.valueFieldName = "id_nomenclature";
    this.config.textFieldName = "label_fr";
    this.dataItems = this.$store.getters.nomenclaturesOfType(
      this.config.nomenclatureType
    );
    if (this.config.nomenclatureType == "OEASC_PEUPLEMENT_TYPE") {
      this.dataItems = [
        "FREG",
        "FIRR",
        "TAIL",
        "MEL",
        "NSP"
      ].map(cd_nomenclature =>
        this.dataItems.find(item => item.cd_nomenclature == cd_nomenclature)
      );
    }
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
