"""
api pour la table ref_geo
"""

# from geojson import FeatureCollection
from sqlalchemy import text, select
from flask import Blueprint, request, current_app
from utils_flask_sqla.response import json_resp

from .models import (
    TAreas as TA,
    VAreas,
    VLAreasSimples as VLAS,
    LAreas as LA,
    BibAreasType,
    CorHierarchieArea
)
from .schema import (
    TAreasSchema,
    VAreasSchema,
    LAreasSchema,
    VLAreasSchema,
    VLAreasSimplesSchema,
    BibAreasTypeSchema,
    CorHierarchieAreaSchema
)

from .repository import (
    get_id_type,
    areas_from_type_code,
    areas_from_type_code_container,
    areas_post,
    set_table_and_schema,
    build_area_hierarchy
)

bp = Blueprint("ref_geo", __name__)

config = current_app.config

DB = config["DB"]


@bp.route("type_codes_oeasc")
@json_resp
def get_type_code_oeasc():
    """
    renvoie les element de bibareastype relatifs à l'OEASC
    """
    stmt_data = (select(BibAreasType)
                 .where(BibAreasType.ref_name.in_(("OEASC", "ONF")))
                 .order_by(BibAreasType.type_code)
    )
    data = DB.session.execute(stmt_data).scalars().all()

    areasType_dict = BibAreasTypeSchema(many=True).dump(data)
    # areasType_dict = [d.as_dict() for d in data]

    return areasType_dict


@bp.route("get_id_type/<string:type_code>")
@json_resp
def get_id_type_api(type_code):
    """
    TODO in join request
    """
    return get_id_type(type_code)


@bp.route("area/<string:data_type>/<int:id_area>")
@json_resp
def get_area(data_type, id_area):
    """
    Récupère une aire spécifique en fonction de son identifiant.
    data_type : t -> renvoie seulement les attributs
                l -> renvoie aussi la géométrie
    Exemple d'URL : /area/l/277431
    """
    table, schema = set_table_and_schema(b_simple=True, data_type=data_type)

    stmt_area = (
        select(table)
        .where(table.id_area == id_area)
        .limit(1)
    )
    data = DB.session.execute(stmt_area).scalars().first()

    if data_type == "l":
        result = schema(as_geojson=True).dump(data)
        return result
    else:
        return schema().dump(data)
    

@bp.route("areas/<string:data_type>/<string:id_areas>", methods=["GET"])
@json_resp
def get_areas_liste(data_type, id_areas):
    """
    data_type : t -> renvoie seulement les attributs
                l -> renvoie aussi la géométrie
    Cette fonction est utilisée pour récupérer des aires spécifiques en fonction de leurs identifiants.
    Exemple d'URL : /areas/l/277431-277432-277433
    """
    # On découpe la chaîne d'identifiants en liste
    liste_areas = id_areas.split("-")
    # On récupère la table et le schéma correspondant au type de données
    table, schema = set_table_and_schema(b_simple=True, data_type=data_type)

    # On prépare la requête pour récupérer les aires dont l'id est dans la liste
    stmt_area = (
        select(table)
        .where(table.id_area.in_(liste_areas))
    )

    # On exécute la requête et on récupère les résultats
    data = DB.session.execute(stmt_area).scalars().all()

    # Si le type de données est "l", on retourne les résultats au format GeoJSON
    if data_type == "l":
        return schema(many=True, as_geojson=True).dump(data)
    else:
        # Sinon, on retourne les résultats sous forme de dictionnaires classiques
        return schema(many=True).dump(data)


@bp.route("areas_post/<string:data_type>", methods=["POST"])
@json_resp
def get_areas_post(data_type):
    """
    TODO make it get
    """
    data_in = request.get_json()

    areas = data_in["areas"]

    b_simple = False

    return areas_post(b_simple, data_type, areas)


@bp.route("areas_from_type/<string:data_type>", methods=["GET"])
@json_resp
def get_areas(data_type):
    """
    TODO make it get
    """
    areas = request.args.getlist("id_area")

    b_simple = False

    return areas_post(b_simple, data_type, areas)


@bp.route("areas_simple/<string:data_type>", methods=["GET"])
@json_resp
def get_areas_simple(data_type):
    """
    TODO make it get
    """
    areas = request.args.getlist("id_area")

    b_simple = True

    return areas_post(b_simple, data_type, areas)


# @bp.route("areas_test_post/<string:data_type>", methods=["GET"])
# @json_resp
# def get_areas_test_post(data_type):
#     """
#     TODO make it get
#     """
#     areas = [{"id_area": 277431}]
#     b_simple = False

#     return areas_post(b_simple, data_type, areas)


@bp.route("areas_simples_post/<string:data_type>", methods=["POST"])
@json_resp
def get_areas_simples_post(data_type):
    """
    TODO make it get
    """
    data_in = request.get_json()

    areas = data_in["areas"]

    b_simple = True

    return areas_post(b_simple, data_type, areas)


@bp.route("areas_centroid_post/<string:data_type>", methods=["POST"])
@json_resp
def get_areas_centroid_post(data_type):
    """
    TODO make it GET
    """
    d_areas = request.get_json()

    d_out = {}

    for key, value in d_areas.items():
        v = value

        t = tuple(v)

        if len(v) == 1:
            t = str(t).replace(",", "")

        # sql_text = text(
        #     "SELECT ST_X(c),ST_Y(c) \
        #     FROM (SELECT ST_CENTROID(ST_UNION(geom_4326)) as c \
        #     FROM ref_geo.l_areas \
        #     WHERE id_area in {} )a".format(
        #         t
        #     )
        # )

        sql_text = text("SELECT ST_X(c),ST_Y(c) \
            FROM (SELECT ST_CENTROID(ST_UNION(geom_4326)) as c \
            FROM ref_geo.l_areas \
            WHERE id_area in :areas )a").bindparams(areas=t)
        result = DB.session.execute(sql_text).first()


        v = [result[1], result[0]]
        d_out[key] = v

    return d_out


@bp.route(
    "areas_from_type_code/<string:data_type>/<string:type_code>",
    methods=["GET", "POST"],
)
@json_resp
def get_areas_from_type_code(data_type, type_code):
    """
    retourne toutes les aires pour un type_code donne (par exemple OEASC_CADASTRE)

    data type : t -> renvoie seulement les attributs
                l -> renvoie aussi la geometrie
    """

    return areas_from_type_code(False, data_type, type_code)


@bp.route(
    "areas_simples_from_type_code/<string:data_type>/<string:type_code>",
    methods=["GET", "POST"],
)
@json_resp
def get_areas_simples_from_type_code(data_type, type_code):
    """
    retourne toutes les aires pour un type_code donne (par exemple OEASC_CADASTRE)

    data type : t -> renvoie seulement les attributs
                l -> renvoie aussi la geometrie
    """

    data = areas_from_type_code(True, data_type, type_code)

    return data


@bp.route(
    "areas_from_type_code_container/\
<string:data_type>/\
<string:type_code>/\
<string:ids_area_container>",
    methods=["GET", "POST"],
)
@json_resp
def get_areas_from_type_code_container(data_type, type_code, ids_area_container):
    """
    retourne toutes les aires pour un type_code donne (par exemple OEASC_CADASTRE)
    et étant contenue dans la geometrie identifiée par son id_area : id_area_container
    la recherche de ses élément se fait par rapport aux area_code:
        - soit en comparant les area_code des contenus et du contenant (cas général)
        - soit en se servant d'une table de correlation precalculée
            pour le cas des forêts avec DGD
    data type : t -> renvoie seulement les attributs
                l -> renvoie aussi la geometrie

    """

    b_simple = False
    return areas_from_type_code_container(
        b_simple, data_type, type_code, ids_area_container
    )


@bp.route(
    "areas_simples_from_type_code_container/\
<string:data_type>/\
<string:type_code>/\
<ids_area_container>",
    methods=["GET", "POST"],
)
@json_resp
def get_areas_simples_from_type_code_container(
    data_type, type_code, ids_area_container
):
    """
    retourne toutes les aires pour un type_code donne (par exemple OEASC_CADASTRE)
    et étant contenue dans la geometrie identifiée par son id_area : id_area_container
    la recherche de ses élément se fait par rapport aux area_code:
        - soit en comparant les area_code des contenus et du contenant (cas général)
        - soit en se servant d'une table de correlation precalculée
            pour le cas des forêts avec DGD
    data type : t -> renvoie seulement les attributs
                l -> renvoie aussi la geometrie

    """
    b_simple = True
    return areas_from_type_code_container(
        b_simple, data_type, type_code, ids_area_container
    )


@bp.route("areas_child_of/<int:id_type>/<int:id_area>", methods=["GET"])
@json_resp
def get_areas_child_of(id_type, id_area):
    """
    Récupère les aires enfants d'une aire spécifique en fonction de son identifiant.
    id_type : identifiant du type d'aire 
    id_area : identifiant de l'aire parent
    Exemple d'URL : /areas_child_of/1/277431
    """
    stmt = (
        select(CorHierarchieArea)
        .where(CorHierarchieArea.id_area_parent == id_area)
        .where(CorHierarchieArea.id_type_parent == id_type)
    ) 
    all_child_areas = DB.session.execute(stmt).scalars().all()

    # ensuite, on recupère les aires de data de all_child_areas.id_area_enfant
    stmt_areas = (
        select(VLAS)
        .where(VLAS.id_area.in_([child.id_area_enfant for child in all_child_areas]))
    )
    data = DB.session.execute(stmt_areas).scalars().all()
    # On utilise le schéma LAreasSchema pour sérialiser les données
    all_areas = VLAreasSimplesSchema(many=True, as_geojson=True).dump(data)

    return all_areas


# depuis une liste de id_area, on récupère toutes les infos de ces aires, ainsi que les parents
#  et on créé un json hierarchique. le Json aura aussi id_parent et id_enfant pour chaque aire
@bp.route("areas_hierarchy/<string:id_areas>", methods=["GET"])
@json_resp
def get_areas_hierarchy(id_areas):
    """
        id_areas : liste des identifiants d'aires à récupérer
        Exemple d'URL : /areas_hierarchy/l/277431-277432-277433
        http://localhost:5005//api/ref_geo/areas_hierarchy/t/277372-277409-519079-284370
    """

    # On découpe la chaîne d'identifiants en liste
    liste_areas = id_areas.split("-")
    # On récupère la table et le schéma correspondant au type de données
    # table_area, schema_area = set_table_and_schema(b_simple=False, data_type="t")


    stmt_area = (
        select(VAreas)
        .where(VAreas.id_area.in_(liste_areas))
    )
    data = DB.session.execute(stmt_area).scalars().all()
    data_result = VAreasSchema(many=True).dump(data)

    stmt_hierarchy = (
        select(CorHierarchieArea)
        .where(
            # (CorHierarchieArea.id_area_parent.in_(liste_areas))
            (CorHierarchieArea.id_area_enfant.in_(liste_areas))
        )
    )
    hierarchy_data = DB.session.execute(stmt_hierarchy).scalars().all()
    hierarchy_result = CorHierarchieAreaSchema(many=True).dump(hierarchy_data)


    # On construit la hiérarchie à partir des données récupérées
    hierarchy = build_area_hierarchy(data_result, hierarchy_result)

    return hierarchy



