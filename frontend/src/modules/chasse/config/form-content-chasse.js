// raz des autres champs de localisation
const changeLocalisation = ({baseModel, config}) => {
    for (const name of['secteur', 'zc', 'zi'].filter(n => n != config.name)) {
        baseModel[name] = []
    }
}

export default {
    formDefs: {
        espece: {
            storeName: 'commonsEspece',
            type: 'list_form',
            returnObject: true,
            list_type: 'select',
            label: 'Espece',
            filters: { 'code_espece': ['CF', 'CH', 'MF'] },
            default: 1,
        },
        secteur: {
            storeName: 'commonsSecteur',
            type: 'list_form',
            multiple: true,
            returnObject: false,
            list_type: 'select',
            label: 'Secteur',
            change: changeLocalisation
        },
        zc: {
            storeName: 'chasseZoneCynegetique',
            type: 'list_form',
            multiple: true,
            returnObject: false,
            list_type: 'select',
            label: 'ZC',
            change: changeLocalisation
        },
        zi: {
            storeName: 'chasseZoneIndicative',
            type: 'list_form',
            multiple: true,
            returnObject: false,
            list_type: 'autocomplete',
            label: 'ZI',
            change: changeLocalisation
        },
    },
    groups: [{
        direction: 'row',
        forms: ['espece', 'secteur', 'zc', 'zi'],
    }]
}