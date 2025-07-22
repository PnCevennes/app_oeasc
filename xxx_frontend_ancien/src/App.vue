

<template>
  <v-app>
    <div id="app" ref="app">
      <div class="page-container">
        <!-- menu -->
        <oeasc-app-bar class="oeasc-app-bar" :config="configAppBar" v-model="configDrawer.show"></oeasc-app-bar>
        <div class="oeasc-app-bar space"></div>
        <!-- <v-card color="grey lighten-4" flat tile> -->
        <div class="img-titre" v-if="!$route.meta.hideTitle">
          <h1 class="oeasc-titre">Observatoire de l'équilibre agro‑sylvo‑cynégétique</h1>
        </div>
        <!-- menu sur un panneau latéral -->
        <oeasc-drawer :config="configDrawer"></oeasc-drawer>

        <!-- fil d'ariane -->
        <breadcrump></breadcrump>
        <h1>etiusnretiunetiu</h1>
        
        <div class="main-container" id="scrolling-techniques">
          <!-- contenu de la page, router gére automatiquement les routes inscrites dans router/index.js -->
          <!-- mais dans cette appli on récupère aussi les roude dans modules/index.js et pages/index.js -->
          <router-view></router-view>
        </div>
        
      </div>
    </div>
  </v-app>
</template> 

<script>
import { config } from "@/config/config.js";
import { configAppBar, configDrawerMenus } from "@/config/menu.js"; // config du menu, liste, position et droits
import "@/core/css/main.scss";
import oeascAppBar from "@/components/app/app-bar"; // template de la barre de menu
import oeascDrawer from "@/components/app/drawer";
import breadcrump from "@/components/app/breadcrump";
  
// si la page a la prop page, 
// les routes sont définies dans modules/index.js et pages/index.js
// si elle n'a pas la prop page, le template des page est dans modules/content/content.vue
// sinon le template est dans nom_modules/nom_component

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
    $route() { // si changement de page on lance la fonction process
      this.process()
    }
  },
  methods: {
    process() {
      this.$store.dispatch('testConnexion', {}).then( // verifie si l'utilisateur est connecté
        (user) => {
          this.$store.commit("user", user); // me à jour les données de l'utilisateur
          this.$session.set("user", user); // met à jour la session avec les données de l'utilisateur
          this.checkRigths(); // 
          // titre
          this.setTitle();
        },
        error=> { // si erreur on déconnecte l'utilisateur
          error;
          this.$store.commit("user", {});
          this.$session.set("user", {});

          this.checkRigths();
          // titre
          this.setTitle();

        }
      )
    },
    setTitle() { // modifie le titre de la page
      const title = this.$route.meta.title || this.$route.meta.label;
      document.title = title ? `OEASC - ${title}` : "OEASC";
    },
    checkRigths() { // vefifie l'accès en fonction de la valeur access dans le index.js de chaque module
      const access = this.$route.meta.access;
      const droitMax = this.$store.getters.droitMax;

      if (!access) {
        return;
      }

      if ( access > droitMax) { // si les droit ne sont pas suffisant on redirige vers la page de login
          this.$router.push({
            name: "user.login",
            query: { redirect: this.$route.fullPath },
          });
      }
    }
  },
  // permet de garder les données de l'utilisateur en cas de rechargement de la page
  // notamment pour les droits d'accès et le menu espace utilisateur
  created: function () { // a la creation de la page on lance la fonction process.
    this.process();
  }
}
</script>

<style lang="scss" scoped>
table.v-table tbody td {
  font-size: 5px !important;
}
</style>
