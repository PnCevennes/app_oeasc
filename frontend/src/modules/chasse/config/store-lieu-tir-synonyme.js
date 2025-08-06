export default {
  group: "chasse",
  name: "lieuTirSynonyme",
  label: "Lieu de tir (synonyme)",
  serverSide: true,

  options: {
    // Ajoute des param à la requête get pour filtrer les données
    page: 1, // on affiche la première page par défaut
    sortBy: ["id_lieu_tir_synonyme"],
    sortDesc: [true], // tri en ordre décroissant
    // fields: [
    //   "lieu_tir.id_lieu_tir",
    //   "lieu_tir.nom_lieu_tir",
    //   "lieu_tir.code_lieu_tir"
    // ]
  },


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
