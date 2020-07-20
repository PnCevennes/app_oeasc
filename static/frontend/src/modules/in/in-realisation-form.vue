<template>
  <div v-if="configRealisationForm">
    <generic-form :config="configRealisationForm" :meta="{idRealisation}">
    </generic-form>
  </div>
</template>

<script>
import genericForm from "@/components/form/generic-form";
import configRealisationForm from "./config/form-realisation";

export default {
  name: "in-form",
  computed: {
    idRealisation() {
      return this.$route.params.idRealisation;
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
