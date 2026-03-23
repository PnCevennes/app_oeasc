<!-- // Ce composant Vue "app-bar-menu" affiche dynamiquement un menu d'application basé sur une configuration passée en propriété.
// Il utilise Vuetify pour le rendu des boutons, menus déroulants et icônes.
// 
// Props:
//   - config: Un tableau d'objets représentant la structure du menu. Chaque objet peut contenir :
//       - icon: (optionnel) Nom de l'icône à afficher.
//       - label: (optionnel) Libellé du menu.
//       - path: (optionnel) Chemin de navigation associé au menu.
//       - menus: (optionnel) Tableau d'items pour les sous-menus. Chaque item peut être un séparateur ('-') ou un objet avec :
//           - icon: (optionnel) Icône de l'item.
//           - label: (optionnel) Libellé de l'item.
//           - path: (optionnel) Chemin de navigation de l'item.
//           - meta: (optionnel) Métadonnées, dont "access" pour le contrôle d'accès.
//
// Fonctionnement :
//   - Si un menu n'a pas de sous-menus, il est affiché comme un bouton simple (avec icône et/ou label).
//   - Si un menu possède des sous-menus, il est affiché comme un bouton déclenchant un menu déroulant au survol.
//   - Les sous-menus sont filtrés selon le niveau d'accès maximal de l'utilisateur (via $store.getters.droitMax).
//   - Les séparateurs sont affichés avec <v-divider>.
//   - Les transitions et styles sont gérés via Vuetify.
//
// Remarque :
//   - Ce composant est conçu pour être flexible et s'adapter à différentes configurations de menu.
//   - L'utilisation de Vuetify garantit une intégration visuelle cohérente avec le reste de l'application.
affichage du menu de l'application -->

<template>
  <div>
    <template v-for="(menu, indexMenu) of config">
      <v-btn
        :text="!menu.icon || !!menu.label"
        :key="indexMenu"
        v-if="!menu.menus.length"
        :icon="!!menu.icon"
        :to="menu.path"
        class="text-none"
      >
        <v-icon v-if="!!menu.icon">{{ menu.icon }}</v-icon>
        <template v-else>{{ menu.label }}</template>
      </v-btn>
      <v-menu
        offset-y
        transition="slide-x-transition"
        open-on-hover
        :key="indexMenu"
        v-else
      >
        <template v-slot:activator="{ on: bMenu }">
          <v-btn
            v-on="bMenu"
            :text="!menu.icon || !!menu.label"
            :icon="!menu.label && !!menu.icon"
            class="text-none"
          >
            <v-icon>{{ menu.icon }}</v-icon>
            <span v-if="menu.label">{{ menu.label }}</span>
          </v-btn>
        </template>
        <v-list>
          <template v-for="(item, index) in menu.menus">
            <v-list-item
              :key="index"
              :to="item.path"
              v-if="item == '-' || (item.meta && item.meta.access <= $store.getters.droitMax)"
            >
              <v-list-item-icon v-if="item.icon">
                <v-icon v-text="item.icon"></v-icon>
              </v-list-item-icon>
              <v-list-item-title v-if="item.label">{{ item.label }}</v-list-item-title>
              <v-divider v-if="item == '-'"></v-divider>
            </v-list-item>
          </template>
        </v-list>
      </v-menu>
    </template>
  </div>
</template>

<script>
export default {
  name: 'app-bar-menu',
  props: ['config'],
};
</script>
