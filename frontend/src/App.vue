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
    };
  },

  // permet de garder les données de l'utilisateur en cas de rechargement de la page
  // notamment pour les droits d'accès et le menu espace utilisateur
  created: function () {
    // la session et les droits sont gérés par les gardes du routeur (router/guards.js) :
    // on attend la fin de la navigation initiale avant d'afficher l'application
    this.$router.isReady().then(() => {
      this.loading = false;
    });
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
