'''
    IN models
'''
from flask import current_app

from utils_flask_sqla.serializers import serializable

config = current_app.config
DB = config['DB']


@serializable
class TObservations(DB.Model):
    __tablename__ = 't_observations'
    __table_args__ = {'schema': 'oeasc_in', 'extend_existing': True}

    id_observation = DB.Column(DB.Integer, primary_key=True)
    valid = DB.Column(DB.Boolean)
