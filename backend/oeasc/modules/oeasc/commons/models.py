"""
    pour mapper la vue user de oeasc_commons
"""

from flask import current_app

from sqlalchemy.orm import column_property
from sqlalchemy import select, String
from utils_flask_sqla.serializers import serializable
# from sqlalchemy.ext.hybrid import hybrid_property

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
    __abstract__ = True # evite que la classe soit considérée comme une table
    __allow_unmapped__ = True



cor_content_tag = DB.Table(
    "cor_content_tag",
    DB.Column(
        "id_content",
        DB.Integer,
        DB.ForeignKey("oeasc_commons.t_contents.id_content"),
        primary_key=True,
    ),
    DB.Column(
        "id_tag",
        DB.Integer,
        DB.ForeignKey("oeasc_commons.t_tags.id_tag"),
        primary_key=True,
    ),
    extend_existing=True,
    schema="oeasc_commons",
)


@serializable
class TTags(CustomModel):
    """
    Tags for content
    """

    __tablename__ = "t_tags"
    __table_args__ = {"schema": "oeasc_commons", "extend_existing": True}
    id_tag = DB.Column(DB.Integer, primary_key=True)
    nom_tag = DB.Column(DB.Unicode)
    code_tag = DB.Column(DB.Unicode )

# version sqlalchemy 2.0
# @serializable
# class TTags(DB.Model):
#     """Tags des page pour définir si c'est une actu, une page ou un formulaire"""
#     __tablename__ = "t_tags"
#     __table_args__ = {"schema": "oeasc_commons", "extend_existing": True}
#     id_tag: Mapped[int] = mapped_column(primary_key=True)
#     nom_tag: Mapped[str] = mapped_column(String(30))
#     code_tag: Mapped[str] = mapped_column(String(10))


@serializable
class TContents(CustomModel):
    """
    modele textes
    """

    __tablename__ = "t_contents"
    __table_args__ = {"schema": "oeasc_commons", "extend_existing": True}

    id_content = DB.Column(DB.Integer, primary_key=True)
    code = DB.Column(DB.String(250))
    md = DB.Column(DB.Text)
    meta_create_date = DB.Column(DB.DateTime)
    meta_update_date = DB.Column(DB.DateTime)

    tags = DB.relationship(TTags, secondary=cor_content_tag)



@serializable
class TSecteurs(CustomModel):
    __tablename__ = "t_secteurs"
    __table_args__ = {"schema": "oeasc_commons", "extend_existing": True}

    id_secteur = DB.Column(DB.Integer, primary_key=True)
    code_secteur = DB.Column(DB.String(250))
    nom_secteur = DB.Column(DB.Text)


@serializable
class TEspeces(CustomModel):
    """
    Especes
    """

    __tablename__ = "t_especes"
    __table_args__ = {"schema": "oeasc_commons", "extend_existing": True}

    id_espece = DB.Column(DB.Integer, primary_key=True)
    nom_espece = DB.Column(DB.Unicode)
    code_espece = DB.Column(DB.Unicode)





# Rajoute la colonne type qui filtrera que les nomenclatures qui ont un type qui est en lien avec OEASC. la liste des types requis est 
# dans nomenclature.py -> nomenclature_oeasc_types. Le filtrage se fait dans la definition de route dans api.py
# on le rajoute ici car c'est spécifique à oeasc et le modele est déclaré dans pypnnomenclature
TNomenclatures.type = column_property(
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