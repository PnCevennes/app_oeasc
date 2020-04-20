<template>
  <v-navigation-drawer
  fixed
    v-model="config.show"
    temporary
    width="500"
  >
    <v-list dense nav class="py-0">
      <template v-for="(item, index) of configMenus">
        <v-list-group v-if="item.menus.length" :key="`item.${index}`" :prepend-icon="item.icon">
          <template v-slot:activator>
            <v-list-item-title>{{
              item.labelDrawer || item.label
            }}</v-list-item-title>
          </template>
          <v-list-item
            v-for="(subItem, indexSub) of item.menus"
            :key="`itemSub.${index}.${indexSub}`"
            :to="subItem.path"
            @click="drawer = false"
          >
            <v-list-item-content>
              <v-list-item-title>{{ subItem.label }}</v-list-item-title>
            </v-list-item-content>
            <v-list-item-icon>
              <v-icon>{{ subItem.icon }}</v-icon>
            </v-list-item-icon>
          </v-list-item>
        </v-list-group>

        <v-list-item v-else :key="index" :to="item.path">
          <v-list-item-icon> </v-list-item-icon>
          <v-list-item-content>
            <v-list-item-title>{{
              item.labelDrawer || item.label
            }}</v-list-item-title>
          </v-list-item-content>
          <v-list-item-icon>
            <v-icon>{{ item.icon }}</v-icon>
          </v-list-item-icon>
        </v-list-item>
      </template>
    </v-list>
  </v-navigation-drawer>
</template>

<script>
import { configMenu } from "./menu.js";

export default {
  name: "oeasc-drawer",
  props: ["config"],
  computed: {
    configMenus() {
      return this.config.menus.map(menuName => configMenu(menuName, this));
    }
  }
};
</script>
