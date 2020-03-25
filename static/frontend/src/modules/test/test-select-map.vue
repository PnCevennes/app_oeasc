<template>
  <div>
    <select-map mapId="map" :config="config" :baseModel="baseModel"></select-map>
  </div>
</template>

<script>
import selectMap from "@/components/form/select-map.vue";

let multiple=true;
multiple=false;

export default {
  name: "testMap",
  data: () => ({
    config: {
      multiple,
      name: "select",
      legend: "Forêt relevant du régime forestier",
      url: "api/ref_geo/areas_simples_from_type_code/l/OEASC_ONF_FRT",
      dataFieldNames: {
        value: 'id_area',
        text: 'label'
      }
    },
    baseModel: {
      select: multiple ? []: null
    },
  }),
  components: {
    selectMap
  },
};
</script>
