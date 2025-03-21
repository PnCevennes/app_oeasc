"""
  config
"""

from flask import current_app
from .definitions import GenericRouteDefinitions
from sqlalchemy import func, cast, orm, and_
import unidecode
from sqlalchemy.sql.functions import ReturnTypeFromArgs


# s'assure de retourner le bon type de donnée da la requête sql
class unaccent(ReturnTypeFromArgs):
    inherit_cache = True
    pass


config = current_app.config
DB = config["DB"]

# les routes pour accéder aux modèles de la base de données
definitions = GenericRouteDefinitions()


def getlist(args, key):

    """
    Cette fonction getlist(args, key) est une fonction utilitaire qui améliore la récupération des valeurs d'un paramètre GET dans une requête HTTP. Elle traite les cas où le paramètre peut être :

    Un seul élément (?val=unique_value)
    Une liste d'éléments séparés par des virgules (?val=val1,val2,val3)
    Une liste d'éléments envoyés sous forme de plusieurs occurrences du même paramètre (?val=val1&val=val2)
    retourne ["val1", "val2", "val3"]
    """


    val = args.get(key)

    if not val:
        return []

    if "," in val:
        return val.split(",")

    return args.getlist(key)


def custom_getattr(Model, attr_name, query):

    """
    Cette fonction custom_getattr(Model, attr_name, query) est une fonction utilitaire conçue pour récupérer dynamiquement un attribut d'un modèle SQLAlchemy. Elle permet de gérer :

    Les attributs simples d'un modèle (Model.attr) si attr_name = 'attr'
    Les attributs d'une relation (Model.relation.attr) si attr_name = 'rel.attr'
    Les jointures dynamiques sur une relation (via query.join())
    """

    if "." in attr_name:
        # cas a.b on verra ensuite
        rel = attr_name.split(".")[0]
        col = attr_name.split(".")[1]

        if not hasattr(Model, rel):
            return None, query

        if not hasattr(getattr(Model, rel).mapper.columns, col):
            return None, query

        relationship = getattr(Model, rel)
        alias = orm.aliased(relationship.mapper.entity)  # Model ?????

        query = query.join(alias, relationship)

        model_attribute = getattr(alias, col)

        return model_attribute, query

    else:
        if not hasattr(Model, attr_name):
            return None, query

        return getattr(Model, attr_name), query


def get_objects_type(module_name, object_type, args={}):
    """
    La fonction get_objects_type(module_name, object_type, args={}) construit dynamiquement une requête
    SQLAlchemy pour récupérer des objets en fonction de filtres, de tris et de la pagination. Elle est
    conçue pour être générique, permettant d'interroger n'importe quel modèle SQLAlchemy en fonction
    des paramètres fournis.

    module_name : Nom du module contenant le modèle.
    object_type : Type d'objet (nom du modèle SQLAlchemy).
    args : Dictionnaire contenant les paramètres de filtrage, de tri et de pagination (généralement récupérés depuis request.args).

    clé possible dans args :
    ?name=John → name="John" (égalité)
    ?name__ilike=jo → name ILIKE "%jo%" (recherche insensible à la casse)
    ?status=active,inactive → status IN ('active', 'inactive') (filtrage multiple)
    ?profile.name=Admin → jointure avec une relation (profile) et filtrage sur profile.name

    """

    joins = []

    Model, _ = definitions.get_model(module_name, object_type)
    obj = definitions.get_object_type(module_name, object_type)

    query = DB.session.query(Model)
    query.enable_assertions = True  # prttt ???

    # prefiltres
    pre_filters = obj.get("pre_filters", {})
    for key in pre_filters:
        if not hasattr(Model, key):
            continue
        query = query.filter(getattr(Model, key).in_(pre_filters[key]))

    count = query.count()

    # filtres
    #
    # si ?<key>=<value_filter> -> filtre =
    # si ?<key>__ilike=<value_filter> -> filtre ilike (ajouter sans accents ??)
    #
    # ajouter filtre par relationship (join ???)
    # si . in key
    # ?a.b=<value_filter>
    # a : relationship et b attribut de a
    #
    for key in args:
        # test search- ?

        params_filter = key.split("__")

        key_filter = params_filter[0]

        type_filter = None
        if len(params_filter) > 1:
            type_filter = params_filter[1]

        #  test si clé null à ajouter ???
        value_filter = args[key]

        if not value_filter:
            continue

        # value

        # # si la cle n'est pas présente dans le modèle on passe

        # pour les cas ou key_filter = relationship.attribute
        # (ou plus profond ?? r1.r2.attribute)
        model_attribute, query = custom_getattr(Model, key_filter, query)

        if model_attribute is None:
            continue

        if type_filter == "ilike" and value_filter and value_filter[0] != "=":
            # filre ILIKE
            value_filter_unaccent = unidecode.unidecode(value_filter)
            value_filters = value_filter.split(" ")
            filters = []
            for v in value_filters:
                filters.append(
                    unaccent(cast(model_attribute, DB.String)).ilike(
                        func.concat("%", unaccent(v), "%")
                    )
                )

            query = query.filter(and_(*(tuple(filters))))

        else:
            value_filter_effectif = value_filter
            if value_filter and value_filter[0] == "=":
                value_filter_effectif = value_filter[1:]
            # filtre =

            if len(value_filter_effectif.split(",")) > 1:
                query = query.filter(
                    cast(model_attribute, DB.String).in_(
                        value_filter_effectif.split(",")
                    )
                )
            else:
                query = query.filter(
                    cast(model_attribute, DB.String) == value_filter_effectif
                )

    # print sort by
    sort_by = getlist(args, "sortBy")
    sort_desc = getlist(args, "sortDesc")

    # sort
    order_bys = []
    for index, key in enumerate(sort_by):
        model_attribute, query = custom_getattr(Model, key, query)
        if model_attribute is None:
            continue

        desc = sort_desc[index]
        if desc == "true":
            model_attribute = model_attribute.desc()
        else:
            model_attribute.asc()

        order_bys.append(model_attribute)

    if order_bys:
        query = query.order_by(*(tuple(order_bys)))

    count_filtered = query.count()

    page = args.get("page")
    itemsPerPage = args.get("itemsPerPage")
    if itemsPerPage and int(itemsPerPage) > 0:
        query = query.limit(itemsPerPage)

        if page and int(page) > 1:
            query = query.offset((int(page) - 1) * int(itemsPerPage))

    return query, count, count_filtered


def get_object_type(module_name, object_type, value, field_name=None):
    """

    Objectif :

    Trouver un objet unique (.one()) en fonction de la valeur d'un champ.
    Si field_name n'est pas fourni, utilise l'ID par défaut du modèle.
    Fonction utile pour récupérer un objet via une clé primaire ou une autre colonne unique.

    Paramètres :

    module_name : Nom du module contenant le modèle.
    object_type : Nom du modèle SQLAlchemy.
    value : Valeur à rechercher (Model.<field_name> = value).
    field_name (optionnel) : Nom de la colonne à utiliser pour la recherche (par défaut, la clé primaire du modèle).

    """
    (Model, id_field_name) = definitions.get_model(module_name, object_type)

    if not field_name:
        field_name = id_field_name

    return DB.session.query(Model).filter(getattr(Model, field_name) == value).one()


def create_or_update_object_type(module_name, object_type, id_value, post_data):
    """
    Cette fonction permet de créer ou mettre à jour un objet d’un modèle SQLAlchemy en fonction d’un id_value.

    Objectif :
    Si id_value est fourni → Met à jour l'objet existant.
    Si id_value est None → Crée un nouvel objet.

    Paramètres :

    module_name : Nom du module contenant le modèle.
    object_type : Nom du modèle SQLAlchemy.
    id_value : Valeur de l'identifiant de l'objet (ex: User.id).
    post_data : Dictionnaire contenant les valeurs à mettre à jour/créer.

    """
    (Model, id_field_name) = definitions.get_model(module_name, object_type)

    res = get_object_type(module_name, object_type, id_value) if id_value else Model()

    if id_field_name in post_data and post_data[id_field_name] is None:
        del post_data[id_field_name]

    res.from_dict(post_data, True)

    if not id_value:
        DB.session.add(res)

    DB.session.commit()

    return res


def delete_object_type(module_name, object_type, id_value):
    """
    Objectif :

    Supprimer un objet dans la base de données en fonction de son ID (id_value).
    Retourner les données de l'objet supprimé sous forme de dictionnaire.

    Paramètres :

    module_name : Nom du module contenant le modèle.
    object_type : Nom du modèle SQLAlchemy.
    id_value : Identifiant de l'objet à supprimer.
    """

    (Model, id_field_name) = definitions.get_model(module_name, object_type)

    res = get_object_type(module_name, object_type, id_value)

    if not res:
        return None

    out = res.as_dict(True)

    (DB.session.query(Model).filter(getattr(Model, id_field_name) == id_value).delete())

    DB.session.commit()

    return out
