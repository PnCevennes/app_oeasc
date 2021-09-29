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


@click.command('test_chasse_realisation')
@click.option('-m', '--module_code', 'module_code', default='test')
@click.option('-s', '--schema_name', 'schema_name',  default='example')
@with_appcontext
def cmd_test_chasse_realisation(module_code, schema_name):
    '''
        Commande de test sur un schema
    '''

    post_data = json.loads('{"id_realisation":null,"saison":{"id_saison":7,"nom_saison":"2020-2021","date_debut":"2020-09-02","date_fin":"2021-05-01","current":true,"commentaire":null},"attribution":{"id_attribution":4617,"id_type_bracelet":2,"id_saison":7,"numero_bracelet":"CEFF 3502","id_zone_cynegetique_affectee":4,"id_zone_indicative_affectee":33,"meta_create_date":"2021-08-23 14:53:47.912476","meta_update_date":null,"saison":{"id_saison":7,"nom_saison":"2020-2021","date_debut":"2020-09-02","date_fin":"2021-05-01","current":true,"commentaire":null},"zone_cynegetique_affectee":{"id_zone_cynegetique":4,"code_zone_cynegetique":"MTLO_E_30","nom_zone_cynegetique":"Mont Lozère est (Gard)","id_secteur":3,"secteur":{"id_secteur":3,"code_secteur":"MTLO","nom_secteur":"Mont Lozère"}},"zone_indicative_affectee":{"id_zone_indicative":33,"code_zone_indicative":"6","nom_zone_indicative":"ACPNC - Mont Lozère Est - Gard","id_zone_cynegetique":4,"zone_cynegetique":{"id_zone_cynegetique":4,"code_zone_cynegetique":"MTLO_E_30","nom_zone_cynegetique":"Mont Lozère est (Gard)","id_secteur":3,"secteur":{"id_secteur":3,"code_secteur":"MTLO","nom_secteur":"Mont Lozère"}}},"type_bracelet":{"id_type_bracelet":2,"id_espece":1,"code_type_bracelet":"CEFF","description_type_bracelet":"sexe : Femelle, Indéterminé, Mâle; classe age : Adulte, Indéterminé, Jeune, Sub adulte; espece : Cerf élaphe","espece":{"id_espece":1,"nom_espece":"Cerf","code_espece":"CF"}}},"auteur_tir":null,"auteur_constat":null,"zone_cynegetique_affectee":{"id_zone_cynegetique":4,"code_zone_cynegetique":"MTLO_E_30","nom_zone_cynegetique":"Mont Lozère est (Gard)","id_secteur":3,"secteur":{"id_secteur":3,"code_secteur":"MTLO","nom_secteur":"Mont Lozère"}},"zone_cynegetique_realisee":{"id_zone_cynegetique":4,"code_zone_cynegetique":"MTLO_E_30","nom_zone_cynegetique":"Mont Lozère est (Gard)","id_secteur":3,"secteur":{"id_secteur":3,"code_secteur":"MTLO","nom_secteur":"Mont Lozère"}},"zone_indicative_affectee":{"id_zone_indicative":33,"code_zone_indicative":"6","nom_zone_indicative":"ACPNC - Mont Lozère Est - Gard","id_zone_cynegetique":4,"zone_cynegetique":{"id_zone_cynegetique":4,"code_zone_cynegetique":"MTLO_E_30","nom_zone_cynegetique":"Mont Lozère est (Gard)","id_secteur":3,"secteur":{"id_secteur":3,"code_secteur":"MTLO","nom_secteur":"Mont Lozère"}}},"zone_indicative_realisee":{"id_zone_indicative":33,"code_zone_indicative":"6","nom_zone_indicative":"ACPNC - Mont Lozère Est - Gard","id_zone_cynegetique":4,"zone_cynegetique":{"id_zone_cynegetique":4,"code_zone_cynegetique":"MTLO_E_30","nom_zone_cynegetique":"Mont Lozère est (Gard)","id_secteur":3,"secteur":{"id_secteur":3,"code_secteur":"MTLO","nom_secteur":"Mont Lozère"}}},"lieu_tir_synonyme":null,"date_exacte":null,"date_enreg":null,"mortalite_hors_pc":null,"parcelle_onf":null,"nomenclature_sexe":null,"nomenclature_classe_age":null,"nomenclature_mode_chasse":null,"poid_entier":null,"poid_vide":null,"poid_c_f_p":null,"long_mandibules_droite":null,"long_mandibules_gauche":null,"long_dagues_droite":null,"long_dagues_gauche":null,"cors_nb":null,"cors_commentaires":null,"gestation":null,"commentaires":null,"freeze":false,"id_zone_cynegetique_affectee":4,"id_zone_indicative_affectee":33}')
    print('test')
    create_or_update_object_type('chasse', 'realisation', None, post_data)
    print('test ok')

# liste des commande pour export dans blueprint.py
commands = [
    cmd_test_chasse_realisation,
]