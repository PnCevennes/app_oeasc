<template>
  <v-app>
    <div id="app">
      <div class="page-container">
        <!-- <v-card color="grey lighten-4" flat tile> -->
        <div class="img-titre">
          <h1 class="oeasc-titre">
            Observatoire de l'équilibre agro‑sylvo‑cynégétique
          </h1>
        </div>
        <oeasc-app-bar :config="configAppBar"></oeasc-app-bar>
        <oeasc-drawer :config="configDrawer"></oeasc-drawer>

        <div class="main-container">
            <router-view></router-view>
        </div>
      </div>
    </div>
  </v-app>
</template>

<script>
import { config } from "@/config/config.js";
import "@/core/css/main.scss";
import oeascAppBar from "@/components/app/app-bar";
import oeascDrawer from "@/components/app/drawer";

export default {
  name: "App",
  components: { oeascAppBar, oeascDrawer },
  data() {
    return {
      drawer: false,
      menus: config.menus,
      userIcon: "person",
      configAppBar: {
        menus: config.menus,
        navIconClick: () => {
          this.configDrawer.show = !this.configDrawer.show;
        }
      },
      configDrawer: {
        menus: config.menus,
        show: false
      }
    };
  },
  watch: {
    $route() {
      this.checkRigths();
    }
  },
  methods: {
    checkRigths() {
      const access = this.$route.meta.access;
      const droitMax = this.$store.getters.droitMax;
      if (!access) {
        return;
      }
      // redirect to login
      if (access > droitMax) {
        this.$router.push({
          name: "login",
          params: { redirect: this.$route.fullPath }
        });
      }
    }
  },
  created: function() {
    this.$store.commit("user", this.$session.get("user"));
    this.checkRigths();
  }
};
</script>

<style lang="scss" scoped></style>
