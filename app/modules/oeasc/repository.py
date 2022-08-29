from sqlalchemy import text
from app.ref_geo.models import VAreas as TAreas
from flask import current_app
from pypnusershub.db.models import User
from pypnnomenclature.models import TNomenclatures


config = current_app.config
DB = config["DB"]


def test_db():

    sql_text = text("SELECT 'a'")
    result = DB.engine.execute(sql_text).first()[0]

    return result


# def get_db(type, key, val):

#     switch_model = {

#         "user": User,
#         "t_areas": TAreas,
#         "nomenclature": TNomenclatures,
#     }

#     table = switch_model.get(type, None)

#     if table:

#         data = DB.session.query(table).filter(getattr(table, key) == val).first()

#         if data:

#             return as_dict(data, True)

#     return "None"
