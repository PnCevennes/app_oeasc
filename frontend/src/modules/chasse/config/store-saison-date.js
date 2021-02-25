export default {
  group: "chasse",
  name: "saisonDate",
  label: "Saisons (date/espèce)",
  defs: {
    id_saison_date: {
      label: "ID",
      hidden: true,
    },
    id_saison: {
        label: 'saison',
        storeName: 'chasseSaison'
    },
    id_espece: {
        label: 'Espèce',
        storeName: 'commonsEspece'
    },
    id_nomenclature_type_chasse: {
        label: 'Type de chasse',
        storeName: 'commonsNomenclature',
        type: 'nomenclature',
        nomenclatureType: "OEASC_MOD_CHASSE",
    },
    date_debut: {
      label: "Date début",
      type: "date",
      required: true
    },
    date_fin: {
      label: "Date fin",
      type: "date",
      required: true
    },
  }
};
