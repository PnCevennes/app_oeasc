"""
Schema marshmallow pour la sérialisation et désérialisation des données
"""

from flask import current_app
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import Nested, fields
from marshmallow import EXCLUDE
from .models import *
# from pypnnomenclature.schemas import NomenclatureSchema, BibNomenclaturesTypesSchema

config = current_app.config
DB = config["DB"]


"""
pour mapper la vue user de oeasc_commons
"""

from flask import current_app

# from sqlalchemy.orm import column_property , relationship, Mapped
# from sqlalchemy import select, String
# from utils_flask_sqla.serializers import serializable


config = current_app.config
DB = config["DB"]





class TTagsSchema(SQLAlchemyAutoSchema):
    id_tag = fields.Integer(allow_none=True)
    class Meta:
        model = TTags 
        load_instance = True
        include_fk = True
        sqla_session = DB.session,
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus

class TListeOrganismesSchema(SQLAlchemyAutoSchema):
    id_organisme = fields.Integer(allow_none=True)
    class Meta:
        model = TListeOrganismes
        load_instance = True
        include_fk = True
        sqla_session = DB.session,
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus

class TContentsSchema(SQLAlchemyAutoSchema):
    id_content = fields.Integer(allow_none=True)
    tags = Nested(
        TTagsSchema,
        many=True,
        metadata={"load_instance": True},
    )

    class Meta:
        model = TContents
        load_instance = True
        include_fk = True
        sqla_session = DB.session,
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus

class TSecteursSchema(SQLAlchemyAutoSchema):
    id_secteur = fields.Integer(allow_none=True)
    circuits = Nested(
        "TCircuitsSchema",
        many=True,
        metadata={"load_instance": True},
    )

    class Meta:
        model = TSecteurs
        load_instance = True
        include_fk = True
        sqla_session = DB.session,
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus

class TEspecesSchema(SQLAlchemyAutoSchema):
    id_espece = fields.Integer(allow_none=True)
    class Meta:
        model = TEspeces
        load_instance = True
        include_fk = True
        sqla_session = DB.session,
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus

class TCommunesSchema(SQLAlchemyAutoSchema):
    code = fields.Integer(dump_only=True, allow_none=True)
    class Meta:
        model = TCommunes
        load_instance = True
        include_fk = True
        sqla_session = DB.session,
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


class TNomenclaturesOeascSchema(SQLAlchemyAutoSchema):
    id_type = fields.Integer(allow_none=True)
    class Meta:
        model = TNomenclaturesOeasc
        load_instance = True
        include_fk = True
        sqla_session = DB.session,
        unknown = EXCLUDE  # retire du schema les champs inconnus ou superflus


