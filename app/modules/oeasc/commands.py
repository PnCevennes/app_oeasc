"""
    module MODULES administration commands

    - create_schema : generate schema template
    - sql_schema : generate schema sql
    - test_schema : process tests on a specified schema
"""

import click
import json
import time

from flask.cli import AppGroup, with_appcontext

from app.utils.env import DB

from app.modules.oeasc.chasse.models import TRealisationsChasse

from app.modules.oeasc.generic.repository import (
    get_objects_type,
    get_object_type,
    create_or_update_object_type,
    delete_object_type,
)


@click.command("test_chasse_realisation")
@click.option("-m", "--module_code", "module_code", default="test")
@click.option("-s", "--schema_name", "schema_name", default="example")
@with_appcontext
def cmd_test_chasse_realisation(module_code, schema_name):
    """
    Commande de test sur un schema
    """

    data_text = """
    {
        "id_realisation":null,
        "attribution" : { "id_attribution" : 7678 },
        "zone_cynegetique_realisee" : {"id_zone_cynegetique_realisee": 1},
        "zone_indicative_realisee" : {"id_zone_indicative_realisee": 1}
    }
    """

    post_data = json.loads(data_text)
    print("test")
    print(json.dumps(post_data, indent=4))
    create_or_update_object_type("chasse", "realisation", None, post_data)
    print("test ok")


# liste des commande pour export dans blueprint.py
commands = [
    cmd_test_chasse_realisation,
]
