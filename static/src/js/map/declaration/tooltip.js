const dDegatTypeIcon = {
    'ABR': 'fa fa-seedling',
    'ÉCO': 'fas fa-tree',
    'SANG': 'fas fa-square',
    'FRO': 'fas fa-angle-double-down',
    'P/C': 'fas fa-exclamation-triangle',
    'ABS': 'fas fa-ban',
  };
  
  const dDegatGraviteColor = {
    'DG_FBL': 'yellow',
    'DG_MOY': 'orange',
    'DG_IMPT': 'red',
  };
  
  const sTooltipDegats = (degats) => {
    let sTooltip = '';
    for (const degat of degats) {
      let color = 'white';
      let colorSave = '';
      const cdDeg = degat.degat_type_code;
      const icon = dDegatTypeIcon[cdDeg];
  
      for (const degatEssence of degat.degat_essences) {
        if (!degatEssence || !degatEssence.degat_gravite_code) {
          return;
        }
        color = dDegatGraviteColor[degatEssence.degat_gravite_code];
        if (color === 'yellow' && ['red, orange'].includes(colorSave)) {
          color = colorSave;
        }
        if (color === 'orange' && colorSave === 'red') {
          color = colorSave;
        }
  
        colorSave = color;
      }
      sTooltip += `<i style="color:${color}" class="${icon} fa-2x shadow"></i>`;
    }
  
    return sTooltip;
  };

  export { sTooltipDegats }
