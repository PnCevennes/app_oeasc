"""
api pour les resultats
"""

import json

# from sqlalchemy import select, func
from flask import Blueprint, current_app, request
from utils_flask_sqla.response import json_resp
from utils_flask_sqla.generic import GenericQuery
from ..user.utils import check_auth_redirect_login
from sqlalchemy import select

# from .repository import result_custom, cache_generic_table
from .repository import result_custom

# from ..generic.repository import getlist

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


# en comnmentaire pour voir si on en a besoin
@bp.route("get_view/<string:schema>/<string:view>", methods=["GET"])
@check_auth_redirect_login(1)
@json_resp
def get_view(schema, view):
    """
    pas sur que ce soit utilisé
    retourne la vue schema.view
    TODO args pour filtres etc...
    """
    # print ('test pour voir si on arrive ici')
    # data = GenericQuery(DB, view, schema).as_dict()

    # return data["items"]


@bp.route("get_views", methods=["GET"])
@check_auth_redirect_login(1)
@json_resp
def get_views():
    """
    Pas sûr que ce soit utilisé
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
    API custom result pour les restitutions customisées (avec formulaire de choix des paramètres)

    Cette fonction est utilisée pour générer des résultats personnalisés à partir d'une vue SQL,
    selon des paramètres envoyés par le frontend (type de données, champs d'analyse, filtres, etc).
    Elle est appelée lorsque le frontend veut afficher des statistiques ou des analyses dynamiques
    sur les résultats de chasse, par exemple dans des tableaux croisés ou des graphiques.

    Les arguments de route :
    - data_type : type de données -> permet de définir la vue utilisée
    - field_name : champ de la vue servant pour l'analyse principale. Sont des pseudo-champs de la vue SQL
    - field_name_2 : champ secondaire pour une analyse croisée (optionnel)
    - filters : filtres à appliquer sur les données
    - sort : ordre de tri
    """

    cache_generic_table = {}  # Non utilisé ici, prévu pour du cache éventuel

    # Initialisation du dictionnaire des arguments
    args = {}

    # Récupération des paramètres envoyés par le frontend (en camelCase)
    # On les convertit en snake_case pour l'utilisation côté SQL
    args["field_name"] = request.args.get("fieldName")
    args["field_name_2"] = request.args.get("fieldName2")
    args["data_type"] = request.args.get("dataType")
    args["sort"] = request.args.get("sort")

    # Gestion des filtres : récupérés en JSON, transformés en dict Python
    args["filters"] = request.args.get("filters", {})
    args["filters"] = args["filters"] and json.loads(args["filters"])

    # On retire les filtres vides (valeur [])
    # et on enveloppe les valeurs uniques en liste
    # Cela évite des erreurs lors de l'appel de la fonction SQL
    args["filters"] = {
        k: (v if isinstance(v, list) else [v])
        for (k, v) in args["filters"].items()
        if v
    }

    # On récupère la vue SQL associée au type de données demandé
    args["view"] = data_type_view_dict[args["data_type"]]

    # Appel de la fonction qui exécute la requête SQL personnalisée
    # result_custom va interroger la base et renvoyer les résultats sous forme de liste de dicts
    res = result_custom(args)

    # Si on n'a pas de champ secondaire (field_name_2) ou si c'est le même que le champ principal,
    # on retourne simplement le résultat principal
    if not args["field_name_2"] or args["field_name"] == args["field_name_2"]:
        return res

    # Si field_name_2 est défini, on veut faire une analyse croisée :
    # Pour chaque valeur du champ principal, on calcule les sous-données groupées par le champ secondaire

    # On sauvegarde le nom du champ principal
    field_name_save = args["field_name"]

    # On groupe désormais par le champ secondaire
    args["field_name"] = args["field_name_2"]

    # Pour chaque résultat du premier regroupement
    for r in res:
        # On ajoute un filtre pour le champ principal, limité à la valeur courante
        args["filters"][field_name_save] = [r["text"]]
        # On place le résultat du sous-groupement dans r['data']
        r["data"] = result_custom(args)

    # On complète les sous-groupes pour que chaque valeur possible du champ secondaire apparaisse dans chaque groupe
    texts = []
    for r in res:
        for d in r["data"]:
            if d["text"] in texts:
                continue
            texts.append(d["text"])

    # Pour chaque valeur possible, on ajoute un sous-groupe avec count=0 si absent
    for text in texts:
        for r in res:
            if [d for d in r["data"] if d["text"] == text]:
                continue
            r["data"].append({"text": text, "count": 0})

    # On retourne la structure finale, adaptée pour des tableaux croisés ou des graphiques
    return res
