''' api pour les indices nocturnes '''
import time
from flask import Blueprint, current_app, request
from utils_flask_sqla.response import json_resp, json_resp_accept_empty_list

from .repository import in_data
from .models import TObservations, TRealisations

from utils_flask_sqla.generic import GenericQuery


bp = Blueprint('in_api', __name__)

config = current_app.config
DB = config['DB']


@bp.route('results/', methods=['GET'])
@json_resp
def in_results():
    '''
        renvoie les résultats des in pour faire les graphs (IN, variance, ug, année)
    '''

    return in_data()

@bp.route('valid_obs/', methods=['PATCH'])
@json_resp
def in_valid_obs():
    '''
        valide ou invalide une observation
    '''

    data = request.get_json()



    # update observation
    (
        DB.session.query(TObservations)
        .filter(TObservations.id_observation == data['id_observation'])
        # .one()
        .update({'valid': data['valid']})
    )
    DB.session.commit()

    obs = (
        DB.session.query(TObservations)
        .filter(TObservations.id_observation == data['id_observation'])
        .one()
    )

    return obs.as_dict()


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
@bp.route('realisation/', methods=['POST'], defaults={'id_realisation': None})
@json_resp
def create_edit_realisation(id_realisation):
    '''
    '''

    post_data = request.get_json()

    realisation = (
        TRealisations() if not id_realisation
        else (
            DB.session.query(TRealisations).
            filter(TRealisations.id_realisation == id_realisation)
            .one()
        )
    )


    # realisation(**post_data)
    # realisation.from_dict(post_data)
    print(post_data)
    realisation.from_dict(post_data, True)
    # setattr(realisation, 'observations', post_data['observations'])


    DB.session.commit()

    print(realisation.as_dict(True))

    return realisation.as_dict(True)


@bp.route('realisation/<int:id_realisation>', methods=['DELETE'])
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
