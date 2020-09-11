import domtoimage from "dom-to-image";

const mapExport = {
  toImg(options = {}) {
    const methods = {
      png: "toPng",
      jpg: "toJpeg"
    };
    const method = methods[options.format] || "toPng";
    return new Promise(resolve => {
      const elem = document.getElementById(this._id);

      // preporcess

      elem.classList.add("map-img");

      // image
      domtoimage[method](elem, {
        height: Math.floor(elem.clientHeight),
        witdh: Math.floor(elem.clientWidth)

      }).then(dataUrl => {
        var img = new Image();
        img.src = dataUrl;
        elem.after(img);

        // hide elem
        elem.style.display = "none";
        
        resolve(elem);
      });
    });
  }
};

export { mapExport };
