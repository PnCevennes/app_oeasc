<template>
  <div>
    <list-form v-if="configList" :config="configList" :baseModel="baseModel"></list-form>
  </div>
</template>

<script>
import listForm from "./list-form";

export default {
  name: "nomenclatureForm",
  components: { listForm },
  props: ["config", "baseModel"],
  data: () => ({
    configList: null
  }),
  created: function() {
    this.config.url = `api/oeasc/nomenclatures/${this.config.nomenclatureType}`;
    this.config.valueFieldName = "id_nomenclature";
    this.config.textFieldName = "label_fr";
    this.$store.dispatch("nomenclatures").then(() => {
      this.config.items = this.$store.getters.nomenclaturesOfType(
        this.config.nomenclatureType
      );

      // TODO DANS LA CONFIG OU AUTRE
      if (this.config.nomenclatureType == "OEASC_PEUPLEMENT_TYPE") {
        this.config.items = [
          "FREG",
          "FIRR",
          "TAIL",
          "MEL",
          "NSP"
        ].map(cd_nomenclature =>
          this.config.items.find(
            item => item.cd_nomenclature == cd_nomenclature
          )
        );
      }
      this.configList = this.config;
    });
  }
};
</script>

<style lang="scss" scoped>
.md-checkbox,
.md-radio {
  display: flex;
}
</style>
