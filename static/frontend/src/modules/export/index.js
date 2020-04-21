import html2pdf from "html2pdf.js";

const exportPDF = function(id, filename, $store) {
  return new Promise(resolve => {
    const opt = {
      filename,
      pagebreak: {
        mode: "avoid-all"
      },
      html2canvas: { dpi: 72, letterRendering: true }
    };

    const element = document.getElementById(id);
    element.classList.add("pdf");
    setTimeout(() => {
      console.log("map imgs");
      const mapImgpromises = $store.getters
        .elemMapServices(id)
        .map(mapService => mapService.toImg());

      Promise.all(mapImgpromises).then(mapElems => {
        console.log("mapDones", mapElems);
        console.log("imgMapDone");
        html2pdf()
          .from(element)
          .set(opt)
          .save()
          .then(() => {
        //remap the map remove imgs
        console.log("finish");
        mapElems;
        element.classList.remove("pdf");
        for (const map of mapElems) {
          console.log("mapElem", mapElems);
          map.style.display = "block";
          console.log(map.nextSibbling)
          map.parentElement.removeChild(map.nextSibling);
          map.classList.remove('map-img')
        }

        console.log("class-list", element.classList);
        resolve();
          });
      });
    }, 100);
  });
};

export { exportPDF };
