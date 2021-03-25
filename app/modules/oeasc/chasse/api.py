'''
api chasse
'''

from .models import (
    TPersonnes, TZoneCynegetiques, TZoneInterets,
    TLieuTirs, TSaisons, TSaisonDates,
    TAttributionMassifs, TTypeBracelets, TAttributions, TRealisationsChasse
)
from ..generic.definitions import GenericRouteDefinitions
from flask import Blueprint, current_app, request


bp = Blueprint('chasse_api', __name__)
grd = GenericRouteDefinitions()

droits = { 'C': 5, 'R': 0, 'U': 5, 'D': 5 }

definitions = {
    'personne': {
        'model': TPersonnes,
        'droits': droits
    },
    'zone_cynegetique': {
        'model': TZoneCynegetiques,
        'droits': droits
    },
    'zone_cynegetique': {
        'model': TZoneCynegetiques,
        'droits': droits
    },
    'zone_interet': {
        'model': TZoneInterets,
        'droits': droits
    },
    'lieu_tir': {
        'model': TLieuTirs,
        'droits': droits
    },
    'saison': {
        'model': TSaisons,
        'droits': droits
    },
    'saison_date': {
        'model': TSaisonDates,
        'droits': droits
    },
    'attribution_massif': {
        'model': TAttributionMassifs,
        'droits': droits
    },
    'type_bracelet': {
        'model': TTypeBracelets,
        'droits': droits
    },
    'attribution': {
        'model': TAttributions,
        'droits': droits
    },
    'realisation': {
        'model': TRealisationsChasse,
        'droits': droits
    },
}

grd.add_generic_routes('chasse', definitions)
