'''
    IN models
'''
from flask import current_app

from utils_flask_sqla.serializers import serializable

config = current_app.config
DB = config['DB']


@serializable
class TCircuits(DB.Model):
    __tablename__ = 't_circuits'
    __table_args__ = {'schema': 'oeasc_in', 'extend_existing': True}

    id_circuit = DB.Column(DB.Integer, primary_key=True)
    nom_circuit = DB.Column(DB.String(250))
    numero_circuit = DB.Column(DB.Integer)
    ug = DB.Column(DB.String(250))
    km = DB.Column(DB.Integer)

@serializable
class TObservations(DB.Model):
    __tablename__ = 't_observations'
    __table_args__ = {'schema': 'oeasc_in', 'extend_existing': True}

    id_observation = DB.Column(DB.Integer, primary_key=True)
    id_realisation = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_in.t_realisations.id_realisation')
    )
    espece = DB.Column(DB.String(250))
    nb = DB.Column(DB.Integer)
    valid = DB.Column(DB.Boolean)


@serializable
class TRealisations(DB.Model):
    __tablename__ = 't_realisations'
    __table_args__ = {'schema': 'oeasc_in', 'extend_existing': True}

    id_realisation = DB.Column(DB.Integer, primary_key=True)
    id_circuit = DB.Column(
        DB.Integer,
        DB.ForeignKey('oeasc_in.t_circuits.id_circuit')
    )
    serie = DB.Column(DB.Integer)

    vent = DB.Column(DB.String(250))
    temps = DB.Column(DB.String(250))
    temperature = DB.Column(DB.String(250))
    date_realisation = DB.Column(DB.Date)
    observers = DB.Column(DB.String(250))

    observations = DB.relationship(
        TObservations,
        cascade="save-update, merge, delete, delete-orphan"
    )
