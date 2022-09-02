"""
    fichier server app oeasc
"""

import json
import re

from flask import Flask, redirect, session, request, url_for, send_from_directory
from jinja2 import evalcontextfilter, Markup, escape

from app.utils.config import config
from app.utils.env import DB, mail

from flask_cors import CORS

if config.get("SENTRY_DSN"):
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration

    sentry_sdk.init(
        config.get("SENTRY_DSN"),
        integrations=[FlaskIntegration()],
        traces_sample_rate=1.0,
    )


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

app.config.update(config)

cors = CORS(app, resources={r"*": {"origins": "*"}}, supports_credentials=True)


# app.wsgi_app = ReverseProxied(app.wsgi_app)


# Emails configuration
if app.config.get("MAIL_CONFIG"):
    conf = app.config.copy()
    conf.update(app.config.get("MAIL_CONFIG"))
    app.config = conf
    mail.init_app(app)


DB.init_app(app)

app.config["DB"] = DB
app.config["MAIL"] = mail


@app.route("/oeasc/", defaults={"text": ""})
@app.route("/oeasc/<path:text>")
def redirect_front(text):
    return redirect("/front/", code=302)


@app.route("/google4b0945b8a2f6425f.html")
def google():
    return redirect(url_for("static", filename="google4b0945b8a2f6425f.html"))


with app.app_context():

    from app.modules.oeasc.user.mail import function_dict

    app.config["after_USERSHUB_request"] = function_dict

    from app.modules.oeasc.utils import utils_dict

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

    from app.ref_geo import api as ref_geo_api

    app.register_blueprint(ref_geo_api.bp, url_prefix="/api/ref_geo")

    from app.modules.oeasc.user import api as api_user

    app.register_blueprint(api_user.bp, url_prefix="/api/user")

    from app.modules.oeasc import api as oeasc_api

    app.register_blueprint(oeasc_api.bp, url_prefix="/api/oeasc")

    from app.modules.oeasc.declaration import api as declaration_api

    app.register_blueprint(declaration_api.bp, url_prefix="/api/declaration")

    from app.modules.oeasc.degat_foret import api as degat_foret_api

    app.register_blueprint(degat_foret_api.bp, url_prefix="/api/degat_foret")

    from app.modules.oeasc.resultat import api as resultats_api

    app.register_blueprint(resultats_api.bp, url_prefix="/api/resultat")

    from app.modules.oeasc.commons import api as commons_api

    app.register_blueprint(commons_api.bp, url_prefix="/api/commons")

    from app.modules.oeasc.generic import api as generic_api

    app.register_blueprint(generic_api.bp, url_prefix="/api/generic")

    from app.modules.oeasc.i_n import api as in_api

    app.register_blueprint(in_api.bp, url_prefix="/api/in")

    from app.modules.oeasc.chasse import api as chasse_api

    app.register_blueprint(chasse_api.bp, url_prefix="/api/chasse")

    from pypnusershub import routes

    app.register_blueprint(routes.routes, url_prefix="/pypn/auth")

    from pypnusershub import routes_register

    app.register_blueprint(routes_register.bp, url_prefix="/pypn/register")

    from pypnnomenclature.routes import routes

    app.register_blueprint(routes, url_prefix="/api/nomenclatures")

    from app.modules.oeasc.commands import commands

    for cmd in commands:
        app.cli.add_command(cmd)


if __name__ == "__main__":
    app.run(debug=config.DEBUG, port=config.PORT)

_paragraph_re = re.compile(r"(?:\r\n|\r|\n){2,}")


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = "\n\n".join(
        "<p>%s</p>" % p.replace("\n", "<br>\n") for p in _paragraph_re.split(escape(value))
    )
    if eval_ctx.autoescape:
        result = Markup(result)
    return result


@app.template_filter()
@evalcontextfilter
def nopar(eval_ctx, value):

    if not value:

        return ""

    s2 = re.sub(r"\(.*\)", "", value)
    s2 = s2.strip()
    return s2


@app.template_filter()
@evalcontextfilter
def cleanid(eval_ctx, value):

    if not value:

        return ""

    s2 = value.replace(" ", "")
    s2 = s2.replace(".", "")
    s2 = s2.strip()
    return s2
