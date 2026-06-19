"""
modeles alerte OEASC
"""

from flask import current_app
from pypnusershub.db.models import User
from utils_flask_sqla.serializers import serializable
from utils_flask_sqla_geo.serializers import geoserializable
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    Boolean,
    Date,
    DateTime,
    Float,
    ARRAY,
    ForeignKey,
    func,
)

from pypnnomenclature.models import TNomenclatures, BibNomenclaturesTypes

from geoalchemy2 import Geometry

config = current_app.config
DB = config["DB"]


# les class heritent de CustomModel plutôt que de DB.Model pour ajouter allow_unmapped pour la migration vers sqlalchemy 2.0
# Cela permet de ne pas générer d'erreur avec l'ancienne manière de déclarer les models.
# Une fois la migration en 2.0 terminée il faudra réécrire les models en utilisant Mapped (cette fonction n'est pas dispo dans la 1.4)
class CustomModel(DB.Model):
    __abstract__ = True  # evite que la classe soit considérée comme une table
    __allow_unmapped__ = True


@serializable
class CorAreasDeclaration(CustomModel):
    """
    Correspondance entre les declarations et les areas (localisation de la déclaration)
    """

    __tablename__ = "cor_areas_declarations"
    __table_args__ = {"schema": "oeasc_declarations", "extend_existing": True}

    id_declaration: Mapped[int] = Column(
        Integer,
        ForeignKey("oeasc_declarations.t_declarations.id_declaration"),
        primary_key=True,
    )
    id_area: Mapped[int] = Column(
        Integer, ForeignKey("ref_geo.l_areas.id_area"), primary_key=True
    )

    def __init__(self, id_area=None):
        super(CorAreasDeclaration, self).__init__()
        self.id_area = id_area


@serializable
class CorNomenclatureDeclarationEssenceSecondaire(CustomModel):
    """
    nomenclatures essences secondaires
    """

    __tablename__ = "cor_nomenclature_declarations_essence_secondaire"
    __table_args__ = {"schema": "oeasc_declarations", "extend_existing": True}

    id_nomenclature: Mapped[int] = Column(
        Integer,
        ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
    )
    id_declaration: Mapped[int] = Column(
        Integer,
        ForeignKey("oeasc_declarations.t_declarations.id_declaration"),
        primary_key=True,
    )

    def __init__(self, id_nomenclature=None):
        super(CorNomenclatureDeclarationEssenceSecondaire, self).__init__()
        self.id_nomenclature = id_nomenclature


@serializable
class CorNomenclatureDeclarationEssenceComplementaire(CustomModel):
    """
    nomenclatures essences complementaires
    """

    __tablename__ = "cor_nomenclature_declarations_essence_complementaire"
    __table_args__ = {"schema": "oeasc_declarations", "extend_existing": True}

    id_nomenclature: Mapped[int] = Column(
        Integer,
        ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
    )
    id_declaration: Mapped[int] = Column(
        Integer,
        ForeignKey("oeasc_declarations.t_declarations.id_declaration"),
        primary_key=True,
    )

    def __init__(self, id_nomenclature=None):
        super(CorNomenclatureDeclarationEssenceComplementaire, self).__init__()
        self.id_nomenclature = id_nomenclature


@serializable
class CorNomenclatureDeclarationMaturite(CustomModel):
    """
    nomenclatures peuplement maturite
    """

    __tablename__ = "cor_nomenclature_declarations_maturite"
    __table_args__ = {"schema": "oeasc_declarations", "extend_existing": True}

    id_nomenclature: Mapped[int] = Column(
        Integer,
        ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
    )
    id_declaration: Mapped[int] = Column(
        Integer,
        ForeignKey("oeasc_declarations.t_declarations.id_declaration"),
        primary_key=True,
    )

    def __init__(self, id_nomenclature=None):
        super(CorNomenclatureDeclarationMaturite, self).__init__()
        self.id_nomenclature = id_nomenclature


@serializable
class CorNomenclatureDeclarationOrigine(CustomModel):
    """
    nomenclatures peuplement origine
    """

    __tablename__ = "cor_nomenclature_declarations_origine"
    __table_args__ = {"schema": "oeasc_declarations", "extend_existing": True}

    id_nomenclature: Mapped[int] = Column(
        Integer,
        ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
    )
    id_declaration: Mapped[int] = Column(
        Integer,
        ForeignKey("oeasc_declarations.t_declarations.id_declaration"),
        primary_key=True,
    )

    def __init__(self, id_nomenclature=None):
        super(CorNomenclatureDeclarationOrigine, self).__init__()
        self.id_nomenclature = id_nomenclature


@serializable
class CorNomenclatureDeclarationProtectionType(CustomModel):
    """
    nomenclatures protection type
    """

    __tablename__ = "cor_nomenclature_declarations_protection_type"
    __table_args__ = {"schema": "oeasc_declarations", "extend_existing": True}

    id_nomenclature: Mapped[int] = Column(
        Integer,
        ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
    )
    id_declaration: Mapped[int] = Column(
        Integer,
        ForeignKey("oeasc_declarations.t_declarations.id_declaration"),
        primary_key=True,
    )

    def __init__(self, id_nomenclature=None):
        super().__init__()
        self.id_nomenclature = id_nomenclature


@serializable
class CorNomenclatureDeclarationPaturageType(CustomModel):
    """
    nomenclatures paturage type
    """

    __tablename__ = "cor_nomenclature_declarations_paturage_type"
    __table_args__ = {"schema": "oeasc_declarations", "extend_existing": True}

    id_nomenclature: Mapped[int] = Column(
        Integer,
        ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
    )
    id_declaration: Mapped[int] = Column(
        Integer,
        ForeignKey("oeasc_declarations.t_declarations.id_declaration"),
        primary_key=True,
    )

    def __init__(self, id_nomenclature=None):
        super(CorNomenclatureDeclarationPaturageType, self).__init__()
        self.id_nomenclature = id_nomenclature


@serializable
class CorNomenclatureDeclarationPaturageSaison(CustomModel):
    """
    nomenclatures paturage saison
    """

    __tablename__ = "cor_nomenclature_declarations_paturage_saison"
    __table_args__ = {"schema": "oeasc_declarations", "extend_existing": True}

    id_nomenclature: Mapped[int] = Column(
        Integer,
        ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
    )
    id_declaration: Mapped[int] = Column(
        Integer,
        ForeignKey("oeasc_declarations.t_declarations.id_declaration"),
        primary_key=True,
    )

    def __init__(self, id_nomenclature=None):
        super(CorNomenclatureDeclarationPaturageSaison, self).__init__()
        self.id_nomenclature = id_nomenclature


@serializable
class CorNomenclatureDeclarationEspece(CustomModel):
    """
    nomenclatures especes
    """

    __tablename__ = "cor_nomenclature_declarations_espece"
    __table_args__ = {"schema": "oeasc_declarations", "extend_existing": True}

    id_nomenclature: Mapped[int] = Column(
        Integer,
        ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature"),
        primary_key=True,
    )
    id_declaration: Mapped[int] = Column(
        Integer,
        ForeignKey("oeasc_declarations.t_declarations.id_declaration"),
        primary_key=True,
    )

    def __init__(self, id_nomenclature=None):
        super(CorNomenclatureDeclarationEspece, self).__init__()
        self.id_nomenclature = id_nomenclature


@serializable
class TDegatEssence(CustomModel):
    """
    modele degat essence
    """

    __tablename__ = "t_degat_essences"
    __table_args__ = {"schema": "oeasc_declarations", "extend_existing": True}

    id_degat_essence: Mapped[int] = Column(Integer, primary_key=True)
    id_nomenclature_degat_essence: Mapped[int] = Column(
        Integer, ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    id_nomenclature_degat_etendue: Mapped[int] = Column(
        Integer, ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    id_nomenclature_degat_gravite: Mapped[int] = Column(
        Integer, ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )
    id_nomenclature_degat_anteriorite: Mapped[int] = Column(
        Integer, ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )

    id_degat: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_declarations.t_degats.id_degat")
    )


@serializable
class TDegat(CustomModel):
    """
    modele degat
    """

    __tablename__ = "t_degats"
    __table_args__ = {"schema": "oeasc_declarations", "extend_existing": True}

    id_degat: Mapped[int] = Column(Integer, primary_key=True)

    id_nomenclature_degat_type: Mapped[int] = Column(
        Integer, ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )

    id_declaration: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_declarations.t_declarations.id_declaration")
    )

    degat_essences: Mapped[list["TDegatEssence"]] = relationship(
        "TDegatEssence",
        cascade="save-update, merge, delete, delete-orphan",
    )


# @serializable
@geoserializable
class TDeclaration(CustomModel):
    """
    modele declaration
    """

    __tablename__ = "t_declarations"
    __table_args__ = {"schema": "oeasc_declarations", "extend_existing": True}

    id_declaration: Mapped[int] = Column(Integer, primary_key=True)
    id_declarant: Mapped[int] = Column(
        Integer, ForeignKey(User.id_role), nullable=False
    )

    id_nomenclature_proprietaire_declarant: Mapped[int] = Column(Integer, nullable=True)

    id_foret: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_forets.t_forets.id_foret"), nullable=False
    )
    id_nomenclature_peuplement_origine: Mapped[int] = Column(Integer, nullable=True)
    id_nomenclature_foret_type: Mapped[int] = Column(
        Integer, nullable=True
    )  # pas utilisé, il faudra le supprimer dans une migration
    id_nomenclature_peuplement_type: Mapped[int] = Column(Integer, nullable=False)
    id_nomenclature_peuplement_paturage_frequence: Mapped[int] = Column(
        Integer, nullable=True
    )
    id_nomenclature_peuplement_paturage_statut: Mapped[int] = Column(
        Integer, nullable=True
    )
    id_nomenclature_peuplement_acces: Mapped[int] = Column(Integer, nullable=False)
    id_nomenclature_peuplement_essence_principale: Mapped[int] = Column(
        Integer, nullable=False
    )
    peuplement_surface: Mapped[float] = Column(Float, nullable=True)

    b_peuplement_protection_existence: Mapped[bool] = Column(
        Boolean, nullable=False, default=False
    )
    b_peuplement_paturage_presence: Mapped[bool] = Column(
        Boolean, nullable=False, default=False
    )
    b_autorisation: Mapped[bool] = Column(
        Boolean, nullable=True, default=False
    )  # autorisation du partage d'informations
    b_valid: Mapped[bool] = Column(
        Boolean, nullable=False, default=False
    )  # validation de la déclaration

    areas_localisation: Mapped[list[CorAreasDeclaration]] = relationship(
        "CorAreasDeclaration", cascade="save-update, merge, delete, delete-orphan"
    )

    nomenclatures_peuplement_essence_secondaire: Mapped[
        list[CorNomenclatureDeclarationEssenceSecondaire]
    ] = relationship(
        "CorNomenclatureDeclarationEssenceSecondaire",
        cascade="save-update, merge, delete, delete-orphan",
    )

    nomenclatures_peuplement_essence_complementaire: Mapped[
        list[CorNomenclatureDeclarationEssenceComplementaire]
    ] = relationship(
        "CorNomenclatureDeclarationEssenceComplementaire",
        cascade="save-update, merge, delete, delete-orphan",
    )

    nomenclatures_peuplement_maturite: Mapped[
        list[CorNomenclatureDeclarationMaturite]
    ] = relationship(
        "CorNomenclatureDeclarationMaturite",
        cascade="save-update, merge, delete, delete-orphan",
    )

    nomenclatures_peuplement_protection_type: Mapped[
        list[CorNomenclatureDeclarationProtectionType]
    ] = relationship(
        "CorNomenclatureDeclarationProtectionType",
        cascade="save-update, merge, delete, delete-orphan",
    )

    nomenclatures_peuplement_paturage_type: Mapped[
        list[CorNomenclatureDeclarationPaturageType]
    ] = relationship(
        "CorNomenclatureDeclarationPaturageType",
        cascade="save-update, merge, delete, delete-orphan",
    )

    nomenclatures_peuplement_paturage_saison: Mapped[
        list[CorNomenclatureDeclarationPaturageSaison]
    ] = relationship(
        "CorNomenclatureDeclarationPaturageSaison",
        cascade="save-update, merge, delete, delete-orphan",
    )

    nomenclatures_peuplement_espece: Mapped[list[CorNomenclatureDeclarationEspece]] = (
        relationship(
            "CorNomenclatureDeclarationEspece",
            cascade="save-update, merge, delete, delete-orphan",
        )
    )

    nomenclatures_peuplement_origine2: Mapped[
        list[CorNomenclatureDeclarationOrigine]
    ] = relationship(
        "CorNomenclatureDeclarationOrigine",
        cascade="save-update, merge, delete, delete-orphan",  # permet de supprimer les Cornomenclatures liées à une déclaration si la déclaration est supprimée
    )

    degats: Mapped[list[TDegat]] = relationship(
        "TDegat",
        cascade="save-update, merge, delete, delete-orphan",
    )

    autre_protection: Mapped[str] = Column(Unicode(100), nullable=True)
    precision_localisation: Mapped[str] = Column(Unicode, nullable=True)
    commentaire: Mapped[str] = Column(Unicode, nullable=True)

    meta_create_date: Mapped[DateTime] = Column(DateTime, default=func.now())
    meta_update_date: Mapped[DateTime] = Column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    centroid: Mapped[list[float]] = Column(ARRAY(Float), nullable=True)
    date_fin: Mapped[Date] = Column(Date, nullable=True)
    statut: Mapped[int] = Column(
        Integer, nullable=True, default=0
    )  # 0 : en attente de validation, 1 : validée, 2 : refusée
    token_renouvellement: Mapped[str] = Column(Unicode(255), nullable=True)
    date_fin_token: Mapped[DateTime] = Column(DateTime, nullable=True)
    id_declaration_originale: Mapped[int] = Column(Integer, nullable=True)

    geom: Mapped[object] = Column(Geometry("MULTIPOLYGON", 4326))


################################################################
############ TABLES DU SCHEMAS OEASC_FORETS ############
################################################################


@serializable
class CorAreasForet(CustomModel):
    """
    areas foret
    """

    __tablename__ = "cor_areas_forets"
    __table_args__ = {"schema": "oeasc_forets", "extend_existing": True}

    id_area: Mapped[int] = Column(
        Integer, ForeignKey("ref_geo.l_areas.id_area"), primary_key=True
    )
    id_foret: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_forets.t_forets.id_foret"), primary_key=True
    )

    def __init__(self, id_area=None):
        super(CorAreasForet, self).__init__()
        self.id_area = id_area


# PROBLEME DE CLE PRIMAIRE et de DOUBLON dans la table
# @serializable
class CorDgdCadastre(CustomModel):
    """
    Correspondance entre les codes DGD et les codes cadastre pour les forêts (permet de faire le lien entre les données de la DGD et les données cadastrales)
    """

    __tablename__ = "cor_dgd_cadastre"
    __table_args__ = {"schema": "oeasc_forets", "extend_existing": True}

    # donc pas possible de faire des clés étrangères.
    area_code_dgd: Mapped[str] = Column(Unicode, primary_key=True)
    area_code_cadastre: Mapped[str] = Column(Unicode, primary_key=True)


@serializable
class TProprietaire(CustomModel):
    """
    modeles proprietaires
    """

    __tablename__ = "t_proprietaires"
    __table_args__ = {"schema": "oeasc_forets", "extend_existing": True}

    id_proprietaire: Mapped[int] = Column(Integer, primary_key=True)
    id_declarant: Mapped[int] = Column(Integer)

    nom_proprietaire: Mapped[str] = Column(Unicode(250))
    telephone: Mapped[str] = Column(Unicode(20))
    email: Mapped[str] = Column(Unicode(250))
    adresse: Mapped[str] = Column(Unicode(250))
    s_code_postal: Mapped[str] = Column(Unicode(10))
    s_commune_proprietaire: Mapped[str] = Column(Unicode(100))

    id_nomenclature_proprietaire_type: Mapped[int] = Column(
        Integer, ForeignKey("ref_nomenclatures.t_nomenclatures.id_nomenclature")
    )


@serializable
class TForet(CustomModel):
    """
    modele foret
    """

    __tablename__ = "t_forets"
    __table_args__ = {"schema": "oeasc_forets", "extend_existing": True}

    id_foret: Mapped[int] = Column(Integer, primary_key=True)

    id_proprietaire: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_forets.t_proprietaires.id_proprietaire")
    )

    b_statut_public: Mapped[bool] = Column(Boolean)
    b_document: Mapped[bool] = Column(Boolean)

    nom_foret: Mapped[str] = Column(Unicode(250))
    code_foret: Mapped[str] = Column(Unicode(250))
    label_foret: Mapped[str] = Column(Unicode(250))

    surface_calculee: Mapped[float] = Column(Float)
    surface_renseignee: Mapped[float] = Column(Float)

    nom_proprietaire: Mapped[str] = Column(Unicode(255), nullable=True)
    adresse_proprietaire: Mapped[str] = Column(Unicode(255), nullable=True)
    cp_proprietaire: Mapped[str] = Column(Unicode(5), nullable=True)
    commune_proprietaire: Mapped[str] = Column(Unicode(255), nullable=True)
    email_proprietaire: Mapped[str] = Column(Unicode(255), nullable=True)
    tel_proprietaire: Mapped[str] = Column(Unicode(255), nullable=True)
    id_nomenclature_proprietaire_type: Mapped[int] = Column(Integer, nullable=True)
    id_declarant: Mapped[int] = Column(Integer, nullable=True)

    areas_foret: Mapped[list[CorAreasForet]] = relationship(
        "CorAreasForet", cascade="save-update, merge, delete, delete-orphan"
    )
