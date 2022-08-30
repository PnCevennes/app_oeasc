from flask_sqlalchemy import SQLAlchemy

from flask_mail import Mail

from pathlib import Path

# from .config import config

DB = SQLAlchemy()
mail = Mail()

ROOT_DIR = Path(__file__).absolute().parent.parent.parent

# URL_REDIRECT = "{}/{}".format(config.URL_APPLICATION, "oeasc/login")

DEFAULT_CONFIG_FILE = ROOT_DIR / "config/oeasc_config.toml"