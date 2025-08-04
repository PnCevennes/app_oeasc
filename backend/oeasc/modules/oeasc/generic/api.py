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

# from oeasc.modules.oeasc.chasse.models import TLieuTirs

bp = Blueprint("generic_api", __name__)


@bp.route("<string:module_name>/<string:object_types>/", methods=["GET"])
@check_object_type(
    droit_type="R"
)  # Vérifie les droits en lecture et si le module existe
@json_resp_accept_empty_list
def get_all_generic(module_name, object_types):
    """
    get_all_generic
    Retourne des dictionnaires représentant tous les objets d'une requête.
    Si 'only_fields' est présent dans les arguments, on retourne seulement les champs demandés.
    Utilisation typique : pour lister tous les objets d'un certain type dans un module, par exemple pour afficher une liste dans une interface.
    """

    # On enlève le 's' à la fin du type d'objet pour obtenir le nom singulier (convention de nommage)
    object_type = object_types[:-1]

    # Récupération des arguments de la requête (filtres, pagination, etc.)
    args = request.args

    # Appel au repository pour récupérer les objets, le nombre total et le nombre filtré
    res, count, count_filtered = get_objects_type(module_name, object_type, args)

    # Récupération de la classe de schéma pour sérialiser les objets
    class_schema = definitions.get_schema_from_definition(module_name, object_type)
    
    # Si l'argument 'count' est présent, on retourne uniquement le nombre total d'objets
    if "count" in args:
        return count

    # Si la clé 'only_fields' est présente, on retourne seulement les champs demandés pour chaque objet
    if "only_fields" in args:
        only_fields = args.get("only_fields").split(",")
        # Création du schéma avec uniquement les champs demandés
        schema = class_schema(many=True, only_fields=only_fields)
        # Suppression des doublons et récupération des objets
        res = res.unique().all()
        # Sérialisation des objets
        items = schema.dump(res)
    else:
        # Si aucun champ spécifique n'est demandé, on retourne tous les champs
        schema = class_schema(many=True)
        res = res.unique().all()
        items = schema.dump(res)

    # On retourne un dictionnaire avec le nombre total, le nombre filtré et la liste des objets
    return {"total": count, "total_filtered": count_filtered, "items": items}




@bp.route("<string:module_name>/<string:object_type>/<value>", methods=["GET"])
@check_object_type("R")
@json_resp
def get_generic(module_name, object_type, value):
    """
    Récupère un objet générique à partir de son module, type et valeur.

    Cette fonction est utilisée pour obtenir une représentation sérialisée d'un objet
    spécifique, identifié par son module (`module_name`), son type (`object_type`) et une valeur
    d'identification (`value`). Elle est généralement appelée lors d'une requête GET sur l'API
    pour accéder à une ressource précise.

    Arguments:
        module_name (str): Nom du module auquel appartient l'objet.
        object_type (str): Type d'objet à récupérer.
        value (str): Valeur d'identification de l'objet (ex: identifiant primaire).

    Paramètres de requête:
        field_name (str, optionnel): Nom du champ à utiliser pour la recherche de l'objet.

    Retour:
        dict: Représentation sérialisée de l'objet si trouvé, sinon None.

    Utilisation typique:
        Cette fonction est utilisée dans le cadre d'une API REST pour permettre aux clients
        d'obtenir les détails d'un objet en fonction de son type et de son identifiant.
        Elle s'appuie sur des définitions dynamiques pour déterminer le schéma de sérialisation
        et la logique de récupération de l'objet.

    Remarques:
        - La fonction vérifie d'abord si l'objet existe, puis le sérialise à l'aide du schéma approprié.
        - Elle est décorée pour vérifier le type d'objet, formater la réponse en JSON et gérer la route.
    """
    field_name = request.args.get("field_name")
    # in_relationship = request.args.get("in_relationship")

    # (Model, id_field_name) = definitions.get_model(module_name, object_type)
    schema_class = definitions.get_schema_from_definition(module_name, object_type)
    res = get_object_type(module_name, object_type, value, field_name)

    if not res:
        return None

    # relat = [db_rel.key for db_rel in Model.__mapper__.relationships]
    res_dict = schema_class(many=False).dump(res)

    return res_dict




@bp.route("<string:module_name>/<string:object_type>/<int:id_value>", methods=["PATCH"])
@check_object_type("U")  # Vérifie les droits en modification (Update)
@json_resp
def patch_generic(module_name, object_type, id_value):
    """
    Met à jour un objet générique à partir de son module, type et identifiant.

    Cette fonction est appelée lors d'une requête PATCH sur l'API pour modifier partiellement
    un objet existant. Elle reçoit les nouvelles données dans le corps de la requête (JSON),
    puis utilise la logique métier pour appliquer les modifications.

    Arguments:
        module_name (str): Nom du module auquel appartient l'objet.
        object_type (str): Type d'objet à modifier.
        id_value (int): Identifiant de l'objet à mettre à jour.

    Utilisation typique:
        - Lorsqu'un client souhaite modifier certains champs d'un objet existant via l'API REST.
        - Par exemple, pour mettre à jour le statut ou une propriété d'un enregistrement.

    Remarques:
        - La fonction vérifie les droits d'accès en modification.
        - Elle utilise le schéma dynamique pour sérialiser la réponse.
        - Si l'objet n'existe pas ou la modification échoue, elle retourne None.
    """

    # Récupère les données envoyées dans la requête (au format JSON)
    post_data = request.get_json()

    # Appelle la fonction métier pour créer ou mettre à jour l'objet
    res = create_or_update_object_type(module_name, object_type, id_value, post_data)

    # Récupère la classe de schéma pour sérialiser l'objet modifié
    schema_class = definitions.get_schema_from_definition(module_name, object_type)
    if not res:
        # Si l'objet n'a pas été trouvé ou la modification a échoué, retourne None
        return None
    else:
        # Sérialise l'objet modifié et retourne le dictionnaire correspondant
        return schema_class(many=False).dump(res)




@bp.route("<string:module_name>/<string:object_type>/", methods=["POST"])
@check_object_type("C")  # Vérifie les droits en création (Create)
@json_resp
def post_generic(module_name, object_type):
    """
    Crée un nouvel objet générique à partir de son module et de son type.

    Cette fonction est appelée lors d'une requête POST sur l'API pour ajouter un nouvel objet.
    Les données de l'objet à créer sont envoyées dans le corps de la requête au format JSON.

    Arguments:
        module_name (str): Nom du module auquel appartient l'objet.
        object_type (str): Type d'objet à créer.

    Utilisation typique:
        - Lorsqu'un client souhaite ajouter un nouvel enregistrement via l'API REST.
        - Par exemple, pour créer une nouvelle entité dans une interface d'administration.

    Remarques:
        - La fonction vérifie les droits d'accès en création.
        - Elle utilise le schéma dynamique pour sérialiser la réponse.
        - Si la création échoue, elle retourne None.
    """

    # Récupère les données envoyées dans la requête (au format JSON)
    post_data = request.get_json()

    # Récupère la classe de schéma pour sérialiser l'objet créé
    schema_class = definitions.get_schema_from_definition(module_name, object_type)

    # Appelle la fonction métier pour créer l'objet (id_value=None indique une création)
    res = create_or_update_object_type(module_name, object_type, None, post_data)

    if not res:
        # Si la création a échoué, retourne None
        return None
    else:
        # Sérialise l'objet créé et retourne le dictionnaire correspondant
        return schema_class(many=False).dump(res)



@bp.route(
    "<string:module_name>/<string:object_type>/<int:id_value>", methods=["DELETE"]
)
@check_object_type("D")  # Vérifie les droits en suppression (Delete)
@json_resp
def delete_generic(module_name, object_type, id_value):
    """
    Supprime un objet générique à partir de son module, type et identifiant.

    Cette fonction est appelée lors d'une requête DELETE sur l'API pour supprimer un objet existant.
    Elle reçoit en paramètres le nom du module, le type d'objet et l'identifiant de l'objet à supprimer.

    Arguments:
        module_name (str): Nom du module auquel appartient l'objet.
        object_type (str): Type d'objet à supprimer.
        id_value (int): Identifiant de l'objet à supprimer.

    Utilisation typique:
        - Lorsqu'un client souhaite supprimer un enregistrement via l'API REST.
        - Par exemple, pour retirer une entité dans une interface d'administration.

    Remarques:
        - La fonction vérifie les droits d'accès en suppression.
        - Elle utilise la logique métier pour effectuer la suppression.
        - Si la suppression réussit, elle retourne le résultat (souvent un booléen ou un message).
        - Si l'objet n'existe pas ou la suppression échoue, elle retourne None ou une erreur.
    """

    # Appelle la fonction métier pour supprimer l'objet correspondant à l'identifiant donné
    return delete_object_type(module_name, object_type, id_value)
