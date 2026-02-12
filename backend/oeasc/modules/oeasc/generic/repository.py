"""
config
"""

from flask import current_app
from .definitions import GenericRouteDefinitions

from sqlalchemy import func, cast, select, orm, and_
from sqlalchemy.sql.functions import ReturnTypeFromArgs
from ..declaration.schema import *
from ..chasse.schema import *
from ..commons.schema import *
from ..i_n.schema import *


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
    Fonction utilitaire pour récupérer une liste de valeurs à partir des paramètres d'une requête HTTP (par exemple, request.args dans Flask).

    Cette fonction gère plusieurs cas d'usage :
    - Si le paramètre est absent, elle retourne une liste vide.
    - Si le paramètre est une chaîne contenant des virgules (ex: ?val=a,b,c), elle découpe la chaîne en liste.
    - Si le paramètre est présent plusieurs fois (ex: ?val=a&val=b), elle utilise la méthode getlist pour récupérer toutes les occurrences.
    - Si le paramètre est une valeur unique (ex: ?val=a), elle retourne une liste contenant cette valeur.

    Utilisation typique :
    - Pour les filtres ou le tri dans une API REST, où l'utilisateur peut envoyer plusieurs valeurs pour un même champ (ex: tri sur plusieurs colonnes, filtrage sur plusieurs états).

    Args:
        args: Dictionnaire des paramètres (ex: request.args)
        key: Nom du paramètre à récupérer

    Returns:
        Liste de valeurs (toujours une liste, même si une seule valeur)
    """

    val = args.get(key)

    # Si le paramètre n'est pas présent, retourne une liste vide
    if not val:
        return []

    # Si la valeur contient des virgules, on la découpe en liste
    if "," in val:
        return val.split(",")

    # Sinon, on utilise getlist pour récupérer toutes les occurrences du paramètre
    return args.getlist(key)


def custom_getattr(Model, attr_name, stmt):
    """
    Fonction utilitaire pour récupérer dynamiquement un attribut d'un modèle SQLAlchemy.

    Cette fonction gère deux cas principaux :
    - Attribut simple du modèle (ex: Model.attr)
    - Attribut d'une relation (ex: Model.relation.attr), avec jointure dynamique

    Utilisation typique :
    - Dans les fonctions de filtrage ou de tri génériques, où le nom de l'attribut peut être passé dynamiquement (ex: ?sortBy=profile.name).
    - Permet d'écrire du code générique pour accéder à n'importe quel champ ou relation d'un modèle SQLAlchemy.
    """

    # Cas où l'attribut est une relation (ex: "profile.name")
    if "." in attr_name:
        # On sépare le nom de la relation et le nom de la colonne
        rel = attr_name.split(".")[0]
        col = attr_name.split(".")[1]

        # Vérifie que le modèle possède bien la relation
        if not hasattr(Model, rel):
            # Si la relation n'existe pas, on retourne None
            return None, stmt

        relationship = getattr(Model, rel)
        # Récupère le modèle cible de la relation
        target_model = relationship.prop.mapper.class_

        # Vérifie que la colonne existe dans le modèle cible
        if not hasattr(target_model, col):
            # Si la colonne n'existe pas, on retourne None
            return None, stmt

        # Crée un alias pour la jointure (utile si plusieurs jointures du même type)
        alias = orm.aliased(target_model)
        # Ajoute la jointure à la requête SQLAlchemy
        stmt = stmt.join(alias, relationship)

        # Récupère l'attribut (colonne) sur le modèle cible
        model_attribute = getattr(alias, col)

        # Retourne l'attribut et la requête modifiée (avec la jointure)
        return model_attribute, stmt

    else:
        # Cas d'un attribut simple du modèle
        if not hasattr(Model, attr_name):
            # Si l'attribut n'existe pas, on retourne None
            return None, stmt

        # Retourne l'attribut et la requête inchangée
        return getattr(Model, attr_name), stmt


def get_objects_type(module_name, object_type, args={}):
    """
    Fonction générique pour récupérer une liste d'objets d'un modèle SQLAlchemy en fonction de filtres, tris et pagination.

    Utilisation typique :
    - Dans une API REST pour lister des objets avec des options de recherche avancées (filtres, tri, pagination).
    - Permet d'interroger dynamiquement n'importe quel modèle en fonction des paramètres reçus (ex: request.args dans Flask).

    Args:
        module_name: Nom du module contenant le modèle
        object_type: Nom du modèle SQLAlchemy
        args: Dictionnaire des paramètres de requête (filtres, tri, pagination)

    Returns:
        data_result: Résultat de la requête (itérable d'objets)
        count: Nombre total d'objets (avant filtrage)
        count_filtered: Nombre d'objets après filtrage
    """

    # Récupère le modèle SQLAlchemy et le nom du champ id
    Model, _ = definitions.get_model(module_name, object_type)

    # Récupère la définition du modèle (peut contenir des pré-filtres)
    obj = definitions.get_object_type(module_name, object_type)

    # Initialise la requête SQLAlchemy
    stmt = select(Model)

    # Application des pré-filtres (toujours appliqués, ex: filtrer sur un statut par défaut)
    pre_filters = obj.get("pre_filters", {})
    for key in pre_filters:
        # Vérifie que le modèle possède bien le champ
        if not hasattr(Model, key):
            continue
        # Ajoute le filtre IN sur le champ
        stmt = stmt.where(getattr(Model, key).in_(pre_filters[key]))

    # Calcule le nombre total d'objets avant filtrage
    count_result = DB.session.execute(
        select(func.count()).select_from(stmt.subquery())
    ).scalar_one()
    count = count_result or 0

    # Application des filtres dynamiques (reçus via args)
    for key in args:
        params_filter = key.split(
            "__"
        )  # Permet de gérer les filtres avancés (ex: name__ilike)
        key_filter = params_filter[0]  # Nom du champ à filtrer

        type_filter = None
        if len(params_filter) > 1:
            type_filter = params_filter[1]  # Type de filtre (ex: ilike)

        value_filter = args[key]

        if not value_filter:
            continue

        # Récupère dynamiquement l'attribut du modèle (peut gérer les relations)
        model_attribute, stmt = custom_getattr(Model, key_filter, stmt)

        if model_attribute is None:
            continue

        # Filtre de type ILIKE (recherche insensible à la casse, utile pour les champs texte)
        if type_filter == "ilike" and value_filter and value_filter[0] != "=":
            value_filters = value_filter.split(" ")
            filters = []
            for v in value_filters:
                # Utilise la fonction unaccent pour ignorer les accents
                filters.append(
                    unaccent(cast(model_attribute, DB.String)).ilike(
                        func.concat("%", unaccent(v), "%")
                    )
                )
            # Combine les filtres avec AND
            stmt = stmt.where(and_(*(tuple(filters))))

        else:
            # Filtre d'égalité ou IN
            value_filter_effectif = value_filter
            if value_filter and value_filter[0] == "=":
                value_filter_effectif = value_filter[1:]
            # Si plusieurs valeurs séparées par des virgules, utilise IN
            if len(value_filter_effectif.split(",")) > 1:
                stmt = stmt.where(
                    cast(model_attribute, DB.String).in_(
                        value_filter_effectif.split(",")
                    )
                )
            else:
                # Sinon, filtre sur l'égalité
                stmt = stmt.where(
                    cast(model_attribute, DB.String) == value_filter_effectif
                )

    # Gestion du tri (sortBy et sortDesc)
    sort_by = getlist(args, "sortBy")  # Liste des champs à trier
    sort_desc = getlist(args, "sortDesc")  # Liste des directions (asc/desc)

    order_bys = []
    for index, key in enumerate(sort_by):
        # Récupère dynamiquement l'attribut à trier (peut être une relation)
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

    # Calcule le nombre d'objets après filtrage
    count_filtered_result = DB.session.execute(
        select(func.count()).select_from(stmt.subquery())
    ).scalar_one()
    count_filtered = count_filtered_result or 0

    # Gestion de la pagination (page et itemsPerPage)
    page = args.get("page")
    itemsPerPage = args.get("itemsPerPage")
    if itemsPerPage and int(itemsPerPage) > 0:
        stmt = stmt.limit(int(itemsPerPage))
        if page and int(page) > 1:
            stmt = stmt.offset((int(page) - 1) * int(itemsPerPage))

    # Exécution de la requête et récupération des objets
    data_result = DB.session.execute(stmt).scalars()

    # Retourne les objets, le nombre total et le nombre filtré
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

    Utilisation typique :
    - Récupérer un objet précis dans une API REST (ex: GET /user/123).
    - Vérifier l'existence d'un objet avant une mise à jour ou une suppression.
    - Accéder à un objet via une clé unique autre que l'ID (ex: email, code, etc.).
    """

    # Récupère le modèle SQLAlchemy et le nom du champ id par défaut
    Model, id_field_name = definitions.get_model(module_name, object_type)

    # Si aucun nom de champ n'est fourni, utilise la clé primaire du modèle
    if not field_name:
        field_name = id_field_name

    # Construit la requête SQLAlchemy pour sélectionner l'objet correspondant à la valeur
    select_object = select(Model).where(getattr(Model, field_name) == value).limit(1)

    # Exécute la requête et récupère l'objet unique ou None si non trouvé
    result = DB.session.execute(select_object).unique().scalars().one_or_none()

    # Retourne l'objet trouvé ou None
    return result


def create_or_update_object_type(module_name, object_type, id_value, post_data):
    """
    Crée ou met à jour un objet du type spécifié avec les données fournies en utilisant un schéma Marshmallow.

    Utilisation typique :
    - Dans une API REST, pour gérer les opérations de création (POST) ou de mise à jour (PUT/PATCH) sur un objet.
    - Permet de factoriser la logique de création/mise à jour pour tous les modèles de la base de données.

    Args:
        module_name: Nom du module contenant le modèle
        object_type: Type d'objet à créer/mettre à jour
        id_value: Valeur d'ID pour la mise à jour (None pour création)
        post_data: Données à appliquer à l'objet

    Returns:
        L'objet créé ou mis à jour
    """

    # Récupère le modèle SQLAlchemy et le nom du champ id
    Model, id_field_name = definitions.get_model(module_name, object_type)

    # Recherche du schéma Marshmallow correspondant au modèle (ex: UserSchema pour User)
    schema_name = f"{Model.__name__}Schema"
    schema = globals().get(schema_name)

    # Vérifie que le schéma existe bien dans le contexte global
    if not schema:
        raise ValueError(
            f"Schéma {schema_name} non trouvé pour le modèle {Model.__name__}"
        )

    try:
        if id_value:
            # Cas d'une mise à jour : on récupère l'objet existant
            res = get_object_type(module_name, object_type, id_value)
            if not res:
                # Si l'objet n'existe pas, on lève une erreur
                raise ValueError(
                    f"Objet {object_type} avec {id_field_name}={id_value} non trouvé"
                )
            # Charge les nouvelles données dans l'objet existant (mise à jour partielle possible)
            obj = schema().load(
                post_data, instance=res, session=DB.session, partial=True
            )
        else:
            # Cas d'une création : on instancie un nouvel objet avec les données fournies
            obj = schema().load(post_data, session=DB.session)

        # Ajoute l'objet (nouveau ou modifié) à la session SQLAlchemy
        DB.session.add(obj)
        # Valide la transaction en base de données
        DB.session.commit()
        # Retourne l'objet créé ou mis à jour
        return obj

    except Exception as e:
        # En cas d'erreur, annule la transaction pour éviter les incohérences
        DB.session.rollback()
        # Propage l'exception pour gestion par le contrôleur ou l'API
        raise e


def delete_object_type(module_name, object_type, id_value):
    """
    Objectif :
    Supprimer un objet dans la base de données en fonction de son ID (id_value).
    Retourner les données de l'objet supprimé sous forme de dictionnaire.

    Utilisation typique :
    - Dans une API REST, pour gérer la suppression d'un objet (ex: DELETE /user/123).
    - Permet de factoriser la logique de suppression pour tous les modèles de la base de données.
    - Utile pour retourner à l'utilisateur les données de l'objet supprimé (pour affichage ou audit).

    Paramètres :
    module_name : Nom du module contenant le modèle.
    object_type : Nom du modèle SQLAlchemy.
    id_value : Identifiant de l'objet à supprimer.
    """

    # Récupère le schéma Marshmallow associé au modèle (pour sérialiser l'objet supprimé)
    schema = definitions.get_schema_from_definition(module_name, object_type)

    # Récupère l'objet à supprimer en fonction de son ID
    res = get_object_type(module_name, object_type, id_value)

    # Si l'objet n'existe pas, retourne None (rien à supprimer)
    if not res:
        return None

    # Sérialise l'objet en dictionnaire (sans les relations)
    # Utile pour retourner les données à l'utilisateur après suppression
    out = schema().dump(res)

    try:
        # Supprime l'objet de la session SQLAlchemy
        DB.session.delete(res)
        # Valide la suppression en base de données
        DB.session.commit()
    except Exception as e:
        # En cas d'erreur lors de la suppression, affiche un message (à améliorer pour la gestion d'erreur)
        print("Erreur lors de la suppression de l'objet : ", e)

    # Retourne les données de l'objet supprimé
    return out
