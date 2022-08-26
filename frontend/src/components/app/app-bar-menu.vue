<template>
  <div>
    <template v-for="(menu, indexMenu) of config">
      <v-btn :text="!menu.icon || !!menu.label" :key="indexMenu" v-if="!menu.menus.length"
        :icon="!!menu.icon" :to="menu.path" class="text-none">
        <v-icon v-if="!!menu.icon">{{ menu.icon }}</v-icon>
        <template v-else>{{ menu.label }}</template>
      </v-btn>
      <v-menu offset-y transition="slide-x-transition" open-on-hover :key="indexMenu" v-else>
        <template v-slot:activator="{ on: bMenu }">
          <v-btn v-on="bMenu" :text="!menu.icon || !!menu.label" :icon="!menu.label && !!menu.icon"
            class="text-none">
            <v-icon>{{ menu.icon }}</v-icon>
            <span v-if="menu.label">{{ menu.label }}</span>
          </v-btn>
        </template>
        <v-list>
          <template v-for="(item, index) in menu.menus">
            <v-list-item :key="index" :to="item.path"
              v-if="item.meta.access <= $store.getters.droitMax">
              <v-list-item-icon v-if="item.icon">
                <v-icon v-text="item.icon"></v-icon>
              </v-list-item-icon>
              <v-list-item-title>{{ item.label }}</v-list-item-title>
            </v-list-item>
          </template>
        </v-list>
      </v-menu>
    </template>
  </div>
</template>

<script>
export default {
  name: "app-bar-menu",
  props: ["config"],
};
</script>
