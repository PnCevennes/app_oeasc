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
DB = config["DB"]


def print_date(s_date):
    """
    pour affichage dans tableau
    """
    if not s_date:
        return ""
    return parser.parse(s_date).strftime("%d/%m/%Y")


def get_some_config(config_text):
    """
    Récupère certains éléments de configuration à utiliser dans les templates Jinja.

    Cette fonction est utile lorsque l'on souhaite exposer uniquement quelques paramètres
    de configuration à la couche de présentation (par exemple dans un template HTML Jinja),
    sans transmettre toute la configuration de l'application.

    Args:
        config_text (dict): Dictionnaire contenant la configuration complète de l'application.

    Returns:
        dict: Dictionnaire filtré contenant uniquement les clés d'intérêt.
    """
    # Liste des clés de configuration à exposer dans Jinja
    keys = [
        "ID_APP",         # Identifiant de l'application
        "MODE_TEST",      # Mode test activé ou non
        "URL_USERSHUB",   # URL du service UsersHub
        "URL_APPLICATION" # URL principale de l'application
    ]

    # On filtre le dictionnaire de configuration pour ne garder que les clés souhaitées
    return {k: v for k, v in config_text.items() if k in keys}


def to_string(x):
    """
    patch jinja
    """
    return str(x)


utils_dict = {
    # "get_db": get_db,
    "print_date": print_date,
    "get_areas_from_type_code": get_areas_from_type_code,
    "get_foret_type": get_foret_type,
    "get_some_config": get_some_config,
    "to_string": to_string,
}
