"""
Fonctions pour récupérer les géometries
"""

from sqlalchemy import and_, text, select, func
from sqlalchemy.orm import Session
from flask import current_app
from geojson import FeatureCollection

from .models import (
    VAreas as VA,
    VLAreas as VLA,
    VAreasSimples as VAS,
    VLAreasSimples as VLAS,
    BibAreasType,

)

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

    stmt = select(BibAreasType.type_code).where(
        BibAreasType.id_type == id_type
    ).limit(1)
    res = DB.session.execute(stmt).scalars().one_or_none()
    print("get_type_code", res)
    return res

# def get_type_code(id_type):
#     """
#     TODO
#     """

#     # return DB.session.execute(
#     #     "SELECT type_code FROM ref_geo.bib_areas_types WHERE  id_type = :id_type;",
#     #     {"id_type": id_type},
#     # ).first()[0]


def set_table(b_simple, data_type):
    """
    choisi la table qui correspond aux données demandées
    - b_simple : geometrie simplifée ou brute
    - data_type : t -> attributs seul
                l -> on ajoute la geometrie
    """
    if b_simple:
        attributs = VAS
        layers = VLAS

    else:
        attributs = VA
        layers = VLA

    if data_type == "l":
        table = layers

    else:
        table = attributs

    return table


def areas_from_type_code(b_simple, data_type, type_code):
    """
    retourne toutes les aires pour un type_code donne (par exemple OEASC_CADASTRE)

    b_simple : renvoie  geométrie simplifiee si vrai
                        géométrie d'origine sinon

    data type : t -> renvoie seulement les attributs
                l -> renvoie aussi la geometrie
    """

    table = set_table(b_simple, data_type)

    id_type = get_id_type(type_code)


    stmt = ((select(table)
            .where(table.id_type == id_type)
            .where(table.enable)
            .order_by(table.label)))
    data = DB.session.execute(stmt).scalars().all()
        


    if data_type == "l":
        out = FeatureCollection([d.get_geofeature() for d in data])
    else:
        out = [d.as_dict() for d in data]

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
    table = set_table(b_simple, data_type)

    id_type = get_id_type(type_code)
    v = ids_area_container.split("-")

    out = []


    for id_area_container in v:

        stmt_container = (
            select(table)
                .where(table.id_area == id_area_container)
                .order_by(table.label)
                .limit(1) # ajout le limit pour optimiser la requete
        )
        container = DB.session.execute(stmt_container).scalars().first()


        id_type_commune = get_id_type("OEASC_COMMUNE")
        id_type_dgd = get_id_type("OEASC_DGD")

        # cas des section de communes
        if container.id_type == id_type_commune:

            # fonction de la base de données refgeo.
            # sql_text = text(
            #     "SELECT ref_geo.get_old_communes('{}')".format(container.area_code)
            # )
            stmt_old_communes = select(func.ref_geo.get_old_communes(container.area_code))
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
                    .order_by(table.label)
                )

                data = DB.session.execute(stmt).scalars().all() + data



        # cas des dgd
        elif container.id_type == id_type_dgd:

            stmt_cadastre = (select(CorDgdCadastre.area_code_cadastre).where(
                CorDgdCadastre.area_code_dgd == container.area_code
            ))
            res = DB.session.execute(stmt_cadastre).all()
            
            
            v = [r[0] for r in res]

            stmt_by_area_code = (
                select(table)
                .where(table.area_code.in_(v))
                .order_by(table.label)
            )
            data = DB.session.execute(stmt_by_area_code).scalars().all()


        # autres cas ONF
        else:

            stmt = (select(table)
                .where(
                    and_(
                        table.id_type == id_type,
                        table.enable,
                        table.area_code.like(container.area_code + "-%"),
                    )
                )
                .order_by(table.label)
            )
            data = DB.session.execute(stmt).scalars().all()


        # output
        if data_type == "l":
            out = out + [d.get_geofeature() for d in data]

        else:
            out = out + [d.as_dict() for d in data]

    # output final
    if data_type == "l":
        out = FeatureCollection(out)

    return out


def areas_post(b_simple, data_type, areas):
    """
    TODO
    """
    table = set_table(b_simple, data_type)

    out = []

    t_areas = areas
    stmt_areas = (
        select(table)
        .where(table.id_area.in_(t_areas))
    )
    data = DB.session.execute(stmt_areas).scalars().all()


    if data_type == "l":
        out = FeatureCollection([d.get_geofeature() for d in data])

    else:
        out = [d.as_dict() for d in data]

    return out
