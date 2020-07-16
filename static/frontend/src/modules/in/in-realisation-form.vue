<template>
  <div v-if="configRealisationForm">
    <generic-form :configRealisationForm="configRealisationForm">
    </generic-form>
  </div>
</template>

<script>
import genericForm from "@/components/form/generic-form";
// import { formFunctions } from '../../components/form/functions';
import configRealisationForm from "./config/form-realisation";

export default {
  name: "in-form",
  computed: {
    idRealisation() {
      return this.$route.params.idRealisation;
    },
    configRealisationForm() {
      return {
        forms: configRealisationForm.forms,
        struct: configRealisationForm.struct,
        preLoadData: () => {
          return new Promise(resolve => {
            if (!this.idRealisation) {
              resolve();
            }
            this.$store
              .dispatch("in_realisation", this.idRealisation)
              .then(data => {
                console.log(data);
                this.config.value = data;
                resolve();
              });
          });
        },

        switchDisplay: this.idRealisation,
        request: {
          url: `api/in/realisation/${this.idRealisation || ""}`,
          method: `${this.idRealisation ? "PATCH" : "POST"}`,
          onSuccess: data => {
            console.log("success", data);
          }
        }
      };
    }
  },
  data: function() {
    return {};
  },
  components: {
    genericForm
  }
};
</script>
