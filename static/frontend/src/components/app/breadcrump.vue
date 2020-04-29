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
        console.log(list);
        return list;
      }
      const route = this.$router.options.routes.find(
        route => route.name == name
      );
      console.log(name, route, this.$router.options.routes);
      list.unshift({
          text: route.label,
          to: route.path

      });
      return this.breadcrumpList(route.parent, list);
    }
  }
};
</script>

<style lang="css">
/* .breadcrump {
  margin-left: 100px;
} */
</style>
