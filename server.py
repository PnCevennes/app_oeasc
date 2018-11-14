from flask import Flask, redirect, session, request, url_for

import json

from app.utils.env import DB, mail
from config import config

import re

from jinja2 import evalcontextfilter, Markup, escape


class ReverseProxied(object):

    def __init__(self, app, script_name=None, scheme=None, server=None):
        self.app = app
        self.script_name = script_name
        self.scheme = scheme
        self.server = server

    def __call__(self, environ, start_response):
        script_name = environ.get('HTTP_X_SCRIPT_NAME', '') or self.script_name
        if script_name:
            environ['SCRIPT_NAME'] = script_name
            path_info = environ['PATH_INFO']
            if path_info.startswith(script_name):
                environ['PATH_INFO'] = path_info[len(script_name):]
        scheme = environ.get('HTTP_X_SCHEME', '') or self.scheme
        if scheme:
            environ['wsgi.url_scheme'] = scheme
        server = environ.get('HTTP_X_FORWARDED_SERVER', '') or self.server
        if server:
            environ['HTTP_HOST'] = server
        return self.app(environ, start_response)


app = Flask(__name__, template_folder="app/templates", static_folder='static')

# app.wsgi_app = ReverseProxied(app.wsgi_app)

app.secret_key = 'dtgperçtuiperotivemrtikotiçà80979837589UJ5?OI3J?LORJ?C3LKJVL3V5V35'


app.config.from_pyfile('config/config.py', silent=True)


mail.init_app(app)
DB.init_app(app)

app.config['DB'] = DB
app.config['MAIL'] = mail


def redirect_on_valid_temp_user(dict_in):

    identifiant = dict_in["identifiant"]
    return url_for('oeasc.login', identifiant=identifiant, validation_compte="valid")


app.config['redirect_on_valid_temp_user'] = redirect_on_valid_temp_user
app.config["route_change_password"] = "oeasc.change_password"
# app.config["route_valid_temp_user"] = "register.valid_temp_user"
app.config['template_demande_validation_compte'] = 'modules/oeasc/mail/demande_validation_compte.html'
app.config['template_change_password'] = 'modules/oeasc/mail/change_password.html'


@app.route('/')
def accueil():
    return redirect("/oeasc", code=302)


with app.app_context():

    @app.after_request
    def after_login_method(response):

        if not request.cookies.get('token'):
            session["current_user"] = None

        if request.endpoint == 'auth.login' and response.status_code == 200:
            current_user = json.loads(response.get_data().decode('utf-8'))
            session["current_user"] = current_user["user"]

        return response

    from app.ref_geo import api as ref_geo_api
    app.register_blueprint(ref_geo_api.bp, url_prefix='/api/ref_geo')

    from app.modules.oeasc import routes as oeasc_routes
    app.register_blueprint(oeasc_routes.bp, url_prefix='/oeasc')

    from app.modules.oeasc import api as oeasc_api
    app.register_blueprint(oeasc_api.bp, url_prefix='/api/oeasc')

    from app.modules.oeasc import api_test as api_test
    app.register_blueprint(api_test.bp, url_prefix='/api/test')

    from app.modules.oeasc import route_test as route_test
    app.register_blueprint(route_test.bp, url_prefix='/test')

    from pypnusershub import routes
    app.register_blueprint(routes.routes, url_prefix='/pypn/auth')

    from pypnusershub import routes_register
    app.register_blueprint(routes_register.bp, url_prefix='/pypn/register')

    from pypnnomenclature.routes import routes
    app.register_blueprint(routes, url_prefix='/api/nomenclatures')



if __name__ == '__main__':
    app.run(debug=config.DEBUG, port=config.PORT)


from app.modules.oeasc.utils import utils_dict
app.jinja_env.globals["utils"] = utils_dict()


_paragraph_re = re.compile(r'(?:\r\n|\r|\n){2,}')


@app.template_filter()
@evalcontextfilter
def nl2br(eval_ctx, value):
    result = u'\n\n'.join(u'<p>%s</p>' % p.replace('\n', '<br>\n') \
        for p in _paragraph_re.split(escape(value)))
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


import click
from flask import Flask

from flask_bcrypt import (
    generate_password_hash
)

@app.cli.command()
@click.argument('password')
def password_hash(password):

    password_hash = generate_password_hash(password.encode('utf-8')).decode('utf-8')
    print(password_hash)
