from flask import (
    Blueprint,
    request
)

from .models import (
    TAreas as TA,
    LAreas as LA,
)

from sqlalchemy.sql import func

from sqlalchemy import and_

# from geoalchemy2 import functions

from app.utils.env import DB

from app.utils.utilssqlalchemy import json_resp

from geojson import FeatureCollection

from .repository import get_id_type


def f_area_code(area_code, n):
    return '-'.join(str(area_code).split('-')[:n])


bp = Blueprint('ref_geo', __name__)


@bp.route('get_id_type/<string:code_type>')
@json_resp
def get_id_type_api(code_type):

    return get_id_type(code_type)


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


@bp.route('areas/<string:data_type>/<string:type_code>//', defaults={'area_code': "-", 'type_code_container': "-", 'area_code_container': "-"})
@bp.route('areas/<string:data_type>/<string:type_code>/<string:area_code>/', defaults={'type_code_container': "-", 'area_code_container': "-"})
@bp.route('areas/<string:data_type>/<string:type_code>/<string:area_code>/<string:type_code_container>', defaults={'area_code_container': "-"})
@bp.route('areas/<string:data_type>/<string:type_code>/<string:area_code>/<string:type_code_container>/<string:area_code_container>', methods=['GET'])
@json_resp
def get_areas(data_type, type_code, area_code, type_code_container, area_code_container):

    if data_type == 'l' or type_code_container != "-":
        table = LA
    else:
        table = TA

    table_parent = LA

    id_type = get_id_type(type_code)

    if area_code != "-":
        data = DB.session.query(table).filter(and_(table.id_type == id_type, table.enable, table.area_code == area_code))
    else:
        data = DB.session.query(table).filter(and_(table.id_type == id_type, table.enable))

    if type_code_container != "-":

        id_type_container = DB.session.execute("select ref_geo.get_id_type(:type_code);", {'type_code': type_code_container}).first()[0]

        if area_code_container != "-":
            container = DB.session.query(table_parent.geom_4326.label('geom_4326')).filter(and_(table_parent.id_type == id_type_container, table_parent.area_code == area_code_container)).subquery()
        else:
            container = DB.session.query(table_parent.geom_4326.label('geom_4326')).filter(table.id_type == id_type_container).subquery()

        data = data.filter(func.ST_INTERSECTS(table.geom_4326, container.c.geom_4326))

        data = data.filter(func.ST_AREA(func.ST_INTERSECTION(table.geom_4326, container.c.geom_4326)) >= 0.01 * func.ST_AREA(table.geom_4326))

        data = data.order_by(table.area_name)

    if data_type == 'l':
        return FeatureCollection([d.get_geofeature() for d in data])
    else:
        return [d.as_dict() for d in data]
