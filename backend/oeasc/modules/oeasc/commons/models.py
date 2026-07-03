"""
pour mapper la vue user de oeasc_commons
"""

from flask import current_app

from sqlalchemy.orm import column_property, relationship, Mapped

from utils_flask_sqla.serializers import serializable
from sqlalchemy import (
    Column,
    Table,
    Integer,
    Unicode,
    DateTime,
    ForeignKey,
    func,
    select,
    String,
)

from pypnnomenclature.models import BibNomenclaturesTypes, TNomenclatures

# pour sqlalchemy 2.0
# from sqlalchemy.orm import Mapped
# from sqlalchemy.orm import mapped_column


config = current_app.config
DB = config["DB"]


# les class heritent de CustomModel plutôt que de DB.Model pour ajouter allow_unmapped pour la migration vers sqlalchemy 2.0
# Cela permet de ne pas générer d'erreur avec l'ancienne manière de déclarer les models.
# Une fois la migration en 2.0 terminée il faudra réécrire les models en utilisant Mapped (cette fonction n'est pas dispo dans la 1.4)
class CustomModel(DB.Model):
    __abstract__ = True  # evite que la classe soit considérée comme une table
    __allow_unmapped__ = True


cor_content_tag = Table(
    "cor_content_tag",
    DB.metadata,
    Column(
        "id_content",
        Integer,
        ForeignKey("oeasc_commons.t_contents.id_content"),
        primary_key=True,
    ),
    Column(
        "id_tag",
        Integer,
        ForeignKey("oeasc_commons.t_tags.id_tag"),
        primary_key=True,
    ),
    schema="oeasc_commons",
    extend_existing=True,
)


@serializable
class TTags(CustomModel):
    """
    Tags for content
    """

    __tablename__ = "t_tags"
    __table_args__ = {"schema": "oeasc_commons", "extend_existing": True}

    id_tag: Mapped[int] = Column(Integer, primary_key=True)
    nom_tag: Mapped[str] = Column(Unicode(30))
    code_tag: Mapped[str] = Column(Unicode(10))


@serializable
class TListeOrganismes(CustomModel):
    """
    Liste des organismes de l'oeasc
    """

    __tablename__ = "t_liste_organismes"
    __table_args__ = {"schema": "oeasc_commons", "extend_existing": True}

    id_organisme: Mapped[int] = Column(Integer, primary_key=True)


@serializable
class TContents(CustomModel):
    """
    modele textes
    """

    __tablename__ = "t_contents"
    __table_args__ = {"schema": "oeasc_commons", "extend_existing": True}

    id_content: Mapped[int] = Column(Integer, primary_key=True)
    code: Mapped[str] = Column(String(250))
    md: Mapped[str] = Column(Unicode)
    meta_create_date: Mapped[DateTime] = Column(DateTime, default=func.now())
    meta_update_date: Mapped[DateTime] = Column(
        DateTime, default=func.now(), onupdate=func.now()
    )

    tags: Mapped[list["TTags"]] = relationship(
        "oeasc.modules.oeasc.commons.models.TTags", secondary=cor_content_tag
    )


@serializable
class TSecteurs(CustomModel):
    __tablename__ = "t_secteurs"
    __table_args__ = {"schema": "oeasc_commons", "extend_existing": True}

    id_secteur: Mapped[int] = Column(Integer, primary_key=True)
    code_secteur: Mapped[str] = Column(String(250))
    nom_secteur: Mapped[str] = Column(Unicode)


@serializable
class TEspeces(CustomModel):
    """
    Especes
    """

    __tablename__ = "t_especes"
    __table_args__ = {"schema": "oeasc_commons", "extend_existing": True}

    id_espece: Mapped[int] = Column(Integer, primary_key=True)
    nom_espece: Mapped[str] = Column(Unicode)
    code_espece: Mapped[str] = Column(String(250))
    cd_nom: Mapped[str] = Column(String(250))


class TCommunesFrance(CustomModel):
    """
    communes. Uniquement utilisé pour les adresse des propiétaires de forets.
    """

    __tablename__ = "t_communes"
    __table_args__ = {"schema": "oeasc_commons", "extend_existing": True}

    code: Mapped[str] = Column(String(6), primary_key=True)
    nom: Mapped[str] = Column(Unicode)
    cp: Mapped[str] = Column(String(5))
    population: Mapped[int] = Column(Integer)


# Rajoute la colonne type qui filtrera que les nomenclatures qui ont un type qui est en lien avec OEASC. la liste des types requis est
# dans nomenclature.py -> nomenclature_oeasc_types. Le filtrage se fait dans la definition de route dans api.py
# on le rajoute ici car c'est spécifique à oeasc et le modele est déclaré dans pypnnomenclature


class TNomenclaturesOeasc(TNomenclatures):
    """
    Nomenclature
    """

    type = column_property(
        select(BibNomenclaturesTypes.mnemonique)
        .where(BibNomenclaturesTypes.id_type == TNomenclatures.id_type)
        .correlate_except(BibNomenclaturesTypes)
        .scalar_subquery()
    )


# Supprimé car le modele est déja défini dans le module nomenclature. Surement il est apparue dans une mise à jour
# @serializable
# class BibNomenclaturesTypes(CustomModel):
#     """
#     Nomenclature type
#     """

#     __tablename__ = "bib_nomenclatures_types"
#     __table_args__ = {"schema": "ref_nomenclatures", "extend_existing": True}

#     id_type = DB.Column(DB.Integer, primary_key=True)
#     mnemonique = DB.Column(DB.Unicode)
#     label_fr = DB.Column(DB.Unicode)
#     definition_fr = DB.Column(DB.Unicode)
