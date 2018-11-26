from sqlalchemy import and_, text

from geojson import FeatureCollection

from .models import (
    VAreas as VA,
    VLAreas as VLA,
    VAreasSimples as VAS,
    VLAreasSimples as VLAS,
)

from flask import current_app

config = current_app.config
DB = config['DB']


def get_id_type(type_code):

    return DB.session.execute("SELECT ref_geo.get_id_type(:type_code);", {'type_code': type_code}).first()[0]


def get_type_code(id_type):

    return DB.session.execute("SELECT type_code FROM ref_geo.bib_areas_types WHERE  id_type = :id_type;", {'id_type': id_type}).first()[0]


def set_table(b_simple, data_type):
    '''
        choisi la table qui correspond aux données demandées
        - b_simple : geometrie simplifée ou brute
        - data_type : t -> attributs seul
                    l -> on ajoute la geometrie
    '''
    if b_simple:

        attributs = VAS
        layers = VLAS

    else:

        attributs = VA
        layers = VLA

    if data_type == 'l':

        table = layers

    else:

        table = attributs

    return table


def areas_from_type_code(b_simple, data_type, type_code):
    '''
        retourne toutes les aires pour un type_code donne (par exemple OEASC_CADASTRE)

        b_simple : renvoie  geométrie simplifiee si vrai
                            géométrie d'origine sinon

        data type : t -> renvoie seulement les attributs
                    l -> renvoie aussi la geometrie
    '''

    table = set_table(b_simple, data_type)

    id_type = get_id_type(type_code)

    data = DB.session.query(table).filter(and_(table.id_type == id_type, table.enable)).order_by(table.label).all()

    if data_type == 'l':
        return FeatureCollection([d.get_geofeature() for d in data])
    else:
        return [d.as_dict() for d in data]


def areas_from_type_code_container(b_simple, data_type, type_code, ids_area_container):
    '''
        retourne toutes les aires pour un type_code donne (par exemple OEASC_CADASTRE)
        et étant contenue dans la geometrie identifiée par son id_area : id_area_container
        la recherche de ses élément se fait par rapport aux area_code:
            - soit en comparant les area_code des contenus et du contenant (cas général)
            - soit en se servant d'une table de correlation precalculée pour le cas des forêts avec DGD

        data type : t -> renvoie seulement les attributs
                    l -> renvoie aussi la geometrie

        b_simple : renvoie  geométrie simplifiee si vrai
                            géométrie d'origine sinon

    '''
    table = set_table(b_simple, data_type)

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

                data = DB.session.query(table).filter(and_(table.id_type == id_type, table.enable, table.area_code.like(area_code + "-%"))).order_by(table.label).all() + data

        # cas des dgd
        elif(container.id_type == id_type_dgd):

            res = DB.engine.execute(text("SELECT area_code_cadastre FROM ref_geo.cor_dgd_cadastre WHERE area_code_dgd = '{}' ;".format(container.area_code)))

            v = [r[0] for r in res]

            data = DB.session.query(table).filter(table.area_code.in_(v)).order_by(table.label).all()

        # autres cas ONF
        else:

            data = DB.session.query(table).filter(and_(table.id_type == id_type, table.enable, table.area_code.like(container.area_code + "-%"))).order_by(table.label).all()

        # output
        if data_type == 'l':

            out = out + [d.get_geofeature() for d in data]

        else:

            out = out + [d.as_dict() for d in data]

    # output final
    if data_type == 'l':

        out = FeatureCollection(out)

    return out


def areas_post(b_simple, data_type, areas):

    table = set_table(b_simple, data_type)

    out = []

    t_areas = tuple([area['id_area'] for area in areas])

    data = DB.session.query(table).filter(table.id_area.in_(t_areas)).all()

    if data_type == 'l':

        out = FeatureCollection([d.get_geofeature() for d in data])

    else:

        out = [d.as_dict() for d in data]

        print("\n\n\nbb", out)

    return out
