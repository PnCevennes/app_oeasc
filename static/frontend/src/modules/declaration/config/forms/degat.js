const formsDegat = {
    degats: {
        label: 'Indiquez les différents types de dégâts constatés',
        type: 'degats',
        required: true,
        valueFieldName: "id_nomenclature",
        textFieldName: "label_fr",
        multiple: true,
        require: true,
    },
    degats_precision_localisation: {
        type: 'text_area',
        label: 'Indications pour la localisation des dégats'
    }
};

export { formsDegat };
