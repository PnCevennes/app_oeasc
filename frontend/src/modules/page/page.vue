<!-- Va chercher le contenu d'une page en bdd et l'affiche.
A supprimé lorsque les pages sont repassées en statique. -->
<template>
  <div>
    <div v-if="contentCode">
      <oeasc-content
        :code="contentCode"
        :class="{ page: true, large: isLarge }"
      ></oeasc-content>
    </div>
  </div>
</template>

<script>
import oeascContent from '@/modules/content/content';
import './page.css';

export default {
  name: 'page',
  components: { oeascContent },
  computed: {
    contentCode() {
      return this.$route.meta.content || this.$route.params.code;
    },
    // certaines pages (tableaux de bord avec graphiques) ont besoin de plus de largeur
    // que la colonne de lecture par défaut (voir large: true dans la config de route concernée)
    isLarge() {
      return !!this.$route.meta.large;
    },
  },
};
</script>
