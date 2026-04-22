// import moment from "moment";
import { copy } from '@/core/js/util/util';

import config_variables from '@/../../config/variables/declaration.json';

/**
 * Retourne les zones de localisation associées à une déclaration selon son statut public et la présence d'un document.
 *
 * Si la déclaration est publique (`b_statut_public === true`) et possède un document (`b_document == true`),
 * la fonction retourne les zones de localisation ONF/UG (`areas_localisation_onf_ug`).
 * Sinon, elle retourne les zones de localisation cadastrales (`areas_localisation_cadastre`).
 *
 * Cette fonction est généralement utilisée lors de l'affichage ou du traitement des informations de localisation
 * d'une déclaration, afin de sélectionner dynamiquement les zones pertinentes selon le contexte de la déclaration.
 *
 * @param {Object} d - Objet représentant une déclaration, contenant les propriétés de statut, document et zones de localisation.
 * @param {boolean} d.b_statut_public - Indique si la déclaration est publique.
 * @param {boolean} d.b_document - Indique si la déclaration possède un document associé.
 * @param {Array|Object} d.areas_localisation_onf_ug - Zones de localisation ONF/UG.
 * @param {Array|Object} d.areas_localisation_cadastre - Zones de localisation cadastrales.
 * @returns {Array|Object} Les zones de localisation pertinentes selon le statut et le document de la déclaration.
 */
const declarationLocalisationAreas = function (d) {
  return d.b_statut_public === true && d.b_document == true
    ? d.areas_localisation_onf_ug
    : d.areas_localisation_cadastre;
};

/**
 * Retourne les zones de forêt associées à une déclaration selon l'état des propriétés du document.
 *
 * - Si le document n'est pas présent (`b_document == false`), retourne directement la section des zones de forêt (`areas_foret_section`).
 * - Si le document est présent et est public (`b_statut_public == true`), retourne la zone de forêt ONF (`areas_foret_onf`) sous forme de tableau.
 * - Sinon, retourne la zone de forêt DGD (`areas_foret_dgd`) sous forme de tableau.
 *
 * Cette fonction est généralement utilisée lors du traitement ou de l'affichage des déclarations de zones forestières,
 * afin de déterminer dynamiquement quelles zones doivent être prises en compte selon le statut du document et sa visibilité.
 *
 * @param {Object} d - Objet représentant une déclaration, contenant les propriétés nécessaires à la sélection des zones.
 * @param {boolean} d.b_document - Indique si le document est présent ou non.
 * @param {boolean} d.b_statut_public - Indique si le document est public.
 * @param {Array|Object} d.areas_foret_section - Liste ou objet des zones de forêt de la section.
 * @param {Object} d.areas_foret_onf - Zone de forêt ONF.
 * @param {Object} d.areas_foret_dgd - Zone de forêt DGD.
 * @returns {Array|Object} Les zones de forêt pertinentes selon le statut du document.
 */
const declarationForetAreas = function (d) {
  return d.b_document == false
    ? d.areas_foret_section
    : d.b_statut_public
      ? [d.areas_foret_onf]
      : [d.areas_foret_dgd];
};

/**
 * Récupère les données de déclaration en dispatchant l'action "areas" avec les zones de localisation de la déclaration.
 *
 * @param {Object} params - Les paramètres de la fonction.
 * @param {Object} params.declaration - L'objet déclaration contenant les informations nécessaires.
 * @param {Object} params.$store - L'instance du store Vuex utilisée pour dispatcher les actions.
 * @returns {Promise<void>} Une promesse qui est résolue lorsque l'action "areas" a été dispatchée et terminée.
 *
 * @description
 * Cette fonction est généralement utilisée lors de l'initialisation ou de la mise à jour des données de déclaration,
 * afin de charger les zones de localisation associées à une déclaration spécifique dans le store.
 */
const getDeclarationData = function ({ declaration, $store }) {
  return new Promise((resolve) => {
    $store.dispatch('areas', declarationLocalisationAreas(declaration)).then(() => {
      resolve();
    });
  });
};

/**
 * Transforme un objet de déclaration brute en un objet prêt à être affiché dans l'interface utilisateur.
 *
 * Cette fonction prend une déclaration et le store Vuex, puis enrichit et formate les données pour l'affichage :
 * - Traduit les valeurs booléennes en labels lisibles (ex : "Validé", "Non validé", "En attente").
 * - Formate la date de création.
 * - Récupère les labels des nomenclatures via les getters du store pour plusieurs champs.
 * - Remplace certains labels par des valeurs personnalisées si nécessaire (ex : protection "Autre").
 * - Pour chaque dégât et essence de dégât, ajoute les labels correspondants.
 * - Génère une chaîne descriptive des parcelles à partir des zones de localisation.
 *
 * Cette fonction est généralement utilisée lors de l'affichage d'une déclaration dans l'application,
 * afin de présenter des informations compréhensibles à l'utilisateur.
 *
 * @function
 * @param {Object} params - Les paramètres de la fonction.
 * @param {Object} params.declaration - L'objet déclaration brut à transformer.
 * @param {Object} params.$store - L'instance du store Vuex pour accéder aux getters de nomenclature.
 * @returns {Object} Un nouvel objet déclaration enrichi et formaté pour l'affichage.
 */
const rawToDisplay = function ({ declaration, $store }) {
  const d = copy(declaration);

  d.valide =
    declaration.b_valid === true
      ? 'Validé'
      : declaration.b_valid === false
        ? 'Non validé'
        : 'En attente';

  if (d.meta_create_date) {
    d.declaration_date = new Date(d.meta_create_date).toLocaleDateString();
  }

  d.peuplement_acces_label = $store.getters.nomenclatureString(d.id_nomenclature_peuplement_acces);

  d.espece_label = $store.getters.nomenclatureString(d.nomenclatures_peuplement_espece);

  d.statut_public =
    d.b_statut_public === true ? 'Public' : d.b_statut_public === false ? 'Privé' : 'Indéfini';

  d.foret_type_label = $store.getters.nomenclatureString(d.id_nomenclature_proprietaire_type);

  d.peuplement_ess_1_label = $store.getters.nomenclatureString(
    d.id_nomenclature_peuplement_essence_principale
  );

  d.peuplement_ess_2_label = $store.getters.nomenclatureString(
    d.nomenclatures_peuplement_essence_secondaire
  );
  d.peuplement_ess_3_label = $store.getters.nomenclatureString(
    d.nomenclatures_peuplement_essence_complementaire
  );

  d.peuplement_origine_label = $store.getters.nomenclatureString(
    d.id_nomenclature_peuplement_origine
  );
  d.peuplement_origine2_label = $store.getters.nomenclatureString(
    d.nomenclatures_peuplement_origine2
  );

  d.peuplement_type_label = $store.getters.nomenclatureString(d.id_nomenclature_peuplement_type);
  d.peuplement_maturite_label = $store.getters.nomenclatureString(
    d.nomenclatures_peuplement_maturite
  );

  d.peuplement_protection_type_label = $store.getters.nomenclatureString(
    d.nomenclatures_peuplement_protection_type
  );
  if (d.autre_protection) {
    d.peuplement_protection_type_label = d.peuplement_protection_type_label.replace(
      'Autre (préciser)',
      d.autre_protection
    );
  }

  d.peuplement_paturage_type_label = $store.getters.nomenclatureString(
    d.nomenclatures_peuplement_paturage_type
  );

  d.peuplement_paturage_statut_label = $store.getters.nomenclatureString(
    d.id_nomenclature_peuplement_paturage_statut
  );

  d.peuplement_paturage_frequence_label = $store.getters.nomenclatureString(
    d.id_nomenclature_peuplement_paturage_frequence
  );

  d.peuplement_paturage_saison_label = $store.getters.nomenclatureString(
    d.nomenclatures_peuplement_paturage_saison
  );

  for (const degat of d.degats || []) {
    degat.degat_type_label = $store.getters.nomenclatureString(degat.id_nomenclature_degat_type);
    degat.degat_type_mnemo = $store.getters.nomenclatureString(
      degat.id_nomenclature_degat_type,
      'mnemonique'
    );

    for (const degatEssence of degat.degat_essences || []) {
      degatEssence.degat_essence_label = $store.getters.nomenclatureString(
        degatEssence.id_nomenclature_degat_essence
      );
      degatEssence.degat_gravite_label = $store.getters.nomenclatureString(
        degatEssence.id_nomenclature_degat_gravite
      );
      degatEssence.degat_anteriorite_label = $store.getters.nomenclatureString(
        degatEssence.id_nomenclature_degat_anteriorite
      );
      degatEssence.degat_etendue_label = $store.getters.nomenclatureString(
        degatEssence.id_nomenclature_degat_etendue
      );
    }
  }

  const areas_parcelles = declarationLocalisationAreas(d);

  d.parcelles = $store.getters.areaString(areas_parcelles);

  return d;
};

/**
 * Formate et regroupe une liste de parcelles agricoles sous forme de chaîne de caractères.
 *
 * Cette fonction prend une chaîne de caractères représentant des parcelles séparées par des virgules,
 * où chaque parcelle est au format "section-numero-index" (ex: "A-12-3, A-12-4, B-15-1").
 * Elle regroupe les parcelles ayant la même section et le même numéro, et affiche les index entre parenthèses
 * si plusieurs parcelles appartiennent au même groupe (ex: "A-12-(3, 4), B-15-1").
 * Si le format de la première parcelle ne correspond pas au format attendu, la chaîne d'entrée est retournée telle quelle.
 *
 * @param {string} parcelles - Chaîne de caractères contenant la liste des parcelles à formater.
 * @returns {string} La chaîne de caractères formatée et regroupée.
 *
 * @example
 * // Affiche : "A-12-(3, 4), B-15-1"
 * displayParcelles("A-12-3, A-12-4, B-15-1");
 *
 * @occasion
 * Cette fonction est utilisée lors de l'affichage des parcelles dans l'interface utilisateur,
 * afin de présenter les informations de manière plus lisible et synthétique.
 */
const displayParcelles = function (parcelles) {
  const parcellesArray = parcelles.split(', ');
  if (parcellesArray[0].split('-').length != 3) {
    return parcelles;
  }

  const groups = {};
  for (const parcelle of parcellesArray) {
    const parcelleArray = parcelle.split('-');
    const group_key = parcelleArray[0] + '-' + parcelleArray[1];
    if (!Object.keys(groups).includes(group_key)) {
      groups[group_key] = [];
    }
    groups[group_key].push(parcelleArray[2]);
  }
  return Object.keys(groups)
    .map((group_key) => {
      const group = groups[group_key];
      return group.length == 1 ? `${group_key}-${group[0]}` : `${group_key}-(${group.join(', ')})`;
    })
    .join(', ');
};

const displayDate = function (date) {
  // retourne unet date au format jj/mm/aaaa
  if (!date) {
    return '';
  }
  const d = new Date(date);
  const day = String(d.getDate()).padStart(2, '0');
  const month = String(d.getMonth() + 1).padStart(2, '0');
  const year = d.getFullYear();
  return `${day}/${month}/${year}`;
};

/**
 * Affiche le statut d'une déclaration à partir de son code. Calcule le numéro de relance
 * la première relance correspond normalement a 100, la deuxième a 101 etc
 *
 * @param {*} statut
 * @returns
 */
const displayStatut = function (statut) {
  if (statut == config_variables['STATUT_DECLARATION']['Active']) {
    return 'Active';
  } else if (statut == config_variables['STATUT_DECLARATION']['Archivée']) {
    return 'Archivée';
  } else if (statut == config_variables['STATUT_DECLARATION']['Archivée sans réponse']) {
    return 'Archivée ss réponse';
  } else if (statut >= config_variables['STATUT_DECLARATION']['Relance']) {
    return 'Relance no ' + (statut - config_variables['STATUT_DECLARATION']['Relance'] + 1);
  } else {
    return 'Inconnu';
  }
};

export {
  displayParcelles,
  rawToDisplay,
  getDeclarationData,
  displayDate,
  displayStatut,
  // declarationForetAreas,
  // declarationLocalisationAreas
};
