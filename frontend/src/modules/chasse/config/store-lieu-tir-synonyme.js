export default {
  group: "chasse",
  name: "lieuTirSynonyme",
  label: "Lieu de tir (synonyme)",
  serverSide: true,
  defs: {
    id_lieu_tir_synonyme: {
      label: "ID synonyme",
      type: "text",
      hidden: true
    },
    nom_lieu_tir_synonyme: {
      label: "Nom",
      type: "text",
      required: true
    },
    lieu_tir: {
      label: "Lieu tir",
      type: "list_form",
      list_type: "autocomplete",
      dataReloadOnSearch: true,
      returnObject: true,
      storeName: "chasseLieuTir"
    },
    id_lieu_tir: {
      label: "ID lieu tir",
      type: "text",
      hidden: true
    }
  }
};
