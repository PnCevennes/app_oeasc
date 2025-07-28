import domtoimage from "dom-to-image";

const mapExport = {

  /**
   * Génère une image à partir d'un élément de carte et l'ajoute au DOM.
   *
   * @param {Object} [options={}] - Options de génération de l'image.
   * @param {'png'|'jpg'} [options.format='png'] - Format de l'image à générer ('png' ou 'jpg').
   * @param {number} [options.height] - Hauteur de l'image générée (en pixels).
   * @param {number} [options.width] - Largeur de l'image générée (en pixels).
   * @returns {Promise<HTMLElement>} Une promesse qui se résout avec l'élément de la carte exporté (caché après export).
   *
   * @description
   * Cette méthode prépare l'élément de la carte pour l'exportation en image :
   * - Ajoute une classe CSS pour le style d'export.
   * - Sauvegarde les dimensions originales de la carte.
   * - Redimensionne l'élément selon les options fournies.
   * - Force le redessin de la carte et réinitialise le zoom.
   * - Attend que la carte soit redessinée avant d'exporter l'image.
   * - Utilise la librairie dom-to-image pour générer l'image au format demandé.
   * - Ajoute l'image générée juste après l'élément source dans le DOM.
   * - Cache l'élément source après l'export.
   */
  toImg(options = {}) {
    const methods = {
      png: "toPng",
      jpg: "toJpeg"
    };
    const method = methods[options.format] || "toPng";
    return new Promise(resolve => {
      let elem = document.getElementById(this._id);

      // preporcess
      elem.classList.add("map-img");

      this.heightSave = Math.floor(elem.clientHeight);
      this.widthSave = Math.floor(elem.clientWidth);

      const height = options.height || this.heightSave;
      const width = options.width || this.widthSave;

      elem.style.height = `${height}px`;
      elem.style.width = `${width}px`;

      this._map.invalidateSize();
      this.reinitZoom();

      // on laisse temps à la carte de se redessiner 500ms ??
      setTimeout(() => {
        elem = document.getElementById(this._id);
        domtoimage[method](elem, {
          height,
          width
        }).then(dataUrl => {
          var img = new Image();
          img.src = dataUrl;
          img.style.height = elem.style.height;
          img.style.width = elem.style.width;
          elem.after(img);

          // hide elem
          elem.style.display = "none";

          resolve(elem);
        });
      }, 2000);
    });
  },



  /**
   * Génère et télécharge une image du composant de carte au format spécifié.
   *
   * @param {Object} options - Options pour l'exportation de l'image.
   * @param {string} [options.format="png"] - Format de l'image à exporter (par exemple, "png").
   * @param {string} [options.filename="map"] - Nom du fichier à télécharger.
   * @returns {Promise<Element>} Une promesse qui se résout avec l'élément de la carte exportée.
   *
   * Détails du fonctionnement :
   * - Utilise la méthode `toImg` pour générer une image de la carte selon les options fournies.
   * - Récupère l'élément image généré et son contenu en base64.
   * - Crée dynamiquement un lien de téléchargement et déclenche le téléchargement du fichier image.
   * - Réinitialise le style de la carte après l'exportation.
   */
  toImgFile(options = { format: "png", filename: "map" }) {
    return new Promise(resolve => {
      this.toImg(options).then(mapElem => {
        const img = mapElem.nextElementSibling;
        const base64 = img.src;
        var link = document.createElement("a");
        document.body.appendChild(link); // for Firefox
        link.setAttribute("href", base64);
        link.setAttribute("download", options.filename);
        link.click();
        this.resetMapStyle(mapElem);
        resolve(mapElem);
      });
    });
  },



  /**
   * Réinitialise le style de la carte après une exportation ou une modification.
   * 
   * @param {HTMLElement} elem - L'élément DOM représentant la carte à réinitialiser.
   * 
   * Cette méthode effectue les opérations suivantes :
   * - Supprime l'image exportée qui suit immédiatement l'élément de la carte.
   * - Retire la classe CSS "map-img" de l'élément pour restaurer son style original.
   * - Réaffiche l'élément de la carte en modifiant sa propriété display.
   * - Rétablit la largeur et la hauteur de la carte à leurs valeurs sauvegardées.
   * - Force la carte à recalculer sa taille via la méthode invalidateSize().
   * - Réinitialise le niveau de zoom de la carte.
   */
  resetMapStyle(elem) {
    const img = elem.nextElementSibling;
    img.remove();
    elem.classList.remove("map-img");
    elem.style.display = "block";
    elem.style.width = this.widthSave + "px";
    elem.style.height = this.heightSave + "px";
    this._map.invalidateSize();
    this.reinitZoom();
  }


};

export { mapExport };
