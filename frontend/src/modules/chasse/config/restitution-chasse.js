/**
 *
 * configuration pour la restitution custom de type 'chasse'
 *
 * TODO compléter la vue sql et la config en fonction des besoins
 */

export default {

    // données d'exemple (dev)
    default: {
        display: 'graph',
        fieldName: 'mois_txt',
        fieldName2: 'bracelet',
        dataType: 'chasse',
        typeGraph: 'column',
        stacking: true,
        filters: {
            nom_espece: [ "Cerf" ],
            nom_saison: ['2020-2021']
        },
        filterList: [ "nom_espece", "nom_saison" ]
    },

    // definitions et labels, en lien avec la vue
    items: {
        label_mode_chasse: {
            text: 'Mode de chasse'
        },
        label_sexe: {
            text: 'Sexe'
        },
        label_classe_age: {
            text: "Classe d'age"
        },
        nom_zone_indicative: {
            text: "Zone indicative"
        },
        nom_zone_cynegetique: {
            text: 'Massif Cynégetique'
        },
        bracelet: {
          text: "Type de bracelet",
        },
        nom_espece: {
            text: 'Espece',
            id: "id_espece"
        },
        nom_saison: {
            text: 'Saison',
            sort: 'nom_saison+'
        },
        mois_txt: {
            text: "Mois",
            sort: "mois_txt_sort"
        }
    }
}