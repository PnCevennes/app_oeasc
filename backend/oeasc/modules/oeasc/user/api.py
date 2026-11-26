"""
api user
"""

from flask import Blueprint, request, redirect, current_app, session, jsonify
from flask_login import login_user
from pypnusershub.schemas import UserSchema
from oeasc.utils.current_user import get_current_user
from utils_flask_sqla.response import json_resp

# from utils_flask_sqla.response import json_resp, json_resp_accept
from .repository import (
    get_user_form_email,
    get_users,
    get_liste_organismes_oeasc,
    admin_update_user,
)
from ..user.utils import check_auth_redirect_login
from . import oidc
from utils_flask_sqla.response import csv_resp

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
    return get_current_user()


@bp.route("oidc/config", methods=["GET"])
def oidc_config():
    """Indique au front si la connexion via Échange est activée."""
    return {"enabled": oidc.is_enabled(), "provider": oidc.provider_name()}


@bp.route("oidc/authorize", methods=["GET"])
def oidc_authorize():
    """
    URL du fournisseur vers laquelle rediriger le navigateur.
    `state` et le `code_verifier` PKCE sont gardés par le front (sessionStorage) ;
    seule l'empreinte (`code_challenge`) est envoyée ici.
    `silencieux=1` : prompt=none, sonde « suis-je connecté à Échange ? » sans page.
    """
    state = request.args.get("state", "")
    code_challenge = request.args.get("code_challenge", "")
    if (
        not oidc.is_enabled()
        or not state
        or not oidc.RE_CHALLENGE.match(code_challenge)
    ):
        return {"err": "oidc unavailable"}, 400
    try:
        return {
            "url": oidc.authorize_url(
                state, code_challenge, silencieux=request.args.get("silencieux") == "1"
            )
        }
    except (OSError, ValueError, KeyError):
        return {"err": "provider unreachable"}, 502


@bp.route("oidc/callback", methods=["POST"])
def oidc_callback():
    """
    Échange le code renvoyé par Échange contre une session OEASC.
    Données POST : {"code": str, "code_verifier": str}
    Retour : même JSON que auth/login ({user, expires, token}), ou 400 / 403 / 502.
    """
    data = request.get_json(silent=True) or {}
    code = str(data.get("code") or "")
    code_verifier = str(data.get("code_verifier") or "")
    if not oidc.is_enabled() or not code or not oidc.RE_VERIFIER.match(code_verifier):
        return {"err": "oidc unavailable"}, 400
    try:
        user = oidc.find_user(oidc.exchange_code(code, code_verifier))
    except oidc.InvalidAuthError:
        return {"err": "invalid auth"}, 403
    except (OSError, ValueError):
        return {"err": "provider unreachable"}, 502

    # même ouverture de session que auth/login (cookie « token » remember-me de flask-login)
    login_user(user, remember=True)
    # permet à auth/logout (qui exige un provider en session) de fonctionner
    session["current_provider"] = "local_provider"
    result = UserSchema(
        exclude=["remarques"], only=["+max_level_profil", "+providers"]
    ).dump_with_token(user)
    # équivalent de after_login_method (app.py), qui ne reconnaît que l'endpoint auth.login
    session["current_user"] = result["user"]
    return jsonify(result)


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
    params = (
        request.args
    )  # Récupère les paramètres de la requête (ex: ?redirect=/autre_page)
    if "redirect" in params:
        resp = redirect(
            params["redirect"], code=302
        )  # Redirige vers l'URL passée en paramètre
    else:
        resp = redirect("/", code=302)  # Redirige vers la page d'accueil par défaut
    resp.delete_cookie("token")  # Supprime le cookie d'authentification "token"
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

    columns = list(
        data[0].keys()
    )  # Définit les colonnes du CSV à partir des clés du premier utilisateur

    return (
        file_name,
        data,
        columns,
        separator,
    )  # Retourne les informations nécessaires à l'export CSV


@bp.route("/admin_update/<int:id_role>", methods=["POST"])
@check_auth_redirect_login(4)
@json_resp
def api_admin_update_user(id_role):
    """
    Modification par un administrateur (droit >= 4) de l'e-mail (= identifiant de connexion),
    de l'organisme et/ou du rôle d'un utilisateur de droit strictement inférieur.
    Retourne l'utilisateur mis à jour.
    """
    data = request.get_json() or {}
    user, error = admin_update_user(
        id_role, data, get_current_user().get("id_role")
    )
    if error:
        return {"message": error[0]}, error[1]
    return user
