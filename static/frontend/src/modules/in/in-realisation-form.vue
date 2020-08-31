<template>
  <div v-if="configRealisationForm">
    <generic-form :config="configRealisationForm" :meta="{id}">
    </generic-form>
  </div>
</template>

<script>
import genericForm from "@/components/form/generic-form";
import configRealisationForm from "./config/form-realisation";

export default {
  name: "in-form",
  computed: {
    id() {
      return this.$route.params.id;
    },
  },
  data: () => ({
    configRealisationForm
  }),
  components: {
    genericForm
  }
};
</script>
