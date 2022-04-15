const localisationTitle = (data) => {
  return data.nom_zone_indicative
? ` - ZI : ${data.nom_zone_indicative}`
: data.nom_zone_cynegetique
  ? ` - ZC : ${data.nom_zone_cynegetique}`
  : data.nom_secteur
    ? ` - Secteur : ${data.nom_secteur}`
    : ''
};

const dataTxt = (data) => {
  return {
    dataTypeTitle: data.data_type == 'poids' ? 'Masse corporelle' : 'Longueur des dagues',
    dataTypeAxis: data.data_type == 'poids' ? 'Poids (kg)' : 'Longueur des dagues (mm)',
    dataTypeSerie: data.data_type == 'poids' ? 'Poids vide moyen (kg)' : 'Longueur des dagues (mm)',
  }
}

export {
  localisationTitle,
  dataTxt
}