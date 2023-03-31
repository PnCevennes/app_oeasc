"""
    api commons
"""

import os
from pathlib import Path

from flask import Blueprint, current_app, request
from utils_flask_sqla.response import json_resp_accept_empty_list, json_resp
from sqlalchemy import text

from app.utils.env import ROOT_DIR

from .models import (
    TContents,
    TTags,
    TSecteurs,
    TEspeces,
    TNomenclatures,
    BibNomenclaturesTypes,
)
from ..generic.definitions import GenericRouteDefinitions

from ..nomenclature import nomenclature_oeasc_types


grd = GenericRouteDefinitions()

config = current_app.config
DB = config["DB"]

definitions = {
    "content": {"model": TContents, "droits": {"C": 5, "R": 0, "U": 5, "D": 5}},
    "tag": {"model": TTags, "droits": {"C": 5, "R": 0, "U": 5, "D": 5}},
    "secteur": {"model": TSecteurs, "droits": {"C": 5, "R": 0, "U": 5, "D": 5}},
    "espece": {"model": TEspeces, "droits": {"C": 5, "R": 0, "U": 5, "D": 5}},
    "nomenclature": {
        "model": TNomenclatures,
        "droits": {"C": 5, "R": 0, "U": 5, "D": 5},
        "pre_filters": {"type": nomenclature_oeasc_types},
    },
    "nomenclature_type": {
        "model": BibNomenclaturesTypes,
        "droits": {"C": 5, "R": 0, "U": 5, "D": 5},
        "pre_filters": {"mnemonique": nomenclature_oeasc_types},
    },
}

grd.add_generic_routes("commons", definitions)

bp = Blueprint("commons_api", __name__)


@bp.route("communes/<string:test>", methods=["GET"])
@bp.route("communes/", defaults={"test": None}, methods=["GET"])
@json_resp_accept_empty_list
def api_communes(test):
    """
    api pour avoir la liste des communes de france pour les adresses
    """

    if not test:
        return []

    s_trans_I = "àâäéèêëîïöùûü"
    s_trans_O = "aaaeeeeiiouuu"

    for index, _ in enumerate(s_trans_I):
        test = test.replace(s_trans_I[index], s_trans_O[index])

    tests = test.strip().split(" ")

    cond_text = " AND ".join(
        [
            (
                " ( TRANSLATE(nom, '{1}', '{2}') ILIKE '{3}{0}%' OR cp ILIKE '{3}{0}%' ) "
            ).format(s_test, s_trans_I, s_trans_O, "" if s_test == tests[0] else "%")
            for s_test in tests
        ]
    )

    sql_text = """
    SELECT
        CONCAT(nom, ' ', cp) as nom_cp
        FROM oeasc_commons.t_communes WHERE {0} ORDER BY population DESC, nom, cp LIMIT 20
    """.format(
        cond_text
    )

    result = DB.engine.execute(text(sql_text))
    out = [{"nom_cp": res[0]} for res in result]
    return out


@bp.route("files/<string:dir_file>", methods=["GET"])
@json_resp_accept_empty_list
def api_images(dir_file):
    """
    renvoie la liste des image du repertoire image
    """

    if not dir_file in ["img", "doc"]:
        return []

    file_dir_path = Path(ROOT_DIR, "static/medias/" + dir_file)
    files_out = []
    for root, dirs, files in os.walk(file_dir_path):
        for i in files:
            if i[0] == ".":
                continue
            files_out.append(i)

    files_out.sort()

    return files_out


@bp.route("add_file/<string:dir_file>", methods=["POST"])
@json_resp
def api_add_images(dir_file):
    """ """

    if not dir_file in ["img", "doc"]:
        return

    file = request.files.get("file")

    if not file:
        return request.get_json()

    out = {}
    for key in request.form:
        out[key] = request.form.get(key)
        if out[key] == "null":
            out[key] = None
        if out[key] == "false":
            out[key] = False
        if out[key] == "true":
            out[key] = True

    filename = file.filename
    for c in "/!;, ()}{}":
        filename = filename.replace(c, "_")

    file.save(os.path.join(ROOT_DIR, "static/medias/" + dir_file, filename))
    out["src"] = filename

    return out
