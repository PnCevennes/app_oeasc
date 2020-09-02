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

export default {
  name: "manage-user",
  components: { genericTable },
  data: () => ({
    users: [],
    bShowMailList: false,
    pathExportUser: `${config.URL_APPLICATION}/api/user/export`,
    configTable: {
      idFieldName: "id_role",
      labelFieldName: "nom_complet",
      title: "Liste des utilisateurs",
      sortBy: ["create_date"],
      sortDesc: [true],
      dense: true,
      striped: true,
      headers: {
        org_mnemo: {
          text: "Organisme",
        },
        nom_complet: {
          text: "Nom, prénom",
        },
        email: {
          text: "E-mail",
        },
        desc_role: {
          text: "Rôle",
          display: (val) => {
            return val.split(" ")[0].split(",")[0];
          },
        },
        id_droit_max: {
          text: "Droits",
          edit: {
            condition: ({ $store, baseModel }) => {
              return $store.getters.droitMax > baseModel.id_droit_max;
            },
            action: {
              preProcess: ({ baseModel }) => {
                return {
                  id_role: baseModel.id_role,
                  id_droit: baseModel.id_droit_max,
                  id_application: config.ID_APPLICATION,
                };
              },
              request: {
                url: "pypn/register/post_usershub/change_application_right",
                method: "POST",
              },
            },
            formDefs: {
              id_droit_max: {
                type: "list_form",
                display: "select",
                items: ({ $store }) =>
                  [1, 2, 3, 4, 5, 6].filter(
                    (droit) => $store.getters.droitMax > droit
                  ),
                required: true,
              },
            },
          },
        },
        nb_declarations: {
          text: "Nb déclarations",
        },
        create_date: {
          text: "Date inscription",
          type: "date",
        },
      },
    },
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
