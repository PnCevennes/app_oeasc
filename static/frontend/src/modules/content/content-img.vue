<template>
  <div
    :class="classes"
  >
  <a
        :href="isLink ? `${$store.getters.mediaImgPath}${link || src}` : null"
  >
    <figure
    >
      <img
        :src="`${$store.getters.mediaImgPath}${src}`"
        :title="`${title || src || ''} ${source || ''}`.trim()"
        :alt="`${title || src || ''} ${source || ''}`.trim()"
        :width="width"
        :height="height"
      />
      <figcaption>
        <div class="img-text">
          {{ title || "" }}
          <i class="source" v-if="source"> - {{ source }}</i>
        </div>
      </figcaption>
    </figure>
    </a>
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
        risetitle: this["risetitle"] == "",
        'no-link': !this.isLink
      };
      return classes;
    },
    isLink() {
      return this.link != undefined;
    }
  },
  props: [
    "src",
    "height",
    "width",
    "float",
    "center",
    "title",
    "source",
    "risetitle",
    "link"
  ]
};
</script>
