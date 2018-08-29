from app.utils.utilssqlalchemy import (
    serializable, geoserializable
)

from app.utils.env import DB
from geoalchemy2 import Geometry


@serializable
class BibAreasType(DB.Model):
    __tablename__ = 'bib_areas_types'
    __table_args__ = {'schema': 'ref_geo', 'extend_existing': True}

    id_type = DB.Column(DB.Integer, primary_key=True)
    type_name = DB.Column(DB.String(200))
    type_code = DB.Column(DB.String(25))
    type_desc = DB.Column(DB.Text)
    ref_name = DB.Column(DB.String(200))
    ref_version = DB.Column(DB.Integer)
    num_version = DB.Column(DB.String(50))


@serializable
class TAreas(DB.Model):
    __tablename__ = 'l_areas'
    __table_args__ = {'schema': 'ref_geo', 'extend_existing': True}

    id_area = DB.Column(DB.Integer, primary_key=True, server_default=DB.text("nextval('ref_geo.l_areas_id_area_seq'::regclass)"))
    id_type = DB.Column(DB.Integer, nullable=False)
    area_name = DB.Column(DB.String(250))
    area_code = DB.Column(DB.String(25))
    source = DB.Column(DB.String(250))
    comment = DB.Column(DB.Text)
    enable = DB.Column(DB.Boolean, nullable=False, server_default=DB.text("true"))
    meta_create_date = DB.Column(DB.DateTime)
    meta_update_date = DB.Column(DB.DateTime)


@serializable
@geoserializable
class LAreas(TAreas):
    geom_4326 = DB.Column(Geometry('MULTIPOLYGON', 4326))

    def get_geofeature(self, recursif=True):
        return self.as_geofeature('geom_4326', 'id_area', recursif)


# @serializable
# class TAreasCadastre(DB.Model):
#     __tablename__ = 'l_areas_cadastre'
#     __table_args__ = {'schema': 'ref_geo', 'extend_existing': True}

#     id_area = DB.Column(DB.Integer, primary_key=True, server_default=DB.text("nextval('ref_geo.l_areas_id_area_seq'::regclass)"))
#     id_type = DB.Column(DB.Integer, nullable=False)
#     area_name = DB.Column(DB.String(250))
#     area_code = DB.Column(DB.String(25))
#     source = DB.Column(DB.String(250))
#     comment = DB.Column(DB.Text)
#     enable = DB.Column(DB.Boolean, nullable=False, server_default=DB.text("true"))
#     meta_create_date = DB.Column(DB.DateTime)
#     meta_update_date = DB.Column(DB.DateTime)


# @serializable
# @geoserializable
# class LAreasCadastre(TAreasCadastre):
#     geom_4326 = DB.Column(Geometry('MULTIPOLYGON', 4326))

#     def get_geofeature(self, recursif=True):
#         return self.as_geofeature('geom_4326', 'id_area', recursif)


@serializable
class LiForetsGestionOnfPec(DB.Model):
    __tablename__ = 'li_forets_gestion_onf_pec'
    __table_args__ = {'schema': 'ref_geo'}

    id = DB.Column(DB.Integer, primary_key=True, server_default=DB.text("nextval('ref_geo.li_forets_gestion_onf_pec_id_seq'::regclass)"))
    id_area = DB.Column(DB.Integer, nullable=False)
    ccod_frt = DB.Column(DB.String(11))
    ccod_tpde = DB.Column(DB.String(4))
    ccod_ut = DB.Column(DB.String(8))
    llib_frt = DB.Column(DB.String(80))
    llib_ut = DB.Column(DB.String(50))
    qsret_frt = DB.Column(DB.Float(53))
    dept = DB.Column(DB.String(4))
    date_maj = DB.Column(DB.String(10))


@serializable
class VOeascOnfFrt(DB.Model):
    __tablename__ = 'vl_oeasc_onf_frt'
    __table_args__ = {'schema': 'ref_geo'}

    id = DB.Column(DB.Integer, primary_key=True)
    id_area = DB.Column(DB.ForeignKey('ref_geo.l_areas.id_area', onupdate='CASCADE'), nullable=False)
    area_code = DB.Column(DB.String(25))
    ccod_frt = DB.Column(DB.String(11))
    ccod_tpde = DB.Column(DB.String(4))
    ccod_ut = DB.Column(DB.String(8))
    llib_frt = DB.Column(DB.String(80))
    llib_ut = DB.Column(DB.String(50))
    qsret_frt = DB.Column(DB.Float(53))
    dept = DB.Column(DB.String(4))
    date_maj = DB.Column(DB.String(10))


@serializable
class VOeascOnfPrf(DB.Model):
    __tablename__ = 'vl_oeasc_onf_prf'
    __table_args__ = {'schema': 'ref_geo'}
    id = DB.Column(DB.Integer, primary_key=True)
    id_area = DB.Column(DB.ForeignKey('ref_geo.l_areas.id_area', onupdate='CASCADE'), nullable=False)
    area_code = DB.Column(DB.String(25))
    objectid = DB.Column(DB.Integer)
    ccod_tpde = DB.Column(DB.String(5))
    ccod_frt = DB.Column(DB.String(8))
    llib_ut = DB.Column(DB.String(50))
    llib_prf = DB.Column(DB.String(50))
    qsret_prf = DB.Column(DB.Float(53))
    dept = DB.Column(DB.String(4))
    ccod_pst = DB.Column(DB.String(10))
    ccod_ut = DB.Column(DB.BigInteger)
    llib_frt = DB.Column(DB.String(50))
    agent_pst = DB.Column(DB.String(50))
    ccod_prf = DB.Column(DB.String(5))
    date_maj = DB.Column(DB.String(10))
    concat = DB.Column(DB.String(50))


@serializable
class VOeascOnfUG(DB.Model):
    __tablename__ = 'vl_oeasc_onf_ug'
    __table_args__ = {'schema': 'ref_geo'}
    id = DB.Column(DB.Integer, primary_key=True)
    id_area = DB.Column(DB.ForeignKey('ref_geo.l_areas.id_area', onupdate='CASCADE'), nullable=False)
    area_code = DB.Column(DB.String(25))
    objectid = DB.Column(DB.BigInteger)
    ccod_frt = DB.Column(DB.String(11))
    ccod_prf = DB.Column(DB.String(11))
    ccod_ug = DB.Column(DB.String(10))
    ccod_ut = DB.Column(DB.String(9))
    maj_date = DB.Column(DB.String(10))
    camgt_prf = DB.Column(DB.String(12))
    llib_prf = DB.Column(DB.String(25))
    qsret_prf = DB.Column(DB.Float(53))
    qsret_ugs = DB.Column(DB.Float(53))
    qssy_ugs = DB.Column(DB.Float(53))
    cgrpl_ug = DB.Column(DB.String(11))
    cgrpn_ug = DB.Column(DB.String(11))
    llib_grpn = DB.Column(DB.String(16))
    concat = DB.Column(DB.String(20))
    dept = DB.Column(DB.String(4))
    ccod_tpde = DB.Column(DB.String(4))
    llib_frt = DB.Column(DB.String(200))
    agent_pst = DB.Column(DB.String(50))
    ccod_pst = DB.Column(DB.String(10))
    cvrai_ug = DB.Column(DB.String(1))
    llib_ut = DB.Column(DB.String(50))
    concat_ug = DB.Column(DB.String(40))
    suffix = DB.Column(DB.Integer)


@serializable
@geoserializable
class VLOeascOnfFrt(VOeascOnfFrt):
    geom_4326 = DB.Column(Geometry('MULTIPOLYGON', 4326))

    def get_geofeature(self, recursif=True):
        return self.as_geofeature('geom_4326', 'id_area', recursif)


@serializable
@geoserializable
class VLOeascOnfPrf(VOeascOnfPrf):
    geom_4326 = DB.Column(Geometry('MULTIPOLYGON', 4326))

    def get_geofeature(self, recursif=True):
        return self.as_geofeature('geom_4326', 'id_area', recursif)


@serializable
@geoserializable
class VLOeascOnfUG(VOeascOnfUG):
    geom_4326 = DB.Column(Geometry('MULTIPOLYGON', 4326))

    def get_geofeature(self, recursif=True):
        return self.as_geofeature('geom_4326', 'id_area', recursif)
