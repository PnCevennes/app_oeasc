<!-- // Composant Vue représentant la barre de menu principale de l'application.
// Ce composant inclut la barre supérieure (v-app-bar) et le menu latéral gauche.
// Il utilise les composants enfants 'app-bar-menu' pour afficher les menus de gauche et de droite,
// dont la configuration est passée via la prop 'config'.
//
// Props :
// - config : objet contenant les noms des menus à afficher à gauche et à droite.
// - modelValue : booléen indiquant l'état d'ouverture du menu latéral (drawer), via v-model.
//
// Computed :
// - configMenus : génère les configurations des menus de gauche et de droite en filtrant ceux qui sont cachés.
//
// Méthodes :
// - drawnerClick : émet 'update:modelValue' pour inverser l'état du menu latéral lors du clic sur l'icône de navigation.
//
// Utilise Vuetify pour la structure visuelle (v-app-bar, v-app-bar-nav-icon, v-spacer).
// Le composant est conçu pour être réutilisable et configurable selon les besoins de l'application. -->

<template>
  <v-app-bar dense>
    <v-app-bar-nav-icon @click="drawnerClick()"></v-app-bar-nav-icon>
    <app-bar-menu :config="configMenus.leftMenus"></app-bar-menu>

    <v-spacer></v-spacer>
    <app-bar-menu :config="configMenus.rightMenus"></app-bar-menu>
  </v-app-bar>
</template>

<script>
import { configMenu } from './menu.js';
import appBarMenu from './app-bar-menu.vue';

export default {
  name: 'oeasc-app-bar',
  components: { appBarMenu },
  props: ['config', 'modelValue'],
  emits: ['update:modelValue'],
  computed: {
    configMenus() {
      return {
        rightMenus: this.config.rightMenus
          .map((menuName) => configMenu(menuName, this))
          .filter((m) => !m.hidden),
        leftMenus: this.config.leftMenus
          .map((menuName) => configMenu(menuName, this))
          .filter((m) => !m.hidden),
      };
    },
  },
  methods: {
    drawnerClick() {
      this.$emit('update:modelValue', !this.modelValue);
    },
  },
};
</script>
