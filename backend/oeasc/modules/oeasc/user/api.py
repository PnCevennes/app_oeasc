"""
api user
"""

from flask import Blueprint, request, redirect, current_app, session
from utils_flask_sqla.response import json_resp

# from utils_flask_sqla.response import json_resp, json_resp_accept
from .repository import get_user_form_email, get_users, get_liste_organismes_oeasc
from ..user.utils import check_auth_redirect_login
from utils_flask_sqla.response import csv_resp


config = current_app.config

bp = Blueprint("user_api", __name__)



@bp.route("test", methods=["GET"])
@json_resp
def api_test():
    """
    Route pour tester la connexion à l'application.

    Cette fonction est utilisée pour vérifier si un utilisateur est actuellement connecté.
    Elle retourne le contenu de la session sous la clé "current_user".
    Utile pour les tests d'intégration ou pour vérifier l'état de connexion côté frontend.
    """
    return session.get("current_user")


@bp.route("login_error", methods=["GET"])
@json_resp
def login_error():
    return "login error", 403


@bp.route("organismes", methods=["GET"])
@json_resp
def api_organimes():
    return get_liste_organismes_oeasc()


@bp.route("/logout_external", methods=["GET", "POST"])
@json_resp
def logout_external():
    """
    Déconnexion externe de l'utilisateur.

    Cette fonction est appelée lorsqu'un utilisateur souhaite se déconnecter via une route externe à l'application principale.
    Elle est utile dans le cas où la déconnexion doit être gérée côté frontend ou par une application tierce, sans redirection automatique.
    Elle supprime l'utilisateur courant de la session en mettant la clé "current_user" à None.

    Retourne :
        Un message JSON confirmant la déconnexion.
    """
    session["current_user"] = None  # Suppression de l'utilisateur courant de la session

    return {"msg": "logout ok"}  # Message de confirmation


@bp.route("/logout", methods=["GET", "POST"])
def logout():
    """
    Déconnexion de l'utilisateur avec redirection.

    Cette fonction est appelée lorsqu'un utilisateur souhaite se déconnecter via la route "/logout".
    Elle supprime le cookie "token" du navigateur pour invalider la session côté client.
    Si un paramètre "redirect" est présent dans l'URL, l'utilisateur est redirigé vers cette adresse.
    Sinon, il est redirigé vers la page d'accueil "/".

    Utilisation typique :
        - Lorsqu'un utilisateur clique sur "Déconnexion" dans l'interface.
        - Lorsqu'une application tierce souhaite forcer la déconnexion et rediriger l'utilisateur.

    Retourne :
        Une réponse HTTP de redirection vers l'URL spécifiée ou la racine.
    """
    params = request.args  # Récupère les paramètres de la requête (ex: ?redirect=/autre_page)
    resp.delete_cookie("token")  # Supprime le cookie d'authentification "token"
    if "redirect" in params:
        resp = redirect(params["redirect"], code=302)  # Redirige vers l'URL passée en paramètre
    else:
        resp = redirect("/", code=302)  # Redirige vers la page d'accueil par défaut
    return resp  # Retourne la réponse de redirection


@bp.route("/get_user_from_email/<email>", methods=["GET"])
@json_resp
def api_get_user_from_mail(email):
    """
    Récupère les informations d'un utilisateur à partir de son adresse email.

    Cette route est utilisée pour obtenir les détails d'un utilisateur en fournissant son email dans l'URL.
    Elle est utile dans les cas suivants :
        - Lorsqu'une application frontend souhaite afficher les informations d'un utilisateur à partir de son email.
        - Lorsqu'un processus d'authentification ou de vérification nécessite de récupérer les données utilisateur via l'email.
        - Pour des intégrations avec des systèmes externes qui identifient les utilisateurs par leur adresse email.

    Paramètres :
        email (str) : L'adresse email de l'utilisateur à rechercher.

    Retourne :
        Un dictionnaire contenant les informations de l'utilisateur correspondant à l'email fourni,
        ou None si aucun utilisateur n'est trouvé.
    """
    return get_user_form_email(email)


@bp.route("/user_information/<int:id_role>", methods=["GET"])
@check_auth_redirect_login(1)
@json_resp
def api_get_user(id_role):
    """
    Récupère les informations d'un utilisateur à partir de son id_role.

    Cette route permet d'obtenir les détails d'un utilisateur en fournissant son identifiant de rôle (id_role) dans l'URL.
    Elle est utile dans les cas suivants :
        - Lorsqu'une application frontend souhaite afficher les informations d'un utilisateur à partir de son id_role.
        - Lorsqu'un processus d'authentification ou de gestion des rôles nécessite de récupérer les données utilisateur via l'id_role.
        - Pour des intégrations avec des systèmes externes qui identifient les utilisateurs par leur rôle.

    Paramètres :
        id_role (int) : L'identifiant du rôle de l'utilisateur à rechercher.

    Retourne :
        Un dictionnaire contenant les informations de l'utilisateur correspondant à l'id_role fourni,
        ou None si aucun utilisateur n'est trouvé.
    """
    users = get_users()  # Récupère la liste de tous les utilisateurs
    out = None  # Variable pour stocker l'utilisateur trouvé
    for user in users:
        # Parcourt chaque utilisateur et vérifie si l'id_role correspond à celui demandé
        if user["id_role"] == id_role:
            out = user  # Si trouvé, stocke l'utilisateur

    return out  # Retourne l'utilisateur trouvé ou None si aucun ne correspond


@bp.route("/users", methods=["GET"])
@check_auth_redirect_login(1)
@json_resp
def api_get_users():
    """
    api_get_users
    """
    return get_users()


@bp.route("/export", methods=["GET"])
@check_auth_redirect_login(1)
@csv_resp
def api_export_user():
    """
    Exportation des utilisateurs au format CSV.

    Cette fonction est utilisée pour exporter la liste des utilisateurs sous forme de fichier CSV.
    Elle est utile dans les cas suivants :
        - Lorsque l'administrateur souhaite télécharger la liste complète des utilisateurs pour analyse ou archivage.
        - Pour des besoins d'intégration avec des outils externes nécessitant un export CSV.
        - Pour la génération de rapports ou la migration de données.

    Fonctionnement :
        - Récupère la liste des utilisateurs via la fonction get_users().
        - Définit le nom du fichier exporté et le séparateur utilisé dans le CSV.
        - Utilise les clés du premier utilisateur comme colonnes du fichier CSV.

    Retourne :
        Un tuple contenant le nom du fichier, les données à exporter, les colonnes et le séparateur.
        Le décorateur @csv_resp se charge de la conversion et de la réponse HTTP.
    """
    file_name = "export_user_oeasc"  # Nom du fichier CSV exporté
    separator = ";"  # Séparateur utilisé dans le fichier CSV

    data = get_users()  # Récupère la liste des utilisateurs

    columns = list(data[0].keys())  # Définit les colonnes du CSV à partir des clés du premier utilisateur

    return (file_name, data, columns, separator)  # Retourne les informations nécessaires à l'export CSV
