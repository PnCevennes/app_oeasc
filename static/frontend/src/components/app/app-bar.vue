<template>
  <v-card>
    <v-app-bar dense fixed>
      <v-app-bar-nav-icon @click="drawnerClick()"></v-app-bar-nav-icon>
          <app-bar-menu :config="configMenus.leftMenus"></app-bar-menu>

          <v-spacer></v-spacer>
          <app-bar-menu :config="configMenus.rightMenus"></app-bar-menu>
    </v-app-bar>
  </v-card>
</template>

<script>
import { configMenu } from "./menu.js";
import appBarMenu from './app-bar-menu'

export default {
  name: "oeasc-app-bar",
  components: {appBarMenu},
  props: ["config", "value"],
  computed: {
    configMenus() {
      console.log('app_bar', this.config.leftMenus)
      return {
        rightMenus: this.config.rightMenus.map(menuName =>
          configMenu(menuName, this)
        ).filter(m => m.condition),
        leftMenus: this.config.leftMenus.map(menuName =>
          configMenu(menuName, this)
        ).filter(m => {console.log(m); return m.condition}),
      };
    }
  },
  methods: {
    drawnerClick() {
      this.$emit("input", !this.value);
    }
  }
};
</script>
