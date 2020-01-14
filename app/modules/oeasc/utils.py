"""
    Fonctions à utilisé danbs Jinja
    ex: utils.print_date pour afficher la date au format jour-mois-année
"""
from dateutil import parser
from flask import current_app

from .repository import get_db
from .declaration.repository import get_foret_type
from .declaration.utils import get_areas_from_type_code

config = current_app.config
DB = config['DB']


def print_date(s_date):
    """
        pour affichage dans tableau
    """
    return parser.parse(s_date).strftime("%d-%m-%Y")


# def arrays_to_csv(filename, data, columns, separator):

#     outdata = [separator.join(columns)]

#     headers = Headers()
#     headers.add('Content-Type', 'text/plain')
#     headers.add(
#         'Content-Disposition',
#         'attachment',
#         filename='export_%s.csv' % filename
#     )


#     for l in data:
#         outdata.append(
#             separator.join(
#                 '"%s"' % (str(e) if e else '') for e in l
#             )
#         )

#     out = '\r\n'.join(outdata)

#     return Response(out, headers=headers)


def get_some_config(config_text):
    """
        pour avoir des elements de config dans jinja
    """
    keys = [
        "ID_APP",
        "MODE_TEST",
        "URL_USERHUB",
        "URL_APPLICATION",
    ]

    return {k: v for k, v in config_text.items() if k in keys}


def to_string(x):
    """
        patch jinja
    """
    return str(x)


utils_dict = {
    "get_db": get_db,
    'print_date': print_date,
    'get_areas_from_type_code': get_areas_from_type_code,
    'get_foret_type': get_foret_type,
    'get_some_config': get_some_config,
    'to_string': to_string
}
