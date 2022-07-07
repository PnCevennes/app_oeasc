import html2pdf from "html2pdf.js";

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

const exportPDF = function(id, filename, $store) {
  return new Promise(resolve => {
    const opt = {
      filename,
      jsPDF: { unit: "in", format: "letter", orientation: "portrait" },
      html2canvas: { dpi: 1000, letterRendering: false}
    };

    const element = document.getElementById(id);
    element.classList.add("pdf");
    setTimeout(() => {

      const mapImgpromises = $store.getters
        .elemMapServices(id)
        .map(mapService => mapService.toImg());

      Promise.all(mapImgpromises).then(mapElems => {
        console.log('html2pdf')
        html2pdf()
          .from(element)
          .set(opt)
          .save()
          .then(() => {
            //remap the map remove imgs
            console.log('html2pdf end')

            mapElems;
            element.classList.remove("pdf");
            resolve(true);
            for (const map of mapElems) {
              console.log('map reset', map)

              resetMapStyle(map)
              // map.style.display = "block";

              // // map.parentElement.removeChild(map.nextSibling);
              // map.classList.remove("map-img");
            }

            console.log('resolve')
            resolve(true);
          });
      });
    }, 1000);
  });
};

export { exportPDF };
