'''
  config
'''

from flask import current_app
from.definitions import GenericRouteDefinitions
from sqlalchemy import func, cast

config = current_app.config
DB = config['DB']


definitions = GenericRouteDefinitions()



# def count_objects_type(module_name, object_type, args={}):
#     '''
#         get count
#     '''
#     Model, _ = definitions.get_model(module_name, object_type)
#     obj = definitions.get_object_type(module_name, object_type)
#     query = DB.session.query(Model)

#     # prefiltres 
#     pre_filters = obj.get('pre_filters', {})
#     for key in pre_filters:
#         if not hasattr(Model, key):
#             pass
#         query = query.filter(getattr(Model, key).in_(pre_filters[key]))

#     return query.count()


def getlist(args, key): 
    '''
        patch getlist pour tenir compte des cas ?val='val1,val2'
    '''

    val = args.get(key)

    if not val:
        return []

    if ',' in val:
        return val.split(',')       

    return args.getlist(key)


def get_objects_type(module_name, object_type, args={}):
    '''
        get all
    '''
    Model, _ = definitions.get_model(module_name, object_type)
    obj = definitions.get_object_type(module_name, object_type)

    query = DB.session.query(Model)
    query.enable_assertions = True # prttt ???


    # prefiltres 
    pre_filters = obj.get('pre_filters', {})
    for key in pre_filters:
        if not hasattr(Model, key):
            continue
        query = query.filter(getattr(Model, key).in_(pre_filters[key]))

    # filtres
    for key in args:
        if not hasattr(Model, key):
            continue
        query = query.filter(cast(getattr(Model, key), DB.String ).ilike('%' + args[key] + '%'))

    # print sort by
    sort_by = getlist(args, 'sortBy')
    sort_desc = getlist(args, 'sortDesc')

    # sort
    order_bys = []
    for index, key in enumerate(sort_by):
        if not hasattr(Model,key):
            continue
        print(key)
        desc = sort_desc[index]
        od = getattr(Model, key)
        if(desc == 'true'):
            od = od.desc()
        else: 
            od.asc()

        order_bys.append(od)


    if order_bys:
        query = query.order_by(*(tuple(order_bys)))

    count = query.count()

    page = args.get('page')
    itemsPerPage = args.get('itemsPerPage')
    if itemsPerPage and int(itemsPerPage) > 0:
        query = query.limit(itemsPerPage)

        if page:
            query = query.offset((int(page)-1))

    return query, count


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
