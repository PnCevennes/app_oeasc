""" api pour les indices nocturnes """
from flask import Blueprint, current_app, request
from utils_flask_sqla.response import json_resp

from app.modules.oeasc.user.utils import check_auth_redirect_login

from .repository import in_data

from .models import (
    TRealisations,
    TCircuits,
    TTags,
    TObservers,
    CorRealisationTag,
)

from ..generic.definitions import GenericRouteDefinitions

grd = GenericRouteDefinitions()


bp = Blueprint("in_api", __name__)

config = current_app.config
DB = config["DB"]

definitions = {
    "realisation": {"model": TRealisations, "droits": {"C": 5, "R": 0, "U": 5, "D": 5}},
    "circuit": {"model": TCircuits, "droits": {"C": 5, "R": 0, "U": 5, "D": 5}},
    "tag": {"model": TTags, "droits": {"C": 5, "R": 0, "U": 5, "D": 5}},
    "observer": {"model": TObservers, "droits": {"C": 5, "R": 0, "U": 5, "D": 5}},
}

grd.add_generic_routes("in", definitions)


@bp.route("results/", methods=["GET"])
@json_resp
def in_results():
    """
    renvoie les résultats des in pour faire les graphs (IN, variance, ug, année)
    """
    out = in_data()

    return out


@bp.route("test/results/", methods=["GET"])
@json_resp
def in_test_results():
    """
    renvoie les résultats des in pour faire les graphs (IN, variance, ug, année)
    """

    return in_data()["especes"]["Cerf"]["ugs"]["Méjean"]


@bp.route("valid_realisation/", methods=["PATCH"])
@check_auth_redirect_login(5)
@json_resp
def in_valid_realisation():
    """
    valide ou invalide une realisation
    """

    data = request.get_json()

    id_realisation = (data["id_realisation"],)
    id_tag = data["id_tag"]

    cor = (
        DB.session.query(CorRealisationTag)
        .filter_by(id_realisation=id_realisation, id_tag=id_tag)
        .update(data, synchronize_session=False)
    )

    DB.session.commit()

    return cor
