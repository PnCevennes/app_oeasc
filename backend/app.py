"""
    fichier server app oeasc
"""

###########################
# pour la migration vers sqlalchemy 2.0. affiche les warnings
import os
import warnings
from sqlalchemy import exc
os.environ["PYTHONWARNINGS"] = "always"
os.environ["SQLALCHEMY_WARN_20"] = "1"
warnings.simplefilter("always", exc.SAWarning)


##########################
# import sys
# base_path = os.path.abspath(os.path.join(os.getcwd(), '..'))
# sys.path.append(os.path.join(base_path, 'config'))

import json
import re
from pathlib import Path
from pkg_resources import iter_entry_points
from flask import Flask, redirect, session, request, url_for, send_from_directory, current_app
from flask_migrate import Migrate
#from jinja2 import evalcontextfilter, Markup, escape n'est plus supporté
from jinja2 import pass_context
from markupsafe import Markup, escape
from oeasc.utils.env import db
# import config
# from ..config import config
from flask_cors import CORS
from pypnusershub.auth import auth_manager
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
# from os import environ
from importlib import import_module

# permet de définir des actions apres l'enregistrement d'un utilisateur (envoi de mail, ...)
from pypnusershub.env import REGISTER_POST_ACTION_FCT

# db = DB 

class ReverseProxied(object):
    def __init__(self, app_in, script_name=None, scheme=None, server=None):
        self.app = app_in
        self.script_name = script_name
        self.scheme = scheme
        self.server = server

    def __call__(self, environ, start_response):
        script_name = environ.get("HTTP_X_SCRIPT_NAME", "") or self.script_name
        if script_name:
            environ["SCRIPT_NAME"] = script_name
            path_info = environ["PATH_INFO"]
            if path_info.startswith(script_name):
                environ["PATH_INFO"] = path_info[len(script_name) :]
        scheme = environ.get("HTTP_X_SCHEME", "") or self.scheme
        if scheme:
            environ["wsgi.url_scheme"] = scheme
        server = environ.get("HTTP_X_FORWARDED_SERVER", "") or self.server
        if server:
            environ["HTTP_HOST"] = server
        return self.app(environ, start_response)

# initiation du framework flask
app = Flask(__name__, template_folder="oeasc/templates", static_folder="../static")

# cors permet de gérer les requetes venant d'autres domaines. * signifie que tout le monde peut se connecter
cors = CORS(app, resources={r"*": {"origins": "*"}}, supports_credentials=True)

# app.wsgi_app = ReverseProxied(app.wsgi_app)

# intégration des données de configuration dans l'application. Mettre silent=True en production
app.config.from_pyfile("../config/config.py", silent=False)

ROOT_DIR = Path(__file__).absolute().parent.parent.parent
app.config["ROOT_DIR"] = ROOT_DIR


app.config["URL_REDIRECT"] = app.config["URL_FRONTEND"] + app.config['REDIRECT_ON_FORBIDDEN']


##################### CONFIGURATION DE SENTRY (appli de monitoring) ############################
# try:
#     sentry_config = app.config["SENTRY_DSN"]
#     if sentry_config:
#         import sentry_sdk
#         from sentry_sdk.integrations.flask import FlaskIntegration

#         sentry_sdk.init(
#             sentry_config,
#             integrations=[FlaskIntegration()],
#             traces_sample_rate=1.0,
#         )
# except AttributeError:
#     pass


##################### CONFIGURATION DE LA BDD ############################

# on force la connexion la config de la base à se faire dans ce module pour pouvoir y ajouter des options nécéssaires
# pour la migration vers sqlalchemy 2.0. On peut retirer la ligne suivante après
# os.environ["FLASK_SQLALCHEMY_DB"] = f"{__name__}.db"

# db_path = os.environ.get("FLASK_SQLALCHEMY_DB")

# if db_path and db_path != f"{__name__}.db":
#     print("èzist")
#     db_module_name, db_object_name = db_path.rsplit(".", 1)
#     db_module = import_module(db_module_name)
#     try:
#         db = getattr(db_module, db_object_name)
#     except AttributeError:
#         raise AttributeError(f"The module '{db_module_name}' does not have an attribute '{db_object_name}'. Ensure the database object is correctly defined.")

#     # Merge the engine options from config.py
#     db.engine.update_execution_options(**app.config['SQLALCHEMY_ENGINE_OPTIONS'])

# else:
#     print("n'existe pas")
    
#     db = SQLAlchemy( engine_options=app.config['SQLALCHEMY_ENGINE_OPTIONS']) # future pour sqlalchemy 2.0
#     os.environ["FLASK_SQLALCHEMY_DB"] = f"{__name__}.db"

#     # pour la migration sqlalchemy 2.0 il faut déclarer la Base
#     # Base = db.Model

# initialisation de sqlalchemy pour Flask. Créé les engines et les sessions
# récupère les paramètres de la base de données dans config.py via app.config
db.init_app(app)

# ajoute l'instance sqlalchemy à la configuration de l'application pour y acceder facilement
app.config["DB"] = db


##################### CONFIGURATION DES MAIL ############################
mail = Mail()
app.config["MAIL"] = mail
# initialisation des parametres de mails. Récupère les paramètres dans config.py via app.config
mail.init_app(app)
# ajoute l'instance mail à la configuration de l'application pour y acceder facilement
app.config["MAIL"] = mail 

# pour signer les cookies de session et proteger contre les attaques CSRF
# inutile c'est déja déclaré dans app.config.from_pyfile("../config/config.py", silent=True)
app.secret_key = app.config['SECRET_KEY']


# configuration et initialisation du gestionnaire d'authentification propre au parc (pypnusershub)
# configure aussi le blueprint de l'authentification
# on utilise le provider local par défaut
providers_config = [
    {
    "module" : "pypnusershub.auth.providers.default.LocalProvider",
    "id_provider":"local_provider"
    },
]
# initialise et integre les route "auth/"
auth_manager.init_app(app,providers_declaration=providers_config)


# initalisation de la gestion de migration alembic
migrate = Migrate()
# on definit le repertoire de migration
migrate.init_app(app, db, directory=Path(__file__).absolute().parent / "oeasc" /"migrations")
@migrate.configure
def configure_alembic(alembic_config):
    """
    This function add to the 'version_locations' parameter of the alembic config the
    'migrations' entry point value of the 'alembic' group for all packages having such entry point.
    Thus, alembic will find migrations provided by all installed packages.
    """
    # Ignore version_locations provided in configuration as TaxHub migrations are also
    # detected by iter_entry_points so we current_app.config["ID_APP"]avoid adding twice
    # version_locations = alembic_config.get_main_option('version_locations', default='').split()
    version_locations = []
    if "ALEMBIC_VERSION_LOCATIONS" in current_app.config:
        version_locations.extend(current_app.config["ALEMBIC_VERSION_LOCATIONS"].split())
    for entry_point in iter_entry_points("alembic", "migrations"):
        _, migrations = str(entry_point).split("=", 1)
        version_locations += [migrations.strip()]
    alembic_config.set_main_option("version_locations", " ".join(version_locations))
    return alembic_config


##################################################################
###################### ROUTES  ###################################
##################################################################

# utilisé par le serveur apache en production. À refaire en plus propre
# @app.route("/oeasc/", defaults={"text": ""})
# @app.route("/oeasc/<path:text>")
# def redirect_front(text):
#     return redirect("/front/", code=302)

# route de verification google
@app.route("/google4b0945b8a2f6425f.html")
def google():
    return redirect(url_for("static", filename="google4b0945b8a2f6425f.html"))

# Importation des routes des modules
# on utilise le contexte de l'application pour pouvoir utiliser les fonctions de l'application
with app.app_context():

    # ajouter à after_USERSHUB_request des fonction qui seront executé après les requetes
    from oeasc.modules.oeasc.user.mail import function_dict
    # ici on ajoute des fonctions d'envoi de mail
    # configuration of post_request actions for registrations
    REGISTER_POST_ACTION_FCT.update(function_dict)
    #app.config["after_USERSHUB_request"] = function_dict # obsolete


    # intègre au générateur de template Jinja des données comme (print_date, get_areas_from_type_code, get_foret_type, get_some_config, to_string)
    from oeasc.modules.oeasc.utils import utils_dict
    app.jinja_env.globals["utils"] = utils_dict

    # gestion d'authentification utilisateur
    @app.after_request
    def after_login_method(response):
        #verifie si le cookie de session est absent
        if not request.cookies.get("token"):
            # l'utilisateur n'est pas connecté
            session["current_user"] = None

        if request.endpoint == "auth.login" and response.status_code == 200:
            # connexion réussie
            if response.get_data().decode("utf-8"):
                # transforme les données de l'utilisateur en dictionnaire
                current_user = json.loads(response.get_data().decode("utf-8"))
                # met a jour la session avec les données de l'utilisateur
                session["current_user"] = current_user["user"]

        return response

    # import du blueprint ref_geo pour les données géographiques (zones, types de zones, communes, coordonnées)
    from oeasc.ref_geo import api as ref_geo_api
    app.register_blueprint(ref_geo_api.bp, url_prefix="/api/ref_geo")

    # import du blueprint user pour la gestion des utilisateurs
    from oeasc.modules.oeasc.user import api as api_user
    app.register_blueprint(api_user.bp, url_prefix="/api/user")

    # retourne principalement des dictionnaire de nomenclatures.
    from oeasc.modules.oeasc import api as oeasc_api
    app.register_blueprint(oeasc_api.bp, url_prefix="/api/oeasc")

    # route des données de la table declaration. Contient les models et les fonctions le lecture
    from oeasc.modules.oeasc.declaration import api as declaration_api
    app.register_blueprint(declaration_api.bp, url_prefix="/api/declaration")

    #routes concernant la déclaration des dégats en forêt. Fait appels aux models contenues dans declaration
    from oeasc.modules.oeasc.degat_foret import api as degat_foret_api
    app.register_blueprint(degat_foret_api.bp, url_prefix="/api/degat_foret")

    # route pour les résultat d'indices nocturnes et resultats du système d'alertes
    from oeasc.modules.oeasc.resultat import api as resultats_api
    app.register_blueprint(resultats_api.bp, url_prefix="/api/resultat")

    # route des communs. Contient le contenu textuel des pages, les tags, la liste des communes avec leur cp
    from oeasc.modules.oeasc.commons import api as commons_api
    app.register_blueprint(commons_api.bp, url_prefix="/api/commons")

    # generic gère des routes dynamiques pour plusieurs modules. Permet d'accéder à des models et de gérér les accès selon les droits utilisateurs
    from oeasc.modules.oeasc.generic import api as generic_api
    app.register_blueprint(generic_api.bp, url_prefix="/api/generic")

    # routes pour les indices nocturnes
    from oeasc.modules.oeasc.i_n import api as in_api
    app.register_blueprint(in_api.bp, url_prefix="/api/in")

    # module de chasse 
    from oeasc.modules.oeasc.chasse import api as chasse_api
    app.register_blueprint(chasse_api.bp, url_prefix="/api/chasse")

    # routes pour l'enregistrement des utilisateurs, changer mots de passe, éditer droits utilisateurs
    from pypnusershub import routes_register
    app.register_blueprint(routes_register.bp, url_prefix="/register")
    

    from pypnnomenclature.routes import routes
    app.register_blueprint(routes, url_prefix="/api/nomenclatures")

    from oeasc.modules.oeasc.commands import commands
    for cmd in commands:
        app.cli.add_command(cmd)


# lancement de l'appli
if __name__ == "__main__":
    app.run(debug=app.config["DEBUG"], port=app.config["PORT"])






# filtre HTML. Modifie les retours à la ligne en BR et le met dans un paragraphe
# utilisé dans les templates de mails
# _paragraph_re = re.compile(r"(?:\r\n|\r|\n){2,}")
# @app.template_filter()
# @pass_context
# def nl2br(eval_ctx, value):
#     result = "\n\n".join(
#         "<p>%s</p>" % p.replace("\n", "<br>\n")
#         for p in _paragraph_re.split(escape(value))
#     )
#     if eval_ctx.autoescape:
#         result = Markup(result)
#     return result


# @app.template_filter()
# @pass_context
# def nopar(eval_ctx, value):
#     if not value:
#         return ""

#     s2 = re.sub(r"\(.*\)", "", value)
#     s2 = s2.strip()
#     return s2


# @app.template_filter()
# @pass_context
# def cleanid(eval_ctx, value):
#     if not value:
#         return ""

#     s2 = value.replace(" ", "")
#     s2 = s2.replace(".", "")
#     s2 = s2.strip()
#     return s2
