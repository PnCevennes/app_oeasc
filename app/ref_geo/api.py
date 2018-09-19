from flask import (
    Blueprint,
    request
)

from .models import (
    TAreas as TA,
    LAreas as LA,
)

import time

from sqlalchemy.sql import func

from sqlalchemy import and_, text

# from geoalchemy2 import functions

from app.utils.env import DB

from app.utils.utilssqlalchemy import json_resp, as_dict

from geojson import FeatureCollection


from .repository import get_id_type


def f_area_code(area_code, n):
    return '-'.join(str(area_code).split('-')[:n])


bp = Blueprint('ref_geo', __name__)


@bp.route('get_id_type/<string:type_code>')
@json_resp
def get_id_type_api(type_code):

    return get_id_type(type_code)


@bp.route('area/<string:data_type>/<int:id_area>')
@json_resp
def get_area(data_type, id_area):

    if data_type == 'l':
        table = LA
    else:
        table = TA

    data = DB.session.query(table).filter(id_area == table.id_area).all()

    if data_type == 'l':
        return FeatureCollection([d.get_geofeature() for d in data])
    else:
        return [d.as_dict() for d in data]


@bp.route('areas_post/<string:data_type>', methods=['POST'])
@json_resp
def get_areas_post(data_type):

    data_in = request.get_json()

    areas = data_in['areas']

    if data_type == 'l':
        table = LA
    else:
        table = TA

    out = []

    for area in areas:
        data = DB.session.query(table).filter(area['id_area'] == table.id_area).all()

        if data_type == 'l':
            out += [d.get_geofeature() for d in data]
        else:
            out += [d.as_dict() for d in data]

    if data_type == 'l':

        out = FeatureCollection(out)

    return out


@bp.route('areas_centroid_post/<string:data_type>', methods=['POST'])
@json_resp
def get_areas_centroid_post(data_type):

    data_in = request.get_json()

    areas = data_in['areas']

    v = [area['id_area'] for area in areas]

    t = tuple(v)

    if len(v) == 1:

        t = str(t).replace(",", "")

    sql_text = text("SELECT ST_X(c),ST_Y(c) \
        FROM (SELECT ST_CENTROID(ST_UNION(geom_4326)) as c \
        FROM ref_geo.l_areas \
        WHERE id_area in {} )a".format(t))

    result = DB.engine.execute(sql_text).first()

    v = [result[0], result[1]]
    v = [result[1], result[0]]

    return v


@bp.route('areas_from_type_code/<string:data_type>/<string:type_code>')
@json_resp
def get_areas_from_type_code(data_type, type_code):
    '''
        retourne toutes les aires pour un type_code donne (par exemple OEASC _CADASTRE)
    '''

    if data_type == 'l':
        table = LA
    else:
        table = TA

    id_type = get_id_type(type_code)

    data = DB.session.query(table).filter(and_(table.id_type == id_type, table.enable)).all()

    if data_type == 'l':
        return FeatureCollection([d.get_geofeature() for d in data])
    else:
        return [d.as_dict() for d in data]


@bp.route('areas_from_type_code_container/<string:data_type>/<string:type_code>/<int:id_area_container>')
@json_resp
def get_areas_from_type_code_container(data_type, type_code, id_area_container):
    '''
        retourne toutes les aires pour un type_code donne (par exemple OEASC _CADASTRE)
        et étant contenue dans la geometrie d'id_rea id_area_container
    '''

    if data_type == 'l':
        table = LA
    else:
        table = TA

    id_type = get_id_type(type_code)

    container = DB.session.query(table).filter(table.id_area == id_area_container).first()

    id_type_commune = get_id_type('OEASC_COMMUNE')
    id_type_dgd = get_id_type('OEASC_DGD')

    out = []

    # cas des section de communes
    if(container.id_type == id_type_commune):

        sql_text = text("SELECT ref_geo.get_old_communes('{}')".format(container.area_code))

        result = DB.engine.execute(sql_text)

        for r in result:

            area_code = r[0]

            data = DB.session.query(table).filter(and_(table.id_type == id_type, table.enable, table.area_code.like(area_code + "-%"))).all()

            if data_type == 'l':

                out += [d.get_geofeature() for d in data]

            else:

                out += [d.as_dict() for d in data]


    # cas des dgd
    elif(container.id_type == id_type_dgd):

        t1 = time.time()
        print("avant exec")

        aire_container = DB.session.query(func.ST_AREA(container.geom_4326)).first()[0]

        data = DB.session.query(table).filter(and_(table.id_type == id_type, table.enable))
        # data = data.filter(func.ST_INTERSECTS(table.geom_4326, container.geom_4326)).subquery()
        data = data.filter(func.ST_INTERSECTS(table.geom_4326, container.geom_4326))

        print("avant req")
        data = data.all()
        print("apres_req")


        data2 = []

        for d in data:

            aire_intersection = DB.session.query(func.ST_AREA(func.ST_INTERSECTION(d.geom_4326, container.geom_4326))).first()[0]

            aire_geom = DB.session.query(func.ST_AREA(d.geom_4326)).first()[0]

            print(aire_container, aire_intersection, aire_geom)

            rel = aire_intersection * (1. / aire_container + 1. / aire_geom)

            if rel > 0.05:
                data2.append(d)

        data = data2

        if data_type == 'l':

            out += [d.get_geofeature() for d in data]

        else:

            out += [d.as_dict() for d in data]

        print(t1 - time.time())

    # autres cas ONF
    else:

        data = DB.session.query(table).filter(and_(table.id_type == id_type, table.enable, table.area_code.like(container.area_code + "-%"))).all()

        if data_type == 'l':

            out = [d.get_geofeature() for d in data]

        else:

            out = [d.as_dict() for d in data]

    if data_type == 'l':

        out = FeatureCollection(out)

    return out

# @bp.route('areas/<string:data_type>/<string:type_code>//', defaults={'area_code': "-", 'type_code_container': "-", 'area_code_container': "-"})
# @bp.route('areas/<string:data_type>/<string:type_code>/<string:area_code>/', defaults={'type_code_container': "-", 'area_code_container': "-"})
# @bp.route('areas/<string:data_type>/<string:type_code>/<string:area_code>/<string:type_code_container>', defaults={'area_code_container': "-"})
# @bp.route('areas/<string:data_type>/<string:type_code>/<string:area_code>/<string:type_code_container>/<string:area_code_container>', methods=['GET'])
# @json_resp
# def get_areas(data_type, type_code, area_code, type_code_container, area_code_container):

#     if data_type == 'l' or type_code_container != "-":
#         table = LA
#     else:
#         table = TA

#     table_parent = LA

#     id_type = get_id_type(type_code)

#     if area_code != "-":
#         data = DB.session.query(table).filter(and_(table.id_type == id_type, table.enable, table.area_code == area_code))
#     else:
#         data = DB.session.query(table).filter(and_(table.id_type == id_type, table.enable))

#     if type_code_container != "-":

#         id_type_container = DB.session.execute("select ref_geo.get_id_type(:type_code);", {'type_code': type_code_container}).first()[0]

#         if area_code_container != "-":
#             container = DB.session.query(table_parent.geom_4326.label('geom_4326')).filter(and_(table_parent.id_type == id_type_container, table_parent.area_code == area_code_container)).subquery()
#         else:
#             container = DB.session.query(table_parent.geom_4326.label('geom_4326')).filter(table.id_type == id_type_container).subquery()

#         data = data.filter(func.ST_INTERSECTS(table.geom_4326, container.c.geom_4326))

#         data = data.filter(func.ST_AREA(func.ST_INTERSECTION(table.geom_4326, container.c.geom_4326)) >= 0.01 * func.ST_AREA(table.geom_4326))

#         data = data.order_by(table.area_name)

#     if data_type == 'l':
#         return FeatureCollection([d.get_geofeature() for d in data])
#     else:
#         return [d.as_dict() for d in data]
