<template>

  <div>
    <div v-if="contentCode"  >
      <oeasc-content :code="contentCode" :class="{page: true, large}"></oeasc-content>
    </div>
  </div>
</template>

<script>
import oeascContent from "@/modules/content/content";
import './page.css';

export default {
  name: "page",
  props: ["large"],
  components: { oeascContent },
  computed: {
    contentCode() {
      return this.$route.meta.content || this.$route.params.code;
    }
  }
};
</script>
