<template>
  <div>
    <h1>Gestion des utilisateurs</h1>
    <div>
      <v-btn class="btn-spaced" color="primary" :href="pathExportUser">Export CSV</v-btn>
      <v-btn class="btn-spaced" color="primary" @click="mailingListClipboard()">
        Mailing list
        <v-icon>mdi-clipboard-text-play-outline</v-icon>
      </v-btn>
      <v-snackbar color="success" v-model="bShowMailList" :timeout="3000">
        La mailling list ({{ mailingList.split(",").length }} adresses) a été
        copiée dans le presse papier
      </v-snackbar>
    </div>

    <div>
      <generic-table :config="configTable"></generic-table>
    </div>
  </div>
</template>

<script>
import { config } from "@/config/config";
import genericTable from "@/components/table/generic-table";
import configUserTable from "./config/table-user.js"

export default {
  name: "manage-user",
  components: { genericTable },
  data: () => ({
    users: [],
    bShowMailList: false,
    pathExportUser: `${config.URL_APPLICATION}/api/user/export`,
    configTable: configUserTable,
  }),
  computed: {
    mailingList() {
      return this.users
        .filter((user) => user.accept_email)
        .map((user) => user.email)
        .join(", ");
    },
  },
  methods: {
    mailingListClipboard() {
      navigator.clipboard.writeText(this.mailingList).then(() => {
        this.bShowMailList = true;
      });
    },
  },
  mounted() {
    this.$store.dispatch("users").then((users) => {
      this.users = users;
      this.configTable = { ...this.configTable, items: users };
    });
  },
};
</script>
