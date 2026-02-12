from sqlalchemy.inspection import inspect

from ..declaration.schema import *
from ..chasse.schema import *
from ..commons.schema import *
from ..i_n.schema import *


class GenericRouteDefinitions:
    """Singleton pour stocker les définitions des routes génériques de chaque module.
    Les définitions sont ajoutées par chaque module dans le fichier api.py.
    Elles comporte le modèle SQLAlchemy associé, le schéma Marshmallow et les droits d'accès.
    """

    # partage tout avec toutes les instances de classe
    # ref: https://python-3-patterns-idioms-test.readthedocs.io/en/latest/Singleton.html
    _shared_state = {}
    _definitions = {}

    def __init__(self):
        self.__dict__ = self._shared_state

    def add_generic_routes(self, module_name, definitions):
        self._definitions[module_name] = definitions

    def get_module(self, module_name):
        return self._definitions.get(module_name, {})

    def get_object_type(self, module_name, object_type):
        """retourne un dictionnaire contenant le modèle et diverses infos comme les droits d'accès"""
        return self.get_module(module_name).get(object_type, {})

    def get_model(self, module_name, object_type):
        """Retourne le modèle et le nom de sa clé primaire"""
        Model = self.get_object_type(module_name, object_type).get("model")

        id_field_name = inspect(Model).primary_key[0].name if Model else None

        return Model, id_field_name

    def get_schema_from_definition(self, module_name, object_type):
        """Retourne le schéma enregistré dans les définitions
        Voir dans le fichier api.py de chaque module"""
        schema = self.get_object_type(module_name, object_type).get("schema")
        return schema
