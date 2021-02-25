'''
  config
'''

from flask import current_app
from.definitions import GenericRouteDefinitions

config = current_app.config
DB = config['DB']


definitions = GenericRouteDefinitions()


def get_objects_type(module_name, object_type, args={}):
    '''
        get all
    '''
    Model, _ = definitions.get_model(module_name, object_type)
    obj = definitions.get_object_type(module_name, object_type)
    print(obj)

    query = DB.session.query(Model)

    # prefiltres 
    pre_filters = obj.get('pre_filters', {})
    for key in pre_filters:
        if not hasattr(Model, key):
            pass
        query = query.filter(getattr(Model, key).in_(pre_filters[key]))

    # filtres TODO
    for key in args:
        print(key)

    return query.all()


def get_object_type(module_name, object_type, value, field_name=None):
    '''
        get one
        value = model.<field_name>
        default field_name = id_field_name
    '''
    (Model, id_field_name) = definitions.get_model(module_name, object_type)

    if not field_name:
        field_name = id_field_name

    return (
        DB.session.query(Model).
        filter(getattr(Model, field_name) == value)
        .one()
    )


def create_or_update_object_type(module_name, object_type, id_value, post_data):
    '''
        toujours par id_value
    '''
    (Model, _) = definitions.get_model(module_name, object_type)

    res = None

    if not id_value:
        res = Model()
        DB.session.add(res)
    else:
        res = get_object_type(module_name, object_type, id_value)

    res.from_dict(post_data, True)

    DB.session.commit()

    return res

def delete_object_type(module_name, object_type, id_value):
    '''
        toujours par id_value
    '''

    (Model, id_field_name) = definitions.get_model(module_name, object_type)

    res = get_object_type(module_name, object_type, id_value)

    if not res:
        return None

    out = res.as_dict(True)

    (
        DB.session.query(Model)
        .filter(getattr(Model, id_field_name) == id_value)
        .delete()
    )

    DB.session.commit()

    return out
