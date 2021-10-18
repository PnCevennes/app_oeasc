'''
    decorator
'''

from functools import wraps
from flask import session
from .definitions import GenericRouteDefinitions

definitions = GenericRouteDefinitions()


def check_object_type(droit_type):
    '''
        decorateur qui verifie les droits et les définitions
    '''
    def check_object_type_(fn):
        @wraps(fn)
        def check_object_type__(*args, **kwargs):

            module_name = kwargs.get('module_name')
            object_type = kwargs.get('object_type') or kwargs.get('object_types')[:-1]
            current_user = session.get('current_user', {})

            module = definitions.get_module(module_name)
            if not module:
                return (
                    "pas de module défini pour {}".format(module_name),
                    403
                )

            object_definition = definitions.get_object_type(module_name, object_type)

            if not object_definition:
                return (
                    "pas d'object défini pour {} {}".format(module_name, object_type),
                    403
                )

            # s'il n'y a pas de droit définis pour de type de droit : route fermée
            id_droit_max_object_type = object_definition.get('droits', {}).get(droit_type, None)
            if id_droit_max_object_type is None:
                return (
                    "pas de droits définis en {} pour la route {} {} : route fermée"
                    .format(droit_type, module_name, object_type),
                    403
                )

            # s'il n'y a pas de current user => droit à 0
            id_droit_max_user = current_user['id_droit_max'] if current_user else 0

            print(current_user, id_droit_max_user, id_droit_max_object_type)
            if id_droit_max_user < id_droit_max_object_type:
                return (
                    "pas de droit suffisant pour {} en {} : ({} < {})".format(
                        object_type,
                        droit_type,
                        id_droit_max_user,
                        id_droit_max_object_type
                    ),
                    403
                )
            return fn(*args, **kwargs)
        return check_object_type__
    return check_object_type_
