import html2pdf from "html2pdf.js";
// import html2canvas from "html2canvas";

/**
 * Réinitialise le style d'un élément de carte après une exportation ou une modification.
 * 
 * Cette fonction supprime l'image associée à l'élément, restaure sa visibilité et ses dimensions originales,
 * et retire la classe CSS spécifique à l'image de carte. Elle suppose que les propriétés `widthSave` et `heightSave`
 * sont accessibles dans le contexte d'exécution (probablement via `this`).
 *
 * @param {HTMLElement} elem - L'élément DOM représentant la carte à réinitialiser.
 *
 * @throws {TypeError} Si l'élément suivant n'est pas une image ou ne peut pas être supprimé.
 *
 * @example
 * // Supposons que `mapElement` soit un élément de carte exporté
 * resetMapStyle(mapElement);
 */
const  resetMapStyle = (elem) => {
  const img = elem.nextElementSibling;
  img.remove();
  elem.classList.remove("map-img");
  elem.style.display = "block";
  elem.style.width = this.widthSave + "px";
  elem.style.height = this.heightSave + "px";
  // this._map.invalidateSize();
  // this.reinitZoom();
}

/**
 * Exports the content of a DOM element as a PDF file using html2pdf.
 *
 * @param {string} id - The ID of the DOM element to export as PDF.
 * @param {string} filename - The desired filename for the exported PDF.
 * @param {Object} $store - The Vuex store instance, used to access map services.
 * @returns {Promise<boolean>} Resolves to true when the PDF export is complete.
 *
 * @description
 * - Ajoute temporairement la classe "pdf" à l'élément cible pour appliquer des styles spécifiques.
 * - Attend 1 seconde pour s'assurer que les styles sont appliqués.
 * - Récupère les services de carte associés à l'élément et génère leurs images.
 * - Utilise html2pdf pour convertir l'élément en PDF avec les options spécifiées.
 * - Après l'export, réinitialise le style des cartes et retire la classe "pdf".
 * - Résout la promesse une fois le processus terminé.
 */
const exportPDF = function(id, filename, $store) {
  return new Promise(resolve => {
    const opt = {
      filename,
      jsPDF: { unit: "in", format: "letter", orientation: "portrait" },
      html2canvas: { 
        dpi: 1000,
        letterRendering: false,
        scale: 2,
        allowTaint: true,
        useCORS: true
      }
    };

    const element = document.getElementById(id);
    element.classList.add("pdf");
    setTimeout(() => {

      // Récupère les services de carte associés à l'élément et génère leurs images
      const mapImgpromises = $store.getters
        .elemMapServices(id) // Obtient les services de carte liés à l'élément avec l'id donné
        .map(mapService => mapService.toImg()); // Pour chaque service, génère une image de la carte

      // console.log(mapImgpromises)

      Promise.all(mapImgpromises).then(mapElems => {
        // Utilise html2pdf pour convertir l'élément en PDF avec les options spécifiées
        html2pdf()
            .from(element)  // Définit l'élément source
            .set(opt)       // Configure les options d'export
            .save()         // Enregistre le PDF
            .then(() => {
            // Une fois l'export PDF terminé:
            
            // Supprime la classe "pdf" de l'élément
            element.classList.remove("pdf");
            
            // Parcourt tous les éléments de carte et réinitialise leur style
            for (const map of mapElems) {
              resetMapStyle(map);
            }
            
            // Résout la promesse pour indiquer que l'export est terminé
            resolve(true);
          });
        });
    }, 2000);
  });
};

export { exportPDF };
