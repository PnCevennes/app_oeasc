<template>
<div>
  <list-form
    v-if="configList"
    :config="configList"
    :baseModel="baseModel"
    :ref="`listForm_${config.name}`"
  ></list-form>
</div>
</template>

<script>
import listForm from "./list-form";
import { formFunctions } from "@/components/form/functions/form";

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
        this.processChange();
      },
      deep: true
    },
    config: {
      handler() {
        this.processChange();
      },
      deep: true
    }
  },
  methods: {
    processChange() {
      this.getEssenceSelected();
      this.$refs[`listForm_${this.configList.name}`].getData();
    },
    getEssenceSelected() {
      this.configList.essencesSelected = formFunctions.getEssencesSelected({
        baseModel: this.config.declaration || this.baseModel,
        $store: this.$store
      });
    }
  },
  created: function() {
    this.config.list_type = "autocomplete";
    this.config.url = "api/oeasc/nomenclatures/OEASC_PEUPLEMENT_ESSENCE";
    this.config.processItems = formFunctions.processItems.essence;
    this.config.valueFieldName = "id_nomenclature";
    this.config.displayFieldName = "label_fr";
    this.config.items = this.$store.getters.nomenclaturesOfType(
      "OEASC_PEUPLEMENT_ESSENCE"
    );

  },
  mounted() {
    this.configList = this.config;
    this.getEssenceSelected();
  }
};
</script>

<style lang="scss" scoped>
.md-checkbox,
.md-radio {
  display: flex;
}
</style>
