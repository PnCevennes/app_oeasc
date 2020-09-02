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
        ></v-text-field>-->
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
            <td v-for="header of configTable.headers" :key="header.value">
              <v-text-field
                v-if="!header.noSearch"
                dense
                v-model="searchs[header.value]"
                type="text"
              ></v-text-field>
            </td>
          </tr>
        </template>
        <template
          v-for="(value, index) of (configTable.headers || []).map(
            header => header.value
          )"
          #[`item.${value}`]="props"
        >
          <div :key="index">
            <div v-if="value == 'actions'">
              <template v-for="(action, indexAction) of props.header.list || []">
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
                  <v-icon small>{{ action.icon }}</v-icon>
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
              <v-btn small @click="openEditDialog(value, props.item[configTable.id])">
                {{
                (typeof props.header.display == 'function' &&
                props.header.display(props.item[value], {$store})) ||
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
              (typeof props.header.display == 'function' &&
              props.header.display(props.item[value], {$store})) ||
              props.item[value]
              }}
            </div>
          </div>
        </template>
      </v-data-table>
    </v-card>
        <v-snackbar color="error" v-model="bError" :timeout="5000">
      {{
      msgError
      }}
    </v-snackbar>

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
    saveValue: null,
    msgError: null,
    bError: false,
  }),
  watch: {
    config: {
      handler() {
        this.initConfig();
      },
      deep: true,
    },
  },
  methods: {
    configForm(item, value) {
      const header = this.configTable.headers.find(
        (header) => header.value == value
      );
      if (!header.edit) {
        return {};
      }
      const configForm = copy(header.edit);
      configForm.title = `Modifier ${header.text} pour ${
        item[this.configTable.labelFieldName || this.configTable.idFieldName]
      }`;
      configForm.value = item;
      configForm.cancel = {
        action: () => {
          this.cancel(value, item[this.configTable.id]);
          this.closeDialog();
        },
      };
      configForm.formDefs[value].label = `${header.text}`;

      if (configForm.action.onSuccess) {
        configForm.action.onSuccess2 = configForm.action.onSuccess;
      }
      configForm.action.onSuccess = (data) => {
        configForm.action.onSuccess2 && configForm.action.onSuccess2(data);
        this.closeDialog();
      };
      return configForm;
    },
    cancel(value, id) {
      this.configTable.items.find((item) => item[this.configTable.id] == id)[
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
        (item) => item[this.configTable.id] == id
      )[value];
    },
    initConfig() {
      const config = copy(this.config);
      config.loaded = false;
      config.storeList = {};

      if (config.storeName) {
        config.storeList.items = config.storeName;
      }

      const headers = [];
      this.bEditDialogs = {};
      for (const [value, header] of Object.entries(config.headers)) {
        this.bEditDialogs[value] = {};
        header.value = value;
        if (header.type == "date") {
          header.sort = sortDate;
          header.display = (a) =>
            a && a.includes("-") ? a.split("-").reverse().join("/") : a;
        }

        if (header.storeName) {
          if(!Object.values(config.storeList).includes(header.storeName)) {
            config.storeList[value] = header.storeName;
          }
          if (header.displayFieldName) {
            header.display = (id, { $store }) =>
              ($store.getters[header.storeName](id) || {})[
                header.displayFieldName
              ];
          }
          header.sort = (a, b) => {
            const aa = header.display ? header.display(a, {$store: this.$store}) :a;
            const bb = header.display ? header.display(b, {$store: this.$store}) :b;
            return aa == bb ? 0 : aa < bb ? -1 : 1;
          }
        }

        if (!header.condition || header.condition({ $store: this.$store })) {
          headers.push(header);
        }
      }

      config.headers = headers;
      config.classes = {
        "small-table": config.small,
        striped: config.striped,
      };

      if (Object.keys(config.storeList).length) {
        config.preloadData = ({ $store }) => {
          const actions = [];
          for (const storeName of Object.values(config.storeList)) {
            const storeNames = `${storeName}s`;
            const namesCapitalized =
              `${storeNames}`.charAt(0).toUpperCase() + storeNames.slice(1);
            actions.push($store.dispatch(`get${namesCapitalized}`));
          }
          return Promise.all(actions);
        };
      }

      if (config.headers.some((h) => h.preProcess)) {
        config.preProcess = ({data}) => {
          return data.map(d => {
            for (const header of this.configTable.headers.filter(h => h.preProcess)) {
              d[header.value] = header.preProcess(d)
            }
            return d;
          });
        };
      }

      this.configTable = config;

      if (this.configTable.preloadData && !this.configTable.loaded) {
        config.preloadData({ $store: this.$store }).then(
          (res) => {
            for (const [index, key] of Object.keys(
              this.configTable.storeList
            ).entries()) {
              if (key == "items") {
                const items = res[index];
                if (items) {
                  this.configTable.items = this.configTable.preProcess
                    ? this.configTable.preProcess({ data: items })
                    : items;
                }
              }
            }
            // this.configTable = copy(this.configTable)
            this.configTable.loaded = true;
            this.configTable = copy(this.configTable);
          },
          (error) => {
            console.log("process error", error);
            this.msgError = error;
            this.bError=true;
          }
        );
      }
    },
  },
  computed: {
    filteredItems() {
      if (!this.configTable.items) {
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

          const val = header.display
            ? header.display(item[header.value])
            : item[header.value];
          cond =
            cond && String(val).toLowerCase().includes(search.toLowerCase());
        }
        if (cond) {
          filteredItems.push(item);
        }
      }
      return filteredItems;
    },
  },
  mounted() {
    this.initConfig();
  },
};
</script>
