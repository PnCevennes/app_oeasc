''' api pour les indices nocturnes '''
import time
from flask import Blueprint, current_app, request
from utils_flask_sqla.response import json_resp

from .repository import in_data
from .models import TObservations

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
        renvoie les résultats des in pour faire les graphs (IN, variance, ug, année)
    '''

    data = request.get_json()



    # update observation
    obs = (
        DB.session.query(TObservations)
        .filter(TObservations.id_observation == data['id_observation'])
        .one()
    )

    setattr(obs, 'valid', data['valid'])
    DB.session.commit()
    time.sleep(0.1)

    # DB.engine.execution_options(autocommit=True).execute(
    #     "UPDATE oeasc_in.t_observations SET valid = {} WHERE id_observation = {}"
    #     .format(data['valid'], data['id_observation'])
    # )

    # DB.session.commit()

    # return  in data
    return in_data()
