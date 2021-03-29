export default {
  group: "chasse",
  name: "saisonDate",
  label: "Saisons (date/espèce)",
  serverSide: true,
  defs: {
    id_saison_date: {
      label: "ID",
      hidden: true,
    },
    saison: {
        label: 'saison',
        storeName: 'chasseSaison',
        type: 'list_form',
        list_type: 'autocomplete',
        returnObject: true,
        dataReloadOnSearch: true,
    },
    espece: {
        label: 'Espèce',
        storeName: 'commonsEspece',
        type: 'list_form',
        list_type: 'select',
        returnObject: true,
    },
    nomenclature_type_chasse: {
        label: 'Type de chasse',
        storeName: 'commonsNomenclature',
        type: 'nomenclature',
        nomenclatureType: "OEASC_MOD_CHASSE",
        list_type: 'select',
        returnObject: true,
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
