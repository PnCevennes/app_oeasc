"""
    Fonctions à utilisé danbs Jinja
    ex: utils.print_date pour afficher la date au format jour-mois-année
"""
from dateutil import parser
from flask import current_app

# from .repository import get_db
from .declaration.repository import get_foret_type
from .declaration.utils import get_areas_from_type_code

config = current_app.config
DB = config['DB']


def print_date(s_date):
    """
        pour affichage dans tableau
    """
    if not s_date:
        return ''
    return parser.parse(s_date).strftime("%d/%m/%Y")


def get_some_config(config_text):
    """
        pour avoir des elements de config dans jinja
    """
    keys = [
        "ID_APP",
        "MODE_TEST",
        "URL_USERSHUB",
        "URL_APPLICATION",
    ]

    return {k: v for k, v in config_text.items() if k in keys}


def to_string(x):
    """
        patch jinja
    """
    return str(x)


utils_dict = {
    # "get_db": get_db,
    'print_date': print_date,
    'get_areas_from_type_code': get_areas_from_type_code,
    'get_foret_type': get_foret_type,
    'get_some_config': get_some_config,
    'to_string': to_string
}
