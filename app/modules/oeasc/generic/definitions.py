from sqlalchemy.inspection import inspect


class GenericRouteDefinitions:
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
        return self.get_module(module_name).get(object_type, {})

    def get_model(self, module_name, object_type):
        Model = self.get_object_type(module_name, object_type).get("model")

        id_field_name = inspect(Model).primary_key[0].name if Model else None

        return Model, id_field_name
