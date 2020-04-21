<template>
  <v-app>
    <div id="app" ref="app">
      <div class="page-container">
        <oeasc-app-bar
        class="oeasc-app-bar"
          :config="configAppBar"
          v-model="configDrawer.show"
        ></oeasc-app-bar>
        <div class="oeasc-app-bar space"></div>
        <!-- <v-card color="grey lighten-4" flat tile> -->
        <div class="img-titre">
          <h1 class="oeasc-titre">
            Observatoire de l'équilibre agro‑sylvo‑cynégétique
          </h1>
        </div>
        <oeasc-drawer :config="configDrawer"></oeasc-drawer>

        <div class="main-container" id="scrolling-techniques" style="height=100px">
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
  computed: {},
  data() {
    return {
      drawer: false,
      menus: config.menus,
      userIcon: "person",
      configAppBar: {
        rightMenus: ["user"],
        leftMenus: ["accueil", "observatoire", "systeme_alerte"]
      },
      configDrawer: {
        menus: [
          "accueil",
          "observatoire",
          "systeme_alerte",
          "user",
          "documentation",
          "contact",
          "partenaires"
        ],
        show: this.drawer
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
      console.log(access, droitMax);
      if (!access) {
        return;
      }
      // redirect to login
      if (access > droitMax) {
        console.log('aaaa', this.$route.fullPath)
        this.$router.push({
          name: "user.login",
          query: { redirect: this.$route.fullPath }
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

<style lang="scss" scoped>
table.v-table tbody td {
  font-size: 5px !important;
}
</style>
