<template>
  <div>
    <chained-form :config="configFormChainedDeclaration" :meta="{idDeclaration}"></chained-form>
  </div>
</template>

<script>
import configFormChainedDeclaration from "./config/form-chained-declaration";
import chainedForm from "@/components/form/chained-form"

export default {
  name: "declarationForm",
  components: {chainedForm},
  data: () => ({
    configFormChainedDeclaration
  }),

  computed: {
    idDeclaration() {
      return this.$route.params.idDeclaration || null;
    }
  }
};
</script>
