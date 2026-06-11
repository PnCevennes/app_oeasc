"""
Fonctions pour récupérer les géometries
"""

from sqlalchemy import and_, text, select, func
from sqlalchemy.orm import Session
from flask import current_app

# from geojson import FeatureCollection

from .models import (
    BibAreasType,
    LAreas,
    VMAreasSimples,
)
from .schema import LAreasSchema, VMAreasSimplesSchema

from ..modules.oeasc.declaration.models import CorDgdCadastre

config = current_app.config
DB = config["DB"]


def get_id_type(type_code):
    """
    TODO
    """

    stmt = select(func.ref_geo.get_id_type(type_code))
    res = DB.session.execute(stmt).first()[0]

    return res


def get_type_code(id_type):
    """
    Récupère le type_code pour un id_type donné.
    """

    stmt = (
        select(BibAreasType.type_code).where(BibAreasType.id_type == id_type).limit(1)
    )
    res = DB.session.execute(stmt).scalars().one_or_none()
    return res


def set_table_and_schema(b_simple, data_type):
    """
    Choisit la table et le schema selon le niveau de simplification souhaite.

    - b_simple=True: vue materialisee simplifiee
    - b_simple=False: table ref_geo.l_areas
    - data_type est conserve pour compatibilite de signature
    """
    if b_simple:
        return VMAreasSimples, VMAreasSimplesSchema

    return LAreas, LAreasSchema


def _order_column(table):
    """Retourne la colonne de tri compatible selon le modele utilise."""
    if hasattr(table, "label"):
        return table.label
    return table.area_name


def refresh_vm_lareas_simples(concurrently=False):
    """Refresh explicite de la vue materialisee ref_geo.vm_lareas_simples."""
    concurrently_sql = "CONCURRENTLY " if concurrently else ""
    stmt = text(f"REFRESH MATERIALIZED VIEW {concurrently_sql}ref_geo.vm_lareas_simples")
    DB.session.execute(stmt)
    DB.session.commit()


def areas_from_type_code(b_simple, data_type, type_code):
    """
    retourne toutes les aires pour un type_code donne (par exemple OEASC_CADASTRE)

    b_simple : renvoie  geométrie simplifiee si vrai
                        géométrie d'origine sinon

    data type : t -> renvoie seulement les attributs
                l -> renvoie aussi la geometrie
    """

    table, schema = set_table_and_schema(b_simple, data_type)

    id_type = get_id_type(type_code)

    stmt = (
        select(table)
        .where(table.id_type == id_type)
        .where(table.enable)
        .order_by(_order_column(table))
    )
    data = DB.session.execute(stmt).scalars().all()

    if data_type == "l":
        # out = FeatureCollection([d.get_geofeature() for d in data])
        out = schema(many=True, as_geojson=True).dump(data)
    else:
        out = schema(many=True, as_geojson=False).dump(data)
        # out = [d.as_dict() for d in data]

    if data_type == "l":
        for o in out["features"]:
            o["properties"]["type"] = type_code
    else:
        for o in out:
            o["type"] = type_code

    return out


def areas_from_type_code_container(b_simple, data_type, type_code, ids_area_container):
    """
    retourne toutes les aires pour un type_code donne (par exemple OEASC_CADASTRE)
    et étant contenue dans la geometrie identifiée par son id_area : id_area_container
    la recherche de ses élément se fait par rapport aux area_code:
        - soit en comparant les area_code des contenus et du contenant (cas général)
        - soit en se servant d'une table de correlation
        precalculée pour le cas des forêts avec DGD

    data type : t -> renvoie seulement les attributs
                l -> renvoie aussi la geometrie

    b_simple : renvoie  geométrie simplifiee si vrai
                        géométrie d'origine sinon

    """
    table, schema = set_table_and_schema(b_simple, data_type)

    id_type = get_id_type(type_code)
    v = ids_area_container.split("-")

    out = []

    for id_area_container in v:

        stmt_container = (
            select(table)
            .where(table.id_area == id_area_container)
            .order_by(_order_column(table))
            # .limit(1) # ajout le limit pour optimiser la requete
        )
        container = DB.session.execute(stmt_container).scalars().first()

        id_type_commune = get_id_type("OEASC_COMMUNE")
        id_type_dgd = get_id_type("OEASC_DGD")

        # cas des section de communes
        if container.id_type == id_type_commune:

            stmt_old_communes = select(
                func.ref_geo.get_old_communes(container.area_code)
            )
            result = DB.session.execute(stmt_old_communes).scalars().all()

            data = []

            for r in result:
                area_code = r[0]

                stmt = (
                    select(table)
                    .where(
                        and_(
                            table.id_type == id_type,
                            table.enable,
                            table.area_code.like(area_code + "-%"),
                        )
                    )
                    .order_by(_order_column(table))
                )

                data = DB.session.execute(stmt).scalars().all() + data

        # cas des dgd
        elif container.id_type == id_type_dgd:

            stmt_cadastre = select(CorDgdCadastre.area_code_cadastre).where(
                CorDgdCadastre.area_code_dgd == container.area_code
            )
            res = DB.session.execute(stmt_cadastre).all()

            v = [r[0] for r in res]

            stmt_by_area_code = (
                select(table).where(table.area_code.in_(v)).order_by(_order_column(table))
            )
            data = DB.session.execute(stmt_by_area_code).scalars().all()

        # autres cas ONF
        else:

            stmt = (
                select(table)
                .where(
                    and_(
                        table.id_type == id_type,
                        table.enable,
                        table.area_code.like(container.area_code + "-%"),
                    )
                )
                .order_by(_order_column(table))
            )
            data = DB.session.execute(stmt).scalars().all()

    # output final
    if data_type == "l":
        # out = FeatureCollection(out)
        out = schema(many=True, as_geojson=True).dump(data)
    else:
        # out = [d.as_dict() for d in data]
        out = schema(many=True, as_geojson=False).dump(data)

    return out


def areas_post(b_simple, data_type, areas):
    """
    TODO
    """
    table, schema = set_table_and_schema(b_simple, data_type)

    out = []

    t_areas = areas
    stmt_areas = select(table).where(table.id_area.in_(t_areas))
    data = DB.session.execute(stmt_areas).scalars().all()

    if data_type == "l":
        # out = FeatureCollection([d.get_geofeature() for d in data])
        out = schema(many=True, as_geojson=True).dump(data)

    else:
        # out = [d.as_dict() for d in data]
        out = schema(many=True).dump(data)

    return out


def build_area_hierarchy(data, hierarchy_data):
    """
    Construit un json hiérarchique à partir des données d'aires et de la hiérarchie.
    data ne contient que les aires de cadastre et DG_onf, donc celles qui n'ont pas d'enfants.
    Cette fonction trouve donc les parents des aires de data et constuit la hiérarchie
    en ajoutant les aires enfants à chaque parent.
    En plus des informations sur les aires, chaque element contient aussi:
    - id_parent : l'id du parent de l'aire
    - areas_enfant : une liste des aires enfants de l'aire
    """
    # On construit la hiérarchie à partir des données récupérées
    hierarchy = {}

    # on recherche dans hierachy_data les id_area_parent qui n'apparaissent pas dans les id_area_enfant
    area_children = set([relation["id_area_enfant"] for relation in hierarchy_data])
    area_parents = set([relation["id_area_parent"] for relation in hierarchy_data])
    first_level_parents = area_parents - area_children

    # Build a mapping from id_area to its data
    data_map = {x["id_area"]: x for x in data}
    # Build a mapping from parent to list of children
    children_map = {}
    for relation in hierarchy_data:
        children_map.setdefault(relation["id_area_parent"], []).append(
            relation["id_area_enfant"]
        )

    def build_tree(id_area, parent_id=None):
        node = data_map.get(id_area, {"id_area": id_area})
        node["id_parent"] = parent_id
        node["areas_enfant"] = [
            build_tree(child_id, id_area) for child_id in children_map.get(id_area, [])
        ]
        return node

    # Only build trees for top-level parents
    result = [
        build_tree(id_area) for id_area in first_level_parents if id_area in data_map
    ]

    return result
