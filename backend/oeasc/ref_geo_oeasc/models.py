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
from ref_geo.models import BibAreasTypes as RefBibAreasTypes
from ref_geo.models import LAreas as RefLAreas

from utils_flask_sqla.serializers import serializable
from utils_flask_sqla_geo.serializers import geoserializable
from sqlalchemy import (
    ForeignKey,
    Column,
    Integer,
    String,
    Text,
    Boolean,
    DateTime,
    Float,
)
from sqlalchemy.orm import Mapped

config = current_app.config
DB = config["DB"]


class CustomModel(DB.Model):
    __abstract__ = True  # evite que la classe soit considérée comme une table
    __allow_unmapped__ = True


@serializable
class BibAreasType(RefBibAreasTypes):
    """Extension locale de ref_geo.BibAreasTypes pour conserver l'API OEASC."""

    pass


@serializable
@geoserializable
class LAreas(RefLAreas):
    """Extension locale de ref_geo.LAreas pour conserver l'API OEASC."""

    # Compatibilite: le code OEASC historique utilise LAreas.comment.
    comment = RefLAreas.description

    def get_geofeature(self, recursif=False):
        """
        Retourne la représentation GeoJSON de l'aire.

        Cette méthode utilise la fonction utilitaire as_geofeature pour sérialiser l'objet
        en une feature GeoJSON, en utilisant le champ 'geom_4326' comme géométrie et 'id_area'
        comme identifiant. Le paramètre 'recursif' permet d'inclure ou non les relations imbriquées.

        Utilisation typique :
        - Pour l'affichage sur une carte (frontend)
        - Pour l'export GeoJSON
        - Pour les API spatiales

        Args:
            recursif (bool): Si True, inclut les relations imbriquées dans la feature.

        Returns:
            dict: Représentation GeoJSON de l'aire.
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

    id_area_enfant: Mapped[int] = Column(
        Integer, ForeignKey("ref_geo.l_areas.id_area"), primary_key=True
    )
    id_type_enfant: Mapped[int] = Column(Integer, primary_key=True)
    id_area_parent: Mapped[int] = Column(
        Integer, ForeignKey("ref_geo.l_areas.id_area"), primary_key=True
    )
    id_type_parent: Mapped[int] = Column(Integer, primary_key=True)


class TCommunesArea(CustomModel):
    """
    ref_geo.cor_commune_area
    cette table indique quelle area correspond à quelle commune.
    elle est utilisée pour faire le lien entre les aires cadastrales et les communes, par exemple.
    """

    __tablename__ = "communes_aoa"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}


    id = Column(String(25), primary_key=True)
    fid = Column(Integer)
    insee_com = Column(String(5))
    nom = Column(String(80))
    insee_dep = Column(String(5))
    coeur = Column(Integer)
    aire_adhes = Column(Integer)
    aoa = Column(Integer)
    massif = Column(String(50))
    population = Column(Integer)
    siren_epci = Column(String(32))
    nom_ccom = Column(String(51))
    surface_ha = Column(Integer)
    date_creat = Column(DateTime)
    date_maj = Column(DateTime)
    code_siren = Column(String(9))
    code_post = Column(String(5))


class CorAreaIntersect(CustomModel):
    """
    ref_geo.cor_area_intersect
    cette table indique quelles aires s'intersectent entre elles.
    elle est utilisée pour faire le lien entre les aires cadastrales et les communes, par exemple.
    """

    __tablename__ = "cor_area_intersect"
    __table_args__ = {"schema": "ref_geo", "extend_existing": True}

    id = Column(Integer, primary_key=True)
    id_parcelle = Column(Integer)       # parcelle cadastrale (332) ou UG ONF (330)
    id_type_parcelle = Column(Integer)
    id_section_cadastrale = Column(Integer)
    id_commune = Column(Integer)
    id_foret_dgd = Column(Integer)
    id_foret_onf = Column(Integer)
    id_foret_prive = Column(Integer)    # forêt privée sans document (id_type=33)
    id_parcelle_onf = Column(Integer)   # parcellaire ONF (329) contenant l'UG ONF
    id_secteur = Column(Integer)
    in_coeur = Column(Boolean)
    in_aire_adhesion_pnc = Column(Boolean)
    in_oeasc = Column(Boolean)




# @serializable
# class TSecteurs(CustomModel):
#     __tablename__ = "t_secteurs"
#     __table_args__ = {"schema": "ref_geo", "extend_existing": True}

#     id_secteur: Mapped[int] = Column(Integer, primary_key=True)
#     code_secteur: Mapped[str] = Column(String(250))
#     nom_secteur: Mapped[str] = Column(String(250))



@serializable
@geoserializable
class VMAreasSimples(CustomModel):
    """
    Modèle pour la vue matérialisée ref_geo.vm_lareas_simples avec géométrie.

    Cette classe représente les aires géographiques enregistrées dans la table l_areas du schéma ref_geo,
    incluant le champ de géométrie (geom_4326). Elle permet de manipuler à la fois les attributs descriptifs
    et la géométrie spatiale des aires. Ce modèle est utilisé pour les opérations nécessitant la géométrie,
    comme l'affichage cartographique, les exports GeoJSON, ou les traitements spatiaux.
    """

    __tablename__ = "vm_lareas_simples"
    __table_args__ = {"schema": "ref_geo"}
    # Identifiant unique de l'aire (clé primaire, auto-incrémenté)
    id_area: Mapped[int] = Column(
        Integer,
        primary_key=True,
        server_default=DB.text("nextval('ref_geo.l_areas_id_area_seq'::regclass)"),
    )

    # Identifiant du type d'aire (clé étrangère vers bib_areas_types)
    id_type: Mapped[int] = Column(Integer, nullable=False)

    # Nom de l'aire (ex : nom de commune, nom de forêt, etc.)
    area_name: Mapped[str] = Column(String(250))

    # Libellé complémentaire ou alternatif de l'aire
    label: Mapped[str] = Column(String(250))

    # Code court de l'aire (ex : code INSEE, code forêt, etc.)
    area_code: Mapped[str] = Column(String(25))

    # Source des données (ex : IGN, ONF, etc.)
    source: Mapped[str] = Column(String(250))

    # Indique si l'aire est active ou non (true = active)
    enable: Mapped[bool] = Column(
        Boolean, nullable=False, server_default=DB.text("true")
    )

    # Surface calculée automatiquement (ex : via la géométrie, mais non présente ici)
    surface_calculee: Mapped[float] = Column(Float)

    # Surface renseignée manuellement (ex : donnée officielle ou saisie)
    surface_renseignee: Mapped[float] = Column(Float)

    # Géométrie de l'aire au format MULTIPOLYGON en projection EPSG:4326
    geom_4326: Mapped[Geometry] = Column(Geometry("MULTIPOLYGON", 4326))






#########################################################################################
#########################################################################################
#########################################################################################




# @serializable
# class TAreas(CustomModel):
#     """
#     Modèle pour la table ref_geo.l_areas sans géométrie.

#     Cette classe représente les aires géographiques enregistrées dans la table l_areas du schéma ref_geo,
#     mais sans le champ de géométrie (geom_4326). Elle est utile lorsque l'on souhaite manipuler ou afficher
#     les informations attributaires des aires sans avoir besoin de la géométrie associée, par exemple pour
#     des listes, des formulaires ou des exports non spatiaux.
#     """

#     __tablename__ = "l_areas"
#     __table_args__ = {"schema": "ref_geo", "extend_existing": True}

#     # Identifiant unique de l'aire (clé primaire, auto-incrémenté)
#     id_area: Mapped[int] = Column(
#         Integer,
#         primary_key=True,
#         server_default=DB.text("nextval('ref_geo.l_areas_id_area_seq'::regclass)"),
#     )

#     # Identifiant du type d'aire (clé étrangère vers bib_areas_types)
#     id_type: Mapped[int] = Column(Integer, nullable=False)

#     # Nom de l'aire (ex : nom de commune, nom de forêt, etc.)
#     area_name: Mapped[str] = Column(String(250))

#     # Code court de l'aire (ex : code INSEE, code forêt, etc.)
#     area_code: Mapped[str] = Column(String(25))

#     # Source des données (ex : IGN, ONF, etc.)
#     source: Mapped[str] = Column(String(250))

#     # Commentaire libre sur l'aire (informations complémentaires)
#     comment: Mapped[str] = Column(Text)

#     # Indique si l'aire est active ou non (true = active)
#     enable: Mapped[bool] = Column(
#         Boolean, nullable=False, server_default=DB.text("true")
#     )

#     # Date de création de l'enregistrement (utile pour l'audit et le suivi)
#     meta_create_date: Mapped[DateTime] = Column(DateTime)

#     # Date de dernière modification de l'enregistrement
#     meta_update_date: Mapped[DateTime] = Column(DateTime)

#     # Cette classe est utilisée principalement :
#     # - Pour afficher ou manipuler les aires sans géométrie (listes, exports CSV, formulaires)
#     # - Lorsque la géométrie n'est pas nécessaire (optimisation des requêtes)
#     # - Pour des traitements attributaires ou des synchronisations de données non spatiales



# @serializable
# class VAreas(CustomModel):
#     """
#     Modèle pour la vue ref_geo.vl_areas sans géométrie.

#     Cette classe représente la vue matérialisée vl_areas du schéma ref_geo,
#     qui contient des informations attributaires sur les aires géographiques,
#     mais sans le champ de géométrie (geom_4326). Elle est utile pour manipuler
#     ou afficher les données non spatiales des aires, par exemple pour des listes,
#     des exports CSV, ou des formulaires où la géométrie n'est pas nécessaire.
#     """

#     __tablename__ = "vl_areas"
#     __table_args__ = {"schema": "ref_geo", "extend_existing": True}

#     # Identifiant unique de l'aire (clé primaire)
#     id_area: Mapped[int] = Column(Integer, primary_key=True)

#     # Identifiant du type d'aire (clé étrangère vers bib_areas_types)
#     id_type: Mapped[int] = Column(Integer, nullable=False)

#     # Nom de l'aire (ex : nom de commune, nom de forêt, etc.)
#     area_name: Mapped[str] = Column(String(250))

#     # Libellé complémentaire ou alternatif de l'aire
#     label: Mapped[str] = Column(String(250))

#     # Code court de l'aire (ex : code INSEE, code forêt, etc.)
#     area_code: Mapped[str] = Column(String(25))

#     # Source des données (ex : IGN, ONF, etc.)
#     source: Mapped[str] = Column(String(250))

#     # Indique si l'aire est active ou non (true = active)
#     enable: Mapped[bool] = Column(
#         Boolean, nullable=False, server_default=DB.text("true")
#     )

#     # Surface calculée automatiquement (ex : via la géométrie)
#     surface_calculee: Mapped[float] = Column(Float)

#     # Surface renseignée manuellement (ex : donnée officielle ou saisie)
#     surface_renseignee: Mapped[float] = Column(Float)

#     # Utilisation typique :
#     # - Pour afficher ou manipuler les aires sans géométrie (listes, exports non spatiaux)
#     # - Pour des traitements attributaires ou des synchronisations de données non spatiales
#     # - Optimisation des requêtes lorsque la géométrie n'est pas requise


# @serializable
# @geoserializable
# class VAreasSimples(CustomModel):
#     """
#     Modèle pour la vue ref_geo.vl_areas_simples sans géométrie.

#     Cette classe représente la vue matérialisée vl_areas_simples du schéma ref_geo,
#     qui contient des informations attributaires sur les aires géographiques,
#     mais sans le champ de géométrie (geom_4326). Elle est utile pour manipuler
#     ou afficher les données non spatiales des aires, par exemple pour des listes,
#     des exports CSV, ou des formulaires où la géométrie n'est pas nécessaire.

#     Utilisation typique :
#     - Pour afficher ou manipuler les aires sans géométrie (listes, exports non spatiaux)
#     - Pour des traitements attributaires ou des synchronisations de données non spatiales
#     - Optimisation des requêtes lorsque la géométrie n'est pas requise
#     """

#     __tablename__ = "vl_areas_simples"
#     __table_args__ = {"schema": "ref_geo", "extend_existing": True}

#     # Identifiant unique de l'aire (clé primaire, auto-incrémenté)
#     id_area: Mapped[int] = Column(
#         Integer,
#         primary_key=True,
#         server_default=DB.text(
#             "nextval('ref_geo.vl_areas_simples_id_area_seq'::regclass)"
#         ),
#     )

#     # Identifiant du type d'aire (clé étrangère vers bib_areas_types)
#     id_type: Mapped[int] = Column(Integer, nullable=False)

#     # Nom de l'aire (ex : nom de commune, nom de forêt, etc.)
#     area_name: Mapped[str] = Column(String(250))

#     # Libellé complémentaire ou alternatif de l'aire
#     label: Mapped[str] = Column(String(250))

#     # Code court de l'aire (ex : code INSEE, code forêt, etc.)
#     area_code: Mapped[str] = Column(String(25))

#     # Source des données (ex : IGN, ONF, etc.)
#     source: Mapped[str] = Column(String(250))

#     # Indique si l'aire est active ou non (true = active)
#     enable: Mapped[bool] = Column(
#         Boolean, nullable=False, server_default=DB.text("true")
#     )

#     # Surface calculée automatiquement (ex : via la géométrie, mais non présente ici)
#     surface_calculee: Mapped[float] = Column(Float)

#     # Surface renseignée manuellement (ex : donnée officielle ou saisie)
#     surface_renseignee: Mapped[float] = Column(Float)


# @serializable
# @geoserializable
# class VLAreas(CustomModel):
#     """
#     Modèle pour la vue ref_geo.vl_areas avec géométrie.

#     Cette classe représente la vue matérialisée vl_areas du schéma ref_geo,
#     qui contient à la fois les informations attributaires et la géométrie (geom_4326)
#     des aires géographiques. Elle est utilisée pour manipuler ou afficher les données
#     spatiales des aires, par exemple pour l'affichage cartographique, l'export GeoJSON,
#     ou les traitements spatiaux dans l'application.
#     """

#     __tablename__ = "vl_areas"
#     __table_args__ = {"schema": "ref_geo", "extend_existing": True}

#     # Identifiant unique de l'aire (clé primaire)
#     id_area: Mapped[int] = Column(Integer, primary_key=True)

#     # Identifiant du type d'aire (clé étrangère vers bib_areas_types)
#     id_type: Mapped[int] = Column(Integer, nullable=False)

#     # Nom de l'aire (ex : nom de commune, nom de forêt, etc.)
#     area_name: Mapped[str] = Column(String(250))

#     # Libellé complémentaire ou alternatif de l'aire
#     label: Mapped[str] = Column(String(250))

#     # Code court de l'aire (ex : code INSEE, code forêt, etc.)
#     area_code: Mapped[str] = Column(String(25))

#     # Source des données (ex : IGN, ONF, etc.)
#     source: Mapped[str] = Column(String(250))

#     # Surface calculée automatiquement (ex : via la géométrie)
#     surface_calculee: Mapped[float] = Column(Float)

#     # Surface renseignée manuellement (ex : donnée officielle ou saisie)
#     surface_renseignee: Mapped[float] = Column(Float)

#     # Géométrie de l'aire au format MULTIPOLYGON en projection EPSG:4326
#     geom_4326: Mapped[Geometry] = Column(Geometry("MULTIPOLYGON", 4326))

#     def get_geofeature(self, recursif=False):
#         """
#         Retourne la représentation GeoJSON de l'aire.

#         Cette méthode utilise la fonction utilitaire as_geofeature pour sérialiser l'objet
#         en une feature GeoJSON, en utilisant le champ 'geom_4326' comme géométrie et 'id_area'
#         comme identifiant. Le paramètre 'recursif' permet d'inclure ou non les relations imbriquées.

#         Utilisation typique :
#         - Pour l'affichage sur une carte (frontend)
#         - Pour l'export GeoJSON
#         - Pour les API spatiales

#         Args:
#             recursif (bool): Si True, inclut les relations imbriquées dans la feature.

#         Returns:
#             dict: Représentation GeoJSON de l'aire.
#         """
#         return self.as_geofeature("geom_4326", "id_area", recursif)








# @serializable
# @geoserializable
# class VLAreasSimples(CustomModel):
#     """
#     Modèle pour la vue ref_geo.vl_areas_simples avec géométrie.

#     Cette classe représente la vue matérialisée vl_areas_simples du schéma ref_geo,
#     qui contient à la fois les informations attributaires et la géométrie (geom_4326)
#     des aires géographiques. Elle est utilisée pour manipuler ou afficher les données
#     spatiales des aires, par exemple pour l'affichage cartographique, l'export GeoJSON,
#     ou les traitements spatiaux dans l'application.
#     """

#     __tablename__ = "vl_areas_simples"
#     __table_args__ = {"schema": "ref_geo", "extend_existing": True}

#     # Identifiant unique de l'aire (clé primaire)
#     id_area: Mapped[int] = Column(Integer, primary_key=True)

#     # Identifiant du type d'aire (clé étrangère vers bib_areas_types)
#     id_type: Mapped[int] = Column(Integer, nullable=False)

#     # Nom de l'aire (ex : nom de commune, nom de forêt, etc.)
#     area_name: Mapped[str] = Column(String(250))

#     # Libellé complémentaire ou alternatif de l'aire
#     label: Mapped[str] = Column(String(250))

#     # Code court de l'aire (ex : code INSEE, code forêt, etc.)
#     area_code: Mapped[str] = Column(String(25))

#     # Source des données (ex : IGN, ONF, etc.)
#     source: Mapped[str] = Column(String(250))

#     # Surface calculée automatiquement (ex : via la géométrie)
#     surface_calculee: Mapped[float] = Column(Float)

#     # Surface renseignée manuellement (ex : donnée officielle ou saisie)
#     surface_renseignee: Mapped[float] = Column(Float)

#     # Géométrie de l'aire au format MULTIPOLYGON en projection EPSG:4326
#     geom_4326: Mapped[Geometry] = Column(Geometry("MULTIPOLYGON", 4326))

#     def get_geofeature(self, recursif=False):
#         """
#         Retourne la représentation GeoJSON de l'aire.

#         Cette méthode utilise la fonction utilitaire as_geofeature pour sérialiser l'objet
#         en une feature GeoJSON, en utilisant le champ 'geom_4326' comme géométrie et 'id_area'
#         comme identifiant. Le paramètre 'recursif' permet d'inclure ou non les relations imbriquées.

#         Utilisation typique :
#         - Pour l'affichage sur une carte (frontend)
#         - Pour l'export GeoJSON
#         - Pour les API spatiales

#         Args:
#             recursif (bool): Si True, inclut les relations imbriquées dans la feature.

#         Returns:
#             dict: Représentation GeoJSON de l'aire.
#         """
#         return self.as_geofeature("geom_4326", "id_area", recursif)

