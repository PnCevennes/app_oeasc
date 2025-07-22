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
from sqlalchemy import ForeignKey, Column, Integer, String, Text, Boolean, DateTime, Float
from  sqlalchemy.orm import Mapped

config = current_app.config
DB = config["DB"]

class CustomModel(DB.Model):
    __abstract__ = True  # evite que la classe soit considérée comme une table
    __allow_unmapped__ = True

@serializable
class BibAreasType(CustomModel):
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
class TAreas(CustomModel):
    """
    ref_geo.l_areas sans geom
    """

    __tablename__ = "l_areas"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}

    id_area: Mapped[int] = Column(
        Integer,
        primary_key=True,
        server_default=DB.text("nextval('ref_geo.l_areas_id_area_seq'::regclass)"),
    )
    id_type: Mapped[int] = Column(Integer, nullable=False)
    area_name: Mapped[str] = Column(String(250))
    area_code: Mapped[str] = Column(String(25))
    source: Mapped[str] = Column(String(250))
    comment: Mapped[str] = Column(Text)
    enable: Mapped[bool] = Column(Boolean, nullable=False, server_default=DB.text("true"))
    meta_create_date: Mapped[DateTime] = Column(DateTime)
    meta_update_date: Mapped[DateTime] = Column(DateTime)



@serializable
@geoserializable
class LAreas(CustomModel):
    """
    ref_geo.l_areas avec geom
    """

    __tablename__ = "l_areas"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}

    id_area: Mapped[int] = Column( Integer, primary_key=True, server_default=DB.text("nextval('ref_geo.l_areas_id_area_seq'::regclass)"))
    id_type: Mapped[int] = Column(Integer, nullable=False)

    area_name: Mapped[str] = Column(String(250))
    area_code: Mapped[str] = Column(String(25))
    source: Mapped[str] = Column(String(250))
    comment: Mapped[str] = Column(Text)
    enable: Mapped[bool] = Column(Boolean, nullable=False, server_default=DB.text("true"))
    meta_create_date: Mapped[DateTime] = Column(DateTime)
    meta_update_date: Mapped[DateTime] = Column(DateTime)
    geom_4326: Mapped[Geometry] = Column(Geometry("MULTIPOLYGON", 4326))


    def get_geofeature(self, recursif=False):
        """
        utilSqlaGeo
        """
        return self.as_geofeature("geom_4326", "id_area", recursif)


@serializable
class VAreas(CustomModel):
    """
    ref_geo.vl_areas sans geom
    """

    __tablename__ = "vl_areas"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}

    id_area: Mapped[int] = Column(Integer, primary_key=True)
    id_type: Mapped[int] = Column(Integer, nullable=False)
    area_name: Mapped[str] = Column(String(250))
    label: Mapped[str] = Column(String(250))
    area_code: Mapped[str] = Column(String(25))
    source: Mapped[str] = Column(String(250))
    enable: Mapped[bool] = Column(Boolean, nullable=False, server_default=DB.text("true"))
    surface_calculee: Mapped[float] = Column(Float)
    surface_renseignee: Mapped[float] = Column(Float)

@serializable
# @geoserializable
class VAreasSimples(CustomModel):
    """
    ref_geo.vl_areas_simples sans geom
    """

    __tablename__ = "vl_areas_simples"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}

    id_area: Mapped[int] = Column(
        Integer,
        primary_key=True,
        server_default=DB.text("nextval('ref_geo.vl_areas_simples_id_area_seq'::regclass)"),
    )
    id_type: Mapped[int] = Column(Integer, nullable=False)
    area_name: Mapped[str] = Column(String(250))
    label: Mapped[str] = Column(String(250))
    area_code: Mapped[str] = Column(String(25))
    source: Mapped[str] = Column(String(250))
    enable: Mapped[bool] = Column(Boolean, nullable=False, server_default=DB.text("true"))
    surface_calculee: Mapped[float] = Column(Float)
    surface_renseignee: Mapped[float] = Column(Float)



@serializable
@geoserializable
class VLAreas(CustomModel):
    """
    ref_geo.vl_areas avec geom
    """

    __tablename__ = "vl_areas"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}

    id_area: Mapped[int] = Column(Integer, primary_key=True)
    id_type: Mapped[int] = Column(Integer, nullable=False)
    area_name: Mapped[str] = Column(String(250))
    label: Mapped[str] = Column(String(250))
    area_code: Mapped[str] = Column(String(25))
    source: Mapped[str] = Column(String(250))
    surface_calculee: Mapped[float] = Column(Float)
    surface_renseignee: Mapped[float] = Column(Float)
    geom_4326: Mapped[Geometry] = Column(Geometry("MULTIPOLYGON", 4326))

    def get_geofeature(self, recursif=False):
        """
        ??? Use utilsSqlaGeo
        """

        return self.as_geofeature("geom_4326", "id_area", recursif)


@serializable
@geoserializable
class VLAreasSimples(CustomModel):
    """
    ref_geo.vl_areas_simples avec geom
    """

    __tablename__ = "vl_areas_simples"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}

    id_area: Mapped[int] = Column(Integer, primary_key=True)
    id_type: Mapped[int] = Column(Integer, nullable=False)
    area_name: Mapped[str] = Column(String(250))
    label: Mapped[str] = Column(String(250))
    area_code: Mapped[str] = Column(String(25))
    source: Mapped[str] = Column(String(250))
    surface_calculee: Mapped[float] = Column(Float)
    surface_renseignee: Mapped[float] = Column(Float)
    geom_4326: Mapped[Geometry] = Column(Geometry("MULTIPOLYGON", 4326))


    def get_geofeature(self, recursif=False):
        """
        ??? Use utilsSqlaGeo
        """
        return self.as_geofeature("geom_4326", "id_area", recursif)


class CorHierarchieArea(CustomModel):
    """
    ref_geo.cor_hierarchie_area
    cette table indique quelle area se trouve à l'intérieur d'une area parent en fonction de son type.
    par exemple, une commune (id_type=332) intègre un ensemble d'area.
    les foret onf (id_type=328) sont aussi des aires qui intègrent des aires cadastre (id_type=25).
    les forets dgd (id_type=327) intègrent des aires cadastre (id_type=25).
    """

    __tablename__ = "cor_hierarchie_area"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}

    id_area_enfant: Mapped[int] = Column(Integer, ForeignKey("ref_geo.l_areas.id_area"), primary_key=True)
    id_type_enfant: Mapped[int] = Column(Integer, primary_key=True)
    id_area_parent: Mapped[int] = Column(Integer, ForeignKey("ref_geo.l_areas.id_area"), primary_key=True)
    id_type_parent: Mapped[int] = Column(Integer, primary_key=True)


