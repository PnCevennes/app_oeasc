from oeasc.modules.oeasc.nomenclature import (
    nomenclature_oeasc,
    get_nomenclature_from_id,
    get_dict_nomenclature_areas,
    get_nomenclature,
)
from oeasc.ref_geo_oeasc.models import VMAreasSimples
from flask import current_app
from sqlalchemy import func
from .models import TForet
from .schema import TForetSchema
from pypnusershub.db.models import User
from pypnusershub.schemas import UserSchema
from sqlalchemy import select

config = current_app.config
DB = config["DB"]


def get_areas_from_type_code(areas, type_code):
    """
    Retourne la liste des aires dont le type_code correspond à celui passé en paramètre.

    Args:
        areas (list): Liste de dictionnaires représentant des aires géographiques.
        type_code (str): Code du type d'aire recherché (ex : "OEASC_CADASTRE", "OEASC_ONF_UG", etc.).

    Returns:
        list: Liste des aires (dictionnaires) dont le type_code correspond.

    Utilisation :
        Cette fonction est utilisée dans plusieurs autres fonctions utilitaires du module,
        notamment dans check_massif pour filtrer les aires selon leur type et déterminer
        si le massif doit être renseigné automatiquement dans une déclaration.
    """
    out = []
    if not areas:
        # Si la liste des aires est vide ou None, on retourne une liste vide
        return out
    for area in areas:
        # On vérifie pour chaque aire si son type_code correspond à celui recherché
        if area["type_code"] == type_code:
            out.append(area)
    return out
