"""
Schema marshmallow pour la sérialisation et désérialisation des données
"""

from flask import current_app
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema

from marshmallow_sqlalchemy.fields import Nested, fields
from utils_flask_sqla_geo.schema import GeometryField
from utils_flask_sqla_geo.schema import GeoAlchemyAutoSchema
from marshmallow import EXCLUDE
from .models import *

config = current_app.config
DB = config["DB"]


class BibAreasTypeSchema(SQLAlchemyAutoSchema):

    class Meta:
        model = BibAreasType
        sqla_session = DB.session
        load_instance = False
        unknown = EXCLUDE
        dump_only = "__all__"  # Toutes les propriétés sont en dump_only



class LAreasSchema(GeoAlchemyAutoSchema):
    """Schema pour les zones l_area avec les champs géométriques"""

    geom_4326 = GeometryField()

    class Meta:
        model = LAreas
        sqla_session = DB.session
        load_instance = False
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


class VMAreasSimplesSchema(GeoAlchemyAutoSchema):
    """Schema pour les vues VMAreasSimples avec les champs géométriques simplifiés
    A utiliser principalement pour l'affichage web et les requêtes de listes d'aires (ex: liste des aires d'un type)
    
    Note: geom_4326 n'est retourné que si explicitement demandé (via include_geom=True)"""

    geom_4326 = GeometryField()

    def __init__(self, *args, include_geom=False, **kwargs):
        """
        Par défaut, la géométrie simplifiée n'est pas sérialisée.
        Pour l'inclure explicitement:
            VMAreasSimplesSchema(include_geom=True)
        La géométrie est automatiquement incluse quand as_geojson=True.
        """
        if kwargs.get('as_geojson', False):
            include_geom = True
        if not include_geom:
            excluded_fields = set(kwargs.pop("exclude", ()) or ())
            excluded_fields.add("geom_4326")
            kwargs["exclude"] = tuple(excluded_fields)

        super().__init__(*args, **kwargs)

    class Meta:
        model = VMAreasSimples
        sqla_session = DB.session
        load_instance = False  # Empêche la modification lors du load
        unknown = EXCLUDE
        dump_only = "__all__"  # Toutes les propriétés sont en dump_only


class CorAreaIntersectSchema(SQLAlchemyAutoSchema):
    """Schema pour la table de corrélation des intersections d'aires"""

    class Meta:
        model = CorAreaIntersect
        sqla_session = DB.session
        load_instance = False
        unknown = EXCLUDE
        dump_only = "__all__"  # Toutes les propriétés sont en dump_only
        include_fk = True  # Inclut les clés étrangères dans la sérialisation



######################################################################



# class TAreasSchema(SQLAlchemyAutoSchema):
#     """Schema pour les zones l_area mais sans les champs géométriques"""

#     class Meta:
#         model = TAreas
#         sqla_session = DB.session
#         load_instance = False
#         exclude = ("geom", "centroid", "geom_4326")  # Exclut les champs géométriques
#         unknown = EXCLUDE
#         dump_only = "__all__"  # Toutes les propriétés sont en dump_only


# class VAreasSchema(SQLAlchemyAutoSchema):
#     """Schema pour les vues VAreas sans les champs géométriques"""

#     class Meta:
#         model = VAreas
#         sqla_session = DB.session
#         load_instance = False
#         unknown = EXCLUDE
#         dump_only = "__all__"  # Toutes les propriétés sont en dump_only


# class VAreasSimplesSchema(SQLAlchemyAutoSchema):
#     """Schema pour les vues VAreasSimples avec les champs géométriques"""

#     class Meta:
#         model = VAreasSimples
#         sqla_session = DB.session
#         load_instance = False
#         unknown = EXCLUDE
#         exclude = ("geom_4326",)  # Exclut les champs géométriques
#         dump_only = "__all__"  # Toutes les propriétés sont en dump_only


# class VLAreasSchema(GeoAlchemyAutoSchema):
#     geom_4326 = GeometryField()

#     class Meta:
#         model = VLAreas
#         sqla_session = DB.session
#         load_instance = False
#         unknown = EXCLUDE
#         dump_only = "__all__"  # Toutes les propriétés sont en dump_only


# class VLAreasSimplesSchema(GeoAlchemyAutoSchema):
#     geom_4326 = GeometryField()

#     class Meta:
#         model = VLAreasSimples
#         sqla_session = DB.session
#         load_instance = False  # Empêche la modification lors du load
#         unknown = EXCLUDE
#         dump_only = "__all__"  # Toutes les propriétés sont en dump_only
