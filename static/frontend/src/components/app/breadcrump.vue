<template>
  <div>
    <span class="breadcrump">
      <v-breadcrumbs :items="getBreadcrumpList"></v-breadcrumbs>
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
          to: route.path

      });
      return this.breadcrumpList(route.parent, list);
    }
  }
};
</script>
