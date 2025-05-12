"""
config
"""

from flask import current_app
from .definitions import GenericRouteDefinitions

from sqlalchemy import func, cast, select, orm, and_, delete
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


def custom_getattr(Model, attr_name, stmt):
    """
    Cette fonction custom_getattr(Model, attr_name, stmt) est une fonction utilitaire conçue pour récupérer dynamiquement un attribut d'un modèle SQLAlchemy. Elle permet de gérer :

    Les attributs simples d'un modèle (Model.attr) si attr_name = 'attr'
    Les attributs d'une relation (Model.relation.attr) si attr_name = 'rel.attr'
    Les jointures dynamiques sur une relation (via stmt.join())
    """

    if "." in attr_name:
        # cas a.b on verra ensuite
        rel = attr_name.split(".")[0]
        col = attr_name.split(".")[1]

        if not hasattr(Model, rel):
            return None, stmt

        relationship = getattr(Model, rel)
        target_model = relationship.prop.mapper.class_

        # Check if the column exists in the target model
        if not hasattr(target_model, col):
            return None, stmt

        alias = orm.aliased(target_model)
        stmt = stmt.join(alias, relationship)

        model_attribute = getattr(alias, col)

        return model_attribute, stmt

    else:
        if not hasattr(Model, attr_name):
            return None, stmt

        return getattr(Model, attr_name), stmt


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

    Model, _ = definitions.get_model(module_name, object_type)

    # recupère un dictionnaire contenant le modèle et diverses options
    obj = definitions.get_object_type(module_name, object_type)

    # on charge le modèle
    stmt = select(Model)

    # prefiltres
    pre_filters = obj.get("pre_filters", {})
    for key in pre_filters:
        if not hasattr(Model, key):
            continue
        stmt = stmt.where(getattr(Model, key).in_(pre_filters[key]))

    count_result = DB.session.execute(
        select(func.count()).select_from(stmt.subquery())
    ).scalar_one()
    count = count_result or 0

    # filtres
    for key in args:
        params_filter = key.split("__")
        key_filter = params_filter[0]

        type_filter = None
        if len(params_filter) > 1:
            type_filter = params_filter[1]

        value_filter = args[key]

        if not value_filter:
            continue

        model_attribute, stmt = custom_getattr(Model, key_filter, stmt)

        if model_attribute is None:
            continue

        if type_filter == "ilike" and value_filter and value_filter[0] != "=":
            # filtre ILIKE
            value_filters = value_filter.split(" ")
            filters = []
            for v in value_filters:
                filters.append(
                    unaccent(cast(model_attribute, DB.String)).ilike(
                        func.concat("%", unaccent(v), "%")
                    )
                )

            stmt = stmt.where(and_(*(tuple(filters))))

        else:
            value_filter_effectif = value_filter
            if value_filter and value_filter[0] == "=":
                value_filter_effectif = value_filter[1:]
            # filtre =

            if len(value_filter_effectif.split(",")) > 1:
                stmt = stmt.where(
                    cast(model_attribute, DB.String).in_(
                        value_filter_effectif.split(",")
                    )
                )
            else:
                stmt = stmt.where(
                    cast(model_attribute, DB.String) == value_filter_effectif
                )

    # Triage
    sort_by = getlist(args, "sortBy")
    sort_desc = getlist(args, "sortDesc")

    # sort
    order_bys = []
    for index, key in enumerate(sort_by):
        model_attribute, stmt = custom_getattr(Model, key, stmt)
        if model_attribute is None:
            continue

        desc = sort_desc[index] if index < len(sort_desc) else "false"
        if desc == "true":
            order_bys.append(model_attribute.desc())
        else:
            order_bys.append(model_attribute.asc())

    if order_bys:
        stmt = stmt.order_by(*(tuple(order_bys)))

    count_filtered_result = DB.session.execute(
        select(func.count()).select_from(stmt.subquery())
    ).scalar_one()
    count_filtered = count_filtered_result or 0

    # Pagination
    page = args.get("page")
    itemsPerPage = args.get("itemsPerPage")
    if itemsPerPage and int(itemsPerPage) > 0:
        stmt = stmt.limit(int(itemsPerPage))

        if page and int(page) > 1:
            stmt = stmt.offset((int(page) - 1) * int(itemsPerPage))

    # Exécution de la requête
    data_result = DB.session.execute(stmt).scalars()

    return data_result, count, count_filtered


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

    select_object = select(Model).where(getattr(Model, field_name) == value).limit(1)
    result = DB.session.execute(select_object).unique().scalars().one_or_none()

    return result


def create_or_update_object_type(module_name, object_type, id_value, post_data):
    """
    Crée ou met à jour un objet du type spécifié avec les données fournies.

    Args:
        module_name: Nom du module contenant le modèle
        object_type: Type d'objet à créer/mettre à jour
        id_value: Valeur d'ID pour la mise à jour (None pour création)
        post_data: Données à appliquer à l'objet

    Returns:
        L'objet créé ou mis à jour
    """
    (Model, id_field_name) = definitions.get_model(module_name, object_type)

    try:
        if id_value:
            # Récupération de l'objet existant
            res = get_object_type(module_name, object_type, id_value)
            if not res:
                raise ValueError(
                    f"Objet {object_type} avec {id_field_name}={id_value} non trouvé"
                )
        else:
            # Création d'un nouvel objet
            res = Model()
            # En 2.0, on préfère add() explicitement même si ce sera fait lors du commit
            

        # Suppression de l'ID si sa valeur est None
        if id_field_name in post_data and post_data[id_field_name] is None:
            del post_data[id_field_name]

        # Application des données (méthode personnalisée)
        res.from_dict(post_data, recusif=True)

        # Commit des changements
        # if (not id_value):
        DB.session.add(res)

        DB.session.commit()
        return res

    except Exception as e:
        DB.session.rollback()
        # Considérez de logger l'erreur ici
        raise e


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

    # ne retourne pas les relationship. A voir si c'est vraiment utile
    out = res.as_dict()

    try:
        DB.session.delete(res)
        DB.session.commit()
    except Exception as e:
        print ("Erreur lors de la suppression de l'objet : ", e)

     
    return out
