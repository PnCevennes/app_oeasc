from flask import (
    Blueprint
)

import app.modules.oeasc.utils as utils

from .repository import (

    get_db,
    get_declarations,
    nomenclature_oeasc,
    get_dict_nomenclature_areas,

)

from .models import (

    TDeclaration

)

from app.utils.env import DB

from .utils import (

    check_foret

)

from .declaration_sample import declaration_dict_random_sample

from app.utils.utilssqlalchemy import (

    json_resp

)

from .mail import (
    send_mail_test,
    display_mail_test,
)
bp = Blueprint('oeasc_export', __name__)


@bp.route('test_check_foret/<int:id_area>', methods=['GET'])
@json_resp
def test_check_foret(id_area):

    declaration = declaration_dict_random_sample()

    nomenclature = nomenclature_oeasc()

    get_dict_nomenclature_areas(declaration, nomenclature)

    check_foret(declaration)

    return declaration


@bp.route('get_nomenclature', methods=['GET'])
@json_resp
def get_nomenclature():

    declaration = declaration_dict_random_sample()

    nomenclature = nomenclature_oeasc()

    get_dict_nomenclature_areas(declaration, nomenclature)

    return declaration


def get_all_declarations():

    data = DB.session.query(TDeclaration).all()

    if not data:

        return None

    out = [get_dict_nomenclature_areas(d.as_dict(True)) for d in data]

    return out


@bp.route('get_declarations', methods=['GET'])
@json_resp
def declarations():

    return get_all_declarations()


@bp.route('get_degats', methods=['GET'])
@json_resp
def get_degats():

    data = get_all_declarations()

    nb_alertes = len(data)

    out = {'nb_alertes': nb_alertes}

    degat_types = {}

    for d in data:

        degats = d.get('degats', None)

        for degat in degats:

            degat_type = degat['id_nomenclature_degat_type']['label_fr']
            degat_type_mnem = degat['id_nomenclature_degat_type']['mnemonique']

            if not degat_types.get(degat_type_mnem, None):

                degat_types[degat_type_mnem] = {'name': degat_type_mnem, 'label': degat_type, 'value': 1}

            else:

                degat_types[degat_type_mnem]['value'] += 1

    out['data'] = [degat_types[v] for v in degat_types]

    return out


@bp.route("send_mail", methods=['GET'])
def test_mail():

    send_mail_test()

    return "ok"


@bp.route("display_mail/<string:destinataire>", methods=['GET'])
def test_mail_display(destinataire):

    return display_mail_test(destinataire)


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
        'Pâturage type',
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



