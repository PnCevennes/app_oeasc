'''
    pour mapper la vue user de oeasc_commons
'''

from flask import current_app

from app.utils.utilssqlalchemy import (
    serializable
)

config = current_app.config
DB = config['DB']


@serializable
class VUsers(DB.Model):
    '''
        modeles proprietaires
    '''
    __tablename__ = 'v_users'
    __table_args__ = {'schema': 'oeasc_commons', 'extend_existing': True}

    id_role = DB.Column(DB.Integer, primary_key=True)
    identifiant = DB.Column(DB.String(250))
    email = DB.Column(DB.String(250))
    desc_role = DB.Column(DB.String(250))
    nom_complet = DB.Column(DB.String(250))
    nom_role = DB.Column(DB.String(250))
    prenom_role = DB.Column(DB.String(250))
    organisme = DB.Column(DB.String(250))
    create_date = DB.Column(DB.String(250))
    nb_declarations = DB.Column(DB.Integer)
    id_droit_max = DB.Column(DB.Integer)