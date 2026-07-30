<!-- ##################################################################################################
ancienne petite pastille d'aide avec le "?" qui ouvre une fenetre. Elle est maintenant à remplacer 
par help_static.vue qui n'a plus besoin de chercher les contenus dans la base de données mais
qui les charge directement depuis un fichier statique. On le garde le temps de tout changer
################################################################################################## -->

<template>
  <div class="help">
    <v-row justify="center">
      <v-dialog
        v-model="dialog"
        max-width="1000"
        class="help-dialog"
      >
        <v-card>
          <v-card-text>
            <oeasc-content
              :code="code"
              :containerClassIn="'content-help'"
            ></oeasc-content>
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
      >
        help
      </v-icon>
    </v-btn>
  </div>
</template>

<script>
import { defineAsyncComponent } from 'vue';

export default {
  name: 'help',
  props: ['code'],
  components: {
    // import dynamique pour casser le cycle content.vue -> help.vue -> content.vue
    // defineAsyncComponent est indispensable en Vue 3 : une simple fonction () => import(...)
    // n'est plus reconnue comme composant asynchrone (contrairement à Vue 2) et est exécutée
    // comme un composant fonctionnel, ce qui affiche "[object Promise]" au lieu du contenu.
    oeascContent: defineAsyncComponent(() => import('@/modules/content/content.vue')),
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
