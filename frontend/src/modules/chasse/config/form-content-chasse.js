// raz des autres champs de localisation
const changeLocalisation = ({baseModel, config}) => {
    for (const name of['id_secteur', 'id_zone_cynegetique', 'id_zone_indicative'].filter(n => n != config.name)) {
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
        change: changeLocalisation
    },
    id_zone_cynegetique: {
        storeName: 'chasseZoneCynegetique',
        type: 'list_form',
        multiple: true,
        returnObject: false,
        list_type: 'select',
        label: 'ZC',
        change: changeLocalisation
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

// Construction du formulaire en fonction d'une liste de champs passés en argument
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