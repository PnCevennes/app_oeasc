'''
    api commons
'''

import markdown

from flask import Blueprint, current_app, request
from utils_flask_sqla.response import json_resp_accept_empty_list, json_resp
from ..user.utils import check_auth_redirect_login
from .repository import get_content

from sqlalchemy import text

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


@bp.route('communes/<string:test>', methods=['GET'])
@bp.route('communes/', defaults={'test': None}, methods=['GET'])
@json_resp_accept_empty_list
def api_communes(test):
    '''
        delete content
    '''

    if not test:
        return []

    s_trans_I = "àâäéèêëîïöùûü"
    s_trans_O = "aaaeeeeiiouuu"

    for index in range(len(s_trans_I)):
        test = test.replace(s_trans_I[index], s_trans_O[index])

    tests = test.strip().split(' ')

    cond_text = " AND ".join(
        [
            (
                " ( TRANSLATE(nom, '{1}', '{2}') ILIKE '{3}{0}%' OR cp ILIKE '{3}{0}%' ) "
            ).format(s_test, s_trans_I, s_trans_O, '' if s_test == tests[0] else '%')
            for s_test in tests
        ]
    )

    sql_text = """
    SELECT 
        CONCAT(nom, ' ', cp) as nom_cp
        FROM oeasc_commons.t_communes WHERE {0} ORDER BY population DESC, nom, cp LIMIT 20
    """.format(cond_text, s_trans_I, s_trans_O)

    print(sql_text)

    result = DB.engine.execute(text(sql_text))
    out = [ {'nom_cp': res[0]} for res in result]
    return out

