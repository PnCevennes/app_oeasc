from flask import Blueprint, request
from app.utils.utilssqlalchemy import json_resp
from .repository import req_degats_type, req_timeline

bp = Blueprint('resultat_api', __name__)


@bp.route('distribution_degats', methods=['GET'])
@json_resp
def distribution_degats():
    '''
    '''
    type = request.args.get("type", "")

    return req_degats_type(type)


@bp.route('timeline', methods=['GET'])
@json_resp
def timeline():
    '''
    '''

    return req_timeline()
