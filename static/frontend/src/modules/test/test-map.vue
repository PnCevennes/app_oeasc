<template>
  <div style="width:100%">
    <div v-if="bInit">
      <base-map mapId="map" ref="map" :config="config" fillHeight>
        <div slot="aside" class="map-aside">
          <list-form
            :baseModel="settings"
            :config="configChoixColor"
          ></list-form>
        </div>
      </base-map>
    </div>
  </div>
</template>

<script>
import baseMap from "@/modules/map/base-map.vue";
import listForm from "@/components/form/list-form";

const items = [
  {
    text: "Secteur",
    name: "secteur",
    split: ", "
  },
  {
    text: "Organisme",
    name: "organisme",
    split: ", "
  },
  {
    text: "Type de forêt",
    name: "type_foret",
    split: ", "
  },
  {
    text: "Commune",
    name: "communes",
    split: ", "
  },
  {
    text: "Déclarant",
    name: "declarant",
    split: ", "
  },

  {
    text: "Pâturage",
    name: "b_peuplement_paturage_presence",
    replace: [
      [true, "Oui"],
      [false, "Non"]
    ]
  },
  {
    text: "Protection",
    name: "b_peuplement_protection_existence",
    replace: [
      [true, "Oui"],
      [false, "Non"]
    ]
  }
];
export default {
  name: "testMap",
  data() {
    return {
      settings: {},
      name: "",
      configChoixColor: {
        display: "select",
        name: "color",
        label: "Couleur",
        type: "list_form",
        returnObject: true,

        items,
        change: () => {
          this.initMarkers();
        }
      },
      bInit: false,
      declarations: [],
      config: {
        layerList: {
          zc: {},
          aa: {},
          secteurs: {
            zoom: true,
            select: {
              build: true,
              multiple: false,
              display: "autocomplete",
              textFieldName: "label",
              valueFieldName: "id_area",
              zoomOnChange: true,
              markerFilter: {
                markerFieldName: "areas_localisation_raw"
              }
            }
          }
        }
      }
    };
  },
  methods: {
    initMarkers() {
      const colorSetting = this.settings["color"];
      if (!colorSetting) {
        this.initMarkersLocalisation();
        if (this.$refs.map) {
          this.$refs.map.mapService._config = { ...this.config };
          this.$refs.map.mapService.initMarkers();
        }
        return;
      }
      // const name = colorSetting.value;
      // const dataList = restitution.dataList(this.declarations, name, options);

      this.config.markers = {};
      this.config.markers.declarations = {
        type: "circle",
        coords: "centroid",
        data: this.declarations,
        color: {
          options: {
            ...colorSetting,
            nMax: 7
          }
        },
      };

      this.$refs.map.mapService._config = this.config;
      this.$refs.map.mapService.initMarkers();
    },
    initMarkersLocalisation() {
      this.config.markers = {
        declarations: {
          data: this.declarations,
          type: "circle",
          coords: "centroid",
          style: {
            color: "blue",
            icon: "circle-outline"
          },
          legends: [
            {
              icon: "circle-outline",
              text: "Localisation des alertes",
              color: "blue"
            }
          ]
        }
      };
    }
  },
  components: {
    baseMap,
    listForm
  },
  mounted() {
    this.$store.dispatch("declarations").then(declarations => {
      this.declarations = declarations;
      this.initMarkers();
      this.bInit = true;
      setTimeout(() => {
        // this.settings["color"] = items.find(i => i.text == "Organisme");
        // this.initMarkers();
      }, 1000);
    });
  }
};
</script>
