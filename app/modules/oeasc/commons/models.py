'''
    pour mapper la vue user de oeasc_commons
'''

from flask import current_app

from utils_flask_sqla.serializers import serializable

config = current_app.config
DB = config['DB']


@serializable
class TSecteurs(DB.Model):
    __tablename__ = 't_secteurs'
    __table_args__ = {'schema': 'oeasc_commons', 'extend_existing': True}

    id_secteur = DB.Column(DB.Integer, primary_key=True)
    code_secteur = DB.Column(DB.String(250))
    nom_secteur = DB.Column(DB.Text)


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
