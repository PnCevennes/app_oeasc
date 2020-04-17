<template>
  <div>
    <v-card>
      <v-card-title>
        {{ configTable.title }}
        <v-spacer></v-spacer>
        <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          placeholder="Rechercher..."
          single-line
          hide-details
        ></v-text-field>
        {{ search }}
      </v-card-title>
      {{ configTable.editValues }}
      <v-data-table
        :class="{ striped: config.striped }"
        :headers="configTable.headers"
        :items="configTable.items"
        multi-sort
        :sort-by="configTable.sortBy"
        :sort-desc="configTable.sortDesc"
        :search="search"
        :dense="configTable.dense"
        :loading="!configTable.items"
        loading-text="Chargement en cours... merci de patienter"
      >
        <!-- <template  v-for="(value, index) in configTable.editValues" v-slot:item.id_droit_max="props"> -->
        <template
          v-for="(value, index) of (configTable.headers || []).map(
            header => header.value
          )"
          #[`item.${value}`]="props"
        >
          <div :key="index">
            {{ props.item[value] }}
            <v-btn
              icon
              v-if="props.header.edit && (!props.header.edit.condition || props.header.edit.condition({$store, baseModel: props.item}))"
              @click="openEditDialog(value, props.item[configTable.id])"
            >
              <v-icon>edit</v-icon>
            </v-btn>
            <v-dialog
              persistent
              v-model="bEditDialogs[value][props.item[configTable.id]]"
            >
              <v-card>
                <genericForm
                  v-if="bEditDialogs[value][props.item[configTable.id]]"
                  :config="configForm(props.item, value)"
                ></genericForm>
              </v-card>
            </v-dialog>
          </div>
        </template>
      </v-data-table>
    </v-card>
  </div>
</template>

<script>
import { copy } from "@/core/js/util/util.js";
import { sortDate } from "./util.js";
import genericForm from "@/components/form/generic-form";
import "./table.css";

export default {
  name: "generic-table",
  components: { genericForm },
  props: ["config"],
  data: () => ({
    configTable: {},
    search: "",
    bEditDialogs: null,
    saveValue: null
  }),
  watch: {
    config: {
      handler() {
        this.initConfig();
      },
      deep: true
    }
  },
  methods: {
    configForm(item, value) {
      const header = this.configTable.headers.find(
        header => header.value == value
      );
      if (!header.edit) {
        return {};
      }
      const configForm = copy(header.edit);
      configForm.title = `Modifier ${configForm.text} pour ${
        item[this.configTable.label]
      }`;
      configForm.value = item;
      configForm.cancel = {
        action: () => {
          this.cancel(value, item[this.configTable.id]);
          this.closeDialog();
        }
      };
      configForm.forms[value].label = `${header.text}`;
      configForm.request.onSuccess = () => {
        this.closeDialog();
      };
      return configForm;
    },
    cancel(value, id) {
      this.configTable.items.find(item => item[this.configTable.id] == id)[
        value
      ] = this.saveVal;
    },
    closeDialog() {
      this.bEditDialogs = {};
      for (const key of Object.keys(this.config.headers)) {
        this.bEditDialogs[key] = {};
      }
    },
    openEditDialog(value, id) {
      this.closeDialog();
      this.bEditDialogs[value][id] = true;
      this.saveVal = this.configTable.items.find(
        item => item[this.configTable.id] == id
      )[value];
    },
    initConfig() {
      const config = copy(this.config);

      const headers = [];
      this.bEditDialogs = {};
      for (const [value, header] of Object.entries(config.headers)) {
        this.bEditDialogs[value] = {};
        header.value = value;
        if (header.type == "date") {
          header.sort = sortDate;
        }
        headers.push(header);
      }
      config.headers = headers;
      this.configTable = config;
    }
  },
  computed: {},
  mounted() {
    this.initConfig();
  }
};
</script>
