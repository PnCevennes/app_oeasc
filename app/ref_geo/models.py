"""
    modeles pour ref_geo
    TODO !!
    simplifier les vues
    ajouter type dans les vues
    etc...
    améliorer forets
"""
from flask import current_app
from geoalchemy2 import Geometry

from utils_flask_sqla.serializers import serializable
from utils_flask_sqla_geo.serializers import geoserializable

config = current_app.config
DB = config["DB"]


@serializable
class BibAreasType(DB.Model):
    """
    ref_geo.bib_areas_types
    """

    __tablename__ = "bib_areas_types"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}

    id_type = DB.Column(DB.Integer, primary_key=True)
    type_name = DB.Column(DB.String(200))
    type_code = DB.Column(DB.String(25))
    type_desc = DB.Column(DB.Text)
    ref_name = DB.Column(DB.String(200))
    ref_version = DB.Column(DB.Integer)
    num_version = DB.Column(DB.String(50))


@serializable
class TAreas(DB.Model):
    """
    ref_geo.l_areas sans geom
    """

    __tablename__ = "l_areas"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}

    id_area = DB.Column(
        DB.Integer,
        primary_key=True,
        server_default=DB.text("nextval('ref_geo.l_areas_id_area_seq'::regclass)"),
    )
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
class LAreas(DB.Model):
    """
    ref_geo.l_areas avec geom
    """

    __tablename__ = "l_areas"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}

    id_area = DB.Column(
        DB.Integer,
        primary_key=True,
        server_default=DB.text("nextval('ref_geo.l_areas_id_area_seq'::regclass)"),
    )
    id_type = DB.Column(DB.Integer, nullable=False)
    area_name = DB.Column(DB.String(250))
    area_code = DB.Column(DB.String(25))
    source = DB.Column(DB.String(250))
    comment = DB.Column(DB.Text)
    enable = DB.Column(DB.Boolean, nullable=False, server_default=DB.text("true"))
    meta_create_date = DB.Column(DB.DateTime)
    meta_update_date = DB.Column(DB.DateTime)

    geom_4326 = DB.Column(Geometry("MULTIPOLYGON", 4326))

    def get_geofeature(self, recursif=True):
        """
        utilSqlaGeo
        """
        return self.as_geofeature("geom_4326", "id_area", recursif)


@serializable
class VAreas(DB.Model):
    """
    ref_geo.vl_areas sans geom
    """

    __tablename__ = "vl_areas"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}

    id_area = DB.Column(DB.Integer, primary_key=True)
    id_type = DB.Column(DB.Integer, nullable=False)
    area_name = DB.Column(DB.String(250))
    label = DB.Column(DB.String(250))
    area_code = DB.Column(DB.String(25))
    source = DB.Column(DB.String(250))
    enable = DB.Column(DB.Boolean, nullable=False, server_default=DB.text("true"))
    surface_calculee = DB.Column(DB.Float)
    surface_renseignee = DB.Column(DB.Float)


@serializable
@geoserializable
class VAreasSimples(DB.Model):
    """
    ref_geo.vl_areas_simples sans geom
    """

    __tablename__ = "vl_areas_simples"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}

    id_area = DB.Column(
        DB.Integer,
        primary_key=True,
        server_default=DB.text("nextval('ref_geo.l_areas_id_area_seq'::regclass)"),
    )
    id_type = DB.Column(DB.Integer, nullable=False)
    area_name = DB.Column(DB.String(250))
    label = DB.Column(DB.String(250))
    area_code = DB.Column(DB.String(25))
    source = DB.Column(DB.String(250))
    enable = DB.Column(DB.Boolean, nullable=False, server_default=DB.text("true"))
    surface_calculee = DB.Column(DB.Float)
    surface_renseignee = DB.Column(DB.Float)


@serializable
@geoserializable
class VLAreas(DB.Model):
    """
    ref_geo.vl_areas avec geom
    """

    __tablename__ = "vl_areas"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}

    id_area = DB.Column(DB.Integer, primary_key=True)
    id_type = DB.Column(DB.Integer, nullable=False)
    area_name = DB.Column(DB.String(250))
    label = DB.Column(DB.String(250))
    area_code = DB.Column(DB.String(25))
    source = DB.Column(DB.String(250))
    surface_calculee = DB.Column(DB.Float)
    surface_renseignee = DB.Column(DB.Float)
    geom_4326 = DB.Column(Geometry("MULTIPOLYGON", 4326))

    def get_geofeature(self, recursif=True):
        """
        ??? Use utilsSqlaGeo
        """

        return self.as_geofeature("geom_4326", "id_area", recursif)


@serializable
@geoserializable
class VLAreasSimples(DB.Model):
    """
    ref_geo.vl_areas_simples avec geom
    """

    __tablename__ = "vl_areas_simples"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}

    id_area = DB.Column(DB.Integer, primary_key=True)
    id_type = DB.Column(DB.Integer, nullable=False)
    area_name = DB.Column(DB.String(250))
    label = DB.Column(DB.String(250))
    area_code = DB.Column(DB.String(25))
    source = DB.Column(DB.String(250))
    surface_calculee = DB.Column(DB.Float)
    surface_renseignee = DB.Column(DB.Float)
    geom_4326 = DB.Column(Geometry("MULTIPOLYGON", 4326))

    def get_geofeature(self, recursif=True):
        """
        ??? Use utilsSqlaGeo
        """
        return self.as_geofeature("geom_4326", "id_area", recursif)
