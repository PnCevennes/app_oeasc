
# # @TOCLEAN : NOT USE => fichier non chargé
"""
    routes pour les utilisateurs
"""
from flask import (
    Blueprint,
    render_template,
    request,
    session,
    url_for,
    redirect,
    current_app,
)
from pypnusershub.db.models import User

from app.modules.oeasc.nomenclature import nomenclature_oeasc
from .repository import (
    get_liste_organismes_oeasc,
    get_users,
    get_user,
)
from .utils import check_auth_redirect_login

config = current_app.config

bp = Blueprint("user", __name__)


# @TOCLEAN : NOT USE => modules/oeasc/user/* n'existe pas
# @bp.route("/users")
# @check_auth_redirect_login(4)
# def route_users():
#     """
#     liste des utilisateurs
#     possibilité de modifier les droits des utilisateurs
#     """
#     current_user = session["current_user"]

#     users = get_users()

#     return render_template(
#         "modules/oeasc/user/users.html",
#         users=users,
#         current_user=current_user,
#         config=config,
#     )


# @bp.route("/espace_personnel")
# @check_auth_redirect_login(1)
# def espace_personnel():
#     """
#     accès à l'espace personnel
#     redirection vers la route user en s'assurant d'être connecté
#     """
#     return redirect(url_for("user.route_user"))


# @bp.route("/", defaults={"id_user": 0})
# @bp.route("/<int:id_user>")
# # @check_auth_redirect_login(1)
# def route_user(id_user):
#     """
#     Route pour les informations de l'utilisateur
#     ou pour le login ( si id_user vide ou 0)
#     """

#     user = None
#     modify = False

#     current_user = session.get("current_user", None)

#     # current user
#     if not id_user and current_user:

#         id_user = current_user["id_role"]
#         user = get_user(id_user)
#         modify = True

#     # register
#     elif not id_user:

#         user = User().as_dict()

#     # user plus pour les responsable?
#     elif id_user and current_user:

#         user = get_user(id_user)

#         cond_org = (
#             current_user["id_droit_max"] >= 3
#             and current_user["id_organisme"] == user["id_organisme"]
#         )

#         if not current_user["id_droit_max"] >= 4 and not cond_org:

#             user = None

#         modify = (
#             current_user["id_role"] == user["id_role"]
#             or current_user["id_droit_max"] >= 5
#         )

#     return render_template(
#         "modules/oeasc/user/user.html",
#         user=user,
#         current_user=user,
#         modify=modify,
#         nomenclature=nomenclature_oeasc(),
#         config=config,
#         liste_organismes_oeasc=get_liste_organismes_oeasc(),
#     )


# @bp.route("/login")
# def login():
#     """
#     page de connection
#     """

#     browser = request.user_agent.browser

#     redirect_url = request.args.get("redirect", "")
#     token = request.args.get("token", "")
#     identifiant = request.args.get("identifiant", "")
#     type_login = request.args.get("type", "")

#     return render_template(
#         "modules/oeasc/user/login.html",
#         config=config,
#         redirect_url=redirect_url,
#         token=token,
#         identifiant=identifiant,
#         type=type_login,
#         browser=browser,
#     )


# @bp.route("/change_password/", defaults={"token": ""}, methods=["GET"])
# @bp.route("/change_password/<string:token>", methods=["GET"])
# def change_password(token):
#     """
#     page pour recreer un mot de passe
#     """

#     return render_template(
#         "modules/oeasc/user/change_password.html", config=config, token=token
#     )
