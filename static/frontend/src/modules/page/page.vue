<template>

  <div>
    <div v-if="contentCode" class='page'>
      <oeasc-content :code="contentCode"></oeasc-content>
    </div>
  </div>
</template>

<script>
import oeascContent from "@/modules/content/content";
import './page.css';

export default {
  name: "page",
  components: { oeascContent },
  computed: {
    contentCode() {
      return this.$route.meta.content;
    }
  }
};
</script>
