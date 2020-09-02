<template>
  <div class="breadcrumbs">
    <span>
      <v-breadcrumbs :items="getBreadcrumpList" class="pa-0"></v-breadcrumbs>
    </span>
  </div>
</template>

<script>
export default {
  name: "breadcrump",
  computed: {
    getBreadcrumpList() {
      const name = this.$route.name;
      return this.breadcrumpList(name, []);
    }
  },
  methods: {
    breadcrumpList(name, list) {
      if (!name) {
        return list;
      }

      const route = this.$router.options.routes.find(
        route => route.name == name
      );
      list.unshift({
        text: route.label,
        to: route.path,
      });
      return this.breadcrumpList(route.parent, list);
    }
  }
};
</script>

<style>
.breadcrumbs {
  padding: 12px;
  padding-bottom: 0px !important;
}
</style>
