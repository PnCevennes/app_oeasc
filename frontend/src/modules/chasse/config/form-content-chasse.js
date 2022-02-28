// raz des autres champs de localisation
const changeLocalisation = ({baseModel, config}) => {
    for (const name of['secteur', 'zc', 'zi'].filter(n => n != config.name)) {
        baseModel[name] = []
    }
}

export default {
    formDefs: {
        id_espece: {
            storeName: 'commonsEspece',
            type: 'list_form',
            returnObject: false,
            list_type: 'select',
            label: 'Espece',
            filters: { 'code_espece': ['CF', 'CH', 'MF'] },
            default: 1,
        },
        ids_secteur: {
            storeName: 'commonsSecteur',
            type: 'list_form',
            multiple: true,
            returnObject: false,
            list_type: 'select',
            label: 'Secteur',
            change: changeLocalisation
        },
        ids_zone_cynegetique: {
            storeName: 'chasseZoneCynegetique',
            type: 'list_form',
            multiple: true,
            returnObject: false,
            list_type: 'select',
            label: 'ZC',
            change: changeLocalisation
        },
        ids_zone_indicative: {
            storeName: 'chasseZoneIndicative',
            type: 'list_form',
            multiple: true,
            returnObject: false,
            list_type: 'autocomplete',
            label: 'ZI',
            change: changeLocalisation
        },
        // s_min: {
        //     storeName: 'chasseSaison',
        //     type: 'list_form',
        //     multiple: false,
        //     returnObject: false,
        //     list_type: 'autocomplete',
        //     label: "Saison (min)"
        // }
    },
    groups: [{
        direction: 'row',
        forms: ['id_espece', 'ids_secteur', 'ids_zone_cynegetique', 'ids_zone_indicative'],
    }]
}