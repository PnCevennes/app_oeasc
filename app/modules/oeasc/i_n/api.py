''' api pour les indices nocturnes '''

from flask import Blueprint, current_app
from utils_flask_sqla.response import json_resp
from utils_flask_sqla.generic import GenericQuery

from .repository import process_res

bp = Blueprint('in_api', __name__)

config = current_app.config
DB = config['DB']


@bp.route('results_2/', methods=['GET'])
@json_resp
def in_results_2():
    '''
        renvoie les résultats des in pour faire les graphs (IN, variance, ug, année)
    '''

    res = GenericQuery(
        DB,
        'v7',
        'oeasc_in',
        limit=1e6
    ).as_dict()['items']
    return res


@bp.route('results/', methods=['GET'])
@json_resp
def in_results():
    '''
        renvoie les résultats des in pour faire les graphs (IN, variance, ug, année)
    '''

    res = GenericQuery(
        DB,
        'v1',
        'oeasc_in',
        limit=1e6
    ).as_dict()['items']

    out = process_res(res)

    return out
