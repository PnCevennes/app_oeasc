<template>
  <div>
    <v-dialog persistent max-width="600px" v-model="deleteModal">
      <v-card>
        <v-card-title>
          <v-icon large>warning</v-icon>
          Êtes vous sûr de vouloir supprimer la ligne?
        </v-card-title>

        <v-card-text>
          <v-checkbox
            dense
            tiny
            v-model="deleteWithoutWarning"
            label="Ne plus afficher ce message avant la suppression"
          ></v-checkbox>
        </v-card-text>

        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn
            color="green darken-1"
            text
            @click="
              deleteRow(idToDelete);
              idToDelete = null;
              deleteModal = false;
            "
          >
            Oui
          </v-btn>

          <v-btn
            color="green darken-1"
            text
            @click="
              idToDelete = null;
              deleteModal = false;
            "
          >
            Non
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
    <v-card>
      <v-card-title>
        {{ configTable.title }}
        <v-spacer></v-spacer>
      </v-card-title>
  {{options}}

      <v-data-table
        :options.sync="options"
        :class="configTable.classes"
        :headers="configTable.headers"
        :items="filteredItems"
        multi-sort
        :dense="configTable.dense"
        :loading="!configTable.items"
        :server-items-length="itemsServerCount"
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
              <v-tooltip top>
                <template v-slot:activator="{ on }">
                  <v-btn
                    v-on="on"
                    v-if="header.value == 'actions'"
                    color="primary"
                    icon
                    @click="edit('actions')"
                    ><v-icon>fa-plus</v-icon></v-btn
                  >
                </template>
                <span>Ajouter une nouvelle ligne au tableau</span>
              </v-tooltip>
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
              <template
                v-for="(action, indexAction) of props.header.list || []"
              >
                <v-btn
                  small
                  v-if="
                    !action.condition ||
                      action.condition({ $store, item: props.item })
                  "
                  :key="indexAction"
                  icon
                  :to="
                    typeof action.to == 'function'
                      ? action.to({ item: props.item, $store })
                      : action.to
                  "
                  :title="action.title"
                  @click="
                    action.click &&
                      action.click(props.item[configTable.idFieldName])
                  "
                >
                  <v-icon small>{{ action.icon }}</v-icon>
                </v-btn>
              </template>
            </div>

            <div v-if="bEditCell(props)">
              <v-btn
                v-if="value != 'actions'"
                small
                @click="edit(value, props.item[configTable.idFieldName])"
              >
                <span v-html="displayCell(props, value)"></span>
                <!-- {{ displayCell(props, value) }} -->
              </v-btn>
            </div>
            <div v-else>
              <span v-html="displayCell(props, value)"></span>
              <!-- {{ displayCell(props, value) }} -->
            </div>
          </div>
        </template>
      </v-data-table>
    </v-card>
    <v-snackbar color="error" v-model="bError" :timeout="5000">
      {{ msgError }}
    </v-snackbar>
    <v-dialog persistent max-width="1400px" v-model="bEditDialog">
      <v-card>
        <genericForm
          class="edit-dialog"
          v-if="configForm && bEditDialog"
          :config="configForm"
        ></genericForm>
      </v-card>
    </v-dialog>
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
    options: {},
    configTable: {},
    searchs: {},
    saveValue: null,
    msgError: null,
    bError: false,
    idToDelete: null,
    deleteModal: null,
    deleteWithoutWarning: false,
    configForm: null,
    bEditDialog: false,
    itemsServerCount: null
  }),
  watch: {
    config: {
      handler() {
        this.initConfig();
      },
      deep: true
    },
    searchs: {
      handler() {
        this.loadData(false);
      },
      deep: true
    },

    options() {
      this.loadData(false);
    }
  },
  methods: {
    onSearchChange() {},
    displayCell(props, value) {
      const res =
        props.item &&
        (typeof props.header.display == "function"
          ? props.header.display(props.item, { $store: this.$store })
          : props.item[value]);
      return res;
    },
    bEditCell(props) {
      return (
        props.header.edit &&
        (!props.header.edit.condition ||
          props.header.edit.condition({
            $store: this.$store,
            baseModel: props.item
          }))
      );
    },
    getConfigForm(value, id) {
      const item = this.configTable.items.find(
        item => item[this.configTable.idFieldName] === id
      );
      const header = this.configTable.headers.find(
        header => header && header.value == value
      );
      const label = header.text;
      if (!header.edit) {
        return null;
      }
      const configForm = copy(header.edit);

      if (value != "actions") {
        configForm.title = `Modifier ${header.text} pour ${
          item[this.configTable.labelFieldName || this.configTable.idFieldName]
        }`;
        configForm.label = label;
      }
      configForm.idFieldName =
        configForm.idFieldName || this.configTable.idFieldName;
      configForm.value = copy(item) || configForm.value;
      configForm.switchDisplay = false;
      configForm.displayValue = false;
      configForm.cancel = {
        action: () => {
          this.cancel(value, item && item[this.configTable.idFieldName]);
          this.closeDialog();
        }
      };
      if (configForm.action && configForm.action.onSuccess) {
        configForm.action.onSuccess2 = configForm.action.onSuccess;
      } else {
        configForm.action = configForm.action || {};
      }
      configForm.action.onSuccess = ({ data }) => {
        configForm.action.onSuccess2 && configForm.action.onSuccess2({ data });

        let elem = this.configTable.items.find(
          item =>
            item[this.configTable.idFieldName] ==
            data[this.configTable.idFieldName]
        );

        if (!elem) {
          elem = {};
          this.configTable.items.push(elem);
        }

        const processedData = this.configTable.preProcess
          ? this.configTable.preProcess({ data: [data] })[0]
          : data;

        for (const key of Object.keys(processedData)) {
          elem[key] = processedData[key];
        }

        this.closeDialog();
      };
      return configForm;
    },
    cancel(value, id) {
      if (!id) {
        return;
      }
      const elem = this.configTable.items.find(
        item => item[this.configTable.idFieldName] == id
      );
      for (const key of Object.keys(this.saveVal)) {
        elem[key] = this.saveVal[key];
      }
    },
    edit(value, id) {
      this.closeDialog();
      this.configForm = this.getConfigForm(value, id);
      this.saveVal = id
        ? copy(
            this.configTable.items.find(
              item => item[this.configTable.idFieldName] == id
            )
          )
        : null;
      this.bEditDialog = !!this.configForm;
    },

    deleteRow(id) {
      const index = this.configTable.items.findIndex(
        d => d[this.configTable.idFieldName] == id
      );
      if (index !== -1) {
        if (this.configTable.delete) {
          this.configTable.delete(id, { $store: this.$store }).then(
            () => {
              this.configTable.items.splice(index, 1);
            },
            err => {
              this.bError = true;
              this.msgError = err;
            }
          );
        } else {
          this.configTabel.items.splice(index, 1);
        }
      }
    },
    closeDialog() {
      this.bEditDialog = false;
    },
    initConfig() {
      const config = copy(this.config);
      config.loaded = false;
      config.stores = {};

      if (config.storeName) {
        const configStore = this.$store.getters.configStore(config.storeName);
        config.serverSide = configStore.serverSide;
        config.idFieldName = configStore.idFieldName;
        this.options = {
          ...this.options,
          ...(configStore.options || {})
        };
        config.displayFieldName =
          config.displayFieldName || configStore.displayFieldName;
        config.delete = (id, { $store }) => {
          return $store.dispatch(configStore.delete, { value: id });
        };
        config.stores.items = config.storeName;
        if (!config.headerDefs.actions) {
          config.headerDefs.actions = {
            noSearch: true,
            width: "90px",
            text: "Actions",
            sortable: false,
            edit: config.configForm,
            list: [
              {
                title: "Editer la ligne",
                icon: "mdi-pencil",
                click: id => this.edit("actions", id)
              },
              {
                title: "Supprimer la ligne",
                icon: "mdi-trash-can",
                click: id => {
                  if (!this.deleteWithoutWarning) {
                    this.idToDelete = id;
                    this.deleteModal = true;
                  } else {
                    this.deleteRow(id);
                  }
                }
              }
            ]
          };
        }

        // surveille storeNames pour rester à jour????
        // this.$store.watch(
        //   () => {
        //     return this.$store.state[configStore.storeNames];
        //   },
        //   (new_value, old_value) => {
        //     new_value;
        //     old_value;
        //     this.loadData(!this.configTable.loaded);
        //   },
        //   {
        //     // deep: true,
        //   }
        // );
      }
      /** contruction de la variable header */
      const headers = [];

      for (const [value, header] of Object.entries(config.headerDefs)) {
        header.value = value;
        if (header.type == "date") {
          // header.sort = sortDate;
          sortDate;
          header.display = a =>
            a && a[header.value].includes("-")
              ? a[header.value]
                  .split("-")
                  .reverse()
                  .join("/")
              : a[header.value];
        }

        if (header.storeName) {
          const configStore = this.$store.getters.configStore(header.storeName);
          header.displayFieldName =
            header.displayFieldName || configStore.displayFieldName;

          /** test pour ne pas avoir deux fois le même store name */
          if (!Object.values(config.stores).includes(header.storeName)) {
            // config.stores[value] = header.storeName;
          }
          if (header.displayFieldName) {
            // on change ça
            header.display = d => {
              if (!d) {
                return "";
              }

              // case secteur.nom_secteur
              const displayFieldNames = header.displayFieldName.split(".");

              let inter = d[header.value];
              if (!inter) {
                return "";
              }
              return displayFieldNames.map(key => inter[key]).join(" ");
            };
          }
          header.sort = (a, b) => {
            const aa = header.display
              ? header.display(a, { $store: this.$store })
              : a;
            const bb = header.display
              ? header.display(b, { $store: this.$store })
              : b;
            return aa == bb ? 0 : aa < bb ? -1 : 1;
          };
        }
        if (!header.condition || header.condition({ $store: this.$store })) {
          headers.push(header);
        }
      }

      /** on place actions en début de liste */
      const headerActionsIndex = headers.findIndex(h => h.value === "actions");
      if (headerActionsIndex != -1) {
        const headerActions = headers[headerActionsIndex];
        headers.splice(headerActionsIndex, 1);
        headers.unshift(headerActions);
      }

      config.headers = headers;

      config.classes = {
        "small-table": config.small,
        striped: config.striped
      };

      /** preloadData with promises from storeNames */
      if (Object.keys(config.stores).length) {
        config.preloadData = ({ $store }) => {
          const promises = [];
          for (const storeName of Object.values(config.stores)) {
            const configStore = this.$store.getters.configStore(storeName);

            // on ajoute __like apres les clés de filtres
            // pour pouvoir filtrer en ilike ensuite
            const searchOptions = {};
            for (const [keySearch, valueSearch] of Object.entries(
              this.searchs || {}
            )) {
              const header = this.configTable.headers.find(h => h.value === keySearch)
              let key = header.displayFieldName ? `${keySearch}.${header.displayFieldName}` : keySearch
              searchOptions[`${key}__ilike`] = valueSearch;
            }

            // on change les clé de tri pour les storeName
            const sortBy = [...this.options.sortBy]
            for (const [index, keySort] of this.options.sortBy.entries()) {
              const header = this.configTable.headers.find(h => h.value === keySort)
              if (header.displayFieldName) {
                sortBy[index] = `${this.options.sortBy[index]}.${header.displayFieldName}`;
              }
            }

            const options =
              storeName == config.storeName && configStore.serverSide
                ? {
                    ...this.options,
                    notCommit: true,
                    ...searchOptions,
                    sortBy,
                    serverSide: true
                  }
                : {};
            promises.push($store.dispatch(configStore.getAll, options));
          }
          return Promise.all(promises);
        };
      }

      /** preProcess from headerDefs */
      if (config.headers.some(h => h.preProcess)) {
        config.preProcess = ({ data }) => {
          return data.map(d => {
            for (const header of this.configTable.headers.filter(
              h => h.preProcess
            )) {
              d[header.value] = header.preProcess(d);
            }
            return d;
          });
        };
      }

      this.configTable = config;
      this.loadData(this.configTable.loaded);
    },
    loadData(loaded) {
      /** call preloadData */
      if (this.configTable.preloadData && !loaded) {
        this.configTable.preloadData({ $store: this.$store }).then(
          res => {
            for (const [index, key] of Object.keys(
              this.configTable.stores
            ).entries()) {
              if (key == "items") {
                let items = res[index];

                // sortie du
                if (items && items.items) {
                  this.itemsServerCount = items.total_filtered;
                  items = items.items;
                } else if (items) {
                  this.itemsServerCount = items.length;
                }

                if (items) {
                  this.configTable.items = this.configTable.preProcess
                    ? this.configTable.preProcess({ data: items })
                    : items;
                }
              }
            }
            this.configTable.loaded = true;
            this.configTable = copy(this.configTable);
          },
          error => {
            this.msgError = error;
            this.bError = true;
          }
        );
      }
    }
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
            ? header.display(item, { $store: this.$store })
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
