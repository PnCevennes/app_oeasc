"""
IN models
"""

from flask import current_app

from sqlalchemy import Table, Column, Integer, Unicode, Boolean, Date, ForeignKey, Float
from sqlalchemy import and_, select, func, case
from sqlalchemy.orm import relationship, column_property, Mapped
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
    Observers for IN
    """

    __tablename__ = "t_observers"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}

    id_observer: Mapped[int] = Column(Integer, primary_key=True)
    nom_observer: Mapped[str] = Column(Unicode)


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

    id_circuit: Mapped[int] = Column(Integer, primary_key=True)
    nom_circuit: Mapped[str] = Column(Unicode)
    numero_circuit: Mapped[int] = Column(Integer)
    km: Mapped[int] = Column(Integer)
    id_secteur: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_commons.t_secteurs.id_secteur")
    )
    actif: Mapped[bool] = Column(Boolean, default=True)
    secteur: Mapped["TSecteurs"] = relationship(
        TSecteurs,
        back_populates="circuits",
    )
    in_coeur: Mapped[bool] = Column(Boolean, default=True)


# pour éviter une boucle d'importation avec le modele I_N, il faut déclarer cette relation après la définition des classe et depuis ce model
TSecteurs.circuits = relationship(
    "TCircuits", back_populates="secteur", overlaps="secteur", cascade_backrefs=False
)


@serializable
class TObservations(CustomModel):
    """
    Observation for In
    espece
    nb (individus)
    """

    __tablename__ = "t_observations"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}

    id_observation: Mapped[int] = Column(Integer, primary_key=True)
    id_realisation: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_in.t_realisations.id_realisation")
    )
    id_espece: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_commons.t_especes.id_espece")
    )
    espece: Mapped["TEspeces"] = relationship(TEspeces, lazy="joined")
    nb: Mapped[int] = Column(Integer)


@serializable
class CorRealisationObserver(CustomModel):
    """
    Cor Realisation Observer
    """

    __tablename__ = "cor_realisation_observer"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}

    id_observer: Mapped[int] = Column(
        Integer,
        ForeignKey("oeasc_in.t_observers.id_observer"),
        primary_key=True,
    )
    id_realisation: Mapped[int] = Column(
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

    id_realisation: Mapped[int] = Column(Integer, primary_key=True)
    id_circuit: Mapped[int] = Column(
        Integer, ForeignKey("oeasc_in.t_circuits.id_circuit")
    )
    valide_coeur: Mapped[bool] = Column(Boolean, default=True)
    valide_all: Mapped[bool] = Column(Boolean, default=True)
    serie: Mapped[int] = Column(Integer)
    groupes: Mapped[int] = Column(Integer)
    vent: Mapped[str] = Column(Unicode)
    temps: Mapped[str] = Column(Unicode)
    temperature: Mapped[str] = Column(Unicode)
    date_realisation: Mapped[Date] = Column(Date)
    

    circuit: Mapped["TCircuits"] = relationship(
        TCircuits, lazy="joined", overlaps="circuit, secteur"
    )
    observations: Mapped[list["TObservations"]] = relationship(
        TObservations,
        cascade="save-update, merge, delete, delete-orphan",
        lazy="joined",
    )
    observers: Mapped[list["TObservers"]] = relationship(
        TObservers,
        secondary=cor_realisation_observer,
        lazy="joined",
    )
    
    
    observers_table: Mapped[str] = column_property(
        select(func.string_agg(TObservers.nom_observer, ", "))
        .where(
            and_(
                TObservers.id_observer == CorRealisationObserver.id_observer,
                id_realisation == CorRealisationObserver.id_realisation,
            )
        )
        .scalar_subquery()
    )
    # tags_table: Mapped[str] = column_property(
    #     select(
    #         func.string_agg(
    #             func.concat(
    #                 TTagsIn.nom_tag,
    #                 " : ",
    #                 case((CorRealisationTag.valid == True, "o"), else_="x"),
    #             ),
    #             ", ",
    #         )
    #     )
    #     .where(
    #         and_(
    #             CorRealisationTag.id_realisation == id_realisation,
    #             CorRealisationTag.id_tag == TTagsIn.id_tag,
    #         )
    #     )
    #     .scalar_subquery()
    # )
    cerfs: Mapped[int] = column_property(
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
    lievres: Mapped[int] = column_property(
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
    chevreuils: Mapped[int] = column_property(
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
    renards: Mapped[int] = column_property(
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

