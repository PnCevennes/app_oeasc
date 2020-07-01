<template>
  <div>
    <h2>
      Restitution
    </h2>
    <p>Nombre de données {{ dataLength }}</p>
    <listForm
      :config="configChoix('color', 'Couleur')"
      :baseModel="settings"
    ></listForm>
  </div>
</template>

<script>
import listForm from "@/components/form/list-form";

export default {
  name: "restitution",
  props: ["dataIn", "config"],
  components: { listForm },
  data: () => ({
    settings: {}
  }),
  methods: {
    items(name) {
      let items = Object.keys(this.config.items).map(key => ({
        ...this.config.items[key],
        name: key
      }));
      if (this.config[name]) {
          items = items.filter(item => this.config[name].includes(item.name))
      }
      return items;
    },
    configChoix(name, label) {
      return {
        name,
        label,
        display: "autocomplete",
        type: "list_form",
        returnObject: true,
        items: this.items(name),
        change: () => {
          this.processChoix();
        }
      };
    },
    processChoix() {
        console.log('process choix')
    }
  },
  computed: {
    dataLength() {
      return (this.dataIn || []).length;
    }
  }
};
</script>
