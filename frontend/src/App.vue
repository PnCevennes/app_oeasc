<template>
  <v-app>
    <v-overlay
      :model-value="loading"
      absolute
    >
      <v-progress-circular
        indeterminate
        size="64"
        width="6"
        color="primary"
      ></v-progress-circular>
    </v-overlay>

    <div
      id="app"
      ref="app"
      v-if="!loading"
    >
      <div class="page-container">
        <!-- menu -->
        <oeasc-app-bar
          class="oeasc-app-bar"
          :config="configAppBar"
          v-model="configDrawer.show"
        ></oeasc-app-bar>
        <div class="oeasc-app-bar space"></div>
        <!-- <v-card color="grey lighten-4" flat tile> -->
        <div
          class="img-titre"
          v-if="!$route.meta.hideTitle"
        >
          <h1 class="oeasc-titre">Observatoire de l'équilibre agro‑sylvo‑cynégétique</h1>
        </div>
        <!-- menu sur un panneau latéral -->
        <oeasc-drawer :config="configDrawer"></oeasc-drawer>

        <!-- fil d'ariane -->
        <breadcrump></breadcrump>

        <div
          class="main-container"
          id="scrolling-techniques"
          style="margin-top: 50px"
        >
          <!-- contenu de la page, router gére automatiquement les routes inscrites dans router/index.js -->
          <!-- mais dans cette appli on récupère aussi les roude dans modules/index.js et pages/index.js -->
          <router-view></router-view>
          <!-- Le Snackbar Global -->
          <!-- Le Snackbar qui affichera les messages d'erreur ou de succès-->
          <v-snackbar
            v-model="snackbarState.show"
            :color="snackbarState.color"
            :timeout="snackbarState.timeout"
            min-height="100px"
            elevation="2"
            bottom
            center
          >
            <span
              :style="{
                whiteSpace: 'pre-line',
                fontSize: snackbarState.fontSize,
                fontWeight: snackbarState.fontWeight,
                lineHeight: snackbarState.lineHeight,
                color: snackbarState.textColor,
              }"
            >
              {{ snackbarState.message }}
            </span>
            <template v-slot:action="{ attrs }">
              <v-btn
                v-bind="attrs"
                variant="text"
                @click="snackbarState.show = false"
                :style="{ color: snackbarState.textColor, fontSize: '1rem', fontWeight: 400 }"
              >
                Fermer
              </v-btn>
            </template>
          </v-snackbar>
        </div>
      </div>
    </div>
    <!-- <pre>CONFIG:::{{ JSON.stringify(test_affichage_config, null, 2) }}</pre> -->
    <!-- <pre>session:::{{ JSON.stringify(test_affichage_session, null, 2) }}</pre> -->
    <!-- <pre>STORE::: {{ JSON.stringify(test_affichage_store, null, 2) }}</pre> -->
    <!-- <pre>STORE_MUTATION::: {{ JSON.stringify(test_store_mutation, null, 2) }}</pre> -->
    <!-- <pre>STORE_ACTION::: {{ JSON.stringify(test_store_action, null, 2) }}</pre> -->
  </v-app>
</template>

<script>
import { config } from '@/config/config.js'; // rassemble les config (map, style, menu)
import { snackbarStore } from '@/store/snackbar.js'; // store pour le snackbar global
import { configAppBar, configDrawerMenus } from '@/config/menu.js'; // config du menu, liste, position et droits
import '@/core/css/main.scss';
import oeascAppBar from '@/components/app/app-bar'; // template de la barre de menu
import oeascDrawer from '@/components/app/drawer';
import breadcrump from '@/components/app/breadcrump';

// si la page a la prop page,
// les routes sont définies dans modules/index.js et pages/index.js
// si elle n'a pas la prop page, le template des page est dans modules/content/content.vue
// sinon le template est dans nom_modules/nom_component

export default {
  compatConfig: { MODE: 3 }, // verrouille les acquis Phase 4 (composant testé sans warning au 2026-07-10)
  name: 'App',
  components: { oeascAppBar, oeascDrawer, breadcrump },

  computed: {
    test_affichage_store() {
      // a retirer. C'est pour voir le contenu du store sans l'objet _user  }
      const { ...rest } = this.$store.state;
      return rest;
    },
    snackbarState() {
      return snackbarStore.state;
    },
  },

  data() {
    return {
      loading: true,
      drawer: false,
      menus: config.menus,
      userIcon: 'person',
      configAppBar: configAppBar,
      configDrawer: {
        menus: configDrawerMenus,
        show: false,
      },
      snackbar: {
        show: false,
        message: '',
        color: 'error', // 'success', 'info', etc.
      },
      drawerShow: false,
      test_affichage_session: this.$session, // a retirer. C'est pour voir le contenu de la session
      test_affichage_config: config, // a retirer. C'est pour voir le contenu de config
      // test_affichage_store: this.$store.state, // a retirer. C'est pour voir le contenu du store
      test_store_mutation: this.$store._mutations, // a retirer. C'est pour voir le contenu des mutations du store
      test_store_action: this.$store._actions, // a retirer. C'est pour voir le contenu des mutations du store
      // test_store_unique: this.$store.configDrawer
    };
  },

  watch: {
    $route() {
      // si changement de page on lance la fonction process
      this.process();
    },
  },

  methods: {
    process() {
      this.loading = true;
      return this.$store
        .dispatch('testConnexion', {})
        .then(
          // verifie si l'utilisateur est connecté
          (user) => {
            this.$store.commit('user', user); // met à jour les données de l'utilisateur
            this.checkRigths(); //
            // titre
            this.setTitle();
            return user;
          },
          (error) => {
            // si erreur on déconnecte l'utilisateur
            this.$store.commit('user', {});
            this.checkRigths();
            // titre
            this.setTitle();
            // rethrow to allow callers to handle the error if needed
            throw error;
          }
        )
        .finally(() => {
          this.loading = false;
        });
    },
    setTitle() {
      // modifie le titre de la page
      const title = this.$route.meta.title || this.$route.meta.label;
      document.title = title ? `OEASC - ${title}` : 'OEASC';
    },
    checkRigths() {
      // vefifie l'accès en fonction de la valeur access dans le index.js de chaque module
      const access = this.$route.meta.access;
      const droitMax = this.$store.getters.droitMax;

      if (!access) {
        return;
      }

      if (access > droitMax) {
        // si les droit ne sont pas suffisant on redirige vers la page de login
        this.$router.push({
          name: 'user.login',
          query: { redirect: this.$route.fullPath },
        });
      }
    },
  },
  // permet de garder les données de l'utilisateur en cas de rechargement de la page
  // notamment pour les droits d'accès et le menu espace utilisateur
  created: function () {
    // a la creation de la page on lance la fonction process.
    this.process();
  },
};
</script>

<style lang="scss" scoped>
table.v-table tbody td {
  font-size: 5px !important;
}
</style>
