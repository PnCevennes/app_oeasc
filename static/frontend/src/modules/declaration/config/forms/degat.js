const formsDegat = {
    degats: {
        type: 'degats',
        required: true,
        valueFieldName: "id_nomenclature",
        textFieldName: "label_fr",
        multiple: true,
        require: true,
    },
    degats_precision_localisation: {
        type: 'text_area'
    }
};

export { formsDegat };
