<template>
  <div class="help">
    <v-row justify="center">
      <v-dialog v-model="dialog" max-width="1000" class="help-dialog">
        <v-card>
          <v-card-text>
            <oeasc-content :code="code" :containerClassIn="'content-help'"></oeasc-content>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-row>

    <v-btn
      tabindex="-1"
      placeholder="NoTabIndex"
      class="btn"
      icon
      small
      @click.stop="dialog = true"
      title="Cliquer pour obtenir de l'aide"
    >
      <v-icon tabindex="-1">help</v-icon>
    </v-btn>
  </div>
</template>

<script>
export default {
  name: "help",
  props: ["code"],
  components: {
    oeascContent: () => import("@/modules/content/content.vue"),
  },
  data: () => ({
    dialog: false,
  }),
};
</script>

<style>
.help-dialog {
  z-index: 10000;
}
.help {
  display: inline-block;
}
.help:not(:last-child) .btn {
  margin: 0 20px 0 0px;
}
.help-radio-item {
  top: -2px;
  /* left: 0px; */
  padding-left: 5px;
  position: absolute;

  /* float: right; */
  color: red;
}

.help-degat-item {
  top: -3px;
  /* left: 0px; */
  padding-left: 5px;
  position: relative;

  /* float: right; */
  color: red;
}
</style>
