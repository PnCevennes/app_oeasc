<template>
  <div style="width:100%">
    <div v-if="bInit">
      <base-map mapId="map" ref="map" :config="config[$route.params.mapName]">
      </base-map>
    </div>
  </div>
</template>

<script>
import baseMap from "@/modules/map/base-map.vue";

export default {
  name: "testMap",
  data() {
    return {
      bInit: false,
      declarations: [],
      config: {
        restitution: {
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
                  markerFieldName: 'areas_localisation_raw'
                },
              }
            }
          }
        }
      }
    };
  },
  methods: {
    initMarkers() {
      this.config.restitution.markers = {
        declarations: {
          legend: "Localisation des alertes",
          markers: this.declarations.map(d => ({
            coords: d.centroid,
            properties: d,
            // type: 'marker',
            type: 'circle',
            style: {},
            options: {pane: 'PANE_MARKER_1'}
          }))
        }
      };
    },
    updateMarkers() {
      this.initMarkers();
      this.$refs.map.mapService.initMarkers();
    },
  },
  components: {
    baseMap
  },
  mounted() {
    this.$store.dispatch("declarations").then(declarations => {
      this.declarations = declarations;
      this.initMarkers();
      this.bInit = true;
    });
  }
};
</script>
