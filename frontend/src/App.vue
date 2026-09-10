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
        </div>
      </div>
    </div>

    <!-- Snackbar global : messages d'erreur / succès / info (voir store/snackbar.js).
         Placé directement sous <v-app> (hors .main-container) pour un positionnement
         fixe fiable quel que soit le navigateur. -->
    <v-snackbar
      v-model="snackbarState.show"
      :timeout="snackbarState.timeout"
      location="bottom"
      :max-width="480"
      class="oeasc-snackbar"
      :class="`oeasc-snackbar--${snackbarState.type}`"
      :style="snackbarCustomVars"
    >
      <div class="oeasc-snackbar__inner">
        <v-icon
          class="oeasc-snackbar__icon"
          :icon="snackbarState.icon"
          size="26"
        ></v-icon>
        <div class="oeasc-snackbar__message">{{ snackbarState.message }}</div>
        <button
          type="button"
          class="oeasc-snackbar__close"
          aria-label="Fermer"
          @click="snackbarState.show = false"
        >
          <v-icon
            icon="mdi-close"
            size="20"
          ></v-icon>
        </button>
      </div>
    </v-snackbar>

    <!-- <pre>CONFIG:::{{ JSON.stringify(test_affichage_config, null, 2) }}</pre> -->
    <!-- <pre>session:::{{ JSON.stringify(test_affichage_session, null, 2) }}</pre> -->
    <!-- <pre>STORE::: {{ JSON.stringify(test_affichage_store, null, 2) }}</pre> -->
    <!-- <pre>STORE_MUTATION::: {{ JSON.stringify(test_store_mutation, null, 2) }}</pre> -->
    <!-- <pre>STORE_ACTION::: {{ JSON.stringify(test_store_action, null, 2) }}</pre> -->
  </v-app>
</template>

<script>
import { config } from '@/config/config.js'; // rassemble les config (map, style, menu)
import { snackbarStore } from '@/store/snackbar'; // store pour le snackbar global (même specifier que les autres importateurs → une seule instance)
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
    // Couleur d'accent quand une couleur personnalisée a été passée à snackbarStore.show()
    snackbarCustomVars() {
      if (this.snackbarState.type !== 'custom' || !this.snackbarState.customColor) {
        return {};
      }
      return { '--snackbar-custom-accent': this.snackbarState.customColor };
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

/* ---------------------------------------------------------------------------
   Snackbar global — carte blanche, accent coloré selon le type de message
   --------------------------------------------------------------------------- */
.oeasc-snackbar {
  --snackbar-accent: #64748b;

  &.oeasc-snackbar--success {
    --snackbar-accent: #16a34a;
  }
  &.oeasc-snackbar--error {
    --snackbar-accent: #dc2626;
  }
  &.oeasc-snackbar--info {
    --snackbar-accent: #0284c7;
  }
  &.oeasc-snackbar--warning {
    --snackbar-accent: #d97706;
  }
  &.oeasc-snackbar--custom {
    --snackbar-accent: var(--snackbar-custom-accent, #64748b);
  }

  :deep(.v-snackbar__wrapper) {
    min-height: 0;
    padding: 0;
    background: #ffffff;
    color: #1f2933;
    border: 1px solid rgba(15, 23, 42, 0.08);
    border-left: 4px solid var(--snackbar-accent);
    border-radius: 12px;
    box-shadow:
      0 12px 28px -8px rgba(15, 23, 42, 0.28),
      0 6px 12px -6px rgba(15, 23, 42, 0.16);
    overflow: hidden;
  }

  :deep(.v-snackbar__content) {
    width: 100%;
    padding: 0;
  }
}

.oeasc-snackbar__inner {
  display: flex;
  align-items: flex-start;
  gap: 13px;
  padding: 15px 15px 15px 18px;
}

.oeasc-snackbar__icon {
  flex: 0 0 auto;
  margin-top: 1px;
  color: var(--snackbar-accent);
}

.oeasc-snackbar__message {
  flex: 1 1 auto;
  min-width: 0;
  font-size: 1.08rem;
  font-weight: 500;
  line-height: 1.5;
  color: #1f2933;
  white-space: pre-line;
  word-break: break-word;
}

.oeasc-snackbar__close {
  flex: 0 0 auto;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 28px;
  height: 28px;
  margin: -2px -4px 0 0;
  padding: 0;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: #64748b;
  cursor: pointer;
  transition:
    background-color 0.15s ease,
    color 0.15s ease;

  &:hover {
    background: rgba(15, 23, 42, 0.07);
    color: #1f2933;
  }
  &:focus-visible {
    outline: 2px solid var(--snackbar-accent);
    outline-offset: 1px;
  }
}
</style>
