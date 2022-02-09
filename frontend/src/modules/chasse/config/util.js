const localisationTitle = (data) => {
  console.log(data)
  return data.nom_zone_indicative
? ` - ZI : ${data.nom_zone_indicative}`
: data.nom_zone_cynegetique
  ? ` - ZC : ${data.nom_zone_cynegetique}`
  : data.nom_secteur
    ? ` - Secteur : ${data.nom_secteur}`
    : ''
};

export {
  localisationTitle
}