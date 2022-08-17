<template>
  <v-app>
    <div id="app" ref="app">
      <div class="page-container">
        <oeasc-app-bar class="oeasc-app-bar" :config="configAppBar" v-model="configDrawer.show"></oeasc-app-bar>
        <div class="oeasc-app-bar space"></div>
        <!-- <v-card color="grey lighten-4" flat tile> -->
        <div class="img-titre" v-if="!$route.meta.hideTitle">
          <h1 class="oeasc-titre">Observatoire de l'équilibre agro‑sylvo‑cynégétique</h1>
        </div>
        <oeasc-drawer :config="configDrawer"></oeasc-drawer>

        <breadcrump></breadcrump>
        <div class="main-container" id="scrolling-techniques" style="height=100px">
          <router-view></router-view>
        </div>
      </div>
    </div>
  </v-app>
</template>

<script>
import { config } from "@/config/config.js";
import { configAppBar, configDrawerMenus } from "@/config/menu.js";
import "@/core/css/main.scss";
import oeascAppBar from "@/components/app/app-bar";
import oeascDrawer from "@/components/app/drawer";
import breadcrump from "@/components/app/breadcrump";

export default {
  name: "App",
  components: { oeascAppBar, oeascDrawer, breadcrump },
  computed: {},
  data() {
    return {
      drawer: false,
      menus: config.menus,
      userIcon: "person",
      configAppBar: configAppBar,
      configDrawer: {
        menus: configDrawerMenus,
        show: false
      },
      drawerShow: false,
    };
  },
  watch: {
    $route() {
      this.process()
    }
  },
  methods: {
    process() {
      this.$store.dispatch('testConnexion', {}).then(
        (user) => {
          this.$store.commit("user", user);
          this.$session.set("user", user);
          this.checkRigths();
          // titre
          this.setTitle();
        },
        error=> {
          error;
          this.$store.commit("user", {});
          this.$session.set("user", {});

          this.checkRigths();
          // titre
          this.setTitle();

        }
      )
    },
    setTitle() {
      const title = this.$route.meta.title || this.$route.meta.label;
      document.title = title ? `OEASC - ${title}` : "OEASC";
    },
    checkRigths() {
      const access = this.$route.meta.access;
      const droitMax = this.$store.getters.droitMax;

    if (!access) {
      return;
    }

    if ( access > droitMax) {
        this.$router.push({
          name: "user.login",
          query: { redirect: this.$route.fullPath },
        });
      }
    }
  },
  created: function () {
    this.process();
  }
}
</script>

<style lang="scss" scoped>
table.v-table tbody td {
  font-size: 5px !important;
}
</style>
