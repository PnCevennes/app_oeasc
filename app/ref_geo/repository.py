from app.utils.env import DB


def get_id_type(type_code):

    return DB.session.execute("select ref_geo.get_id_type(:type_code);", {'type_code': type_code}).first()[0]
