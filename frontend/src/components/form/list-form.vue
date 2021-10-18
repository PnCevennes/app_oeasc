<template>
  <span>
    <div v-if="!items">{{ info.msg }}</div>
    <span v-else-if="config.displayValue">
      <span>{{ valueDisplay }}</span>
    </span>

    <div v-else>
      <div class="list-form">
        <div v-if="config.list_type === 'button'">
          <div class="select-list-label">{{ config.label }}</div>
          <v-btn-toggle
            v-model="baseModel[config.name]"
            @change="change($event)"
            dense
          >
            <v-btn
              :value="item[config.valueFieldName]"
              v-for="(item, index) of items"
              :key="index"
              >{{ item[config.displayFieldName] }}</v-btn
            >
          </v-btn-toggle>
        </div>

        <!-- select -->
        <div v-else-if="config.list_type === 'combobox'">
          <v-combobox
            ref="autocomplete"
            :id="`form-${config.name}`"
            clearable
            v-model="baseModel[config.name]"
            :items="items"
            :label="config.label"
            :required="config.required ? true : false"
            :multiple="config.multiple ? true : false"
            :item-value="config.valueFieldName"
            :item-text="config.displayFieldName"
            :rules="config.rules"
            :chips="config.multiple ? true : false"
            dense
            :small-chips="config.multiple ? true : false"
            :deletable-chips="config.multiple ? true : false"
            :search-input.sync="search"
            :placeholder="config.placeholder"
            :filter="config.dataReloadOnSearch && customFilter"
            @change="change($event)"
            :return-object="config.returnObject ? true : false"
            :disabled="config.disabled"
            @blur="onBlur($event)"
            no-data-text
          >
            <span slot="label">
              {{ config.label }}
              <i v-if="config.multiple">(plusieurs réponses possibles)</i>
              <span v-if="config.required" class="required">*</span>
            </span>
          </v-combobox>
        </div>
        <div v-else-if="config.list_type === 'autocomplete'">
          <v-autocomplete
            ref="autocomplete"
            :id="`form-${config.name}`"
            clearable
            v-model="baseModel[config.name]"
            :items="items"
            :label="config.label"
            :required="config.required ? true : false"
            :multiple="config.multiple ? true : false"
            :item-value="config.valueFieldName"
            :item-text="config.displayFieldName"
            :rules="config.rules"
            :chips="config.multiple ? true : false"
            dense
            :small-chips="config.multiple ? true : false"
            :deletable-chips="config.multiple ? true : false"
            :search-input.sync="search"
            :placeholder="config.placeholder"
            :filter="config.dataReloadOnSearch && customFilter"
            @change="change($event)"
            :return-object="config.returnObject ? true : false"
            :disabled="config.disabled"
            no-data-text="Pas de donnée disponible"
          >
            <span slot="label">
              {{ config.label }}
              <i v-if="config.multiple">(plusieurs réponses possibles)</i>
              <span v-if="config.required" class="required">*</span>
            </span>

            <help
              slot="prepend"
              :code="`form-${config.name}`"
              v-if="config.help"
            ></help>
          </v-autocomplete>
        </div>

        <div v-else-if="config.list_type === 'select'">
            <!-- {{`form-${config.name}`}} -->

          <v-select
            :id="`form-${config.name}`"
            clearable
            dense
            v-model="baseModel[config.name]"
            :items="items"
            :label="config.label"
            :required="config.required ? true : false"
            :multiple="config.multiple ? true : false"
            :item-value="config.valueFieldName"
            :item-text="config.displayFieldName"
            :rules="config.rules"
            :return-object="config.returnObject ? true : false"
            :disabled="config.disabled"
            @change="change($event)"
          >
            <span slot="label">
              {{ config.label }}
              <i v-if="config.multiple">(plusieurs réponses possibles)</i>
              <span v-if="config.required" class="required">*</span>
            </span>
            <help
              slot="prepend"
              :code="`form-${config.name}`"
              v-if="config.help"
            ></help>
          </v-select>
        </div>

        <!-- checkbox ou radio -->
        <div v-else>
          <!-- checkbox -->
          <div v-if="config.multiple">
            <v-container fluid>
              <div class="select-list-label-container" v-if="!!config.label">
                <span class="select-list-label">{{ config.label }}</span>
                <span v-if="config.required" class="required">*</span>
                <help :code="`form-${config.name}`" v-if="config.help"></help>
                <br />
                <i>(plusieurs réponses possibles)</i>
              </div>
              <v-checkbox
                v-for="(item, index) in items"
                :key="index"
                v-model="baseModel[config.name]"
                :hide-details="index < items.length - 1 ? true : false"
                :value="
                  (config.returnObject && item) || item[config.valueFieldName]
                "
                :label="item[config.displayFieldName]"
                dense
                :rules="config.rules"
                :disabled="config.disabled"
                @change="change($event)"
              ></v-checkbox>
              <help
                class="help-radio-item"
                :code="`item-${item[config.valueFieldName]}`"
                v-if="config.helps"
              ></help>
            </v-container>
          </div>

          <!-- radio -->
          <div v-else>
            <v-container fluid>
              <div class="select-list-label-container" v-if="!!config.label">
                <span class="select-list-label">{{ config.label }}</span>
                <span v-if="config.required" class="required">*</span>
                <help :code="`form-${config.name}`" v-if="config.help"></help>
              </div>
              <v-radio-group
                v-model="baseModel[config.name]"
                :rules="config.rules"
              >
                <template v-for="item in items">
                  <div
                    :key="item[config.valueFieldName]"
                    style="position: relative"
                  >
                    <div class="radio">
                      <v-radio
                        :value="
                          (config.returnObject && item) ||
                            item[config.valueFieldName]
                        "
                        :label="item[config.displayFieldName]"
                        :disabled="config.disabled"
                        @change="change($event)"
                      ></v-radio>
                    </div>
                    <help
                      class="help-radio-item"
                      :code="`list-${item[config.valueFieldName]}`"
                      v-if="
                        config.helps &&
                          !(
                            config.helps.except &&
                            config.helps.except.includes(item.cd_nomenclature)
                          )
                      "
                    ></help>
                  </div>
                </template>
              </v-radio-group>
            </v-container>
          </div>
        </div>
      </div>
    </div>
  </span>
</template>

<script>
import help from "./help";
import { apiRequest } from "@/core/js/data/api.js";

export default {
  name: "lisForm",
  components: { help },
  data: () => ({
    items: null,
    info: {
      status: "loading",
      msg: "Chargement des données"
    },
    defaultConfig: {
      valueFieldName: "value",
      displayFieldName: "text"
    },
    search: "",
    dataItems: null
  }),
  watch: {
    search() {
      if (this.config.dataReloadOnSearch) {
        this.getData();
      }
    },
    baseModel: {
      handler() {},
      deep: true
    },
    config() {
      this.setDefaultConfig();
    }
  },
  methods: {
    onBlur(event) {
        console.log(event, this.items)
    },
    change(event) {
      // cas combobox && string && returnObject =>
      //  value = { <valueFieldName>: null, <displayFieldName>: <current_value>}

      if (this.config.list_type == "combobox" && this.config.returnObject) {
        let values = this.baseModel[this.config.name];
        values = this.config.multiple ? values : [values];

        values = values
          .map(value => {
            if (typeof value === "string") {
              const elem = this.items.find(
                item => item[this.config.displayFieldName] == value
              );
              if (elem) {
                return elem;
              }
              const v = {};
              v[this.config.valueFieldName] = null;
              v[this.config.displayFieldName] = value;
              return v;
            }
            return value;
          })
          .filter((item, pos, self) => {
            const index = self.findIndex(
              e =>
                (e[this.config.valueFieldName] &&
                  e[this.config.valueFieldName] ==
                    item[this.config.valueFieldName]) ||
                e[this.config.displayFieldName] ==
                  item[this.config.displayFieldName]
            );
            return index == pos;
          });
        this.baseModel[this.config.name] = this.config.multiple
          ? values
          : values[0];
      }

      this.config.change &&
        this.config.change({
          baseModel: this.baseModel,
          config: this.config,
          $store: this.$store,
          $event: event
        });
    },
    customFilter(item, queryText) {
      item + queryText;
      return true;
    },
    processItems: function() {
      let items = this.config.processItems
        ? this.config.processItems({
            dataItems: this.dataItems,
            config: this.config,
            baseModel: this.baseModel
          })
        : this.dataItems;

      // filtre des donnés avec config.filters
      if (this.config.filters) {
        items = items.filter(elem =>
          Object.entries(this.config.filters).every(([key, values]) => {
            return values.includes(elem[key]);
          })
        );
      }
      this.items = items;
      // this.setInitSearch();
      // patch search
    },

    setInitSearch() {
      const value =
        this.baseModel[this.config.name] &&
        this.baseModel[this.config.name][this.config.displayFieldName];
      if (
        ["autocomplete", "combobox"].includes(this.config.list_type) &&
        this.config.returnObject &&
        !this.search &&
        value
      ) {
        this.search = value;
      }
    },

    clickChips() {
      setTimeout(() => {
        const chips =
          this.$refs.autocomplete &&
          this.$refs.autocomplete.$el.getElementsByClassName("v-chip");
        chips && chips.length && chips[0].click();
      }, 10);
    },
    setDefaultConfig() {
      if (this.config.storeName) {
        const configStore = this.$store.getters.configStore(
          this.config.storeName
        );
        this.defaultConfig.valueFieldName =
          this.config.valueFieldName || configStore.idFieldName;
        this.defaultConfig.displayFieldName =
          this.config.displayFieldName || configStore.displayFieldName;
      }

      for (const key in this.defaultConfig) {
        this.config[key] = this.config[key] || this.defaultConfig[key];
      }
    },

    getData: function() {
      let promise = null;
      if (this.dataItems && !this.config.dataReloadOnSearch) {
        this.processItems();
      } else if (this.config.storeName) {
        const configStore = this.$store.getters.configStore(
          this.config.storeName
        );

        const params = {
          notCommit: this.config.dataReloadOnSearch,
          sortBy: [this.config.displayFieldName],
          sortDesc: [false],
          itemsPerPage: this.config.dataReloadOnSearch ? 10 : -1,
          ...this.config.params
        };
        if (this.config.dataReloadOnSearch && this.search) {
          params[`${this.config.displayFieldName}__ilike`] = this.search || "";
        }
        promise = this.$store.dispatch(configStore.getAll, params);
        this.config.valueFieldName = configStore.idFieldName;
        this.config.displayFieldName =
          this.config.displayFieldName || configStore.displayFieldName;
      } else if (this.config.url) {
        const url =
          typeof this.config.url === "function"
            ? this.config.url({
                search: this.search || "",
                baseModel: this.baseModel,
                config: this.config
              })
            : this.config.url;
        promise = apiRequest("GET", url, { params: this.config.params || {} });
      }

      if (promise) {
        promise.then(
          apiData => {
            this.dataItems = apiData.items || apiData;
            this.processItems();
          },
          error => {
            this.info = {
              status: "error",
              msg: error
            };
          }
        );
      }
    },
    autocompleteChange: function(e) {
      e;
    }
  },
  computed: {
    valueDisplay() {
      let values = this.baseModel[this.config.name];
      if (!(values || (this.config.multiple && values && !values.length))) {
        return "";
      }
      values = this.config.multiple ? values : [values];

      if (typeof values[0] == "string") {
        return values.join(", ");
      } else {
        const textArray = (this.items || [])
          .filter(item => {
            return values.includes(item[this.config.valueFieldName]);
          })
          .map(item => item[this.config.displayFieldName]);
        return textArray.join(", ");
      }
    }
  },
  props: ["config", "baseModel"],
  created() {
    this.setDefaultConfig();
  },
  mounted: function() {
    if (this.config.items) {
      if (this.config.items.length && typeof this.config.items[0] != "object") {
        this.dataItems = this.config.items.map(item => ({
          text: item,
          value: item
        }));
      } else {
        this.dataItems = this.config.items;
      }
    }
    this.setInitSearch();

    this.getData();
  }
};
</script>

<style lang="scss" scoped>
.md-checkbox,
.md-radio {
  display: flex;
}
.radio {
  display: inline-block;
}
</style>
