<!-- Va chercher le contenu d'une page en bdd et l'affiche.
A supprimé lorsque les pages sont repassées en statique. -->
<template>
  <div>
    <div v-if="contentCode">
      <oeasc-content
        :code="contentCode"
        :class="{ page: true, large }"
      ></oeasc-content>
    </div>
  </div>
</template>

<script>
import oeascContent from '@/modules/content/content';
import './page.css';

export default {
  compatConfig: { MODE: 3 }, // verrouille les acquis Phase 4 (composant testé sans warning au 2026-07-10)
  name: 'page',
  props: ['large'],
  components: { oeascContent },
  computed: {
    contentCode() {
      return this.$route.meta.content || this.$route.params.code;
    },
  },
};
</script>
