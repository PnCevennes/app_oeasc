"""
Schema marshmallow pour la sérialisation et désérialisation des données
"""

from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested, fields
from marshmallow import EXCLUDE
from .models import *

from oeasc.utils.env import db as DB


class TSaisonAgricoleSchema(SQLAlchemyAutoSchema):
    id_saison = fields.Integer(allow_none=True)

    class Meta:
        model = TSaisonAgricole
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


class TTypeCultureSchema(SQLAlchemyAutoSchema):
    id_type_culture = fields.Integer(allow_none=True)

    class Meta:
        model = TTypeCulture
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


class TCultureSchema(SQLAlchemyAutoSchema):
    id_culture = fields.Integer(allow_none=True)

    class Meta:
        model = TCulture
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus

    type_culture = Nested("TTypeCultureSchema", many=False, allow_none=True)


class TUgAgricoleSchema(SQLAlchemyAutoSchema):
    id_ug_agricole = fields.Integer(allow_none=True)

    class Meta:
        model = TUgAgricole
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


class TCommunesAreaSchema(SQLAlchemyAutoSchema):
    """Communes de l'aire de l'observatoire (ref_geo.communes_aoa), limitées aux
    champs utiles aux listes de choix : pas de géométrie, et rien d'autre à
    réécrire quand une déclaration est enregistrée avec sa commune imbriquée."""

    class Meta:
        model = TCommunesArea
        load_instance = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus
        fields = ("id", "insee_com", "nom")


class TDeclarationAgricoleSchema(SQLAlchemyAutoSchema):
    id_declaration = fields.Integer(allow_none=True)

    class Meta:
        model = TDeclarationAgricole
        load_instance = True
        include_fk = True
        sqla_session = (DB.session,)
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus

    # les montants et surfaces sont des NUMERIC : sérialisés en nombres (et non
    # en chaînes) pour l'affichage et le tri dans les tableaux
    surface_detruite = fields.Float(allow_none=True)
    volume_detruit = fields.Float(allow_none=True)
    pourcentage = fields.Float(allow_none=True)
    montant_paye = fields.Float(allow_none=True)
    surface_ressemis = fields.Float(allow_none=True)
    montant_paye_ressemis = fields.Float(allow_none=True)
    montant_total_paye = fields.Float(allow_none=True)

    saison = Nested("TSaisonAgricoleSchema", many=False)
    culture = Nested("TCultureSchema", many=False, allow_none=True)
    ug_agricole = Nested("TUgAgricoleSchema", many=False, allow_none=True)
    espece = Nested("TEspecesSchema", many=False, allow_none=True)
    commune = Nested("TCommunesAreaSchema", many=False, allow_none=True)
