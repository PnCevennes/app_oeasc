from flask import Blueprint, request
from app.utils.utilssqlalchemy import json_resp
from .repository import req_test

bp = Blueprint('resultat_api', __name__)


@bp.route('test', methods=['GET'])
@json_resp
def test():
    '''
    '''
    type = request.args.get("type", "")

    return req_test(type)
