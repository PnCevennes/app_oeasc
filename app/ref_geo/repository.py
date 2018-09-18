from app.utils.env import DB


def get_id_type(type_code):

    return DB.session.execute("SELECT ref_geo.get_id_type(:type_code);", {'type_code': type_code}).first()[0]


def get_type_code(id_type):

    return DB.session.execute("SELECT type_code FROM ref_geo.bib_areas_types WHERE  id_type = :id_type;", {'id_type': id_type}).first()[0]
