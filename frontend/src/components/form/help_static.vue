<!-- #############################################################################################$
Pastille d'aide affichant un "?" qui ouvre une fenêtre de dialogue avec du contenu statique.
on utilisera un fichier du type help_content.vue pour le contenu de la fenêtre. (voir les exemples existants)
############################################################################################## -->

<template>
  <span class="help">
    <v-row justify="center">
      <v-dialog
        v-model="dialog"
        max-width="1000"
        class="help-dialog"
      >
        <v-card>
          <v-card-text>
            <div class="help-card-text">
              <slot></slot>
            </div>
          </v-card-text>
        </v-card>
      </v-dialog>
    </v-row>

    <v-btn
      tabindex="-1"
      placeholder="NoTabIndex"
      class="btn"
      icon
      size="small"
      variant="text"
      @click.stop="dialog = true"
      title="Cliquer pour obtenir de l'aide"
    >
      <v-icon
        tabindex="-1"
        size="22"
        >help</v-icon
      >
    </v-btn>
  </span>
</template>

<script>
export default {
  name: 'help',
  // props: ["code"],
  components: {},
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
  display: inline-flex;
  align-items: left;
  justify-content: center;
  position: relative;
  vertical-align: middle;
  margin-left: 10px;
  margin-right: 10px;
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
.help-card-text {
  font-size: 15px;
  padding-top: 15px;
  padding-bottom: 15px;
}
</style>
