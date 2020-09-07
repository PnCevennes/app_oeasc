''' api pour les indices nocturnes '''
import time
from flask import Blueprint, current_app, request
from utils_flask_sqla.response import json_resp, json_resp_accept_empty_list

from .repository import in_data
from .models import TObservations, TRealisations, TCircuits

from utils_flask_sqla.generic import GenericQuery
from app.modules.oeasc.user.utils import check_auth_redirect_login
from ..generic.definitions import GenericRouteDefinitions

grd = GenericRouteDefinitions()


bp = Blueprint('in_api', __name__)

config = current_app.config
DB = config['DB']

definitions = {
    'realisation': {
        'model': TRealisations,
        'droits': {
            'C': 5, 'R': 0, 'U': 5, 'D': 5
        }
    },
    'circuit': {
        'model': TCircuits,
        'droits': {
            'C': 5, 'R': 0, 'U': 5, 'D': 5
        }

    }
}

grd.add_generic_routes('in', definitions)

@bp.route('results/', methods=['GET'])
@json_resp
def in_results():
    '''
        renvoie les résultats des in pour faire les graphs (IN, variance, ug, année)
    '''

    return in_data()

@bp.route('test/results/', methods=['GET'])
@json_resp
def in_test_results():
    '''
        renvoie les résultats des in pour faire les graphs (IN, variance, ug, année)
    '''

    return in_data()['especes']['Cerf']['ugs']['Méjean']

@bp.route('valid_realisation/', methods=['PATCH'])
@check_auth_redirect_login(5)
@json_resp
def in_valid_realisation():
    '''
        valide ou invalide une realisation
    '''

    data = request.get_json()

    # update observation
    (
        DB.session.query(TRealisations)
        .filter(TRealisations.id_realisation == data['id_realisation'])
        # .one()
        .update({'valid': data['valid']})
    )
    DB.session.commit()

    realisation = (
        DB.session.query(TRealisations)
        .filter(TRealisations.id_realisation == data['id_realisation'])
        .one()
    )

    return realisation.as_dict()


@bp.route('circuits/', methods=['GET'])
@json_resp
def in_get_circuits():
    '''
    '''

    return GenericQuery(
        DB,
        'v_circuits',
        'oeasc_in',
        limit=1e6
    ).as_dict()['items']


@bp.route('observers/', methods=['GET'])
@json_resp_accept_empty_list
def in_get_observers():
    '''
    '''

    return GenericQuery(
        DB,
        'v_observers',
        'oeasc_in',
        limit=1e6
    ).as_dict()['items']


@bp.route('realisations/', methods=['GET'])
@json_resp
def get_realisations():
    '''
    '''

    realisations = (
        DB.session.query(TRealisations)
        .all()
    )

    return [r.as_dict(True) for r in realisations]


@bp.route('realisation/<int:id_realisation>', methods=['GET'])
@json_resp
def get_realisation(id_realisation):
    '''

    '''

    realisation = (
        DB.session.query(TRealisations).
        filter(TRealisations.id_realisation == id_realisation)
        .one()
    )

    return realisation.as_dict(True)


@bp.route('realisation/<int:id_realisation>', methods=['PATCH'])
@bp.route('realisation', methods=['POST'], defaults={'id_realisation': None})
@check_auth_redirect_login(5)
@json_resp
def create_edit_realisation(id_realisation):
    '''

    '''

    post_data = request.get_json()

    realisation = None

    if not id_realisation:
        realisation = TRealisations()
        DB.session.add(realisation)
    else:
        realisation = ( 
            DB.session.query(TRealisations)
            .filter(TRealisations.id_realisation == id_realisation)
            .one()
            )

    print(post_data)
    realisation.from_dict(post_data, True)

    DB.session.commit()

    print(realisation.as_dict(True))

    return realisation.as_dict(True)


@bp.route('realisation/<int:id_realisation>', methods=['DELETE'])
@check_auth_redirect_login(5)
@json_resp
def delete_edit_realisation(id_realisation):
    '''
    
    '''

    (
        DB.session.query(TRealisations)
        .filter(TRealisations.id_realisation == id_realisation)
        .delete()
    )

    return id_realisation
