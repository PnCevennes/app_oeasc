"""
Schema marshmallow pour la sérialisation et désérialisation des données
"""

from flask import current_app
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from pypnnomenclature.utils import NomenclaturesConverter
from marshmallow_sqlalchemy.fields import Nested, fields
from utils_flask_sqla_geo.schema import  GeometryField
# from utils_flask_sqla_geo.schema import GeoAlchemyAutoSchema, GeoModelConverter
from marshmallow import EXCLUDE
from .models import *

config = current_app.config
DB = config["DB"]



class TObserversSchema(SQLAlchemyAutoSchema):
    id_observer = fields.Integer(allow_none=True)
    class Meta:
        model = TObservers
        load_instance = True
        sqla_session = DB.session
        include_fk = True
        unknown = EXCLUDE


class CorRealisationObserverSchema(SQLAlchemyAutoSchema):
    id_observer = fields.Integer(allow_none=True)
    id_realisation = fields.Integer(allow_none=True)
    class Meta:
        model = CorRealisationObserver
        load_instance = True
        sqla_session = DB.session
        include_fk = True
        unknown = EXCLUDE


class TCircuitsSchema(SQLAlchemyAutoSchema):
    id_circuit = fields.Integer(allow_none=True)
    class Meta:
        model = TCircuits
        load_instance = True
        sqla_session = DB.session
        include_fk = True
        unknown = EXCLUDE

    secteur = Nested("TSecteursSchema", exclude=("circuits",), dump_only=False)


class TObservationsSchema(SQLAlchemyAutoSchema):
    id_observation = fields.Integer(allow_none=True)
    class Meta:
        model = TObservations
        load_instance = True
        sqla_session = DB.session
        include_fk = True
        unknown = EXCLUDE

    espece = Nested("TEspecesSchema", dump_only=False)


class TTagsInSchema(SQLAlchemyAutoSchema):
    id_tag = fields.Integer(allow_none=True)
    class Meta:
        model = TTagsIn
        load_instance = True
        sqla_session = DB.session
        include_fk = True
        unknown = EXCLUDE


class CorRealisationTagSchema(SQLAlchemyAutoSchema):
    id_tag = fields.Integer(allow_none=True)
    id_realisation = fields.Integer(allow_none=True)
    class Meta:
        model = CorRealisationTag
        load_instance = True
        sqla_session = DB.session
        include_fk = True
        unknown = EXCLUDE

    tag = Nested("TTagsInSchema", dump_only=False)


class CorRealisationObserverSchema(SQLAlchemyAutoSchema):
    id_observer = fields.Integer(allow_none=True)
    id_realisation = fields.Integer(allow_none=True)
    class Meta:
        model = CorRealisationObserver
        load_instance = True
        sqla_session = DB.session
        include_fk = True
        unknown = EXCLUDE


class TRealisationsSchema(SQLAlchemyAutoSchema):
    id_realisation = fields.Integer(allow_none=True)
    class Meta:
        model = TRealisations
        load_instance = True
        sqla_session = DB.session
        include_fk = True
        unknown = EXCLUDE 

    circuit = Nested("TCircuitsSchema", dump_only=False)
    observations = Nested("TObservationsSchema", many=True, dump_only=False)
    observers = Nested("TObserversSchema", many=True, dump_only=False)
    tags = Nested("CorRealisationTagSchema", many=True, dump_only=False)

    # poun résoudre un bug. Si il y a column_property dans le model, il declarer le type
    observers_table = fields.String(attribute="observers_table", allow_none=True, dump_only=False)
    tags_table = fields.String(attribute="tags_table", dump_only=False)
    cerfs = fields.Integer(attribute="cerfs", dump_only=False)
    lievres = fields.Integer(attribute="lievres", dump_only=False)
    renards = fields.Integer(attribute="renards", dump_only=False)
    chevreuils = fields.Integer(attribute="chevreuils", dump_only=False)


class VResultSchema(SQLAlchemyAutoSchema):
    # id_observation = fields.Integer(allow_none=True)
    class Meta:
        model = VResult
        load_instance = False  # On ne crée pas d'instances, juste lecture
        include_fk = True
        # dump_only = True  # Vue = lecture seule