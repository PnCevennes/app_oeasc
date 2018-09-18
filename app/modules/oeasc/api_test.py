from flask import (
    Blueprint
)

import app.modules.oeasc.utils as utils

from .repository import (

    get_db,
    get_declarations,
    nomenclature_oeasc,
    get_declaration_nomenclature,
    get_dict_nomenclature_areas,
)

from .declaration_sample import declaration_dict_random_sample

from app.utils.utilssqlalchemy import (

    json_resp

)

bp = Blueprint('oeasc_export', __name__)


@bp.route('get_nomenclature', methods=['GET'])
@json_resp
def get_nomenclature():

    declaration = declaration_dict_random_sample()

    nomenclature = nomenclature_oeasc()

    get_dict_nomenclature_areas(declaration, nomenclature)
    # get_dict_nomenclature_areas(declaration['foret'], nomenclature)
    # get_dict_nomenclature_areas(declaration['foret']['proprietaire'], nomenclature)

    # for degat in declaration['degats']:

    #     get_dict_nomenclature_areas(degat, nomenclature)

    #     for degat_essence in degat.get('degat_essences', []):

    #         get_dict_nomenclature_areas(degat_essence, nomenclature)

    return declaration


@bp.route('csv', methods=['GET'])
def csv():

    declarations = get_declarations(True)

    filename = 'declarations'

    colums = [
        'No',
        'Nom',
        'Organisme',
        'Date (Année-Mois-Jour)',
        'Nom forêt',
        'Nom proprietaire',
        'Communes',
        'Parcelles',
        'Essence Principale',
        'Essence(s) Secondaire(s)',
        'Essence(s) Complementaire(s)',
        'Type de peuplement',
        'Origine du peuplement',
        'Paturage type',
        'Pâturage statut',
        'Pâturage frequence',
        'Protection type ',
        'Espèces',
        'Dégat type',
        'Dégat essence',
        'Gravité',
        'Étendue',
        'Antériorité',

    ]

    separator = ';'

    nomenclature = utils.nomenclature_oeasc()

    data = []
    numero = 0

    for declaration in declarations:

        numero += 1
        declarant = declaration['declarant']
        foret = declaration['foret']
        proprietaire = declaration['foret']['proprietaire']

        # essences = [utils.get_nomenclature_from_id(declaration['id_nomenclature_peuplement_essence_principale'], nomenclature)]
        s_essence_principale = utils.get_nomenclature_from_id(declaration['id_nomenclature_peuplement_essence_principale'], nomenclature)

        essences = []
        for id in declaration['nomenclatures_peuplement_essence_secondaire']:
            essences.append(utils.get_nomenclature_from_id(id["id_nomenclature"], nomenclature))
        s_essence_secondaire = ", ".join(sorted(essences))

        essences = []
        for id in declaration['nomenclatures_peuplement_essence_complementaire']:
            essences.append(utils.get_nomenclature_from_id(id["id_nomenclature"], nomenclature))
        s_essence_complementaire = ", ".join(sorted(essences))

        nom_declarant = declarant['nom_role'] + ' ' + declarant['prenom_role']
        organisme_declarant = utils.get_organisme_name_from_id_declarant(declaration['id_declarant'])
        date = utils.print_date(declaration['meta_create_date'])

        nom_foret = foret["nom_foret"]
        nom_proprietaire = proprietaire["nom_proprietaire"]
        communes = ", ".join([utils.print_commune(commune) for commune in foret['communes']])

        parcelles = ", ".join([utils.print_parcelle(get_db('t_areas', 'id_area', area['id_area'])['area_name']) for area in declaration['areas_localisation']])

        peuplement_type = utils.get_nomenclature_from_id(declaration['id_nomenclature_peuplement_type'], nomenclature)
        peuplement_origine = utils.get_nomenclature_from_id(declaration['id_nomenclature_peuplement_origine'], nomenclature)

        # paturage_type = utils.get_nomenclature_from_id(declaration['id_nomenclature_paturage_type'], nomenclature)
        paturage_frequence = utils.get_nomenclature_from_id(declaration['id_nomenclature_peuplement_paturage_frequence'], nomenclature)
        # paturage_statut = utils.get_nomenclature_from_id(declaration['id_nomenclature_paturage_statut'], nomenclature)

        liste = []
        for id in declaration['nomenclatures_peuplement_paturage_type']:
            liste.append(utils.get_nomenclature_from_id(id["id_nomenclature"], nomenclature))
        paturage_type = ", ".join(sorted(liste))

        liste = []
        for id in declaration['nomenclatures_peuplement_paturage_statut']:
            liste.append(utils.get_nomenclature_from_id(id["id_nomenclature"], nomenclature))
        paturage_statut = ", ".join(sorted(liste))

        liste = []
        for id in declaration['nomenclatures_peuplement_protection_type']:
            liste.append(utils.get_nomenclature_from_id(id["id_nomenclature"], nomenclature))
        protection_type = ", ".join(sorted(liste))

        liste = []
        for id in declaration['nomenclatures_peuplement_espece']:
            liste.append(utils.get_nomenclature_from_id(id["id_nomenclature"], nomenclature))
        espece = ", ".join(sorted(liste))

        for degat in declaration['degats']:

            degat_type = utils.get_nomenclature_from_id(degat['id_nomenclature_degat_type'], nomenclature)

            for degat_essence in degat['degat_essences']:

                degat_essence_ = utils.get_nomenclature_from_id(degat_essence['id_nomenclature_degat_essence'], nomenclature)
                degat_etendue = utils.get_nomenclature_from_id(degat_essence['id_nomenclature_degat_etendue'], nomenclature)
                degat_anteriorite = utils.get_nomenclature_from_id(degat_essence['id_nomenclature_degat_anteriorite'], nomenclature)
                degat_gravite = utils.get_nomenclature_from_id(degat_essence['id_nomenclature_degat_gravite'], nomenclature)

                d = [
                    numero,
                    nom_declarant,
                    organisme_declarant,
                    date,
                    nom_foret,
                    nom_proprietaire,
                    communes,
                    parcelles,
                    s_essence_principale,
                    s_essence_secondaire,
                    s_essence_complementaire,
                    peuplement_type,
                    peuplement_origine,
                    paturage_type,
                    paturage_statut,
                    paturage_frequence,
                    protection_type,
                    espece,
                    degat_type,
                    degat_essence_,
                    degat_gravite,
                    degat_etendue,
                    degat_anteriorite,

                ]

                data.append(d)

    return utils.arrays_to_csv(filename, data, colums, separator)


