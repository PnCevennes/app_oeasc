"""
décorateur de route qui verifie si l'utilisateur est connecté
et redirige vers la page requise apres authentification
"""

from functools import wraps
from pypnusershub import routes as fnauth
from flask import current_app, session, redirect
from flask_login import current_user


from oeasc.modules.oeasc.declaration.repository import check_token_renouvellement_declaration

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
            print ("session in check_auth_redirect_login:", session)
            #si il existe un temp_user dans la session, on verifie si le token est valide

            if ((session.get("temp_user", None)) and ((session['current_user'] == "") or (session['current_user'] is None))):
                print ("temp_user in session:", session["temp_user"])
                token = session["temp_user"].get("token", None)
                id_verification = session["temp_user"].get("id_verification", None)
                mode = session["temp_user"].get("mode", None)
                if token and id_verification and mode:
                    if mode == "renouvellement_declaration":
                        response = check_token_renouvellement_declaration(id_declaration=id_verification, token=token, session=session)
                    
                    # si le check a reussi et que la reponse (apiResponse) est un succès
                    if ((response) and (response.success == True)):
                        # Si le token est valide, on connecte l'utilisateur temporaire pour cette requête
                        # print ("Token de renouvellement de déclaration valide. Utilisateur temporaire connecté pour cette requête.")
                        return f(*args, **kwargs)
                    else:
                       return redirect(current_app.config["REDIRECT_ON_FORBIDDEN"]) 
                else:
                    # print ("Token de renouvellement de déclaration invalide ou informations manquantes. Redirection vers la page de login.")
                    #redirection vers la page de login avec un message d'erreur
                    return redirect(current_app.config["REDIRECT_ON_FORBIDDEN"])

            else: # mode normal. On vérifie si l'utilisateur est connecté et a le niveau requis
                # si il existe un temp_user on le supprime
                if session.get("temp_user", None):
                    print ("Suppression de temp_user de la session:", session["temp_user"])
                    session.pop("temp_user", None)
                return fnauth.check_auth(level)(f)(*args, **kwargs)

        return __check_auth_redirect_login

    return _check_auth_redirect_login
