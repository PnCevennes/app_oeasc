<template>
  <div>
    <div v-if="!items">{{ info.msg }}</div>
    <div v-else-if="config.displayValue">
      <span>{{ valueDisplay }}</span>
    </div>
    <div v-else>
      <div>
        <!-- select -->
        <div v-if="config.display === 'autocomplete'">
          <v-autocomplete
            ref="autocomplete"
            clearable
            v-model="baseModel[config.name]"
            :items="items"
            :label="config.label"
            :required="config.required ? true : false"
            :multiple="config.multiple ? true : false"
            :item-value="config.valueFieldName"
            :item-text="config.textFieldName"
            :rules="config.rules"
            :chips="config.multiple ? true :false"
            dense
            :small-chips="config.multiple ? true :false"
            :deletable-chips="config.multiple ? true :false"
            :search-input.sync="search"
            :placeholder="config.placeholder"
            :filter="config.dataReloadOnSearch && customFilter"
            @change="config.change && config.change($event)"
            :return-object="config.returnObject ? true : false"
            :disabled="config.disabled"
            no-data-text="Pas de donnée disponible"
          >
            <span slot="label"
              >{{ config.label }}
              <i v-if="config.multiple"> (plusieurs réponses possibles)</i>
              <span v-if="config.required" class="required">*</span>
            </span>

            <help
              slot="prepend"
              :code="`form-${config.name}`"
              v-if="config.help"
            ></help>
          </v-autocomplete>
        </div>

        <div v-else-if="config.display === 'select'">
          <v-select
            clearable
            :dense="config.dense"
            v-model="baseModel[config.name]"
            :items="items"
            :label="config.label"
            :required="config.required ? true : false"
            :multiple="config.multiple ? true : false"
            :item-value="config.valueFieldName"
            :item-text="config.textFieldName"
            :rules="config.rules"
            :return-object="config.returnObject ? true : false"
            :disabled="config.disabled"
            @change="
              config.change &&
                config.change({ baseModel, $store, config, event: $event })
            "
          ></v-select>
        </div>

        <!-- checkbox ou radio -->
        <div v-else>
          <!-- checkbox -->
          <div v-if="config.multiple">
            <v-container fluid>
              <div class="select-list-label-container" v-if="!!config.label">
                <span class="select-list-label">
                  {{ config.label }}
                </span>
                <span v-if="config.required" class="required"> *</span>
                <help :code="`form-${config.name}`" v-if="config.help"></help>
                <br>                
                <i>(plusieurs réponses possibles)</i>
              </div>
              
              <v-checkbox
                v-model="baseModel[config.name]"
                v-for="(item, index) in items"
                :hide-details="index < items.length - 1 ? true : false"
                :key="item[config.valueFieldName]"
                :value="
                  (config.returnObject && item) || item[config.valueFieldName]
                "
                :label="item[config.textFieldName]"
                :dense="true"
                :rules="config.rules"
                :disabled="config.disabled"
                @change="
                  config.change &&
                    config.change({ baseModel, $store, config, event: $event })
                "
              ></v-checkbox>
              <help
                      class='help-radio-item'
                :code="`item-${item[config.valueFieldName]}`"
                v-if="config.helps"
              ></help>
            </v-container>
          </div>

          <!-- radio -->
          <div v-else>
            <v-container fluid>
              <div class="select-list-label-container"  v-if="!!config.label">
                <span class="select-list-label">
                  {{ config.label }}
                </span>
                <span v-if="config.required" class="required"> *</span>
                <help :code="`form-${config.name}`" v-if="config.help"></help>
              </div>
              <v-radio-group
                v-model="baseModel[config.name]"
                :rules="config.rules"
              >
                <template v-for="item in items">
                  <div :key="item[config.valueFieldName]"
                style='position: relative'
                  >
                    <div class="degat">
                      <v-radio
                        :value="
                          (config.returnObject && item) ||
                            item[config.valueFieldName]
                        "
                        :label="item[config.textFieldName]"
                        :disabled="config.disabled"
                        @change="
                          config.change &&
                            config.change({
                              baseModel,
                              $store,
                              config,
                              event: $event
                            })
                        "
                      >
                      </v-radio>
                     </div>
                    <help
                      class='help-radio-item'
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
  </div>
</template>

<script>
import help from "./help";
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
      textFieldName: "text"
    },
    search: "",
    dataItems: null
  }),
  watch: {
    search() {
      if (this.config.dataReloadOnSearch && this.search) {
        this.getData();
      }
    },
    baseModel: {
      handler() {
        if (this.config.dataReloadOnSearch && !this.search) {
          this.search = this.baseModel[this.config.name];
        }
        if (
          this.config.dataReloadOnSearch &&
          this.search &&
          !this.baseModel[this.config.name]
        ) {
          this.search = "";
        }

        this.valueDisplay;
      },
      deep: true
    },
    config() {
      this.setDefaultConfig();
    }
  },
  methods: {
    customFilter(item, queryText) {
      item + queryText;
      return true;
      // let text = item[this.config.textFieldName].toLowerCase();
      // let searchText = queryText.toLowerCase();

      // // remove accents
      // const sTransI = "àâäéèêëîïöùûü";
      // const sTransO = "aaaeeeeiiouuu";
      // for (let index = 0; index < sTransI.length; index++) {
      //   searchText = searchText.replace(sTransI[index], sTransO[index]);
      //   text = text.replace(sTransI[index], sTransO[index]);
      // }

      // let cond = false;
      // for (const test of searchText.trim().split(" ")) {
      //   cond = cond || text.includes(test);
      // }
      // return cond;
    },
    processItems: function() {
      this.items = this.config.processItems
        ? this.config.processItems({
            dataItems: this.dataItems,
            config: this.config,
            baseModel: this.baseModel
          })
        : this.dataItems;
      // patch search
      this.clickChips();
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
      for (const key in this.defaultConfig) {
        if (!(key in this.config)) {
          this.config[key] = this.defaultConfig[key];
        }
      }
    },

    getData: function() {
      if (this.dataItems && !this.config.dataReloadOnSearch) {
        this.processItems();
      } else {
        if (this.config.url) {
          // const urlParam = this.config.dataReloadOnSearch
          //   ? this.search || ""
          //   : this.baseModel;

          const url =
            typeof this.config.url === "function"
              ? this.config.url({
                  search: this.search || "",
                  baseModel: this.baseModel
                })
              : this.config.url;

          this.$store
            .dispatch("cacheOrRequest", {
              url
            })
            .then(
              apiData => {
                this.dataItems = apiData;
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
      }
    },
    autocompleteChange: function(e) {
      console.log("change", e);
    }
  },
  computed: {
    valueDisplay() {
      let values = this.baseModel[this.config.name];
      if (!(values || (this.config.multiple && values && !values.length))) {
        return "";
      }
      values = this.config.multiple ? values : [values];
      const textArray = this.items
        .filter(item => {
          return values.includes(item[this.config.valueFieldName]);
        })
        .map(item => item[this.config.textFieldName]);
      return textArray.join(", ");
    }
  },
  props: ["config", "baseModel", "dataItemsIn"],
  created() {
    this.setDefaultConfig();
  },
  mounted: function() {
    if(this.config.multiple && !this.baseModel[this.config.name]) {
      this.baseModel[this.config.name] = [];
    }
    const dataItemsIn = this.dataItemsIn || this.config.items;
    if (dataItemsIn) {
      if (
        dataItemsIn &&
        dataItemsIn.length &&
        typeof dataItemsIn[0] != "object"
      ) {
        this.dataItems = dataItemsIn.map(item => ({
          text: item,
          value: item
        }));
      } else {
        this.dataItems = dataItemsIn;
      }
    }
    if (this.config.dataReloadOnSearch) {
      this.search = this.baseModel[this.config.name];
    }
    this.getData();
  }
};
</script>

<style lang="scss" scoped>
.md-checkbox,
.md-radio {
  display: flex;
}
</style>
