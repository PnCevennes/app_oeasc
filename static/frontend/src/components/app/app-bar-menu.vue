<template>
  <div>
    <template v-for="(menu, indexMenu) of config">
      <v-btn
        :text="!menu.icon || !!menu.label"
        :key="indexMenu"
        v-if="!menu.menus.length"
        :icon="menu.icon && !menu.label"
        :to="menu.path"
      >
        <v-icon v-if="!menu.label">{{ menu.icon }}</v-icon>
        {{ menu.label }}
        {{ menu.disabled }}
      </v-btn>
      <v-menu
        offset-y
        transition="slide-x-transition"
        open-on-hover
        :key="indexMenu"
        v-else
      >
        <template v-slot:activator="{ on: bMenu }">
          <v-btn
            v-on="bMenu"
            :text="!menu.icon || !!menu.label"
            :icon="menu.icon && !menu.label"
            :to="menu.path"
            class="text-none"
          >
            <v-icon v-if="!menu.label">{{ menu.icon }}</v-icon>
            {{ menu.label }}
          </v-btn>
        </template>
        <v-list>
          <template v-for="(item, index) in menu.menus">
            <v-list-item v-if="item.condition" :key="index" :to="item.path">
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
  props: ["config"]
};
</script>
