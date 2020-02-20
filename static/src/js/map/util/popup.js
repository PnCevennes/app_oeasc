const bindPopup = (elem, popupConfig, data) => {

 let sPopup = '<table class=\'table-popup\'>';
 for (const key of Object.keys(popupConfig)) {
     if (data[key]) {
     sPopup += `<tr><th>${popupConfig[key]}</th><td>${data[key]}</td></tr>`
     }
 }
 sPopup += '</table>';

 elem.bindPopup(sPopup, {
     pane: 'PANE_30'
 })

}

export { bindPopup };
