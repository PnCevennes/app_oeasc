<template>
  <div>
    <h1>Test formulaire de déclaration</h1>

    <!-- <div class="declaration-data">
        <pre>
        {{ declaration }}
        </pre>
    </div> -->

    <div v-for="[keySession, configSession] of Object.entries(config)" :key="keySession">
      <h2>{{ configSession['title'] }}</h2>
      <div v-for="[keyForm, configForm] in Object.entries(configSession['forms'])" :key="keyForm">
        <!-- :set="config = { name: keyForm, ...configForm }" -->
        <dynamic-form
          :config="{ name: keyForm, ...configForm }"
          :baseModel="declaration"
          :debug="true"
          :bShowError="bShowError"
        ></dynamic-form>
      </div>
    </div>
  </div>
</template>

<script>
import configTest from "./config-test.js";
import dynamicForm from "@/components/form/dynamic-form";
// import Declaration from "./declaration.js";

const initDeclaration = function() {
  const declaration = {};
  for (const configSession of Object.values(configTest)) {
    for (const [keyForm, configForm] of Object.entries(configSession.forms)) {
      declaration[keyForm] = null;
      if (configForm.multiple) {
        declaration[keyForm] = [];
      }
    }
  }
  return declaration;
};

export default {
  name: "testFormulaireDeclaration",
  data: () => ({
    declaration: initDeclaration(),
    config: configTest,
    bShowError: false
  }),
  components: {
    dynamicForm
  },
  created: function() {}
};
</script>

<style lang="scss" scoped>
.declaration-data {
  display: block;
  position: absolute;
  right: 10px;
  color: lightgreen;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.7);
}
</style>