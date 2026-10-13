"""
modele dégâts agricoles (schéma oeasc_agricole)
"""

from utils_flask_sqla.serializers import serializable
from sqlalchemy.orm import relationship, Mapped
from sqlalchemy import (
    Column,
    Integer,
    Unicode,
    String,
    Boolean,
    Date,
    Numeric,
    ForeignKey,
)

from ..commons.models import CustomModel, TEspeces
from oeasc.ref_geo_oeasc.models import TCommunesArea


@serializable
class TSaisonAgricole(CustomModel):
    """
    Saison (« campagne comptable ») : du 1er juillet au 30 juin.
    """

    __tablename__ = "t_saison_agricole"
    __table_args__ = {"schema": "oeasc_agricole", "extend_existing": True}

    id_saison: Mapped[int] = Column(Integer, primary_key=True)
    nom_saison: Mapped[str] = Column(Unicode)
    date_debut: Mapped[Date] = Column(Date)
    date_fin: Mapped[Date] = Column(Date)
    current: Mapped[bool] = Column(Boolean, default=False)


@serializable
class TTypeCulture(CustomModel):
    """Catégorie de cultures (CEREALES, PRAIRIES, FRUITS ET LEGUMES...)."""

    __tablename__ = "t_type_culture"
    __table_args__ = {"schema": "oeasc_agricole", "extend_existing": True}

    id_type_culture: Mapped[int] = Column(Integer, primary_key=True)
    nom_type_culture: Mapped[str] = Column(Unicode)


@serializable
class TCulture(CustomModel):
    """Culture telle que nommée dans le fichier importé (ex. PRAIRIES
    TEMPORAIRES), rattachée à un type de culture (PRAIRIES)."""

    __tablename__ = "t_cultures"
    __table_args__ = {"schema": "oeasc_agricole", "extend_existing": True}

    id_culture: Mapped[int] = Column(Integer, primary_key=True)
    nom_culture: Mapped[str] = Column(Unicode)
    id_type_culture: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_agricole.t_type_culture.id_type_culture")
    )
    type_culture: Mapped["TTypeCulture"] = relationship(
        TTypeCulture, foreign_keys=id_type_culture
    )


@serializable
class TUgAgricole(CustomModel):
    """Unité de gestion agricole (colonne « Secteur » du fichier importé)."""

    __tablename__ = "t_ug_agricole"
    __table_args__ = {"schema": "oeasc_agricole", "extend_existing": True}

    id_ug_agricole: Mapped[int] = Column(Integer, primary_key=True)
    nom_ug_agricole: Mapped[str] = Column(Unicode)
    in_oeasc: Mapped[bool] = Column(Boolean, default=False)


@serializable
class TDeclarationAgricole(CustomModel):
    """
    Déclaration de dégât agricole indemnisée. Un dossier (numero_dossier, par
    saison) regroupe plusieurs déclarations.
    """

    __tablename__ = "t_declaration_agricole"
    __table_args__ = {"schema": "oeasc_agricole", "extend_existing": True}

    id_declaration: Mapped[int] = Column(Integer, primary_key=True)
    id_saison: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_agricole.t_saison_agricole.id_saison")
    )
    saison: Mapped["TSaisonAgricole"] = relationship(
        TSaisonAgricole, foreign_keys=id_saison
    )
    date_creation: Mapped[Date] = Column(Date)
    numero_dossier: Mapped[str] = Column(String(50))
    date_document: Mapped[Date] = Column(Date)

    # pas de contrainte FK en base vers ref_geo.communes_aoa (table vidée puis
    # rechargée par `flask refresh-ref-geo`) : la jointure est décrite ici.
    id_commune: Mapped[str] = Column(String(25))
    commune: Mapped["TCommunesArea"] = relationship(
        TCommunesArea,
        primaryjoin=lambda: TDeclarationAgricole.id_commune == TCommunesArea.id,
        foreign_keys=id_commune,
    )

    id_culture: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_agricole.t_cultures.id_culture")
    )
    culture: Mapped["TCulture"] = relationship(TCulture, foreign_keys=id_culture)
    id_ug_agricole: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_agricole.t_ug_agricole.id_ug_agricole")
    )
    ug_agricole: Mapped["TUgAgricole"] = relationship(
        TUgAgricole, foreign_keys=id_ug_agricole
    )
    surface_detruite: Mapped[float] = Column(Numeric(12, 4))
    volume_detruit: Mapped[float] = Column(Numeric(12, 4))
    unit_quantite_detruite: Mapped[str] = Column(String(50))
    pourcentage: Mapped[float] = Column(Numeric(6, 2))
    id_espece: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_commons.t_especes.id_espece")
    )
    espece: Mapped["TEspeces"] = relationship(TEspeces, foreign_keys=id_espece)
    montant_paye: Mapped[float] = Column(Numeric(12, 2))
    surface_ressemis: Mapped[float] = Column(Numeric(12, 4))
    montant_paye_ressemis: Mapped[float] = Column(Numeric(12, 2))
    montant_total_paye: Mapped[float] = Column(Numeric(12, 2))
