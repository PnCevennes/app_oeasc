<template>
  <div v-if="configRealisationForm">
    <generic-form :config="configRealisationForm">
    </generic-form>
  </div>
</template>

<script>
import genericForm from "@/components/form/generic-form";
import configRealisationForm from "./config/form-realisation";

export default {
  name: "in-form",
  data: () => ({
    configRealisationForm
  }),
  components: {
    genericForm
  }
};
</script>
