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
                multiple: false,
                display: "autocomplete",
                textFieldName: "label",
                valueFieldName: "id_area",
                change: this.selectLayerChange("secteurs")
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
            properties: d
          }))
        }
      };
    },
    processMarkers() {
      let secteurs = this.$refs.map.baseModel["secteurs"];
      if (secteurs && !Array.isArray(secteurs)) {
        secteurs = [secteurs];
      }

      for (const marker of this.$refs.map.mapService._markers) {
        let cond = true;
        cond =
          cond &&
          (!secteurs ||
            secteurs.find(id_area =>
              marker.properties.areas_localisation_raw.includes(id_area)
            ));
        marker.opacity = cond ? 1 : 0.1;
      }
      this.$refs.map.mapService.updateMarkers();
    },
    selectLayerChange(name) {
      return () => {
        this.processMarkers();
        const value = this.$refs.map.baseModel[name];
        const layers = this.$refs.map.mapService.findLayers("id_area", value);
        if (Array.isArray(value) ? value.length : value) {
          this.$refs.map.mapService.zoomOnLayers(layers);
        } else {
          this.$refs.map.mapService.reinitZoom();
        }
      };
    }
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
