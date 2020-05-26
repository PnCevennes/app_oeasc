<template>
  <div>
    <v-card>
      <v-card-title>
        {{ configTable.title }}
        <v-spacer></v-spacer>
        <!-- <v-text-field
          v-model="search"
          append-icon="mdi-magnify"
          placeholder="Rechercher..."
          single-line
          hide-details
        ></v-text-field> -->
        <!-- {{ search }} -->
      </v-card-title>
      {{ configTable.editValues }}
      <v-data-table
        :class="configTable.classes"
        :headers="configTable.headers"
        :items="filteredItems"
        multi-sort
        :sort-by="configTable.sortBy"
        :sort-desc="configTable.sortDesc"
        :dense="configTable.dense"
        :loading="!configTable.items"
        loading-text="Chargement en cours... merci de patienter"
      >
        <template v-slot:body.prepend>
          <tr>
            <td v-for="header in configTable.headers" :key="header.value">
              <v-text-field
                v-if="!header.noSearch"
                dense
                v-model="searchs[header.value]"
                type="text"
              ></v-text-field>
            </td>
          </tr>
        </template>
        <!-- :search="search" -->
        <!-- <template  v-for="(value, index) in configTable.editValues" v-slot:item.id_droit_max="props"> -->
        <template
          v-for="(value, index) of (configTable.headers || []).map(
            header => header.value
          )"
          #[`item.${value}`]="props"
        >
          <div :key="index">
            <div v-if="value == 'actions'">
              <template
                v-for="(action, indexAction) in props.header.list || []"
              >
                <v-btn
                  small
                  v-if="
                    !action.condition ||
                      action.condition({ $store, item: props.item })
                  "
                  :key="indexAction"
                  icon
                  :to="action.to({ item: props.item, $store }) || action.to"
                  :title="action.title"
                >
                  <v-icon small>
                    {{ action.icon }}
                  </v-icon>
                </v-btn>
              </template>
            </div>

            <div
              v-if="
                props.header.edit &&
                  (!props.header.edit.condition ||
                    props.header.edit.condition({
                      $store,
                      baseModel: props.item
                    }))
              "
            >
              <v-btn
                small
                @click="openEditDialog(value, props.item[configTable.id])"
              >
                {{
                  (props.header.display &&
                    props.header.display(props.item[value])) ||
                    props.item[value]
                }}
                <!-- <v-icon small>edit</v-icon> -->
              </v-btn>
              <v-dialog
                persistent
                max-width="800px"
                v-model="bEditDialogs[value][props.item[configTable.id]]"
              >
                <v-card>
                  <genericForm
                    class="edit-dialog"
                    v-if="bEditDialogs[value][props.item[configTable.id]]"
                    :config="configForm(props.item, value)"
                  ></genericForm>
                </v-card>
              </v-dialog>
            </div>
            <div v-else>
              {{
                (props.header.display &&
                  props.header.display(props.item[value])) ||
                  props.item[value]
              }}
            </div>
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
    searchs: {},
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
      configForm.title = `Modifier ${header.text} pour ${
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

      if (configForm.request.onSuccess) {
        configForm.request.onSuccess2 = configForm.request.onSuccess;
      }
      configForm.request.onSuccess = data => {
        configForm.request.onSuccess2 && configForm.request.onSuccess2(data);
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
        if (!header.condition || header.condition({ $store: this.$store })) {
          headers.push(header);
        }
      }
      config.headers = headers;
      config.classes = {
        "small-table": config.small,
        striped: config.striped
      };

      this.configTable = config;
    }
  },
  computed: {
    filteredItems() {
      if(!this.configTable.items) {
        return [];
      }
      const filteredItems = [];
      for (const item of this.configTable.items) {
        var cond = true;
        for (const header of this.configTable.headers) {
          const search = this.searchs[header.value];
          if (!search) {
            continue;
          }
          console.log("search", search);

          const val = header.display
            ? header.display(item[header.value])
            : item[header.value];
          cond =
            cond &&
            String(val)
              .toLowerCase()
              .includes(search.toLowerCase());
        }
        if (cond) {
          filteredItems.push(item);
        }
      }
      return filteredItems;
    }
  },
  mounted() {
    this.initConfig();
  }
};
</script>
