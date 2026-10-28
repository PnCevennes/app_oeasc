"""
Lecture de l'utilisateur connecté dans la session Flask.
Module sans dépendance sur le reste de l'application (pas d'import circulaire possible).
"""

from flask import has_request_context, session as flask_session


def get_current_user(session=None):
    """
    Retourne le dictionnaire de l'utilisateur connecté (clé "current_user" de la session),
    ou {} s'il n'y en a pas (non connecté, hors contexte de requête, valeur vide).

    :param session: session à lire à la place de celle de la requête (optionnel, ex : tests,
        fonctions qui reçoivent déjà la session en paramètre)
    """
    if session is None:
        if not has_request_context():
            return {}
        session = flask_session

    try:
        user = session.get("current_user")
    except Exception:
        return {}

    return user if isinstance(user, dict) else {}
