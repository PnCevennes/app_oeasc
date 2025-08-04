"""
décorateur de route qui verifie si l'utilisateur est connecté
et redirige vers la page requise apres authentification
"""

from functools import wraps
from pypnusershub import routes as fnauth
from flask import current_app

config = current_app.config


def check_auth_redirect_login(level):
    """
    Décorateur qui vérifie le niveau d'authentification de l'utilisateur avant d'accéder à une route.
    Si l'utilisateur n'a pas le niveau requis, il est redirigé vers la page de login.
    Utilisation typique : protéger une route Flask qui nécessite une authentification spécifique.
    Exemple :
        @check_auth_redirect_login("admin")
        def route_admin():
            ...
    Args:
        level (str): Niveau d'authentification requis (ex: "user", "admin").
    Returns:
        function: Décorateur à appliquer sur la route.
    """

    def _check_auth_redirect_login(f):
        @wraps(f)
        def __check_auth_redirect_login(*args, **kwargs):
            # Ici, on pourrait personnaliser la redirection en cas d'échec d'authentification,
            # par exemple vers une page d'erreur ou une page de login avec l'URL demandée en paramètre.
            # Les lignes suivantes sont commentées mais montrent comment faire :
            # redirect_url = "/user/login_error"
            # redirect_url = '/user/login?redirect="{}{}"'.format(
            #     config["URL_APPLICATION"], request.path
            # )
            # return fnauth.check_auth(level, False, redirect_url)(f)(*args, **kwargs)

            # Appel de la fonction d'authentification du module fnauth.
            # Si l'utilisateur est authentifié avec le bon niveau, la route est exécutée.
            # Sinon, l'utilisateur est redirigé selon la configuration de fnauth.
            return fnauth.check_auth(level)(f)(*args, **kwargs)

        return __check_auth_redirect_login

    return _check_auth_redirect_login
