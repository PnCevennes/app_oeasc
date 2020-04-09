<template>
  <v-app>
    <div id="app">
      <div class="page-container">
        <v-card color="grey lighten-4" flat tile>
          <div class="img-titre">
            <h1 class="oeasc-titre">
              Observatoire de l'équilibre agro‑sylvo‑cynégétique
            </h1>
          </div>
          <v-toolbar dense>
            <v-app-bar-nav-icon @click="drawer = !drawer"></v-app-bar-nav-icon>

            <v-spacer></v-spacer>

            <!-- utilisateurs -->
            <v-menu offset-y transition="slide-x-transition" open-on-hover>
              <template v-slot:activator="{ on: menu }">
                <v-btn v-on="menu" icon>
                  <v-icon v-if="$store.getters.isAuth">mdi-account</v-icon>
                  <v-icon v-else>mdi-account-cancel</v-icon>
                </v-btn>
              </template>
              <v-list>
                <v-list-item
                  v-for="(item, index) in userMenu"
                  :key="index"
                  :to="item.to"
                >
                  <v-list-item-title>{{ item.label }}</v-list-item-title>
                </v-list-item>
              </v-list>
            </v-menu>
            <v-btn icon> </v-btn>
          </v-toolbar>
        </v-card>

        <v-navigation-drawer v-model="drawer" absolute temporary floating width="350">
          <v-list dense nav class="py-0">
            <template v-for="(item, index) in menus.listLeftMenu">
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

        <!-- 
        <md-app md-waterfall md-mode="fixed-last">
          <md-app-toolbar class="md-large md-dense">
            <div class="md-toolbar-row">
              <div class="img-titre">
                <h1 class="oeasc-titre">
                  Observatoire de l'équilibre agro‑sylvo‑cynégétique
                </h1>
              </div>
            </div>

            <div class="md-toolbar-row">
              <div class="md-toolbar-section-end">
                <md-menu md-size="medium" md-align-trigger>
                  <md-button md-menu-trigger>
                    {{ $store.getters.nom_complet || "non connecté" }}
                    <md-icon>person</md-icon>
                  </md-button>

                  <md-menu-content>
                    <md-menu-item
                      v-for="item in userMenu"
                      :to="item.to"
                      :key="item.to"
                      >{{ item.label }}</md-menu-item
                    >
                  </md-menu-content>
                </md-menu>
              </div>
              <div class="md-toolbar-section-start">
                <md-button
                  class="md-icon-button"
                  @click="drawer = !drawer"
                >
                  <md-icon>menu</md-icon>
                </md-button>

                <md-tabs>
                  <md-tab
                    v-for="tab in menus.listTopMenu"
                    :id="tab.id"
                    :md-label="tab.label"
                    :md-icon="tab.icon"
                    :to="tab.to"
                    :key="tab.id"
                  ></md-tab>
                </md-tabs>
              </div>
            </div>
          </md-app-toolbar>

          <md-app-drawer :md-active.sync="drawer">
            <md-toolbar class="md-transparent" md-elevation="0"
              >Navigation</md-toolbar
            >
            <div class="full-control">
              <div class="list">
                <md-list :md-expand-single="true">
                  <md-list-item
                    v-for="item in menus.listLeftMenu"
                    :key="item.label"
                    md-expand
                  >
                    <md-icon>{{ item.icon }}</md-icon>
                    <span class="md-list-item-text">{{ item.label }}</span>

                    <md-list v-if="item.subList" slot="md-expand">
                      <md-list-item
                        v-for="subItem in item.subList"
                        :key="subItem.label"
                        :to="subItem.to"
                        @click="drawer = false"
                      >
                        <span class="md-list-item-text">{{
                          subItem.label
                        }}</span>
                      </md-list-item>
                    </md-list>
                  </md-list-item>
                </md-list>
              </div>
            </div>
          </md-app-drawer>

          <md-app-content>
          </md-app-content>
        </md-app>
           -->
        <div class="flex-container">
          <router-view></router-view>
        </div>
      </div>
    </div>
  </v-app>
</template>

<script>
import Vue from "vue";
import VueMaterial from "vue-material";
import "vue-material/dist/vue-material.min.css";
import "vue-material/dist/theme/default.css";

import { config } from "@/config/config.js";

import "@/core/css/main.scss";

Vue.use(VueMaterial);

export default {
  name: "App",
  data() {
    return {
      drawer: false,
      menus: config.menus,
      userIcon: "person"
    };
  },
  watch: {
    $route() {
      this.checkRigths();
    }
  },
  computed: {
    userMenu() {
      return config.menus.userMenu.filter(item => {
        if (["login"].includes(item.name) && this.$store.getters.isAuth) {
          return false;
        }

        if (
          ["logout", "user"].includes(item.name) &&
          !this.$store.getters.isAuth
        ) {
          return false;
        }

        return true;
      });
    }
  },
  methods: {
    checkRigths() {
      const access = this.$route.meta.access;
      const droitMax = this.$store.getters.droit_max;
      if (!access) {
        return;
      }
      // redirect to login
      if (access > droitMax) {
        this.$store.commit("redirectOnLogin", this.$route.fullPath);
        this.$router.push({ name: "login" });
      }
    }
  },
  created: function() {
    this.$store.commit("user", this.$session.get("user"));
    this.checkRigths();
  }
};
</script>

<style lang="scss" scoped>
.md-app {
  min-height: 400px;
  border: 1px solid rgba(#000, 0.12);
}
.img-titre {
  height: 172px;
  width: 100%;
  background-image: url("~@/assets/Bandeau_OEASC_172x1920_v4.jpg");
  display: flex;
  align-items: center;
  justify-content: center;
}
.oeasc-titre {
  text-align: center;
  font-weight: bold;
  border-radius: 5px;
  text-shadow: 0 0 0.5em #000000;
  padding: 10px;
  margin: 0 100px;
  color: white;
  font-size: 2.5rem;
}

.map {
  height: 400px;
}
</style>
