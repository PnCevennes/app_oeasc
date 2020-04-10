<template>
  <div class="help">
    <v-btn
      tabIndex="-1" 
      placeholder="NoTabIndex"
      class="btn"
      icon
      @click.stop="dialog = true"
      title="Cliquer pour obtenir de l'aide"
    >
      <v-icon>help</v-icon>
    </v-btn>

    <v-row justify="center">
      <v-dialog v-model="dialog" max-width="1000">
        <v-card>
          <v-card-text>
            <oeasc-content :code="code" :containerClassIn="'content-help'"></oeasc-content>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-row>
  </div>
</template>

<script>
import oeascContent from "@/modules/content/content";
export default {
  name: "help",
  props: ["code"],
  components: { oeascContent },
  data: () => ({
    dialog: false
  })
};
</script>

<style>
.help {
  display: inline;
  z-index: 10000;
}
.v-btn {
  margin: 0 20px 0 0px;
}
</style>
