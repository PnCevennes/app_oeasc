'''
  config
'''

from flask import current_app
from.definitions import GenericRouteDefinitions

config = current_app.config
DB = config['DB']


definitions = GenericRouteDefinitions()


def get_objects_type(module_name, object_type):
    
    Model, _ = definitions.get_model(module_name, object_type)

    return (
        DB.session.query(Model)
        .all()
    )


def get_object_type(module_name, object_type, id):

    (Model, id_field_name) = definitions.get_model(module_name, object_type)

    return (
        DB.session.query(Model).
        filter(getattr(Model, id_field_name) == id)
        .one()
    )


def create_or_update_object_type(module_name, object_type, id, post_data):
    
    (Model, _) = definitions.get_model(module_name, object_type)

    res = None

    if not id:
        res = Model()
        DB.session.add(res)
    else:
        res = get_object_type(module_name, object_type, id)

    res.from_dict(post_data, True)

    DB.session.commit()

    return res

def delete_object_type(module_name, object_type, id):

    (Model, id_field_name) = definitions.get_model(module_name, object_type)

    res = get_object_type(module_name, object_type, id)

    if not res:
        return None

    out = res.as_dict(True)
    
    (
        DB.session.query(Model)
        .filter(getattr(Model, id_field_name) == id)
        .delete()
    )

    DB.session.commit()

    return out

