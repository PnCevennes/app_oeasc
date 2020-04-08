<template>

  <div>
    <div v-if="contentCode">
      <oeasc-content :code="contentCode"></oeasc-content>
    </div>
  </div>
</template>

<script>
import oeascContent from "@/modules/content/content";

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
