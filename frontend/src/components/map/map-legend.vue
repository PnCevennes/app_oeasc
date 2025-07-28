<!--
  Composant Vue.js : map-legend.vue

  Ce composant affiche une légende pour une carte, basée sur une configuration passée en propriété.
  Il gère deux types de légendes : les groupes de marqueurs et les couches de la carte.

  Structure principale :
  - La légende n'est affichée que si la propriété "config" est définie.
  - Pour chaque groupe de légendes de marqueurs (config.markerLegendGroups) :
    - Affiche le titre du groupe si présent.
    - Pour chaque légende du groupe :
      - Affiche une icône (utilise Material Design Icons) avec la couleur et l'icône spécifiées.
      - Affiche le texte de la légende et éventuellement le nombre d'éléments si "count" est défini.
  - Pour les couches de la carte (config.layers) :
    - Ajoute un saut de ligne si des couches et des marqueurs sont présents.
    - Pour chaque couche :
      - Affiche un carré coloré représentant le style de la couche (couleur de fond, opacité, bordure).
      - Affiche le texte de la légende associé à la couche.

  Props attendues :
  - config : objet contenant la configuration des groupes de légendes de marqueurs et des couches.

  Méthodes utilisées :
  - getColor(fillColor, fillOpacity) : retourne une couleur RGBA à partir d'une couleur et d'une opacité.

  Classes CSS utilisées :
  - legend-container : conteneur principal de la légende.
  - legend : bloc de légende pour chaque groupe ou couche.
  - legendText : style pour le texte de chaque légende.

  Remarque :
  - Ce composant est conçu pour être flexible et afficher dynamiquement les légendes selon la configuration fournie.
-->
<template>
  <div class="legend-container" v-if="config">
    <div
      class="legend"
      v-for="(markerLegendGroup, index1) of config.markerLegendGroups || []"
      :key="index1"
    >
      <template v-if="markerLegendGroup.title">
        <b>{{ markerLegendGroup.title }}</b>
      </template>
      <div
        v-for="(legend, index) of markerLegendGroup.legends || []"
        :key="index"
      >
        <i
          :style="
            `
            font-size: 1.8em;
            color:${legend.color};
          `
          "
          :class="`mdi mdi-${legend.icon}`"
        ></i>
        <span class="legendText">
          {{ legend.text }}
          <span v-if="legend.count">
            ({{ legend.count }})</span
          >
        </span>
      </div>
    </div>
    <div class="legend">
      <div v-if="Object.entries(config.layers || []).length && config.markers">
        <br />
      </div>
      <div
        v-for="[key, layerConfig] of Object.entries(config.layers || [])"
        :key="key"
      >
        <i
          v-if="layerConfig.style"
          :style="
            `
            background-color: ${getColor(
              layerConfig.style.fillColor,
              layerConfig.style.fillOpacity
            )};
            border: ${layerConfig.style.weight}px solid ${
              layerConfig.style.color
            };
          `
          "
        ></i>
        <span class="legendText">
          {{ layerConfig.legend }}
        </span>
      </div>
    </div>
  </div>
</template>



<script>

import chroma from "chroma-js";

export default {
  name: "mapLegend",
  props: ["config"],
  methods: {
    getColor(color, opacity) {
      return chroma(color || "black").alpha(opacity);
    }
  }
};
</script>
