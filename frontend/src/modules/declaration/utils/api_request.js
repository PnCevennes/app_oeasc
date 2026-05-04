import { apiRequest } from '@/core/js/data/api';

const DEFAUT = 0; // Type de carte par défaut affiche uniquement les périmètres sélectionnés dans liste_areas_selected
const COMMUNE = 327; // Type area des communes dans la base de données
const SECTION = 333; // Type area des sections cadastrales dans la bdd
const FORET_DGD = 331; // Type area des forêts DGD dans la bdd
const FORET_ONF = 328; // Type area des forêts ONF dans la bdd
const CADASTRE = 332; // Type area des parcelles cadastrales dans la bdd

const CODE_AREA = {
  327: 'OEASC_COMMUNE',
  333: 'OEASC_SECTION',
  331: 'OEASC_DGD',
  328: 'OEASC_ONF_FRT',
  332: 'OEASC_CADASTRE',
};

// export async function fetch_declaration_by_id(id) {
//   try {
//     // const response = await fetch(`/api/declarations/${id}`);
//     const response = await apiRequest('GET', `api/declaration/declaration${id ? `/${id}` : ''}`);
//     console.log('Réponse de l’API pour la déclaration:', response);
//     return response;
//   } catch (error) {
//     console.error('Erreur lors de la récupération des données', error);
//     return null;
//   }
// }

// export async function fetch_declarations(id) {
//   try {
//     const response = await apiRequest('GET', `api/declaration/declarations`);
//     return response;
//   } catch (error) {
//     console.error('Erreur lors de la liste des déclarations', error);
//     return null;
//   }
// }

export async function fetch_oeasc_perimetre() {
  try {
    const response = await apiRequest(
      'GET',
      `api/ref_geo/areas_simples_from_type_code/l/OEASC_PERIMETRE`
    );
    return response;
  } catch (error) {
    console.error('Erreur lors de la récupération des communes OEASC', error);
    return null;
  }
}

export async function fetch_forets_from_code(codeForet) {
  // codeForet est de la forme "48-BOUGES" (departement-code de la forêt) pour les forêts ONF
  // ou "48474-48-1419-1" pour les forêts DGD (document de gestion durable)
  try {
    const response = await apiRequest('GET', `api/declaration/foret_from_code/${codeForet}`);
    return response;
  } catch (error) {
    console.error('Erreur lors de la récupération des forêts par code', error);
    return null;
  }
}

// export async function fetch_all_foret_onf() {
//   try {
//     const response = await apiRequest(
//       'GET',
//       `api/ref_geo/areas_simples_from_type_code/l/OEASC_ONF_FRT`
//     );
//     return response;
//   } catch (error) {
//     console.error('Erreur lors de la récupération des forêts par code', error);
//     return null;
//   }
// }

// export async function fetch_all_foret_dgd() {
//   try {
//     const response = await apiRequest(
//       'GET',
//       `api/ref_geo/areas_simples_from_type_code/l/OEASC_DGD`
//     );
//     return response;
//   } catch (error) {
//     console.error('Erreur lors de la récupération des forêts par code', error);
//     return null;
//   }
// }

// export async function fetch_proprietaires_from_id_declarant(idDeclarant) {
//   try {
//     const response = await apiRequest(
//       'GET',
//       `api/declaration/proprietaire_from_id_declarant/${idDeclarant}`
//     );
//     return response;
//   } catch (error) {
//     console.error('Erreur lors de la récupération des propriétaires par ID déclarant', error);
//     return null;
//   }
// }

export async function fetch_proprietaires_from_id(id_proprietaire) {
  try {
    const response = await apiRequest(
      'GET',
      `api/declaration/proprietaire_from_id/${id_proprietaire}`
    );
    return response;
  } catch (error) {
    console.error('Erreur lors de la récupération des propriétaires par ID propriétaire', error);
    return null;
  }
}

/**
 * Retourne les zones géographiques de type id_type_area. 327: OEASC_COMMUNE, 333: OEASC_SECTION, 331: OEASC_DGD, 328: OEASC_ONF_FRT, 332: OEASC_CADASTRE
 * @param {*} id_type_area int Correspond à id_type dans la table ref_geo.l_areas.id_type
 * @returns GeoJSON des zones géographiques de type id_type_area
 */
export async function fetch_areas_group_from_id_type(id_type_area) {
  const area_code = CODE_AREA[id_type_area];
  try {
    const response = await apiRequest(
      'GET',
      `api/ref_geo/areas_simples_from_type_code/l/${area_code}`
    );
    return response;
  } catch (error) {
    console.error(`Erreur lors de la récupération des ${area_code} par code`, error);
    return null;
  }
}

// export async function fetch_nomenclatures() {
//   try {
//     const response = await apiRequest('GET', `api/oeasc/nomenclatures`);
//     return response;
//   } catch (error) {
//     console.error(`Erreur lors de la récupération des nomemclatures`, error);
//     return null;
//   }
// }

/**
 *
 * @param {*} id_area_parent
 * @param {*} id_type_parent
 * @returns geoJSON des zones géographiques enfants contenu dans la zone parent. Par exemple les cadastres d'une commune ou les cadastres d'une forêt.
 */
export async function fetch_areas_child_of(id_area_parent, id_type_parent) {
  try {
    const response = await apiRequest(
      'GET',
      `api/ref_geo/areas_child_of/${id_type_parent}/${id_area_parent}`
    );
    return response;
  } catch (error) {
    console.error('Erreur lors de la récupération des zones enfants', error);
    return null;
  }
}

/**
 * les idsSection peuvent être de la forme "277378-277379-277380"
 * @param {*} idsSection string de la forme "277378-277379-277380" ou tableau d'entiers [277378, 277379, 277380]
 * @returns geoJSON des sections oeasc
 */
// export async function fetch_areas_section_by_ids(idsSection) {
//   try {
//     const response = await apiRequest(
//       'GET',
//       `api/ref_geo/areas_simples_from_type_code_container/l/OEASC_SECTION/${idsSection}`
//     );
//     return response;
//   } catch (error) {
//     console.error('Erreur lors de la récupération de la section oeasc', error);
//     return null;
//   }
// }

/**
 * retourne les zones géographiques à partir d'une liste d'identifiants
 * @param {*} list_id_areas
 * @returns  GeoJSON des zones géographiques
 */
export async function fetch_areas_from_list_ids(list_id_areas) {
  const str_ids = list_id_areas.join('-');
  try {
    const response = await apiRequest('GET', `api/ref_geo/areas/l/${str_ids}`);
    return response;
  } catch (error) {
    console.error('Erreur lors de la récupération de la liste des areas', error);
    return null;
  }
}

export async function fetch_hierarchy_areas(list_id_areas) {
  const str_ids = list_id_areas.join('-');
  try {
    const response = await apiRequest('GET', `api/ref_geo/areas_hierarchy/${str_ids}`);
    return response;
  } catch (error) {
    console.error('Erreur lors de la récupération de la hiérarchie des zones géographiques', error);
    return null;
  }
}

export default {};
