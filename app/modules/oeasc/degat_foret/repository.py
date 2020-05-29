'''
    degat module api
'''

from flask import current_app

from ..declaration.models import TProprietaire, TForet, TDeclaration
from ..declaration.repository import patch_areas_declarations


from ..nomenclature import get_area_from_id, get_nomenclature_from_id
from ..user.models import VUsers


config = current_app.config
DB = config['DB']



def create_or_modify(model, key, dict_in):
    """
        fonction generique de creation ou modification
    """
    elem = None

    if key:

        val = dict_in.get(key, None)
        if val:
            elem = DB.session.query(model).filter(getattr(model, key) == val).first()

    print(elem)

    if elem is None:
        elem = model()
        DB.session.add(elem)

    elem.from_dict(dict_in, True)

    DB.session.commit()

    return elem


def get_declaration(id_declaration):
    '''
    create_or_update_declaration
    '''

    try:
        declaration = (
            DB.session.query(TDeclaration)
            .filter(
                TDeclaration.id_declaration == id_declaration
            )
            .one()
        )

        foret = (
            DB.session.query(TForet)
            .filter(
                TForet.id_foret == declaration.id_foret
            )
            .one()
        )

        proprietaire = (
            DB.session.query(TProprietaire)
            .filter(
                TProprietaire.id_proprietaire == foret.id_proprietaire
            )
            .one()

        )


    except Exception:
        return (TDeclaration(), TForet(), TProprietaire())

    return (declaration, foret, proprietaire)


def create_or_update_declaration(post_data):
    '''
    create_or_update_declaration
    '''

    # nomenclature
    for key in post_data:
        if 'nomenclatures_' in key:
            post_data[key] = [
                {
                    'id_declaration': post_data.get('id_declaration'),
                    'id_nomenclature': id_nomenclature
                }
                for id_nomenclature in post_data[key] 
            ]

    # areas
    post_data['areas_foret'] = [] + post_data['areas_foret_communes'] +  post_data['areas_foret_sections']
    if post_data['areas_foret_onf']:
        post_data['areas_foret'].append(post_data['areas_foret_onf'])
    if post_data['areas_foret_dgd']:
        post_data['areas_foret'].append(post_data['areas_foret_dgd'])

    post_data['areas_localisation'] = ( 
        [] +
        post_data['areas_localisation_cadastre'] +
        post_data['areas_localisation_onf_prf'] +
        post_data['areas_localisation_onf_ug']
    ) 

    for key in ['areas_localisation', 'areas_foret']:
        post_data[key] = [
            {
                'id_area': id_area,
                'id_declaration': post_data.get('id_declaration')
            }
            for id_area in post_data[key]
        ]


    if not post_data['b_document']:

        print('id_declarant', post_data['id_declarant'])

        id_declarant = post_data['id_declarant']

        nomenclature = (
            post_data['id_nomenclature_proprietaire_declarant'] and
            get_nomenclature_from_id(post_data['id_nomenclature_proprietaire_declarant']) 
        )

        if nomenclature and nomenclature['cd_nomenclature'] != 'P_D_O_NP':
            post_data['id_declarant'] = None
        # proprietaire
        proprietaire = create_or_modify(
            TProprietaire,
            'id_proprietaire',
            post_data
        )

        post_data['id_proprietaire'] = proprietaire.id_proprietaire

        post_data['id_declarant'] = id_declarant


        # foret
        foret = create_or_modify(
            TForet,
            'id_foret',
            post_data
        )
        post_data['id_foret'] = foret.id_foret

    else:
        # get id_foret form id_areas
        id_area_foret = post_data['areas_foret_onf'] or post_data['areas_foret_dgd']

        code_foret = get_area_from_id(id_area_foret)['area_code']

        foret = DB.session.query(TForet).filter(TForet.code_foret == code_foret).first()

        post_data['id_foret'] = foret.id_foret

    # declaration

    post_data['foret'] = foret.as_dict(True)


    declaration = create_or_modify(
        TDeclaration,
        'id_declaration',
        post_data
    )

    patch_areas_declarations(declaration.id_declaration)

    return declaration.as_dict(True)


def get_id_areas(areas, type_list):
    '''
        get_id_areas
    '''
    
    return [
        x['id_area'] for x in filter(
            lambda x: x['type_code'] in type_list,
            areas
        )
    ]


def get_id_area(areas, type_list):
    '''
        get_id_area
    '''

    id_areas = get_id_areas(areas, type_list)
    return id_areas[0] if id_areas else None

def get_foret_from_code(code_foret):
    '''
        get_foret_from_code
    '''
    print('code_foret', code_foret)
    foret = (
        DB.session.query(TForet)
        .filter(TForet.code_foret == code_foret)
        .first()
    )

    proprietaire = (
        DB.session.query(TProprietaire)
        .filter(TProprietaire.id_proprietaire == foret.id_proprietaire)
        .first()
    )

    return (foret, proprietaire)

def get_proprietaire_from_id_declarant(id_declarant):
    proprietaire = (
        DB.session.query(TProprietaire)
        .filter(TProprietaire.id_declarant == id_declarant)
        .first()
    )

    return proprietaire or TProprietaire()


def get_declarations():

    declarations = (
        DB.session.query(TDeclaration, TForet, VUsers)
        .join(TForet, TForet.id_foret == TDeclaration.id_foret)
        .join(VUsers, VUsers.id_role == TDeclaration.id_declarant)
        .all()
    )

    print(declarations)
    out = []
    for declaration in declarations:
        d = declaration[0].as_dict()
        f = declaration[1].as_dict()
        u = declaration[2].as_dict()
        d.update(f)
        d.update(u)
        out.append(d)

    return out

def hide_proprietaire(proprietaire):
    for key in [
        'nom_proprietaire',
        'adresse',
        's_code_postal',
        's_commune_proprietaire'
    ]:
        proprietaire[key] = '***'

    proprietaire['telephone'] = '09 99 99 99 99'
    proprietaire['email'] = 'prive@prive.prive'
