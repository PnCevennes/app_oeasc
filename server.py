from flask import Flask, redirect, session, request

import json

# from flask_sqlalchemy import SQLAlchemy

from app.utils.env import DB
from config import config

from app.modules.oeasc.utils import utils_dict

""" Serveur de l'application Suivi autorisations """


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

# app.config['SQLALCHEMY_ECHO'] = True

DB.init_app(app)

# import pdb; pdb.set_trace()


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

    from pypnusershub import routes
    app.register_blueprint(routes.routes, url_prefix='/pypn/auth')

    from app.ref_geo import api as ref_geo_api
    app.register_blueprint(ref_geo_api.bp, url_prefix='/api/ref_geo')

    from app.modules.oeasc import routes as oeasc_routes
    app.register_blueprint(oeasc_routes.bp, url_prefix='/oeasc')

    from app.modules.oeasc import api as oeasc_api
    app.register_blueprint(oeasc_api.bp, url_prefix='/api/oeasc')

    from app.modules.oeasc import api_test as api_test
    app.register_blueprint(api_test.bp, url_prefix='/api_test')

    from app.modules.oeasc import route_test as route_test
    app.register_blueprint(route_test.bp, url_prefix='/test')

    from pypnnomenclature.routes import routes
    app.register_blueprint(routes, url_prefix='/api/nomenclatures')


if __name__ == '__main__':
    app.run(debug=config.DEBUG, port=config.PORT)


app.jinja_env.globals["utils"] = utils_dict()
