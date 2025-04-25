"""
routes generiques
"""

from utils_flask_sqla.response import json_resp, json_resp_accept_empty_list
from flask import Blueprint, request

from .decorator import check_object_type

from .definitions import GenericRouteDefinitions

definitions = GenericRouteDefinitions()

from .repository import (
    get_objects_type,
    get_object_type,
    create_or_update_object_type,
    delete_object_type,
)

from oeasc.modules.oeasc.chasse.models import TLieuTirs

bp = Blueprint("generic_api", __name__)


# Cette fonction est une route Flask qui permet de récupérer tous les objets d'un type donné depuis
# la base de données, avec prise en charge de filtres et de pagination.
# <nom_module>/<nom_modele>s ---- exemple: chasse/personnes/ -> récupère tous les objets de type personne
# les types d'objets prennent un s à la fin du nom du modèle (par principe de nommage)
# si "count" est présent dans les arguments, la fonction retourne le nombre total d'objets sans les retourner
# Retourne un objet JSON de la forme :
# {
#   "total": 150,
#   "total_filtered": 10,
#   "items": [
#     {"id": 1, "name": "Alice"},
#     {"id": 2, "name": "Bob"}
#   ]
# }
@bp.route("<string:module_name>/<string:object_types>/", methods=["GET"])
@check_object_type(
    droit_type="R"
)  # verifie les droits en lecture et si le module existe
@json_resp_accept_empty_list
def get_all_generic(module_name, object_types):
    """
    get_all_generic
    """
    # on enleve le s à la fin. Juste pour la déco
    object_type = object_types[:-1]

    args = request.args
    res, count, count_filtered = get_objects_type(module_name, object_type, args)

    # si count dans les arguments on retourne le nombre total
    if "count" in args:
        return count
    # si la clé "fields" est présente dans les arguments, on retourne seulement les champs demandés
    if "fields" in args:
        fields = args.get("fields").split(",")
        items = [r.as_dict(fields=(fields)) for r in res.unique().all()]
    else:
        print("################# fields à rajouter dans les args de la requete")
        items = [r.as_dict() for r in res.all()]

    return {"total": count, "total_filtered": count_filtered, "items": items}


# Cette fonction est une route Flask qui permet de récupérer un objet unique en fonction
# d'une valeur donnée (généralement un identifiant). Elle permet aussi d'utiliser un champ
#  spécifique autre que l'ID (si field_name est fourni).
# <nom_module>/<nom_modele>/<valeur> ---- exemple: chasse/personne/1 -> récupère l'objet de type personne avec l'id 1
# /chasse/personne/john doe?field_name=nom_personne
# si field_name est présent dans les arguments, la fonction utilise ce champ pour la recherche
# Retourne un objet JSON de la forme :
# {
#   "id": 1,
#   "name": "Alice"
# }


@bp.route("<string:module_name>/<string:object_type>/<value>", methods=["GET"])
@check_object_type("R")
@json_resp
def get_generic(module_name, object_type, value):

    field_name = request.args.get("field_name")
    # in_relationship = request.args.get("in_relationship")

    (Model, id_field_name) = definitions.get_model(module_name, object_type)
    res = get_object_type(module_name, object_type, value, field_name)

    if not res:
        return None

    relat = [db_rel.key for db_rel in Model.__mapper__.relationships]

    return res.as_dict(fields=relat)


# Cette fonction est une route Flask qui permet de mettre à jour un objet unique en fonction
# d'une valeur donnée (généralement un identifiant). Si l'objet n'existe pas, il est créé.
# <nom_module>/<nom_modele>/<valeur> ---- exemple: chasse/personne/1 -> met à jour l'objet de type personne avec l'id 1
# <nom_module>/<nom_modele>/ ---- exemple: chasse/personne/ -> crée un nouvel objet de type personne
# Exemple:

# response = requests.patch(
#     url="chasse/personne/1",
#     data=json.dumps("nom": "Alice"),
#     headers={"Content-Type": "application/json"},
# )

# Retourne un objet JSON de la forme :
# {
#   "id": 1,
#   "name": "Alice"
# }


@bp.route("<string:module_name>/<string:object_type>/<int:id_value>", methods=["PATCH"])
@check_object_type("U")  # vérifie les droits en écriture (Update)
@json_resp
def patch_generic(module_name, object_type, id_value):

    post_data = request.get_json()

    res = create_or_update_object_type(module_name, object_type, id_value, post_data)

    return res.as_dict()


# Cette fonction est une route Flask qui permet de créer un nouvel objet d'un type donné.
# <nom_module>/<nom_modele>/ ---- exemple: chasse/personne/ -> crée un nouvel objet de type personne
# corp de la requete: {"nom": "Alice"}
# {
#   "id": 1,
#   "name": "Alice",
# }


@bp.route("<string:module_name>/<string:object_type>/", methods=["POST"])
@check_object_type("C")  # vérifie les droits en création (Create)
@json_resp
def post_generic(module_name, object_type):
    """
    post generic
    """

    post_data = request.get_json()

    res = create_or_update_object_type(module_name, object_type, None, post_data)

    return res.as_dict()


# Cette fonction est une route Flask qui permet de supprimer un objet unique en fonction
# d'une valeur donnée (généralement un identifiant).
# <nom_module>/<nom_modele>/<valeur> ---- exemple: chasse/personne/1 -> supprime l'objet de type personne avec l'id 1
# Retourne un objet JSON de la forme :
# {
#   "id": 1,
#   "name": "Alice"
# }
@bp.route(
    "<string:module_name>/<string:object_type>/<int:id_value>", methods=["DELETE"]
)
@check_object_type("D")  # vérifie les droits en suppression (Delete)
@json_resp
def delete_generic(module_name, object_type, id_value):
    """
    delete generic
    """

    return delete_object_type(module_name, object_type, id_value)
