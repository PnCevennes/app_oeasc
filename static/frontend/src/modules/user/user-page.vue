<template>
  <div>
    <h1>Espace utilisateur</h1>
    <generic-form :config="config" ref="form"></generic-form>
  </div>
</template>

<script>
import genericForm from "@/components/form/generic-form";
// import { apiRequest } from "@/core/js/data/api.js";
import configFormUser from "./config/form-update-user.js";

export default {  
  name: "userPage",
  components: { genericForm },
  data: () => ({
    config: configFormUser
  })
};
</script>

<style lang="scss" scoped></style>
