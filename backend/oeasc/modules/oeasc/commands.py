"""
module MODULES administration commands

- create_schema : generate schema template
- sql_schema : generate schema sql
- test_schema : process tests on a specified schema
"""

import click
import json

from flask.cli import with_appcontext

# from oeasc.utils.env import DB

# from oeasc.modules.oeasc.chasse.models import TRealisationsChasse

from oeasc.modules.oeasc.generic.repository import (
    # get_objects_type,
    # get_object_type,
    create_or_update_object_type,
    # delete_object_type,
)


# Commande CLI pour tester la création ou mise à jour d'une réalisation de chasse
@click.command("test_chasse_realisation")
@click.option("-m", "--module_code", "module_code", default="test")
@click.option("-s", "--schema_name", "schema_name", default="example")
@with_appcontext
def cmd_test_chasse_realisation(module_code, schema_name):
    """
    Commande de test sur un schema

    Utilisation :
    Cette commande est utilisée pour tester la création ou la mise à jour d'un objet 'realisation'
    dans le module 'chasse'. Elle simule l'envoi de données JSON et appelle la fonction
    create_or_update_object_type pour effectuer l'opération en base de données.

    Options :
    -m / --module_code : code du module à utiliser (par défaut "test")
    -s / --schema_name : nom du schéma à utiliser (par défaut "example")
    """

    # Exemple de données JSON simulant une réalisation de chasse
    data_text = """
    {
        "id_realisation":null,
        "attribution" : { "id_attribution" : 7678 },
        "zone_cynegetique_realisee" : {"id_zone_cynegetique_realisee": 1},
        "zone_indicative_realisee" : {"id_zone_indicative_realisee": 1}
    }
    """

    # Chargement des données JSON en dictionnaire Python
    post_data = json.loads(data_text)

    # Appel de la fonction pour créer ou mettre à jour l'objet 'realisation' dans le module 'chasse'
    create_or_update_object_type("chasse", "realisation", None, post_data)


# liste des commande pour export dans blueprint.py
commands = [
    cmd_test_chasse_realisation,
]
