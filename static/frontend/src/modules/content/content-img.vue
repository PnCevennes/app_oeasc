<template>
  <div :class="classes">
    {{$store.getters.distPath}}
    <figure>
      <img
        :src="`${$store.getters.distPath}${src}`"
        :title="`${title || src} ${source || ''}`.trim()"
        :alt="`${title || src} ${source || ''}`.trim()"
        :width="width"
        :height="height"
      />
      <figcaption>
          <div class="img-text">
        {{ title }}
        <i class="source" v-if="source"> - {{ source }}</i>
          </div>
      </figcaption>
    </figure>
  </div>
</template>

<script>
import "./content.css";

export default {
  name: "content-img",
  computed: {
    classes() {
      const classes = {
        "img-content": true,
        center: this.center == "",
        float: this.float,
        left: this.float == "left",
        right: this.float == "right",
        'risetitle': this['risetitle'] == "", 
      };
      return classes;
    }
  },
  props: ["src", "height", "width", "float", "center", "title", "source", 'risetitle']
};
</script>
