"""
Schema marshmallow pour la sérialisation et désérialisation des données
"""

from flask import current_app
from marshmallow_sqlalchemy import SQLAlchemyAutoSchema
from marshmallow_sqlalchemy.fields import fields

from marshmallow import EXCLUDE
from .models import *

config = current_app.config
DB = config["DB"]


class VUsersShema(SQLAlchemyAutoSchema):
    id_role = fields.Integer(allow_none=True)

    class Meta:
        model = VUsers
        load_instance = False
        sqla_session = DB.session
        include_fk = True
        unknown = EXCLUDE
