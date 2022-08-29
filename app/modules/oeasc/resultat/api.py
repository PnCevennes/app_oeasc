"""
    api pour les resultats
"""

import json

from sqlalchemy import select, func
from flask import Blueprint, current_app, request
from utils_flask_sqla.response import json_resp
from utils_flask_sqla.generic import GenericQuery
from ..user.utils import check_auth_redirect_login

from .repository import result_custom, cache_generic_table
from ..generic.repository import getlist

config = current_app.config
DB = config["DB"]
bp = Blueprint("resultat_api", __name__)

# pour les rendus customisés (route 'custom/')
# dictionaire de relation entre
#  - datatype : le type de données
#  - view : la vue utilisée pour ce type de données
data_type_view_dict = {
    "chasse": "oeasc_chasse.v_custom_results",
}


@bp.route("get_view/<string:schema>/<string:view>", methods=["GET"])
@check_auth_redirect_login(1)
@json_resp
def get_view(schema, view):
    """
    retourne la vue schema.view
    TODO args pour filtres etc...
    """

    data = GenericQuery(DB, view, schema).as_dict()

    return data["items"]


@bp.route("get_views", methods=["GET"])
@check_auth_redirect_login(1)
@json_resp
def get_views():
    """
    retourne les vue specifiées en param json : ['schema.view1', 'schema.view2', ect...]
    TODO args pour filtres etc...
    """

    views = request.args.getlist("view")

    data = {}

    for p in views:

        v = p.split(".")
        schema = v[0]
        view = v[1]
        data_view = GenericQuery(DB, view, schema).as_dict()["items"]
        if not data.get(schema):
            data[schema] = {}
        data[schema][view] = data_view

    return data


@bp.route("custom/", methods=["GET"])
@json_resp
def api_result_custom():
    """
    API custom result pour les restitutions customisée (avec formulaire de choix des paramètres)


    les arguments de route
    - data_type : type de données -> permet de définir la vue utilisée
    - field_name : champs de la vue servant pour l'analyse
    - filters : quels filtres appliqués
    """

    cache_generic_table = {}
    # gestion paramètres pour créer args
    args = {}

    #  - les noms qui viennent du frontend sont en camelCase
    #  - les noms utilisés dans la fonction sql sont en snake_case
    args["field_name"] = request.args.get("fieldName")
    args["field_name_2"] = request.args.get("fieldName2")
    args["data_type"] = request.args.get("dataType")
    args["sort"] = request.args.get("sort")

    # filtres
    args["filters"] = request.args.get("filters", {})
    args["filters"] = args["filters"] and json.loads(args["filters"])
    # on retire les filtres qui sont à []
    # sinon cela pose problème dans la fonction sql
    args["filters"] = {
        k: (v if isinstance(v, list) else [v])
        for (k, v) in args["filters"].items()
        if v
    }

    # récupération de la vue associée à data_type
    args["view"] = data_type_view_dict[args["data_type"]]

    # print(json.dumps(args, indent=4))

    # exectution de la function oeasc_chasse.fct_custom_results_j
    # qui renvoie un objet de type dictionnaire

    res = result_custom(args)

    # req = func.oeasc_chasse.fct_custom_results_j(json.dumps(args))
    # res = DB.engine.execute(req).first()[0]

    # ici res est un tableau :
    # [ ...
    #   { text: <text>, count: <count>}
    #   ... ]

    # - si on a pas de args['field_name_2']
    # - ou si c'est le même que args['field_name']
    # - on renvoie res
    if not args["field_name_2"] or args["field_name"] == args["field_name_2"]:
        return res

    # si field_name_2 est défini on calcule les sous-données

    # pour garder en mémoire args['field_name']
    field_name_save = args["field_name"]

    # desormais on groupe par <field_name_2>
    args["field_name"] = args["field_name_2"]

    # pour chaque valeur de res
    for r in res:
        # on défini un filtre pour le champs <field_name_save> à [ r['text'] ]
        args["filters"][field_name_save] = [r["text"]]
        # on place le résultat dans r['data']
        r["data"] = result_custom(args)

    # on complete les zeros ?
    texts = []
    for r in res:
        for d in r["data"]:
            if d["text"] in texts:
                continue
            texts.append(d["text"])

    for text in texts:
        for r in res:
            if [d for d in r["data"] if d["text"] == text]:
                continue
            r["data"].append({"text": text, "count": 0})

    return res
