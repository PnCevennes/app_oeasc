from flask import (
    Blueprint
)

import app.modules.oeasc.utils as utils

from .repository import (

    get_db,
    get_declarations

)

bp = Blueprint('oeasc_export', __name__)


@bp.route('csv', methods=['GET'])
def csv():

    declarations = get_declarations(True)

    filename = 'declarations'

    colums = [

        'Nom',
        'Organisme',
        'Date (Année-Mois-Jour)',
        'Nom forêt',
        'Nom proprietaire',
        'Communes',
        'Parcelles',
        'Essences',
        'Type de peuplement',
        'Origine du peuplement',
        'Dégat type',
        'Dégat essence',
        'Gravité',
        'Étendue',
        'Antériorité',

    ]

    separator = ';'

    nomenclature = utils.nomenclature_oeasc()

    data = []

    for declaration in declarations:

        declarant = declaration['declarant']
        foret = declaration['foret']
        proprietaire = declaration['foret']['proprietaire']

        essences = [utils.get_nomenclature_from_id(declaration['id_nomenclature_peuplement_essence_principale'], nomenclature)]
        for id in declaration['nomenclatures_peuplement_essence_secondaire']:
            essences.append(utils.get_nomenclature_from_id(id["id_nomenclature"], nomenclature))
        s_essences = ", ".join(essences)

        nom_declarant = declarant['nom_role'] + ' ' + declarant['prenom_role']
        organisme_declarant = utils.get_organisme_name_from_id_declarant(declaration['id_declarant'])
        date = utils.print_date(declaration['meta_create_date'])

        nom_foret = foret["nom_foret"]
        nom_proprietaire = proprietaire["nom_proprietaire"]
        communes = ", ".join([utils.print_commune(commune) for commune in foret['communes']])

        parcelles = ", ".join([utils.print_parcelle(get_db('t_areas', 'id_area', area['id_area'])['area_name']) for area in declaration['areas_localisation']])

        peuplement_type = utils.get_nomenclature_from_id(declaration['id_nomenclature_peuplement_type'], nomenclature)
        peuplement_origine = utils.get_nomenclature_from_id(declaration['id_nomenclature_peuplement_origine'], nomenclature)

        for degat in declaration['degats']:

            degat_type = utils.get_nomenclature_from_id(degat['id_nomenclature_degat_type'], nomenclature)

            for degat_essence in degat['degat_essences']:

                degat_essence_ = utils.get_nomenclature_from_id(degat_essence['id_nomenclature_degat_essence'], nomenclature)
                degat_etendue = utils.get_nomenclature_from_id(degat_essence['id_nomenclature_degat_etendue'], nomenclature)
                degat_anteriorite = utils.get_nomenclature_from_id(degat_essence['id_nomenclature_degat_anteriorite'], nomenclature)
                degat_gravite = utils.get_nomenclature_from_id(degat_essence['id_nomenclature_degat_gravite'], nomenclature)

                d = [

                    nom_declarant,
                    organisme_declarant,
                    date,
                    nom_foret,
                    nom_proprietaire,
                    communes,
                    parcelles,
                    s_essences,
                    peuplement_type,
                    peuplement_origine,
                    degat_type,
                    degat_essence_,
                    degat_gravite,
                    degat_etendue,
                    degat_anteriorite,

                ]

                data.append(d)

    return utils.arrays_to_csv(filename, data, colums, separator)
