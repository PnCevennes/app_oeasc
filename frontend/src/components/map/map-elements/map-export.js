import domtoimage from "dom-to-image";

const mapExport = {
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

      // if(elem) {
      //   resolve(elem);
      //   return ;
      // }

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
