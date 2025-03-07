"""
    fichier server app oeasc
"""

import json
import re

from pathlib import Path
from pkg_resources import iter_entry_points
from flask import Flask, redirect, session, request, url_for, send_from_directory, current_app
from flask_migrate import Migrate
#from jinja2 import evalcontextfilter, Markup, escape n'est plus supporté
from jinja2 import pass_context

from markupsafe import Markup, escape
from oeasc.utils.env import DB, mail
from config import config
from flask_cors import CORS
from pypnusershub.auth import auth_manager


# Configure sentry if var SENTRY_DSN is set in config
try:
    sentry_config = config.SENTRY_DSN
    if sentry_config:
        import sentry_sdk
        from sentry_sdk.integrations.flask import FlaskIntegration

        sentry_sdk.init(
            sentry_config,
            integrations=[FlaskIntegration()],
            traces_sample_rate=1.0,
        )
except AttributeError:
    pass


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


app = Flask(__name__, template_folder="app/templates", static_folder="static")

cors = CORS(app, resources={r"*": {"origins": "*"}}, supports_credentials=True)


# app.wsgi_app = ReverseProxied(app.wsgi_app)

app.secret_key = "dfsdbegerbnergfbergqbqerg"

app.config.from_pyfile("../config/config.py", silent=True)
mail.init_app(app)
DB.init_app(app)

app.config["DB"] = DB
app.config["MAIL"] = mail 

providers_config = [
    {
    "module" : "pypnusershub.auth.providers.default.LocalProvider",
    "id_provider":"local_provider"
    },
]
auth_manager.init_app(app,providers_declaration=providers_config)


migrate = Migrate()


migrate.init_app(app, DB, directory=Path(__file__).absolute().parent / "oeasc" /"migrations")

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


@app.route("/oeasc/", defaults={"text": ""})
@app.route("/oeasc/<path:text>")
def redirect_front(text):
    return redirect("/front/", code=302)


@app.route("/google4b0945b8a2f6425f.html")
def google():
    return redirect(url_for("static", filename="google4b0945b8a2f6425f.html"))


with app.app_context():
    from oeasc.modules.oeasc.user.mail import function_dict

    app.config["after_USERSHUB_request"] = function_dict


    from oeasc.modules.oeasc.utils import utils_dict

    app.jinja_env.globals["utils"] = utils_dict

    @app.after_request
    def after_login_method(response):
        if not request.cookies.get("token"):
            session["current_user"] = None

        if request.endpoint == "auth.login" and response.status_code == 200:
            if response.get_data().decode("utf-8"):
                current_user = json.loads(response.get_data().decode("utf-8"))
                session["current_user"] = current_user["user"]

        return response

    from oeasc.ref_geo import api as ref_geo_api

    app.register_blueprint(ref_geo_api.bp, url_prefix="/api/ref_geo")

    from oeasc.modules.oeasc.user import api as api_user

    app.register_blueprint(api_user.bp, url_prefix="/api/user")

    from oeasc.modules.oeasc import api as oeasc_api

    app.register_blueprint(oeasc_api.bp, url_prefix="/api/oeasc")

    from oeasc.modules.oeasc.declaration import api as declaration_api

    app.register_blueprint(declaration_api.bp, url_prefix="/api/declaration")

    from oeasc.modules.oeasc.degat_foret import api as degat_foret_api

    app.register_blueprint(degat_foret_api.bp, url_prefix="/api/degat_foret")

    from oeasc.modules.oeasc.resultat import api as resultats_api

    app.register_blueprint(resultats_api.bp, url_prefix="/api/resultat")

    from oeasc.modules.oeasc.commons import api as commons_api

    app.register_blueprint(commons_api.bp, url_prefix="/api/commons")

    from oeasc.modules.oeasc.generic import api as generic_api

    app.register_blueprint(generic_api.bp, url_prefix="/api/generic")

    from oeasc.modules.oeasc.i_n import api as in_api

    app.register_blueprint(in_api.bp, url_prefix="/api/in")

    from oeasc.modules.oeasc.chasse import api as chasse_api

    app.register_blueprint(chasse_api.bp, url_prefix="/api/chasse")

    from pypnusershub import routes_register

    app.register_blueprint(routes_register.bp, url_prefix="/pypn/register")

    from pypnnomenclature.routes import routes

    app.register_blueprint(routes, url_prefix="/api/nomenclatures")

    from oeasc.modules.oeasc.commands import commands

    for cmd in commands:
        app.cli.add_command(cmd)




if __name__ == "__main__":
    app.run(debug=config.DEBUG, port=config.PORT)

_paragraph_re = re.compile(r"(?:\r\n|\r|\n){2,}")


@app.template_filter()
@pass_context
def nl2br(eval_ctx, value):
    result = "\n\n".join(
        "<p>%s</p>" % p.replace("\n", "<br>\n")
        for p in _paragraph_re.split(escape(value))
    )
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


@app.template_filter()
@pass_context
def nopar(eval_ctx, value):
    if not value:
        return ""

    s2 = re.sub(r"\(.*\)", "", value)
    s2 = s2.strip()
    return s2


@app.template_filter()
@pass_context
def cleanid(eval_ctx, value):
    if not value:
        return ""

    s2 = value.replace(" ", "")
    s2 = s2.replace(".", "")
    s2 = s2.strip()
    return s2
