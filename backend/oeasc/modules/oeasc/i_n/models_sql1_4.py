"""
IN models
"""

from flask import current_app

from sqlalchemy import Table, Column, Integer, Unicode, Boolean, Date, ForeignKey
from sqlalchemy import and_, select, func, case
from sqlalchemy.orm import relationship, column_property
from utils_flask_sqla.serializers import serializable
from ..commons.models import TSecteurs, TEspeces


config = current_app.config
DB = config["DB"]


# les class heritent de CustomModel plutôt que de DB.Model pour ajouter allow_unmapped pour la migration vers sqlalchemy 2.0
# Cela permet de ne pas générer d'erreur avec l'ancienne manière de déclarer les models.
# Une fois la migration en 2.0 terminée il faudra réécrire les models en utilisant Mapped (cette fonction n'est pas dispo dans la 1.4)
class CustomModel(DB.Model):
    __abstract__ = True  # evite que la classe soit considérée comme une table
    __allow_unmapped__ = True


@serializable
class TObservers(CustomModel):
    """
    Tags for circuits
    """

    __tablename__ = "t_observers"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}

    id_observer = Column(Integer, primary_key=True)
    nom_observer = Column(Unicode)


cor_realisation_observer = Table(
    "cor_realisation_observer",
    DB.metadata,
    Column(
        "id_observer",
        Integer,
        ForeignKey("oeasc_in.t_observers.id_observer"),
        primary_key=True,
    ),
    Column(
        "id_realisation",
        Integer,
        ForeignKey("oeasc_in.t_realisations.id_realisation"),
        primary_key=True,
    ),
    extend_existing=True,
    schema="oeasc_in",
)


@serializable
class TCircuits(CustomModel):
    """
    Circuits for IN
    """

    __tablename__ = "t_circuits"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}

    id_circuit = Column(Integer, primary_key=True)
    nom_circuit = Column(Unicode)
    numero_circuit = Column(Integer)
    km = Column(Integer)
    id_secteur = Column(Integer, ForeignKey("oeasc_commons.t_secteurs.id_secteur"))
    actif = Column(Boolean, default=True)
    secteur = relationship(TSecteurs, back_populates="circuits")


@serializable
class TObservations(CustomModel):
    """
    Observation for In
    espece
    nb (individus)
    """

    __tablename__ = "t_observations"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}

    id_observation = Column(Integer, primary_key=True)
    id_realisation = Column(
        Integer, ForeignKey("oeasc_in.t_realisations.id_realisation")
    )
    id_espece = Column(Integer, ForeignKey("oeasc_commons.t_especes.id_espece"))
    espece = relationship(TEspeces, lazy="joined")
    nb = Column(Integer)


@serializable
class TTags(CustomModel):
    """
    Tags for circuits
    """

    __tablename__ = "t_tags"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}
    id_tag = Column(Integer, primary_key=True)
    nom_tag = Column(Unicode)
    code_tag = Column(Unicode)


@serializable
class CorRealisationTag(CustomModel):
    """
    Cor Realisation Tag
    """

    __tablename__ = "cor_realisation_tag"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}

    id_tag = Column(
        Integer,
        ForeignKey("oeasc_in.t_tags.id_tag"),
        primary_key=True,
    )
    id_realisation = Column(
        Integer,
        ForeignKey("oeasc_in.t_realisations.id_realisation"),
        primary_key=True,
    )
    valid = Column(Boolean)

    tag = relationship(TTags, lazy="joined")


@serializable
class CorRealisationObserver(CustomModel):
    """
    Cor Realisation Observer
    """

    __tablename__ = "cor_realisation_observer"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}

    id_observer = Column(
        Integer,
        ForeignKey("oeasc_in.t_observers.id_observer"),
        primary_key=True,
    )
    id_realisation = Column(
        Integer,
        ForeignKey("oeasc_in.t_realisations.id_realisation"),
        primary_key=True,
    )


@serializable
class TRealisations(CustomModel):
    """
    Realisation of a circuit
    """

    __tablename__ = "t_realisations"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}

    id_realisation = Column(Integer, primary_key=True)
    id_circuit = Column(Integer, ForeignKey("oeasc_in.t_circuits.id_circuit"))
    serie = Column(Integer)
    groupes = Column(Integer)

    vent = Column(Unicode)
    temps = Column(Unicode)
    temperature = Column(Unicode)
    date_realisation = Column(Date)

    secteur = relationship(
        TSecteurs,
        secondary="oeasc_in.t_circuits",
        primaryjoin="TRealisations.id_circuit == TCircuits.id_circuit",
        secondaryjoin="TCircuits.id_secteur == TSecteurs.id_secteur",
        uselist=False, 
        back_populates="realisations",
        # overlaps="circuit, secteur",
        # viewonly=True,
    )

    circuit = relationship(TCircuits, lazy="joined")

    observations = relationship(
        TObservations,
        cascade="save-update, merge, delete, delete-orphan",
        lazy="joined",
    )

    observers = relationship(
        TObservers,
        secondary=cor_realisation_observer,
        lazy="joined",
    )

    tags = relationship(
        CorRealisationTag,
        cascade="save-update, merge, delete, delete-orphan",
        lazy="joined",
    )

    observers_table = column_property(
        select(func.string_agg(TObservers.nom_observer, ", "))
        .where(
            and_(
                TObservers.id_observer == CorRealisationObserver.id_observer,
                id_realisation == CorRealisationObserver.id_observer,
            )
        )
        .scalar_subquery()
    )

    tags_table = column_property(
        select(
            func.string_agg(
                func.concat(
                    TTags.nom_tag,
                    " : ",
                    case((CorRealisationTag.valid == True, "o"), else_="x"),
                ),
                ", ",
            )
        )
        .where(
            and_(
                CorRealisationTag.id_realisation == id_realisation,
                CorRealisationTag.id_tag == TTags.id_tag,
            )
        )
        .scalar_subquery()
    )

    cerfs = column_property(
        select(TObservations.nb)
        .where(
            and_(
                TObservations.id_realisation == id_realisation,
                TObservations.id_espece == TEspeces.id_espece,
                TEspeces.nom_espece == "Cerf",
            )
        )
        .scalar_subquery()
    )

    lievres = column_property(
        select(TObservations.nb)
        .where(
            and_(
                TObservations.id_realisation == id_realisation,
                TObservations.id_espece == TEspeces.id_espece,
                TEspeces.nom_espece == "Lièvre",
            )
        )
        .scalar_subquery()
    )

    chevreuils = column_property(
        select(TObservations.nb)
        .where(
            and_(
                TObservations.id_realisation == id_realisation,
                TObservations.id_espece == TEspeces.id_espece,
                TEspeces.nom_espece == "Chevreuil",
            )
        )
        .scalar_subquery()
    )

    renards = column_property(
        select(TObservations.nb)
        .where(
            and_(
                TObservations.id_realisation == id_realisation,
                TObservations.id_espece == TEspeces.id_espece,
                TEspeces.nom_espece == "Renard",
            )
        )
        .scalar_subquery()
    )
