''' api pour les indices nocturnes '''
import time
from flask import Blueprint, current_app, request
from utils_flask_sqla.response import json_resp

from .repository import in_data
from .models import TObservations

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

@bp.route('test_results/<int:id_observation>', methods=['GET'])
@json_resp
def in_test_results(id_observation):
    '''
        renvoie les résultats 'brut' des in pour debug
    '''

    res =  GenericQuery(
        DB,
        'v1',
        'oeasc_in',
        limit=1e6
    ).as_dict()['items']

    test = {}
    for r in res:
        if not r['id_observation'] in test:
            test[r['id_observation']] = r
        else:
            return 'error'

    return test[id_observation]

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

    # obs.from_dict(data)

    # time.sleep(0.01)


    # time.sleep(0.01)
    # DB.engine.execution_options(autocommit=True).execute(
    #     "UPDATE oeasc_in.t_observations SET valid = {} WHERE id_observation = {}"
    #     .format(data['valid'], data['id_observation'])
    # )

    # DB.session.commit()

    # return  in data
    return [obs.valid]
    # return in_data()
