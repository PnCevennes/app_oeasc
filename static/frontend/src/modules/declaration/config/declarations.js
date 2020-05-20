import { apiRequest } from '@/core/js/data/api.js'

const formToPost = function(baseModel) {
  return baseModel;
}

const postDeclaration = function({baseModel}) {

  // prepare les données
  const postData = formToPost(baseModel)
  console.log('id_declarant post', baseModel.id_declarant);

  // post data
  return apiRequest('POST', 'api/degat_foret/declaration', {data: postData})

}


const config = {
  title: "Signaler des dégâts de grand gibier en forêt",
  groups: {
    foret: {
      title: "Informations sur la forêt",
      sessions: ['foret_statut', 'foret_localisation', 'foret_informations', 'foret_proprietaire']
    },
    peuplement: {
      title: "Informations sur le peuplement",
      sessions: [
        "peuplement_localisation",
        "peuplement_description",
        "peuplement_protection",
        "peuplement_paturage",
        "peuplement_autres",
      ]
    },
    degats: {
      title: "Dégâts",
      sessions: [
        "degats_caracterisation",
        "degats_precision_localisation"
      ]
    },
    commentaires: {
      title: "Commentaires",
      sessions: [
        'commentaires'
      ],
    },
    validation: {
      title:"Résumé /validation",
      sessions: [
        'validation'
      ],
    }
  }
};

export { config, postDeclaration };
