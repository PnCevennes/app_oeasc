<template>
  <div>

    <base-map mapId="map" :config="config[$route.params.mapName]">
    </base-map>

  </div>
</template>

<script>
import baseMap from "@/modules/map/base-map.vue";
import { config } from "@/config/config.js";

export default {
  name: "testMap",
  data: () => ({
    config: {
      perimetre: {
        layerList: {
          zc: {},
          aa: {},
          secteurs: {
            zoom: true,
            tooltip: {
              permanent: true,
              className: "tooltip-label",
              label: "label"
            }
          }
        }
      },
      select: {
        name: 'truc',

        layerList: {
          po: {},
          select: {
            ...config.map.configBaseSelect,
            legend: "Forêt relevant du régime forestier",
            url: "api/ref_geo/areas_simples_from_type_code/l/OEASC_ONF_FRT",
            type: "OEASC_ONF_FRT"
          }
        }
      }
    }
  }),
  components: {
    baseMap
  }
};
</script>
