<template>
  <v-card>
    <v-app-bar dense>

      <v-app-bar-nav-icon @click="config.navIconClick()"></v-app-bar-nav-icon>

      <v-spacer></v-spacer>

      <v-menu offset-y transition="slide-x-transition" open-on-hover>
        <template v-slot:activator="{ on: menu }">
          <v-btn v-on="menu" icon>
            <v-icon v-if="$store.getters.isAuth">mdi-account-check</v-icon>
            <v-icon v-else>mdi-account-cancel</v-icon>
          </v-btn>
        </template>
        <v-list>
          <template v-for="(item, index) in config.menus.userMenu">
            <v-list-item
              v-if="!item.condition || item.condition({ $store })"
              :key="index"
              :to="item.to"
            >
              <v-list-item-icon v-if="item.icon">
                <v-icon v-text="item.icon"></v-icon>
              </v-list-item-icon>
              <v-list-item-title>{{ item.label }}</v-list-item-title>
            </v-list-item>
          </template>
        </v-list>
      </v-menu>
    </v-app-bar>
  </v-card>
</template>

<script>
export default {
    name: 'oeasc-app-bar',
    props: ['config']
}
</script>
