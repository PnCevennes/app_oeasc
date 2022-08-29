"""
    IN models
"""
from flask import current_app

from sqlalchemy import and_, select, func, literal_column
from sqlalchemy.orm import aliased
from sqlalchemy.ext.declarative import ConcreteBase
from sqlalchemy.sql.expression import case

from utils_flask_sqla.serializers import serializable

from ..commons.models import TSecteurs, TEspeces
from sqlalchemy.orm import column_property


config = current_app.config
DB = config["DB"]


@serializable
class TObservers(DB.Model):
    """
    Tags for circuits
    """

    __tablename__ = "t_observers"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}

    id_observer = DB.Column(DB.Integer, primary_key=True)
    nom_observer = DB.Column(DB.Unicode)


cor_realisation_observer = DB.Table(
    "cor_realisation_observer",
    DB.Column(
        "id_observer",
        DB.Integer,
        DB.ForeignKey("oeasc_in.t_observers.id_observer"),
        primary_key=True,
    ),
    DB.Column(
        "id_realisation",
        DB.Integer,
        DB.ForeignKey("oeasc_in.t_realisations.id_realisation"),
        primary_key=True,
    ),
    extend_existing=True,
    schema="oeasc_in",
)


@serializable
class TCircuits(DB.Model):
    """
    Circuits for IN
    """

    __tablename__ = "t_circuits"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}

    id_circuit = DB.Column(DB.Integer, primary_key=True)
    nom_circuit = DB.Column(DB.Unicode)
    numero_circuit = DB.Column(DB.Integer)
    km = DB.Column(DB.Integer)
    id_secteur = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_commons.t_secteurs.id_secteur")
    )
    actif = DB.Column(DB.Boolean, default=True)
    secteur = DB.relationship(TSecteurs)


@serializable
class TObservations(DB.Model):
    """
    Observation for In
    espece
    nb (individus)
    """

    __tablename__ = "t_observations"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}

    id_observation = DB.Column(DB.Integer, primary_key=True)
    id_realisation = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_in.t_realisations.id_realisation")
    )
    id_espece = DB.Column(
        DB.Integer, DB.ForeignKey("oeasc_commons.t_especes.id_espece")
    )
    espece = DB.relationship(TEspeces, lazy="joined")
    nb = DB.Column(DB.Integer)


@serializable
class TTags(DB.Model):
    """
    Tags for circuits
    """

    __tablename__ = "t_tags"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}
    id_tag = DB.Column(DB.Integer, primary_key=True)
    nom_tag = DB.Column(DB.Unicode)
    code_tag = DB.Column(DB.Unicode)


@serializable
class CorRealisationTag(DB.Model):
    """
    Cor Realisation Tag
    """

    __tablename__ = "cor_realisation_tag"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}

    id_tag = DB.Column(
        DB.Integer,
        DB.ForeignKey("oeasc_in.t_tags.id_tag"),
        primary_key=True,
    )
    id_realisation = DB.Column(
        DB.Integer,
        DB.ForeignKey(
            "oeasc_in.t_realisations.id_realisation"
        ),  # POURQUOI CA MARCHE PAS ????????????
        primary_key=True,
    )
    valid = DB.Column(DB.Boolean)

    tag = DB.relationship(TTags, lazy="joined")


@serializable
class CorRealisationObserver(DB.Model):
    """
    Cor Realisation Observer
    """

    __tablename__ = "cor_realisation_observer"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}

    id_observer = DB.Column(
        DB.Integer,
        DB.ForeignKey("oeasc_in.t_observers.id_observer"),
        primary_key=True,
    )
    id_realisation = DB.Column(
        DB.Integer,
        DB.ForeignKey(
            "oeasc_in.t_realisations.id_realisation"
        ),  # POURQUOI CA MARCHE PAS ????????????
        primary_key=True,
    )


@serializable
class TRealisations(DB.Model):
    """
    Realisation of a circuit
    """

    __tablename__ = "t_realisations"
    __table_args__ = {"schema": "oeasc_in", "extend_existing": True}

    id_realisation = DB.Column(DB.Integer, primary_key=True)
    id_circuit = DB.Column(DB.Integer, DB.ForeignKey("oeasc_in.t_circuits.id_circuit"))
    serie = DB.Column(DB.Integer)
    groupes = DB.Column(DB.Integer)

    vent = DB.Column(DB.Unicode)
    temps = DB.Column(DB.Unicode)
    temperature = DB.Column(DB.Unicode)
    date_realisation = DB.Column(DB.Date)

    secteur = DB.relationship(
        TSecteurs,
        secondary="oeasc_in.t_circuits",
        primaryjoin="TRealisations.id_circuit == TCircuits.id_circuit",
        secondaryjoin="TCircuits.id_secteur == TSecteurs.id_secteur",
        uselist=False,
    )

    circuit = DB.relationship(TCircuits, lazy="joined")

    observations = DB.relationship(
        TObservations,
        cascade="save-update, merge, delete, delete-orphan",
        lazy="joined",
    )

    observers = DB.relationship(
        TObservers,
        secondary=cor_realisation_observer,
        lazy="joined",
    )

    tags = DB.relationship(
        CorRealisationTag,
        cascade="save-update, merge, delete, delete-orphan",
        lazy="joined",
    )

    observers_table = column_property(
        select([func.string_agg(TObservers.nom_observer, ", ")]).where(
            and_(
                TObservers.id_observer == CorRealisationObserver.id_observer,
                id_realisation == CorRealisationObserver.id_observer,
            )
        )
    )

    tags_table = column_property(
        select(
            [
                func.string_agg(
                    func.concat(
                        TTags.nom_tag,
                        " : ",
                        case([(CorRealisationTag.valid, "o")], else_="x"),
                    ),
                    ", ",
                )
            ]
        ).where(
            and_(
                CorRealisationTag.id_realisation == id_realisation,
                CorRealisationTag.id_tag == TTags.id_tag,
            )
        )
    )

    cerfs = column_property(
        select([TObservations.nb]).where(
            and_(
                TObservations.id_realisation == id_realisation,
                TObservations.id_espece == TEspeces.id_espece,
                TEspeces.nom_espece == "Cerf",
            )
        )
    )

    lievres = column_property(
        select([TObservations.nb]).where(
            and_(
                TObservations.id_realisation == id_realisation,
                TObservations.id_espece == TEspeces.id_espece,
                TEspeces.nom_espece == "Lièvre",
            )
        )
    )

    chevreuils = column_property(
        select([TObservations.nb]).where(
            and_(
                TObservations.id_realisation == id_realisation,
                TObservations.id_espece == TEspeces.id_espece,
                TEspeces.nom_espece == "Chevreuil",
            )
        )
    )

    renards = column_property(
        select([TObservations.nb]).where(
            and_(
                TObservations.id_realisation == id_realisation,
                TObservations.id_espece == TEspeces.id_espece,
                TEspeces.nom_espece == "Renard",
            )
        )
    )
