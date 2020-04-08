'''
    api pour la table ref_geo
'''

from geojson import FeatureCollection
from sqlalchemy import text

from flask import (
    Blueprint,
    request,
    current_app
)

from app.utils.utilssqlalchemy import json_resp

from .models import (
    TAreas as TA,
    LAreas as LA,
    BibAreasType,
)

from .repository import (
    get_id_type,
    areas_from_type_code,
    areas_from_type_code_container,
    areas_post,
)

bp = Blueprint('ref_geo', __name__)

config = current_app.config

DB = config['DB']


@bp.route('type_codes_oeasc')
@json_resp
def get_type_code_oeasc():
    '''
        renvoie les element de bibareastype relatifs à l'OEASC
    '''
    data = DB.session.query(BibAreasType).filter(BibAreasType.ref_name.in_(('OEASC', 'ONF')))

    return [d.as_dict() for d in data]


@bp.route('get_id_type/<string:type_code>')
@json_resp
def get_id_type_api(type_code):
    '''
        TODO in join request
    '''
    return get_id_type(type_code)


@bp.route('area/<string:data_type>/<int:id_area>')
@json_resp
def get_area(data_type, id_area):
    '''
        get area from id
        TODO with get params
    '''
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
    '''
        TODO make it get
    '''
    data_in = request.get_json()

    areas = data_in['areas']

    b_simple = False

    return areas_post(b_simple, data_type, areas)


@bp.route('areas_test_post/<string:data_type>', methods=['GET'])
@json_resp
def get_areas_test_post(data_type):
    '''
        TODO make it get
    '''
    areas = [{'id_area': 277431}]
    b_simple = False

    return areas_post(b_simple, data_type, areas)


@bp.route('areas_simples_post/<string:data_type>', methods=['POST'])
@json_resp
def get_areas_simples_post(data_type):
    '''
        TODO make it get
    '''
    data_in = request.get_json()

    areas = data_in['areas']

    b_simple = True

    return areas_post(b_simple, data_type, areas)


@bp.route('areas_centroid_post/<string:data_type>', methods=['POST'])
@json_resp
def get_areas_centroid_post(data_type):
    '''
        TODO make it GET
    '''
    d_areas = request.get_json()

    d_out = {}

    for key, value in d_areas.items():

        v = value

        t = tuple(v)

        if len(v) == 1:

            t = str(t).replace(",", "")

        sql_text = text("SELECT ST_X(c),ST_Y(c) \
            FROM (SELECT ST_CENTROID(ST_UNION(geom_4326)) as c \
            FROM ref_geo.l_areas \
            WHERE id_area in {} )a".format(t))

        result = DB.engine.execute(sql_text).first()

        v = [result[1], result[0]]
        d_out[key] = v

    return d_out


@bp.route('areas_from_type_code/<string:data_type>/<string:type_code>', methods=['GET', 'POST'])
@json_resp
def get_areas_from_type_code(data_type, type_code):
    '''
        retourne toutes les aires pour un type_code donne (par exemple OEASC_CADASTRE)

        data type : t -> renvoie seulement les attributs
                    l -> renvoie aussi la geometrie
    '''

    return areas_from_type_code(False, data_type, type_code)


@bp.route(
    'areas_simples_from_type_code/<string:data_type>/<string:type_code>',
    methods=['GET', 'POST']
)
@json_resp
def get_areas_simples_from_type_code(data_type, type_code):
    '''
        retourne toutes les aires pour un type_code donne (par exemple OEASC_CADASTRE)

        data type : t -> renvoie seulement les attributs
                    l -> renvoie aussi la geometrie
    '''

    data = areas_from_type_code(True, data_type, type_code)

    return data


@bp.route(
    'areas_from_type_code_container/\
<string:data_type>/\
<string:type_code>/\
<string:ids_area_container>',
    methods=['GET', 'POST']
)
@json_resp
def get_areas_from_type_code_container(data_type, type_code, ids_area_container):
    '''
        retourne toutes les aires pour un type_code donne (par exemple OEASC_CADASTRE)
        et étant contenue dans la geometrie identifiée par son id_area : id_area_container
        la recherche de ses élément se fait par rapport aux area_code:
            - soit en comparant les area_code des contenus et du contenant (cas général)
            - soit en se servant d'une table de correlation precalculée
                pour le cas des forêts avec DGD
        data type : t -> renvoie seulement les attributs
                    l -> renvoie aussi la geometrie

    '''

    b_simple = False
    return areas_from_type_code_container(b_simple, data_type, type_code, ids_area_container)


@bp.route(
    'areas_simples_from_type_code_container/\
<string:data_type>/\
<string:type_code>/\
<ids_area_container>',
    methods=['GET', 'POST']
)
@json_resp
def get_areas_simples_from_type_code_container(data_type, type_code, ids_area_container):
    '''
        retourne toutes les aires pour un type_code donne (par exemple OEASC_CADASTRE)
        et étant contenue dans la geometrie identifiée par son id_area : id_area_container
        la recherche de ses élément se fait par rapport aux area_code:
            - soit en comparant les area_code des contenus et du contenant (cas général)
            - soit en se servant d'une table de correlation precalculée
                pour le cas des forêts avec DGD
        data type : t -> renvoie seulement les attributs
                    l -> renvoie aussi la geometrie

    '''

    print(data_type, type_code, ids_area_container)
    b_simple = True
    return areas_from_type_code_container(b_simple, data_type, type_code, ids_area_container)
