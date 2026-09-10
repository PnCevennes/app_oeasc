"""
decorator
"""

from functools import wraps
from flask import session, current_app
from .definitions import GenericRouteDefinitions

definitions = GenericRouteDefinitions()


def _forbidden(system_error, message=None):
    """
    Réponse 403 uniforme et compréhensible.
    `message` : phrase affichée à l'utilisateur (sans jargon).
    `system_error` : détail technique, ajouté uniquement en mode développement.
    """
    payload = {
        "success": False,
        "message": message
        or "Vous n'avez pas les droits nécessaires pour effectuer cette action.",
        "code": 403,
    }
    if current_app.config.get("DEBUG") or current_app.config.get("MODE_DEVELOPPEMENT"):
        payload["system_error"] = system_error
    return (payload, 403)


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
                return _forbidden(
                    "pas de module défini pour {}".format(module_name),
                    "Cette page n'est pas disponible (module inconnu).",
                )

            # Vérifie que le type d'objet existe dans le module
            object_definition = definitions.get_object_type(module_name, object_type)
            if not object_definition:
                # Cas où l'objet n'est pas défini : accès refusé
                return _forbidden(
                    "pas d'object défini pour {} {}".format(module_name, object_type),
                    "Cette donnée n'est pas disponible (type inconnu).",
                )

            # Vérifie que des droits sont définis pour le type de droit demandé
            id_droit_max_object_type = object_definition.get("droits", {}).get(
                droit_type, None
            )
            if id_droit_max_object_type is None:
                # Cas où aucun droit n'est défini pour ce type de droit : accès refusé
                return _forbidden(
                    "pas de droits définis en {} pour la route {} {} : route fermée".format(
                        droit_type, module_name, object_type
                    ),
                    "Cette action n'est pas autorisée sur cette donnée.",
                )

            # Récupère le niveau de droit maximal de l'utilisateur courant, ou 0 si non connecté
            id_droit_max_user = current_user["max_level_profil"] if current_user else 0

            # Vérifie que l'utilisateur a un niveau de droit suffisant
            if id_droit_max_user < id_droit_max_object_type:
                # Cas où le niveau de droit est insuffisant : accès refusé
                message = "Vous n'avez pas les droits nécessaires pour effectuer cette action."
                if not current_user:
                    message = (
                        "Vous devez être connecté pour effectuer cette action. "
                        "Merci de vous reconnecter."
                    )
                return _forbidden(
                    "pas de droit suffisant pour {} en {} : ({} < {})".format(
                        object_type,
                        droit_type,
                        id_droit_max_user,
                        id_droit_max_object_type,
                    ),
                    message,
                )
            # Si toutes les vérifications sont passées, exécute la fonction de route
            return fn(*args, **kwargs)

        return check_object_type__

    return check_object_type_
