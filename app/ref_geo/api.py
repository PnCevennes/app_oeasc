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

    data = DB.session.query(table).filter(and_(table.id_type == id_type, table.enable)).order_by(table.area_name).all()

    if data_type == 'l':
        return FeatureCollection([d.get_geofeature() for d in data])
    else:
        return [d.as_dict() for d in data]


@bp.route('areas_from_type_code_container/<string:data_type>/<string:type_code>/<string:ids_area_container>')
@json_resp
def get_areas_from_type_code_container(data_type, type_code, ids_area_container):
    '''
        retourne toutes les aires pour un type_code donne (par exemple OEASC _CADASTRE)
        et étant contenue dans la geometrie identifiée par son id_area : id_area_container
        la recherche de ses élément se fait par rapport aux area_code:
            - soit en comparant les area_code des contenus et du contenant (cas général)
            - soit en se servant d'une table de correlation precalculée pour le cas des forêts avec DGD
    '''

    if data_type == 'l':
        table = LA
    else:
        table = TA

    id_type = get_id_type(type_code)
    v = ids_area_container.split("-")

    out = []

    for id_area_container in v:

        container = DB.session.query(table).filter(table.id_area == id_area_container).first()

        id_type_commune = get_id_type('OEASC_COMMUNE')
        id_type_dgd = get_id_type('OEASC_DGD')

        # cas des section de communes
        if(container.id_type == id_type_commune):

            sql_text = text("SELECT ref_geo.get_old_communes('{}')".format(container.area_code))

            result = DB.engine.execute(sql_text)

            data = []

            for r in result:

                area_code = r[0]

                data = DB.session.query(table).filter(and_(table.id_type == id_type, table.enable, table.area_code.like(area_code + "-%"))).order_by(table.area_name).all() + data

        # cas des dgd
        elif(container.id_type == id_type_dgd):

            res = DB.engine.execute(text("SELECT area_code_cadastre FROM ref_geo.cor_dgd_cadastre WHERE area_code_dgd = '{}' ;".format(container.area_code)))

            v = [r[0] for r in res]

            data = DB.session.query(table).filter(table.area_code.in_(v)).all()

        # autres cas ONF
        else:

            data = DB.session.query(table).filter(and_(table.id_type == id_type, table.enable, table.area_code.like(container.area_code + "-%"))).order_by(table.area_name).all()

        # output
        if data_type == 'l':

            out = out + [d.get_geofeature() for d in data]

        else:

            out = out + [d.as_dict() for d in data]

    # output final
    if data_type == 'l':

        out = FeatureCollection(out)

    return out
