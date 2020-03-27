<template>
  <list-form
    v-if="configList"
    :config="configList"
    :baseModel="baseModel"
    :dataItemsIn="dataItems"
    :ref="`listForm_${config.name}`"
  ></list-form>
</template>

<script>
import listForm from "./list-form";
import { formFunctions } from "@/components/form/functions";

export default {
  name: "EssenceForm",
  components: { listForm },
  props: ["config", "baseModel", "data"],
  data: () => ({
    configList: null
  }),
  watch: {
    baseModel: {
      handler() {
        this.configList.essencesSelected = formFunctions.getEssencesSelected(
          this.config.declaration || this.baseModel
        );
        this.$refs[`listForm_${this.config.name}`].getData();
      },
      deep: true
    },
    config  : {
      handler() {
        this.configList.essencesSelected = formFunctions.getEssencesSelected(
          this.config.declaration || this.baseModel
        );
        this.$refs[`listForm_${this.config.name}`].getData();
      },
      deep: true
    }
  },
  created: function() {
    this.config.display = "autocomplete";
    this.config.url = "api/oeasc/nomenclatures/OEASC_PEUPLEMENT_ESSENCE";
    this.config.processItems = formFunctions.processItems.essence;
    this.config.valueFieldName = "id_nomenclature";
    this.config.textFieldName = "label_fr";
    this.dataItems = this.$store.getters.nomenclaturesOfType('OEASC_PEUPLEMENT_ESSENCE');
    this.config.essencesSelected = formFunctions.getEssencesSelected(
      this.config.declaration || this.baseModel
    );
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
