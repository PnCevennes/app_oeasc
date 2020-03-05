'''
    api commons
'''

import markdown

from flask import Blueprint, current_app, request
from utils_flask_sqla.response import json_resp
from ..user.utils import check_auth_redirect_login
from .repository import get_content

config = current_app.config
DB = config['DB']

md = markdown.Markdown()

bp = Blueprint('commons_api', __name__)


def serialize_content(content):
    '''
        serialisation content
    '''

    out = content.as_dict()
    if out['md']:
        out['html'] = md.reset().convert(out['md'])

    return out


@bp.route('content/<string:code>', methods=['GET'])
@json_resp
def api_get_content(code):
    '''
        retourne la vue schema.view
        TODO args pour filtres etc...
    '''

    content = get_content(code)

    return serialize_content(content)


@bp.route('content/', methods=['POST'], defaults={'code': None})
@bp.route('content/<string:code>', methods=['PATCH'])
@check_auth_redirect_login(5)
@json_resp
def api_create_or_update_content(code):
    '''
        create or update pour content
    '''

    data = request.get_json() or {}

    content = get_content(code)

    # cas create (post)
    if not content.id_content:
        DB.session.add(content)

    content.from_dict(data)

    DB.session.commit()

    return serialize_content(content)


@bp.route('content/<string:code>', methods=['DELETE'])
@check_auth_redirect_login(5)
@json_resp
def api_delete_content(code):
    '''
        delete content
    '''

    content = get_content(code)

    DB.session.delete(content)

    return content
