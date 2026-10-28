from flask_sqlalchemy import SQLAlchemy
from os import environ
from importlib import import_module

db_path = environ.get("FLASK_SQLALCHEMY_DB")


if db_path and db_path != f"{__name__}.db":
    db_module_name, db_object_name = db_path.rsplit(".", 1)
    db_module = import_module(db_module_name)
    db = getattr(db_module, db_object_name)

else:
    db = SQLAlchemy(engine_options={"future": True})  # future pour sqlalchemy 2.0
    environ["FLASK_SQLALCHEMY_DB"] = f"{__name__}.db"
    # pour la migration sqlalchemy 2.0 il faut déclarer la Base
    Base = db.Model
