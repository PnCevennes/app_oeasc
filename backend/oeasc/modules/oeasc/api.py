"""
api fonctionalite utilisée dans l'OEASC
"""

from flask import Blueprint, current_app

from oeasc.modules.oeasc.nomenclature import nomenclature_oeasc
from utils_flask_sqla.response import json_resp

# from .repository import get_db

config = current_app.config
DB = config["DB"]

bp = Blueprint("oeasc_api", __name__)


@bp.route("nomenclatures", methods=["GET"])
@json_resp
def get_nomenclature_oeasc():
    """
    Retourne un dictionnaire contenant toutes les nomenclatures concernant l'OEASC.

    Cette fonction est utilisée lorsqu'on souhaite obtenir l'ensemble des nomenclatures
    disponibles pour l'application OEASC. Elle est généralement appelée lors de l'initialisation
    de l'interface utilisateur ou lorsqu'on a besoin d'afficher toutes les options possibles
    pour un formulaire ou une sélection.

    Retour:
        dict: Un dictionnaire contenant toutes les nomenclatures.
    """
    return nomenclature_oeasc()


@bp.route("nomenclatures/<string:nomenclature_type>", methods=["GET"])
@json_resp
def get_nomenclature(nomenclature_type):
    """
    Retourne un dictionnaire contenant les nomenclatures pour un type choisi.

    Cette fonction permet d'obtenir uniquement les valeurs d'une nomenclature spécifique,
    identifiée par le paramètre 'nomenclature_type' passé dans l'URL. Elle est utile lorsque
    l'on souhaite afficher ou utiliser les options d'une seule nomenclature, par exemple pour
    remplir un champ de sélection dans un formulaire ou filtrer des données selon un type précis.

    Args:
        nomenclature_type (str): Le type de nomenclature à récupérer.

    Retour:
        list | dict: Les valeurs associées à la nomenclature demandée.
    """

    # On récupère toutes les nomenclatures, puis on sélectionne celle correspondant au type demandé
    # et on retourne uniquement ses valeurs.
    return nomenclature_oeasc().get(nomenclature_type).get("values")
