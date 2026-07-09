<!-- Menu sandwich en haut à gauche. Affiche un panneau latéral coulissant avec les menus de l'application. -->

<template>
  <v-navigation-drawer
    fixed
    v-model="config.show"
    temporary
    width="500"
  >
    <v-list
      dense
      nav
      class="py-0"
    >
      <template
        v-for="(item, index) of configMenus"
        :key="index"
      >
        <v-list-group
          v-if="item.menus.length"
          :prepend-icon="item.icon"
        >
          <template v-slot:activator>
            <v-list-item-title>{{ item.label }}</v-list-item-title>
          </template>
          <v-list-item
            v-for="(subItem, indexSub) of item.menus"
            :key="`itemSub.${index}.${indexSub}`"
            :to="subItem.path"
            @click="drawer = false"
          >
            <template v-slot:prepend>
              <v-icon>blougi</v-icon>
            </template>
            <v-list-item-title>{{ subItem.label }}</v-list-item-title>
            <template v-slot:append>
              <v-icon>{{ subItem.icon }}</v-icon>
            </template>
          </v-list-item>
        </v-list-group>

        <v-list-item
          v-else
          :to="item.path"
        >
          <v-list-item-title>{{ item.label }}</v-list-item-title>
          <template v-slot:append>
            <v-icon>{{ item.icon }}</v-icon>
          </template>
        </v-list-item>
      </template>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import { configMenu } from './menu.js';

// Création d'un menu latéral coulissant contenu dans menu.js
// temporary : Le drawer est temporaire, ce qui signifie qu'il se superpose au contenu principal et disparaît lorsqu'il est fermé.
// fixed : Le drawer est fixé à sa position et ne défile pas avec le contenu principal.

export default {
  compatConfig: { MODE: 3 }, // verrouille les acquis Phase 4 (composant testé sans warning au 2026-07-10)
  name: 'oeasc-drawer',
  props: ['config'],
  computed: {
    configMenus() {
      return this.config.menus
        .map((menuName) => configMenu(menuName, this))
        .filter((m) => !m.hidden);
    },
  },
};
</script>
