"""
decorator
"""

from functools import wraps
from flask import session
from .definitions import GenericRouteDefinitions

definitions = GenericRouteDefinitions()


def check_object_type(droit_type):
    """
    Décorateur qui vérifie si l'utilisateur a les droits pour accéder à la route.
    Utilisation : à placer au-dessus d'une fonction de route Flask pour restreindre l'accès selon le type d'objet et le niveau de droit.
    Exemple :
        @check_object_type("lecture")
        def ma_route(...):
            ...
    """

    def check_object_type_(fn):
        @wraps(fn)
        def check_object_type__(*args, **kwargs):
            # Récupère le nom du module depuis les arguments de la route
            module_name = kwargs.get("module_name")
            # Récupère le type d'objet depuis les arguments, ou le dernier élément de "object_types"
            object_type = kwargs.get("object_type") or kwargs.get("object_types")[:-1]
            # Récupère l'utilisateur courant depuis la session Flask
            current_user = session.get("current_user", {})

            # Vérifie que le module existe dans les définitions
            module = definitions.get_module(module_name)
            if not module:
                # Cas où le module n'est pas défini : accès refusé
                return ("pas de module défini pour {}".format(module_name), 403)

            # Vérifie que le type d'objet existe dans le module
            object_definition = definitions.get_object_type(module_name, object_type)
            if not object_definition:
                # Cas où l'objet n'est pas défini : accès refusé
                return (
                    "pas d'object défini pour {} {}".format(module_name, object_type),
                    403,
                )

            # Vérifie que des droits sont définis pour le type de droit demandé
            id_droit_max_object_type = object_definition.get("droits", {}).get(
                droit_type, None
            )
            if id_droit_max_object_type is None:
                # Cas où aucun droit n'est défini pour ce type de droit : accès refusé
                return (
                    "pas de droits définis en {} pour la route {} {} : route fermée".format(
                        droit_type, module_name, object_type
                    ),
                    403,
                )

            # Récupère le niveau de droit maximal de l'utilisateur courant, ou 0 si non connecté
            id_droit_max_user = current_user["max_level_profil"] if current_user else 0

            # Vérifie que l'utilisateur a un niveau de droit suffisant
            if id_droit_max_user < id_droit_max_object_type:
                # Cas où le niveau de droit est insuffisant : accès refusé
                return (
                    "pas de droit suffisant pour {} en {} : ({} < {})".format(
                        object_type,
                        droit_type,
                        id_droit_max_user,
                        id_droit_max_object_type,
                    ),
                    403,
                )
            # Si toutes les vérifications sont passées, exécute la fonction de route
            return fn(*args, **kwargs)

        return check_object_type__

    return check_object_type_
