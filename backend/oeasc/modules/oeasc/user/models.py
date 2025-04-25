"""
    pour mapper la vue user de oeasc_commons
"""

from flask import current_app
from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB
from utils_flask_sqla.serializers import serializable
from sqlalchemy.orm import declarative_base

config = current_app.config
DB = config["DB"]

# les class heritent de CustomModel plutôt que de DB.Model pour ajouter allow_unmapped pour la migration vers sqlalchemy 2.0
# Cela permet de ne pas générer d'erreur avec l'ancienne manière de déclarer les models.
# Une fois la migration en 2.0 terminée il faudra réécrire les models en utilisant Mapped (cette fonction n'est pas dispo dans la 1.4)
class CustomModel(DB.Model):
    __abstract__ = True # evite que la classe soit considérée comme une table
    __allow_unmapped__ = True

@serializable
class VUsers(CustomModel):
    """
    modeles proprietaires
    """

    __tablename__ = "v_users"
    __table_args__ = {"schema": "oeasc_commons", "extend_existing": True}

    id_role = Column(Integer, primary_key=True)
    identifiant = Column(String(250))
    email = Column(String(250))
    desc_role = Column(String(250))
    nom_complet = Column(String(250))
    nom_role = Column(String(250))
    prenom_role = Column(String(250))
    organisme = Column(String(250))
    autre_organisme = Column(String(250))
    id_organisme = Column(Integer)
    accept_email = Column(JSONB)
    create_date = Column(String(250))
    nb_declarations = Column(Integer)
    id_droit_max = Column(Integer)
    org_mnemo = Column(String(250))
