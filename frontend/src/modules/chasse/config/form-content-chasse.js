/**
 * Met à jour les propriétés de localisation du modèle de base en réinitialisant certains champs.
 *
 * Cette fonction est utilisée dans le contexte d'un formulaire Vue.js pour la gestion des localisations
 * (secteur, zone cynégétique, zone indicative) lors d'un changement de sélection. Elle permet de réinitialiser
 * les champs de localisation qui ne correspondent pas au champ actuellement modifié, afin d'éviter des incohérences
 * dans les données du formulaire.
 *
 * @param {Object} params - Les paramètres de la fonction.
 * @param {Object} params.baseModel - L'objet représentant le modèle de base du formulaire, dont les propriétés seront modifiées.
 * @param {Object} params.config - La configuration du champ actuellement modifié, contenant au moins la propriété `name`.
 *
 * @example
 * // Utilisé lors du changement de secteur, zone cynégétique ou zone indicative dans un formulaire de localisation.
 * changeLocalisation({ baseModel: formModel, config: { name: 'id_secteur' } });
 */
const changeLocalisation = ({baseModel, config}) => {
    for (const name of ['id_secteur', 'id_zone_cynegetique', 'id_zone_indicative'].filter(n => n != config.name)) {
        baseModel[name] = []
    }
}

// Liste des champs potentiellement présent dans le formulaire de filtre
const FIELDS = {
    id_saison: {
        label: "Saison",
        storeName: "chasseSaison",
        type: "list_form",
        list_type: "select",
        returnObject: false,
        required: true,
        displayFieldName: "nom_saison",
        displayFieldValue: "id_saison",
        displayFieldSortDesc: true,
        default: ({ $store }) => $store._actions.lastSaison[0]($store, { returnObject: false })
    },
    id_espece: {
        storeName: 'commonsEspece',
        type: 'list_form',
        returnObject: false,
        list_type: 'select',
        label: 'Espece',
        filters: { 'code_espece': ['CF', 'CH', 'MF'] },
        default: 1,
    },
    id_secteur: {
        storeName: 'commonsSecteur',
        type: 'list_form',
        multiple: true,
        returnObject: false,
        list_type: 'select',
        label: 'Secteur',
        change: changeLocalisation // si le champ est modifié, on réinitialise les autres champs de localisation
    },
    id_zone_cynegetique: {
        storeName: 'chasseZoneCynegetique',
        type: 'list_form',
        multiple: true,
        returnObject: false,
        list_type: 'select',
        label: 'ZC', 
        change: changeLocalisation // si le champ est modifié, on réinitialise les autres champs de localisation
    },
    id_zone_indicative: {
        storeName: 'chasseZoneIndicative',
        type: 'list_form',
        multiple: true,
        returnObject: false,
        list_type: 'autocomplete',
        label: 'ZI',
        change: changeLocalisation
    }
}

/**
 * Génère une configuration de formulaire basée sur une liste de champs spécifiée.
 *
 * @function generateConfigformDef
 * @param {string[]=} fieldList - Liste optionnelle des clés de champs à inclure dans la configuration du formulaire.
 *                                Si non spécifiée, tous les champs définis dans FIELDS seront utilisés.
 * @returns {Object} Un objet contenant :
 *   - formDefs {Object} : Un objet dont les clés sont les noms des champs et les valeurs sont les définitions associées depuis FIELDS.
 *   - groups {Array} : Un tableau contenant un seul groupe, qui définit la disposition ('row') et la liste des champs à afficher.
 *
 * @example
 * // Utilisation typique dans un composant Vue.js pour générer dynamiquement un formulaire :
 * const config = generateConfigformDef(['nom', 'prenom']);
 * // config.formDefs contiendra uniquement les définitions pour 'nom' et 'prenom'
 * // config.groups permettra d'afficher ces champs dans une ligne du formulaire
 *
 * @description
 * Cette fonction est utilisée dans les modules de configuration de formulaires dynamiques,
 * notamment pour générer des formulaires personnalisés selon les besoins métier.
 * Elle vérifie que les champs demandés existent bien dans la définition globale FIELDS,
 * puis construit la configuration attendue par le composant de formulaire.
 * Utile pour factoriser la génération de formulaires dans des modules Vue.js complexes.
 */
const generateConfigformDef = (fieldList) => {
    // Si pas de champ spécifié => tous les champs
    if (fieldList === undefined) {
        fieldList = Object.keys(FIELDS)
    }
    // Test si les champs sécifiés sont bien défini
    fieldList = fieldList.filter(x => Object.keys(FIELDS).includes(x));

    let fields = {}

    fieldList.forEach(fieldKey => {
        fields[fieldKey] = FIELDS[fieldKey]
    });

    return {
        formDefs: fields,
        groups: [{
            direction: 'row',
            forms: fieldList,
        }]
    }
}

export {
    generateConfigformDef
}