<template>
        <v-navigation-drawer
          v-model="config.show"
          absolute
          temporary
          floating
          width="350"
        >
          <v-list dense nav class="py-0">
            <template v-for="(item, index) in config.menus.listLeftMenu">
              <v-list-group
                v-if="item.subList"
                :key="index"
                :prepend-icon="item.icon"
              >
                <template v-slot:activator>
                  <v-list-item-title>{{ item.label }}</v-list-item-title>
                </template>

                <v-list-item
                  v-for="subItem in item.subList"
                  :key="subItem.label"
                  :to="subItem.to"
                  @click="drawer = false"
                >
                  <v-list-item-icon>
                    <v-icon>{{ subItem.icon }}</v-icon>
                  </v-list-item-icon>

                  <v-list-item-content>
                    <v-list-item-title>{{ subItem.label }}</v-list-item-title>
                  </v-list-item-content>
                </v-list-item>
              </v-list-group>

              <v-list-item v-else :key="index" :to="item.to">
                <v-list-item-icon>
                  <v-icon>{{ item.icon }}</v-icon>
                </v-list-item-icon>

                <v-list-item-content>
                  <v-list-item-title>{{ item.label }}</v-list-item-title>
                </v-list-item-content>
              </v-list-item>
            </template>
          </v-list>
        </v-navigation-drawer>
</template>

<script>
export default {
    name: 'oeasc-drawer',
    props: ['config']

}
</script>
