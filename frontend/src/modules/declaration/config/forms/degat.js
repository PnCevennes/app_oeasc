export default {
    degats: {
        label: 'Indiquez les différents types de dégâts constatés',
        type: 'degats',
        required: true,
        valueFieldName: "id_nomenclature",
        displayFieldName: "label_fr",
        multiple: true,
        require: true,
    },
    precision_localisation: {
        type: 'text_area',
        label: 'Indications pour la localisation des dégats'
    }
};
