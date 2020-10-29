'''
    repo commons
'''

from flask import current_app
from .models import TContents

config = current_app.config
DB = config['DB']


def get_content(code):
    '''
        renvoie l'object text pour un code donné
    '''

    try:
        res = (
            DB.session
            .query(TContents)
            .filter(code == TContents.code)
            .one()
        )

        return res

    except Exception as e:
        print('Exception get_content {}'.format(e))

    out = TContents()

    return out
