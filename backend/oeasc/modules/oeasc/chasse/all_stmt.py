from flask import request, current_app
from ..generic.repository import getlist

# from ..resultat.repository import result_custom
from sqlalchemy import func, cast, select, Integer
from oeasc.modules.oeasc.commons.models import TEspeces
from oeasc.ref_geo_oeasc.models import TSecteurs
from oeasc.ref_geo_oeasc.schema import TSecteursSchema
from sqlalchemy.exc import SQLAlchemyError
from .models import (
    TSaisons,
    TZoneCynegetiques,
    TZoneIndicatives,
    TAttributionMassifs,
    VPlanChasseRealisationBilan,
    TRealisationsChasse,
)
