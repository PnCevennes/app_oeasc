from flask import (
    Blueprint, render_template
)

from pypnusershub import routes as fnauth


# from .declaration_sample import test

from app.utils.utilssqlalchemy import json_resp


bp = Blueprint('test', __name__)


@bp.route('/carte/', defaults={'id_areas': "", 'type_code': 'OEASC_COMMUNE'})
@bp.route('/carte/<string:type_code>', defaults={'id_areas': ""})
@bp.route('/carte/<string:type_code>/<string:id_areas>')
def carte(type_code, id_areas):
    '''
        test cartes

    '''

    areas_container = []

    for id_area in id_areas.split(","):

        if id_area != "":

            areas_container.append({'id_area': int(id_area)})

    data = {

        'type_code': type_code,
        'areas_container': areas_container,

    }

    return render_template('modules/oeasc/test/carte.html', data=data)


@bp.route('/test_connexion', methods=['GET', 'POST'])
@fnauth.check_auth(1)
@json_resp
def test_connexion():
    return {"msg": "ok"}


@bp.route('/d3/')
def test_d3():
    '''
        test graphes
    '''

    return render_template('modules/oeasc/test/d3.html')


@bp.route('/test_webpack/')
def test_webpack():
    '''
        test graphes
    '''

    return render_template('modules/oeasc/test/test_webpack.html')
