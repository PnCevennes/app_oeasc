from flask import (
    Blueprint, render_template
)

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
