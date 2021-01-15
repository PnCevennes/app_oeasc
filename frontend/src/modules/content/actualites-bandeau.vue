<template>
  <div>
    <v-row>
      <v-col v-for="(content, index) of contents" :key="index">
        <v-card height=400px :to="content.to">
          <v-card-text>{{content.date}}</v-card-text>
          <content-img
          class='list-actu'
            :src="content.src"
            alt="content.src"
            height=200px
            center
          ></content-img>
          <v-card-text class="card-title" v-html="content.title"></v-card-text>
        </v-card>
      </v-col>
    </v-row>
  </div>
</template>

<script>
import "./content.css"
import contentImg from "./content-img";
import marked from "marked";
import UtilsContent from './utils.js';

export default {
  name: "actualites-bandeau",
  props: ["tagNames", "nb", "height"],
  components: { contentImg },
  data: () => ({
    contents: []
  }),
  methods: {
    getContents() {
      const storeName = "commonsContent";
      const configStore = this.$store.getters.configStore(storeName);
      this.$store.dispatch(configStore.getAll).then(contents => {
        this.contents = contents
          .filter(content =>
            this.tagNames && this.tagNames.length
              ? this.tagNames.every(nom_tag => {
                  return content.tags.map(t => t.nom_tag).includes(nom_tag);
                })
              : true
          )
          .sort((c1, c2) => c1.meta_create_date < c2.meta_create_date)
          .filter((content, i) => {return i < (this.nb || 3)})
          .map(content => {
            const elem = document.createElement("div");
            let html = marked(content.md || "");
            elem.innerHTML = html;
              const title = elem.querySelector(":is(h1, h2, h3, h4, h5, h6)");
              const img = elem.querySelector(":is(content-img)");
              const imgSrc=img && img.attributes.src.nodeValue;
              return {
                src: imgSrc || "pages_degats_agricole_b_algoet.jpg",
                title: (title && title.innerHTML) || "Pas de titre",
                to: `actualite/${content.code}`,
                date: UtilsContent.displayDateFr(content.meta_create_date),
              };
            });
      });
    }
  },
  mounted() {
    this.getContents();
  }
};
</script>
