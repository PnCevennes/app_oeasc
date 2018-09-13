from flask import (
    Blueprint, render_template
)

bp = Blueprint('test', __name__)


@bp.route('/carte')
def carte():
    '''
        page de connection

    '''
    return render_template('modules/oeasc/test/carte.html')
