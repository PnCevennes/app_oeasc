<template>
  <div v-if="items">
    <v-container fluid>
      <div v-for="(item, index) of items" :key="item.id_nomenclature">
        <v-checkbox
          v-model="degatTypes"
          :hide-details="index < items.length - 1 ? true : false"
          :value="item.id_nomenclature"
          :label="item.label_fr"
          :dense="true"
          :rules="[rule]"
          :disabled="freeze"
          @change="updateDegats($event)"
        ></v-checkbox>

        <div
          v-if="
            baseModel.degats.find(
              d =>
                d.id_nomenclature_degat_type === item.id_nomenclature &&
                item.cd_nomenclature !== 'P/C'
            )
          "
          style="margin-left:50px;"
        >
          <div class="flex-container flex-row flex-5">
            <div><i>Essence (3 essences max.) </i></div>
            <div>
              <span v-if="item.cd_nomenclature !== 'ABS'"><i>Gravité</i></span>
            </div>
            <div>
              <span v-if="item.cd_nomenclature !== 'ABS'"><i>Étendue</i></span>
            </div>
            <div>
              <span v-if="item.cd_nomenclature !== 'ABS'"
                ><i>Antériorité</i></span
              >
            </div>
            <div></div>
          </div>
          <div
            class="flex-container flex-row flex-5"
            v-for="degat_essence of baseModel.degats.find(
              d => d.id_nomenclature_degat_type === item.id_nomenclature
            ).degat_essences || []"
            :key="degat_essence.id_nomenclature_degat_essence"
          >
            <div>
              {{
                $store.getters.nomenclature(
                  degat_essence.id_nomenclature_degat_essence
                ).label_fr
              }}
            </div>

            <template v-if="item.cd_nomenclature !== 'ABS'">
              <div>
                {{
                  $store.getters.nomenclature(
                    degat_essence.id_nomenclature_degat_gravite
                  ).label_fr
                }}
              </div>
              <div>
                {{
                  $store.getters.nomenclature(
                    degat_essence.id_nomenclature_degat_etendue
                  ).label_fr
                }}
              </div>
              <div>
                {{
                  $store.getters.nomenclature(
                    degat_essence.id_nomenclature_degat_anteriorite
                  ).label_fr
                }}
              </div>
            </template>
            <template v-else>
              <div></div>
              <div></div>
              <div></div>
            </template>

            <div>
              <v-btn
                small
                icon
                color="error"
                :disabled="freeze"
                @click="
                  removeDegatEssence(
                    item.id_nomenclature,
                    degat_essence.id_nomenclature_degat_essence
                  )
                "
                ><v-icon>mdi-close</v-icon></v-btn
              >
            </div>
          </div>

          <div
            v-if="
              baseModel.degats.find(
                d =>
                  d.id_nomenclature_degat_type === item.id_nomenclature &&
                  item.cd_nomenclature !== 'P/C' &&
                  (d.degat_essences.length === 0 ||
                    showDegatEssenceForm === d.id_nomenclature_degat_type)
              )
            "
          >
            <div v-if="item.cd_nomenclature != 'ABS'">
              Indiquez les essences touchées, et pour chacune d’elle, l’étendue,
              la gravité et l’antériorité des dégâts, puis validez.
            </div>
            <div v-else>
              Indiquez les essences concernées.
            </div>

            <div class="flex-container flex-row flex-5">
              <div>
                <essence-form
                  :config="configDegatEssence(item.cd_nomenclature).essence"
                  :baseModel="degatEssence"
                ></essence-form>
              </div>

              <div>
                <nomenclature-form
                  v-if="item.cd_nomenclature !== 'ABS'"
                  :config="configDegatEssence(item.cd_nomenclature).gravite"
                  :baseModel="degatEssence"
                ></nomenclature-form>
              </div>

              <div>
                <nomenclature-form
                  v-if="item.cd_nomenclature !== 'ABS'"
                  :config="configDegatEssence(item.cd_nomenclature).etendue"
                  :baseModel="degatEssence"
                ></nomenclature-form>
              </div>

              <div>
                <nomenclature-form
                  v-if="item.cd_nomenclature !== 'ABS'"
                  :config="configDegatEssence(item.cd_nomenclature).anteriorite"
                  :baseModel="degatEssence"
                ></nomenclature-form>
              </div>

              <div>
                <v-btn
                  small
                  color="success"
                  :disabled="
                    !degatEssence.essence ||
                      (item.cd_nomenclature !== 'ABS' &&
                        (!degatEssence.gravite ||
                          !degatEssence.etendue ||
                          !degatEssence.anteriorite))
                  "
                  @click="addDegatEssence(item.id_nomenclature)"
                  ><v-icon>mdi-check</v-icon></v-btn
                >
                <v-btn
                  small
                  color="error"
                  @click="cancelDegatEssence(item.id_nomenclature)"
                  ><v-icon>mdi-close</v-icon></v-btn
                >
              </div>
            </div>
          </div>
          <div>
            <v-btn
              v-if="
                baseModel.degats.find(
                  d =>
                    !freeze &&
                    d.id_nomenclature_degat_type === item.id_nomenclature &&
                    item.cd_nomenclature !== 'P/C' &&
                    d.degat_essences.length > 0 &&
                    d.degat_essences.length < 3 &&
                    d.degat_essences.length <
                      essenceSelected('degats').length &&
                    showDegatEssenceForm !== d.id_nomenclature_degat_type
                )
              "
              small
              color="success"
              @click="displayDegatEssence(item.id_nomenclature)"
              ><v-icon>mdi-plus</v-icon> Ajouter une essence touchée</v-btn
            >
          </div>
        </div>
      </div>
    </v-container>
  </div>
</template>

<script>
import { copy } from "@/core/js/util/util.js";
import { formFunctions } from "@/components/form/functions.js";
import essenceForm from "./essence-form.vue";
import nomenclatureForm from "./nomenclature-form";

export default {
  name: "degatsForm",
  components: {
    essenceForm,
    nomenclatureForm
  },
  data: () => ({
    freeze: false,
    items: null,
    degatTypes: [],
    degatEssence: {
      essence: null,
      gravite: null,
      etendue: null,
      anteriorite: null
    },
    rule: formFunctions.rules.requiredListMultiple,
    showDegatEssenceForm: null
  }),
  watch: {
    baseModel: function() {
      this.degatTypes = this.getDegatTypes()
    }
  },
  props: ["baseModel", "config"],
  methods: {
    getDegatTypes: function() {
      return this.baseModel["degats"].map(
      d => d.id_nomenclature_degat_type
    );
    },
    essenceSelected: function(cd_nomenclature) {
      const essenceSelected = formFunctions.getEssencesSelected(this.baseModel);
      return essenceSelected[cd_nomenclature];
    },

    updateDegats: function() {
      for (const degatType of this.degatTypes) {
        const degat = this.baseModel.degats.find(
          d => degatType === d.id_nomenclature_degat_type
        );
        if (!degat) {
          this.baseModel.degats.push({
            id_nomenclature_degat_type: degatType,
            degat_essences: []
          });
          if (
            this.$store.getters.nomenclature(degatType).cd_nomenclature != "P/C"
          ) {
            this.freeze = true;
          }
        }
      }

      for (const [index, degat] of this.baseModel.degats.entries()) {
        if (
          !this.degatTypes.find(d => d === degat.id_nomenclature_degat_type)
        ) {
          this.baseModel.degats.splice(index, 1);
        }
      }
    },

    configDegatEssence: function(degatType) {
      return {
        essence: {
          name: "essence",
          required: true,
          type: "essence",
          label: "Choisir une essence",
          declaration: this.baseModel,
          essenceType: degatType,
          rules: [formFunctions.rules.requiredListSimple]
        },
        gravite: {
          name: "gravite",
          type: "nomenclature",
          required: true,
          nomenclatureType: "OEASC_DEGAT_GRAVITE",
          rules: [formFunctions.rules.requiredListSimple]
        },
        etendue: {
          name: "etendue",
          type: "nomenclature",
          required: true,
          nomenclatureType: "OEASC_DEGAT_ETENDUE",
          rules: [formFunctions.rules.requiredListSimple]
        },
        anteriorite: {
          name: "anteriorite",
          type: "nomenclature",
          required: true,
          nomenclatureType: "OEASC_DEGAT_ANTERIORITE",
          rules: [formFunctions.rules.requiredListSimple]
        }
      };
    },

    getData: function() {
      this.items = this.$store.getters.nomenclaturesOfType("OEASC_DEGAT_TYPE");
    },

    displayDegatEssence(id_nomenclature_degat_type) {
      this.freeze = true;
      this.showDegatEssenceForm = id_nomenclature_degat_type;
    },

    addDegatEssence(id_nomenclature_degat_type) {
      const degat = this.baseModel.degats.find(
        d => d.id_nomenclature_degat_type === id_nomenclature_degat_type
      );
      degat.degat_essences = degat.degat_essences || [];
      const degat_essence = {
        id_nomenclature_degat_essence: this.degatEssence.essence,
        id_nomenclature_degat_gravite: this.degatEssence.gravite,
        id_nomenclature_degat_etendue: this.degatEssence.etendue,
        id_nomenclature_degat_anteriorite: this.degatEssence.anteriorite
      };
      degat.degat_essences.push(degat_essence);
      this.baseModel.degats = copy(this.baseModel.degats);
      this.clearDegatEssenceForm();
      this.freeze = false;
      this.showDegatEssenceForm = null;
    },

    cancelDegatEssence: function(id_nomenclature_degat_type) {
      const degat = this.baseModel.degats.find(
        d => d.id_nomenclature_degat_type === id_nomenclature_degat_type
      );
      if (degat.degat_essences.length === 0) {
        const index = this.baseModel.degats.indexOf(degat);
        this.baseModel.degats.splice(index, 1);
      } else {
        this.showDegatEssenceForm = null;
      }
      this.degatTypes = this.baseModel.degats.map(
        d => d.id_nomenclature_degat_type
      );
      this.freeze = false;
    },

    removeDegatEssence: function(
      id_nomenclature_degat_type,
      id_nomenclature_degat_essence
    ) {
      const degat = this.baseModel.degats.find(
        d => d.id_nomenclature_degat_type === id_nomenclature_degat_type
      );
      const degat_essence = degat.degat_essences.find(
        de => de.id_nomenclature_degat_essence === id_nomenclature_degat_essence
      );
      const index = degat.degat_essences.indexOf(degat_essence);
      degat.degat_essences.splice(index, 1);

      if (degat.degat_essences.length == 0) {
        this.freeze = true;
      }
    },

    clearDegatEssenceForm: function() {
      this.degatEssence.essence = null;
      this.degatEssence.gravite = null;
      this.degatEssence.etendue = null;
      this.degatEssence.anteriorite = null;
    }
  },

  created: function() {
    this.getData();
    this.degatTypes = this.getDegatTypes();     
  }
};
</script>
