"""
api commons
"""

import os
from pathlib import Path

from flask import Blueprint, current_app, request
from utils_flask_sqla.response import json_resp_accept_empty_list, json_resp
from sqlalchemy import text, select, func
from sqlalchemy.orm import Session

# from oeasc.utils.env import ROOT_DIR

from .models import (
    TContents,
    TTags,
    TSecteurs,
    TEspeces,
    TCommunes,
    TNomenclaturesOeasc,
    TListeOrganismes
)
from .schema import(
    TContentsSchema,
    TTagsSchema,
    TSecteursSchema,
    TEspecesSchema,
    TCommunesSchema,
    TNomenclaturesOeascSchema,
    TListeOrganismesSchema
)

from pypnnomenclature.models import BibNomenclaturesTypes
from pypnnomenclature.schemas import BibNomenclaturesTypesSchema


from ..generic.definitions import GenericRouteDefinitions

from ..nomenclature import nomenclature_oeasc_types


grd = GenericRouteDefinitions()

config = current_app.config
DB = config["DB"]

definitions = {
    "content": {"model": TContents, "droits": {"C": 5, "R": 0, "U": 5, "D": 5}, "schema": TContentsSchema},
    "tag": {"model": TTags, "droits": {"C": 5, "R": 0, "U": 5, "D": 5}, "schema": TTagsSchema},
    "secteur": {"model": TSecteurs, "droits": {"C": 5, "R": 0, "U": 5, "D": 5}, "schema": TSecteursSchema},
    "espece": {"model": TEspeces, "droits": {"C": 5, "R": 0, "U": 5, "D": 5}, "schema": TEspecesSchema},
    "commune": { "model": TCommunes, "droits": {"C": 5, "R": 0, "U": 5, "D": 5}, "schema": TCommunesSchema},
    "liste_organismes": { "model": TListeOrganismes, "droits": {"C": 5, "R": 0, "U": 5, "D": 5}, "schema": TListeOrganismesSchema},
    "nomenclature": {
        "model": TNomenclaturesOeasc,
        "schema": TNomenclaturesOeascSchema,
        "droits": {"C": 5, "R": 0, "U": 5, "D": 5},
        "pre_filters": {"type": nomenclature_oeasc_types},
    },
    "nomenclature_type": {
        "model": BibNomenclaturesTypes,
        "schema": BibNomenclaturesTypesSchema,
        "droits": {"C": 5, "R": 0, "U": 5, "D": 5},
        "pre_filters": {"mnemonique": nomenclature_oeasc_types},
    },

}

grd.add_generic_routes("commons", definitions)

bp = Blueprint("commons_api", __name__)


@bp.route("communes/", methods=["GET"])
def api_all_communes():
    """ recupèration de la liste de toutes les communes via le shema
    pas utilisé poru l'instant, mais peut être utile pour des tests
    """

    
    stmt_commune = (
        select(TCommunes)
        .where(
            (TCommunes.cp.startswith("07")) |
            (TCommunes.cp.startswith("48")) |
            (TCommunes.cp.startswith("30"))
        )
        .order_by(TCommunes.population.desc(), TCommunes.nom, TCommunes.cp)
    )
    result = DB.session.execute(stmt_commune).scalars().all()
    communeSchema= TCommunesSchema()
    out = [communeSchema.dump(res) for res in result]
    return out
    


@bp.route("communes/<string:test>", methods=["GET"])
@json_resp_accept_empty_list
def api_communes(test):
    """
    api qui retourne une liste de commune sous forme de liste de "nom code_postal".(pas en json)
    prend en argument soit le code postal, soit le nom de la commune.
    Utile pour l'autocomplétion des communes dans les formulaires.
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

    stmt_commune = (select(func.concat(TCommunes.nom, ' ', TCommunes.cp).label('nom_cp'))
                    .where(text(cond_text))
                    .order_by(TCommunes.population.desc(), TCommunes.nom, TCommunes.cp)
                    .limit(20))


    result = DB.session.execute(stmt_commune).all()

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

    file_dir_path = Path(config["ROOT_DIR"], "static/medias/" + dir_file)
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

    file.save(os.path.join(config["ROOT_DIR"], "static/medias/" + dir_file, filename))
    out["src"] = filename

    return out
