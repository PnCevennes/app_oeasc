const L = window.L;

const mapMarker = {
  _markers: [],

  // Supprime tous les marqueurs actuellement affichés sur la carte
  removeMarkers() {
    // Parcourt la liste des marqueurs stockés
    for (let marker of this._markers) {
      // Retire chaque marqueur de la carte Leaflet
      this._map.removeLayer(marker);
    }
    // Réinitialise la liste des marqueurs à un tableau vide
    this._markers = [];
  },


  // Génère le contenu HTML pour l'étiquette (label) d'un marqueur
  markerLabel(marker) {
    let defs = []; // Tableau des définitions d'icônes et couleurs à afficher dans le label
    let label = ""; // Chaîne HTML du label à retourner

    // Si le marqueur possède déjà des définitions, on les utilise directement
    if (marker.defs) {
      defs = marker.defs;
    } else {
      // Sinon, on récupère la couleur et l'icône depuis le style du marqueur, ou on utilise des valeurs par défaut
      const color = marker.style.color || "blue";
      const icon = marker.style.icon || "circle";
      // On s'assure que color et icon sont des tableaux pour pouvoir les parcourir
      const colors = Array.isArray(color) ? color : [color];
      const icons = Array.isArray(icon) ? icon : [icon];

      // Si la propriété condSame est vraie, on associe chaque couleur à chaque icône par index
      if (marker.condSame) {
        for (var i = 0; i < colors.length; i++) {
          defs.push({ icon: icons[i], color: color[i] });
        }
      } else {
        // Sinon, on crée toutes les combinaisons possibles entre les couleurs et les icônes
        for (const color of colors) {
          for (const icon of icons) {
            defs.push({ icon: icon, color: color });
          }
        }
      }
    }

    // Pour chaque définition, on ajoute une balise <i> avec la classe et la couleur correspondante
    for (const def of defs) {
      label += `<i class='mdi mdi-${def.icon}' style='color:${def.color}'></i>`;
    }
    
    // On retourne la chaîne HTML générée pour le label
    return label;
  },



  /**
   * Initialise les marqueurs sur la carte.
   * Supprime d'abord tous les marqueurs existants, puis ajoute chaque marqueur
   * défini dans la configuration (_config.markers). Enfin, met à jour la configuration.
   *
   * @returns {void}
   */
  initMarkers() {
    this.removeMarkers();
    for (const marker of this._config.markers || []) {
      this.addMarker(marker);
    }
    this.upConfig();
  },


  /**
   * Ajoute un marqueur sur la carte selon sa configuration.
   * Prend en compte le type de marqueur (marker, circle, label) et applique les options nécessaires.
   * Stocke le marqueur dans la liste interne et applique le style.
   *
   * @param {Object} markerConfig - Configuration du marqueur à ajouter
   */
  addMarker(markerConfig) {
    // Initialise les options du marqueur et définit le pane par défaut si non précisé
    markerConfig.options = {};
    markerConfig.options.pane = markerConfig.pane || "PANE_MARKER_1";

    let marker;
    // Si le type est "marker", crée un marqueur standard Leaflet
    if (markerConfig.type == "marker") {
      marker = L.marker(markerConfig.coords, markerConfig.options).addTo(
        this._map
      );
    // Si le type est "circle", crée un cercle sur la carte
    } else if (markerConfig.type == "circle") {
      marker = L.circleMarker(markerConfig.coords, markerConfig.options).addTo(
        this._map
      );
    // Si le type est "label", crée un cercle invisible et lui associe un tooltip permanent
    } else if (markerConfig.type == "label") {
      marker = L.circle(markerConfig.coords, {
        ...markerConfig.options,
        opacity: 0, // Cercle invisible
        fillOpacity: 0,
        color: "rgba(0,0,0,0)",
        fillColor: "rgba(0,0,0,0)"
      })
        // Ajoute un tooltip avec le label généré par markerLabel
        .bindTooltip(this.markerLabel(markerConfig), {
          pane: "PANE_TOOLTIP",
          permanent: true, // Tooltip toujours visible
          direction: "center",
          color: "white",
          opacity: 1,
          fillOpacity: 1,
          interactive: true,
          className: "tooltip-label"
        })
        .addTo(this._map);
    }

    // Ajoute des propriétés supplémentaires au marqueur pour la gestion interne
    marker.type = markerConfig.type;
    marker.properties = markerConfig.properties;
    marker.style = markerConfig.style;

    // Stocke le marqueur dans la liste interne pour pouvoir le supprimer ou le modifier plus tard
    this._markers.push(marker);

    // Applique le style au marqueur selon son type
    this.setMarkerStyle(marker);
  },



  /**
   * Définit le style d'un marqueur sur la carte en fonction de son type.
   * 
   * @param {Object} marker - L'objet représentant le marqueur à styliser.
   * @param {string} marker.type - Le type du marqueur ("marker", "circle", etc.).
   * @param {Object} [marker.style] - Les propriétés de style du marqueur.
   * @param {number} [marker.style.opacity] - L'opacité du marqueur.
   * @param {number} [marker.style.fillOpacity] - L'opacité de remplissage du marqueur.
   * 
   * Si le type est "marker", applique l'opacité via setOpacity.
   * Si le type est "circle", applique le style via setStyle.
   * Pour tout autre type, rend le marqueur invisible en appliquant une opacité nulle.
   */
  setMarkerStyle(marker) {
    marker.style = marker.style || {};
    marker.style.opacity = 1;
    marker.style.fillOpacity = 0.2;
    if (marker.type == "marker") {
      marker.setOpacity(marker.style.opacity);
    } else if (marker.type == "circle") {
      marker.setStyle(marker.style);
    } else {
      marker.setStyle({ opacity: 0, fillOpacity: 0 });
    }
  }



};



export { mapMarker };
