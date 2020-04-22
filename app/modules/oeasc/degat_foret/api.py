'''
    degat module api
'''

from flask import Blueprint, request, current_app, session
from ..nomenclature import get_area_from_id, get_nomenclature_from_id


from utils_flask_sqla.response import json_resp, json_resp_accept_empty_list

from ..user.utils import check_auth_redirect_login
from .repository import (
    create_or_update_declaration,
    get_declaration,
    get_id_area,
    get_id_areas,
    get_foret_from_code,
    get_proprietaire_from_id_declarant,
    get_declarations,
    hide_proprietaire
    )

from ..declaration.mail import send_mail_validation_declaration
from ..declaration.repository import get_user


bp = Blueprint('degat_foret_api', __name__)


@bp.route('proprietaire_from_id_declarant/<int:id_declarant>', methods=['GET'])
@check_auth_redirect_login(1)
def api_get_proprietaire_from_id_declarant(id_declarant):

    (proprietaire) = get_proprietaire_from_id_declarant(id_declarant)
    out = proprietaire.as_dict(True)
    
    return out



@bp.route('foret_from_code/<string:code_foret>', methods=['GET'])
@check_auth_redirect_login(1)
def api_get_foret_from_code(code_foret):

    (foret, proprietaire) = get_foret_from_code(code_foret)
    out = foret.as_dict(True)
    out.update(proprietaire.as_dict(True))

    nomenclature = get_nomenclature_from_id(proprietaire.id_nomenclature_proprietaire_type)
    if nomenclature['cd_nomenclature'] == 'PT_PRI':
        hide_proprietaire(out)

    return out


@bp.route('declarations/', methods=['GET'])
@check_auth_redirect_login(1)
@json_resp_accept_empty_list
def api_get_declarations():
    return get_declarations()


@bp.route('declaration/<int:id_declaration>', methods=['GET'])
@bp.route('declaration/', methods=['GET'], defaults={'id_declaration': None})
@check_auth_redirect_login(1)
@json_resp_accept_empty_list
def api_get_declaration(id_declaration):
    '''
    api_get_declaraiton
    '''

    (declaration, foret, proprietaire) = get_declaration(id_declaration)

    if not declaration:
        return

    out = declaration.as_dict(True)


    # flat data
    out.update(foret.as_dict(True))

    id_declarant = declaration.id_declarant
    out.update(proprietaire.as_dict(True))
    out['id_declarant'] = id_declarant

    # nomenclature
    for key in out:
        if isinstance(out[key], list) and len(out[key]) > 0 and 'id_nomenclature' in out[key][0]:
            out[key] = [e['id_nomenclature'] for e in out[key]]

    # id_areas TODO in front

    #   foret
    areas_foret = [get_area_from_id(area['id_area']) for area in out['areas_foret']] 

    out['areas_foret_onf'] = get_id_area(areas_foret, ['OEASC_ONF_FRT'])
    out['areas_foret_dgd'] = get_id_area(areas_foret, ['OEASC_DGD'])
    out['areas_foret_communes'] = get_id_areas(areas_foret, ['OEASC_COMMUNE'])
    out['areas_foret_sections'] = get_id_areas(areas_foret, ['OEASC_SECTION'])

    #   declaration
    areas_localisation = [get_area_from_id(area['id_area']) for area in out['areas_localisation']] 
    out['areas_localisation_cadastre'] = get_id_areas(areas_localisation, ['OEASC_CADASTRE'])
    out['areas_localisation_onf_prf'] = get_id_areas(areas_localisation, ['OEASC_ONF_PRF'])
    out['areas_localisation_onf_ug'] = get_id_areas(areas_localisation, ['OEASC_ONF_UG'])

    # hide proprietaire
    current_user = session.get('current_user', None)
    if (current_user['id_droit_max'] < 4) and (current_user['id_role'] != out['id_role']):
        print('hide')
        hide_proprietaire(out)

    return out


@bp.route('declaration', methods=['PATCH'])
@check_auth_redirect_login(1)
@json_resp
def api_post_declaration():
    '''
    api_post_declaration
    '''

    post_data = request.get_json()
    d = create_or_update_declaration(post_data)
    send_mail_validation_declaration(d.as_dict(True), False)
    return d.as_dict(True)

@bp.route('declaration', methods=['POST'])
@check_auth_redirect_login(1)
@json_resp
def api_patch_declaration():
    '''
    api_post_declaration
    '''
    post_data = request.get_json()
    b_create = not (post_data.get('id_declaration'))
    d = create_or_update_declaration(post_data)
    send_mail_validation_declaration(d, b_create)
    
    return d
