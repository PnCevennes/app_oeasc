from dateutil import parser
from werkzeug.datastructures import Headers
from flask import Response

from .repository import get_db
from .declaration.repository import get_foret_type
from .declaration.utils import get_areas_from_type_code
from flask import current_app

config = current_app.config
DB = config['DB']


def copy_list(liste):

    return [elem for elem in liste]


def print_date(s_date):
    """
        pour affichage dans tableau
    """
    return parser.parse(s_date).strftime("%Y-%m-%d")


def arrays_to_csv(filename, data, columns, separator):

    outdata = [separator.join(columns)]

    headers = Headers()
    headers.add('Content-Type', 'text/plain')
    headers.add(
        'Content-Disposition',
        'attachment',
        filename='export_%s.csv' % filename
    )

    for l in data:
        outdata.append(
            separator.join(
                '"%s"' % (str(e)) for e in l
            )
        )

    out = '\r\n'.join(outdata)

    return Response(out, headers=headers)


def get_some_config(config_text):

    keys = [
        "ID_APP",
        "MODE_TEST",
        "URL_USERHUB",
        "URL_APPLICATION",
    ]

    return {k: v for k, v in config_text.items() if k in keys}


utils_dict = {
    "copy_list": copy_list,
    "get_db": get_db,
    'print_date': print_date,
    'get_areas_from_type_code': get_areas_from_type_code,
    'get_foret_type': get_foret_type,
    'get_some_config': get_some_config,
}
