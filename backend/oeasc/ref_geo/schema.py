"""
Schema marshmallow pour la sérialisation et désérialisation des données
"""

from flask import current_app
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from marshmallow_sqlalchemy.fields import Nested, fields
from utils_flask_sqla.schema import SmartRelationshipsMixin
from utils_flask_sqla_geo.schema import  GeometryField
from utils_flask_sqla_geo.schema import GeoAlchemyAutoSchema
from marshmallow import EXCLUDE
from .models import *

config = current_app.config
DB = config["DB"]


# SmartRelationshipsMixin retire les relationships de la serialisation. Il faudra donc les spécifier lors des load ou dump
# via only=[]. Exemple:
# FooSchema().dump() -> {"id": 1, "name": "toto" }
# FooSchema(only=["+default_excluded_field"]).dump() -> {"id": 1, "name": "toto", default_excluded_field: "test" }
# FooSchema(only=["relationship"]).dump() -> {"id": 1, "name": "toto",  relationship : {OtherSchema...} }
# FooSchema(only=["id", "relationship"]).dump() -> {"id": 1, relationship : {OtherSchema...} }


class BibAreasTypeSchema(SQLAlchemyAutoSchema):

    class Meta:
        model = BibAreasType
        sqla_session = DB.session
        load_instance = False
        unknown = EXCLUDE
        dump_only = "__all__"  # Toutes les propriétés sont en dump_only
                
class TAreasSchema(SQLAlchemyAutoSchema):
    """Schema pour les zones l_area mais sans les champs géométriques"""
    class Meta: 
        model = TAreas
        sqla_session = DB.session
        load_instance = False
        exclude = ("geom", "centroid", "geom_4326")  # Exclut les champs géométriques
        unknown = EXCLUDE
        dump_only = "__all__"  # Toutes les propriétés sont en dump_only

class LAreasSchema( GeoAlchemyAutoSchema):
    """Schema pour les zones l_area avec les champs géométriques"""
    geom_4326 = GeometryField()

    class Meta:
        model = LAreas
        sqla_session = DB.session
        load_instance = False
        unknown = EXCLUDE
        dump_only = "__all__"  # Toutes les propriétés sont en dump_only

class VAreasSchema(SQLAlchemyAutoSchema):
    """Schema pour les vues VAreas sans les champs géométriques"""
    
    class Meta:
        model = VAreas
        sqla_session = DB.session
        load_instance = False
        unknown = EXCLUDE
        dump_only = "__all__"  # Toutes les propriétés sont en dump_only

class VAreasSimplesSchema(SQLAlchemyAutoSchema):
    """Schema pour les vues VAreasSimples avec les champs géométriques"""
    class Meta:
        model = VAreasSimples
        sqla_session = DB.session
        load_instance = False
        unknown = EXCLUDE
        exclude = ("geom_4326",)  # Exclut les champs géométriques
        dump_only = "__all__"  # Toutes les propriétés sont en dump_only

class VLAreasSchema( GeoAlchemyAutoSchema):
    geom_4326 = GeometryField()

    class Meta:
        model = VLAreas
        sqla_session = DB.session
        load_instance = False
        unknown = EXCLUDE
        dump_only = "__all__"  # Toutes les propriétés sont en dump_only

class VLAreasSimplesSchema( GeoAlchemyAutoSchema):
    geom_4326 = GeometryField()

    class Meta:
        model = VLAreasSimples
        sqla_session = DB.session
        load_instance = False  # Empêche la modification lors du load
        unknown = EXCLUDE
        dump_only = "__all__"  # Toutes les propriétés sont en dump_only


class CorHierarchieAreaSchema(SQLAlchemyAutoSchema):
    """Schema pour la table de hiérarchie des aires"""
    
    class Meta:
        model = CorHierarchieArea 
        sqla_session = DB.session
        load_instance = False
        unknown = EXCLUDE
        dump_only = "__all__"  # Toutes les propriétés sont en dump_only
        include_fk = True  # Inclut les clés étrangères dans la sérialisation