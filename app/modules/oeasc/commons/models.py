'''
    pour mapper la vue user de oeasc_commons
'''

from flask import current_app

from sqlalchemy.orm import column_property
from sqlalchemy import select
from utils_flask_sqla.serializers import serializable

config = current_app.config
DB = config['DB']


cor_content_tag = DB.Table(
    "cor_content_tag",
    DB.Column(
        'id_content',
        DB.Integer,
        DB.ForeignKey('oeasc_commons.t_contents.id_content'),
        primary_key=True
    ),
    DB.Column(
        'id_tag',
        DB.Integer,
        DB.ForeignKey('oeasc_commons.t_tags.id_tag'),
        primary_key=True
    ),

    extend_existing=True,
    schema='oeasc_commons'

)


@serializable
class TTags(DB.Model):
    '''
        Tags for content
    '''

    __tablename__ = 't_tags'
    __table_args__ = {'schema': 'oeasc_commons', 'extend_existing': True}
    id_tag = DB.Column(DB.Integer, primary_key=True)
    nom_tag = DB.Column(DB.Unicode)
    code_tag = DB.Column(DB.Unicode)


@serializable
class TContents(DB.Model):
    '''
        modele textes
    '''
    __tablename__ = 't_contents'
    __table_args__ = {'schema': 'oeasc_commons', 'extend_existing': True}

    id_content = DB.Column(DB.Integer, primary_key=True)
    code = DB.Column(DB.String(250))
    md = DB.Column(DB.Text)
    meta_create_date = DB.Column(DB.DateTime)
    meta_update_date = DB.Column(DB.DateTime)

    tags = DB.relationship(
        TTags,
        secondary=cor_content_tag
    )

@serializable
class TSecteurs(DB.Model):
    __tablename__ = 't_secteurs'
    __table_args__ = {'schema': 'oeasc_commons', 'extend_existing': True}

    id_secteur = DB.Column(DB.Integer, primary_key=True)
    code_secteur = DB.Column(DB.String(250))
    nom_secteur = DB.Column(DB.Text)


@serializable
class TEspeces(DB.Model):
    '''
        Especes
    '''
    __tablename__ = 't_especes'
    __table_args__ = {'schema': 'oeasc_commons', 'extend_existing': True}

    id_espece = DB.Column(DB.Integer, primary_key=True)
    nom_espece = DB.Column(DB.Unicode)
    code_espece = DB.Column(DB.Unicode)



@serializable
class BibNomenclaturesTypes(DB.Model):
    '''
        Nomenclature type
    '''
    __tablename__ = 'bib_nomenclatures_types'
    __table_args__ = {'schema': 'ref_nomenclatures', 'extend_existing': True}

    id_type = DB.Column(DB.Integer, primary_key=True)
    mnemonique = DB.Column(DB.Unicode)
    label_fr = DB.Column(DB.Unicode)
    definition_fr = DB.Column(DB.Unicode)

@serializable
class TNomenclatures(DB.Model):
    '''
        Nomenclature
    '''
    __tablename__ = 't_nomenclatures'
    __table_args__ = {'schema': 'ref_nomenclatures', 'extend_existing': True}

    id_nomenclature = DB.Column(DB.Integer, primary_key=True)
    cd_nomenclature = DB.Column(DB.Unicode)
    mnemonique = DB.Column(DB.Unicode)
    label_fr = DB.Column(DB.Unicode)
    definition_fr = DB.Column(DB.Unicode)
    id_type = DB.Column(DB.Integer, DB.ForeignKey('ref_nomenclatures.bib_nomenclatures_types.id_type'))

    type = column_property(
        select([BibNomenclaturesTypes.mnemonique]).\
            where(BibNomenclaturesTypes.id_type == id_type)
    )

