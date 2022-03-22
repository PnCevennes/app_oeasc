// raz des autres champs de localisation
const changeLocalisation = ({baseModel, config}) => {
    for (const name of['id_secteur', 'id_zone_cynegetique', 'id_zone_indicative'].filter(n => n != config.name)) {
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
        },
        id_saison: {
            label: "Saison",
            storeName: "chasseSaison",
            type: "list_form",
            list_type: "select",
            returnObject: false,
            required: true,
            default: ({ $store }) => $store._actions.lastSaison[0]($store, {returnObject:false})
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
        forms: ['id_saison', 'id_espece', 'id_secteur', 'id_zone_cynegetique', 'id_zone_indicative'],
    }]
}