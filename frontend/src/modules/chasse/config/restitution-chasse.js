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
        fieldName: 'nom_espece',
        fieldName2: 'label_sexe',
        dataType: 'chasse',
        typeGraph: 'column',
        filters: {
            nom_zone_cynegetique: [ "Causse Méjean" ]
        },
        filterList: [ "nom_zone_cynegetique" ]
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
        nom_espece: {
            text: 'Espece'
        },
        nom_saison: {
            text: 'Saison'
        }
    }
}