'''

'''

from utils_flask_sqla.response import json_resp, json_resp_accept_empty_list
from flask import Blueprint, current_app, request, session

from .decorator import check_object_type

from .repository import (
    get_objects_type,
    get_object_type,
    create_or_update_object_type,
    delete_object_type
)

bp = Blueprint('generic_api', __name__)

@bp.route('<string:module_name>/<string:object_types>/', methods=['GET'])
@check_object_type('R')
@json_resp_accept_empty_list
def get_all_generic(module_name, object_types):
    '''
        get_all_generic
    '''


    # on enleve le s à la fin
    object_type = object_types[:-1]

    res = get_objects_type(module_name, object_type)

    return [r.as_dict(True) for r in res]


@bp.route('<string:module_name>/<string:object_type>/<int:id>', methods=['GET'])
@check_object_type('R')
@json_resp
def get_generic(module_name, object_type, id):
    '''

    '''

    res = get_object_type(module_name, object_type, id)

    if not res:
        return None

    return res.as_dict(True)


@bp.route('<string:module_name>/<string:object_type>/<int:id>', methods=['PATCH'])
@check_object_type('U')
@json_resp
def patch_generic(module_name, object_type, id):

    post_data = request.get_json()

    res = create_or_update_object_type(module_name, object_type, id, post_data)

    return res.as_dict(True)


@bp.route('<string:module_name>/<string:object_type>', methods=['POST'], defaults={'id': None})
@check_object_type('C')
@json_resp
def post_generic(module_name, object_type, id):
    '''

    '''

    post_data = request.get_json()

    res = create_or_update_object_type(module_name, object_type, id, post_data)

    return res.as_dict(True)


@bp.route('<string:module_name>/<string:object_type>/<int:id>', methods=['DELETE'])
@check_object_type('D')
@json_resp
def delete_generec(module_name, object_type, id):
    '''

    '''

    return  delete_object_type(module_name, object_type, id)
