"""api pour les indices nocturnes"""

from flask import Blueprint, current_app, request
from utils_flask_sqla.response import json_resp
from sqlalchemy import update
from oeasc.modules.oeasc.user.utils import check_auth_redirect_login

from .repository import in_data

from .models import (
    TRealisations,
    TCircuits,
    TObservers,
    CorRealisationObserver,
)

from .schema import (
    TRealisationsSchema,
    TCircuitsSchema,
    TObserversSchema,
    CorRealisationObserverSchema,
)

from ..generic.definitions import GenericRouteDefinitions

grd = GenericRouteDefinitions()


bp = Blueprint("in_api", __name__)

config = current_app.config
DB = config["DB"]

definitions = {
    "realisation": {
        "model": TRealisations,
        "droits": {"C": 5, "R": 0, "U": 5, "D": 5},
        "schema": TRealisationsSchema,
    },
    "circuit": {
        "model": TCircuits,
        "droits": {"C": 5, "R": 0, "U": 5, "D": 5},
        "schema": TCircuitsSchema,
    },
    "observer": {
        "model": TObservers,
        "droits": {"C": 5, "R": 0, "U": 5, "D": 5},
        "schema": TObserversSchema,
    },
    "cor_realisation_observer": {
        "model": CorRealisationObserver,
        "droits": {"C": 5, "R": 0, "U": 5, "D": 5},
        "schema": CorRealisationObserverSchema,
    },
}

grd.add_generic_routes("in", definitions)


@bp.route("results", methods=["GET"])
@json_resp
def in_results():
    """
    renvoie les résultats des in pour faire les graphs (IN, variance, ug, année)
    """
    out = in_data()

    return out


@bp.route("test/results", methods=["GET"])
@json_resp
def in_test_results():
    """
    renvoie les résultats des in pour faire les graphs (IN, variance, ug, année)
    """

    return in_data()


@bp.route("valid_realisation", methods=["PATCH"])
@check_auth_redirect_login(5)
@json_resp
def in_valid_realisation():
    """
    Valide ou invalide une réalisation nocturne (IN) en base de données.

    Cette fonction est appelée lors d'une requête PATCH sur l'endpoint
    /valid_realisation/. Elle nécessite que l'utilisateur soit authentifié
    avec un niveau de droit >= 5 (voir le décorateur check_auth_redirect_login).
    Elle est typiquement utilisée depuis l'interface pour valider ou invalider
    une réalisation (par exemple, après vérification ou correction).
    """

    # Récupère les données JSON envoyées dans la requête HTTP
    data = request.get_json()

    # Extraction des identifiants nécessaires pour cibler la bonne réalisation/tag
    id_realisation = data["id_realisation"]
    valide_ZC = data["valide_ZC"]
    valide_PNC = data["valide_PNC"]
    # Prépare la requête SQLAlchemy pour mettre à jour la table de correspondance
    # entre réalisation et tag (CorRealisationTag) avec les nouvelles valeurs
    stmt_cor = (
        update(TRealisations)
        .where(TRealisations.id_realisation == id_realisation)
        .values(valide_ZC=valide_ZC, valide_PNC=valide_PNC)
    )  # Les champs à mettre à jour sont ceux présents dans 'data'

    # Exécute la requête de mise à jour sur la base de données
    cor = DB.session.execute(stmt_cor)
    DB.session.commit()  # Valide la transaction

    # Retourne True pour indiquer le succès de l'opération (formaté en JSON par le décorateur)
    return True
