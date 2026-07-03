"""
api commons
"""

import os
from pathlib import Path

from flask import Blueprint, current_app, request
from utils_flask_sqla.response import json_resp_accept_empty_list, json_resp
from sqlalchemy import text, select, func


from .models import (
    TContents,
    TTags,
    TEspeces,
    TCommunesFrance,
    TNomenclaturesOeasc,
    TListeOrganismes,
)
from .schema import (
    TContentsSchema,
    TTagsSchema,
    TEspecesSchema,
    TCommunesFranceSchema,
    TNomenclaturesOeascSchema,
    TListeOrganismesSchema,
)

from oeasc.modules.oeasc.commons.models import TSecteurs
from oeasc.modules.oeasc.commons.schema import TSecteursSchema


from pypnnomenclature.models import BibNomenclaturesTypes
from pypnnomenclature.schemas import BibNomenclaturesTypesSchema


from ..generic.definitions import GenericRouteDefinitions

from ..nomenclature import nomenclature_oeasc_types

grd = GenericRouteDefinitions()

config = current_app.config
DB = config["DB"]

definitions = {
    "content": {
        "model": TContents,
        "droits": {"C": 5, "R": 0, "U": 5, "D": 5},
        "schema": TContentsSchema,
    },
    "tag": {
        "model": TTags,
        "droits": {"C": 5, "R": 0, "U": 5, "D": 5},
        "schema": TTagsSchema,
    },
    "secteur": {
        "model": TSecteurs,
        "droits": {"C": 5, "R": 0, "U": 5, "D": 5},
        "schema": TSecteursSchema,
    },
    "espece": {
        "model": TEspeces,
        "droits": {"C": 5, "R": 0, "U": 5, "D": 5},
        "schema": TEspecesSchema,
    },
    "commune": {
        "model": TCommunesFrance,
        "droits": {"C": 5, "R": 0, "U": 5, "D": 5},
        "schema": TCommunesFranceSchema,
    },
    "liste_organismes": {
        "model": TListeOrganismes,
        "droits": {"C": 5, "R": 0, "U": 5, "D": 5},
        "schema": TListeOrganismesSchema,
    },
    "nomenclature": {
        "model": TNomenclaturesOeasc,
        "schema": TNomenclaturesOeascSchema,
        "droits": {"C": 5, "R": 0, "U": 5, "D": 5},
        "pre_filters": {"type": nomenclature_oeasc_types},
    },
    "nomenclature_type": {
        "model": BibNomenclaturesTypes,
        "schema": BibNomenclaturesTypesSchema,
        "droits": {"C": 5, "R": 0, "U": 5, "D": 5},
        "pre_filters": {"mnemonique": nomenclature_oeasc_types},
    },
}

grd.add_generic_routes("commons", definitions)

bp = Blueprint("commons_api", __name__)


@bp.route("communes", methods=["GET"])
def api_all_communes():
    """recupèration de la liste de toutes les communes via le shema
    pas utilisé poru l'instant, mais peut être utile pour des tests
    """

    stmt_commune = (
        select(TCommunesFrance)
        .where(
            (TCommunesFrance.cp.startswith("07"))
            | (TCommunesFrance.cp.startswith("48"))
            | (TCommunesFrance.cp.startswith("30"))
        )
        .order_by(
            TCommunesFrance.population.desc(), TCommunesFrance.nom, TCommunesFrance.cp
        )
    )
    result = DB.session.execute(stmt_commune).scalars().all()
    communeSchema = TCommunesFranceSchema()
    out = [communeSchema.dump(res) for res in result]
    return out


@bp.route("communes/<string:test>", methods=["GET"])
@json_resp_accept_empty_list
def api_communes(test):
    """
    api qui retourne une liste de commune sous forme de liste de "nom code_postal".(pas en json)
    prend en argument soit le code postal, soit le nom de la commune.
    Utile pour l'autocomplétion des communes dans les formulaires.

    Cette fonction est utilisée lors d'une requête GET sur l'endpoint "communes/<string:test>".
    Elle permet de filtrer les communes selon le texte saisi par l'utilisateur (nom ou code postal),
    en gérant les accents pour faciliter la recherche.
    """

    # Si aucun paramètre n'est fourni, on retourne une liste vide
    if not test:
        return []

    # Définition des caractères accentués à remplacer
    s_trans_I = "àâäéèêëîïöùûü"
    s_trans_O = "aaaeeeeiiouuu"

    # Remplacement des caractères accentués dans la chaîne de recherche
    for index, _ in enumerate(s_trans_I):
        test = test.replace(s_trans_I[index], s_trans_O[index])

    # Séparation de la recherche en plusieurs mots si nécessaire
    tests = test.strip().split(" ")

    # Construction de la condition SQL pour filtrer sur le nom ou le code postal
    cond_text = " AND ".join(
        [
            (
                " ( TRANSLATE(nom, '{1}', '{2}') ILIKE '{3}{0}%' OR cp ILIKE '{3}{0}%' ) "
            ).format(s_test, s_trans_I, s_trans_O, "" if s_test == tests[0] else "%")
            for s_test in tests
        ]
    )

    # Création de la requête SQL pour récupérer les communes correspondantes
    stmt_commune = (
        select(
            func.concat(TCommunesFrance.nom, " ", TCommunesFrance.cp).label("nom_cp")
        )
        .where(text(cond_text))
        .order_by(
            TCommunesFrance.population.desc(), TCommunesFrance.nom, TCommunesFrance.cp
        )
        .limit(20)
    )

    # Exécution de la requête et récupération des résultats
    result = DB.session.execute(stmt_commune).all()

    # Formatage des résultats sous forme de dictionnaire
    out = [{"nom_cp": res[0]} for res in result]
    return out


@bp.route("files/<string:dir_file>", methods=["GET"])
@json_resp_accept_empty_list
def api_images(dir_file):
    """
    Fonction qui renvoie la liste des fichiers (images ou documents) présents dans le répertoire spécifié.
    Cette fonction est utilisée lors d'une requête GET sur l'endpoint "files/<string:dir_file>".
    Elle permet d'obtenir dynamiquement la liste des fichiers pour affichage ou sélection côté client.

    Arguments :
        dir_file (str): Nom du sous-répertoire à explorer ("img" ou "doc").

    Retour :
        list: Liste des noms de fichiers présents dans le répertoire, triée par ordre alphabétique.
    """

    # Vérifie que le répertoire demandé est autorisé ("img" ou "doc")
    if not dir_file in ["img", "doc"]:
        return []

    # Construit le chemin absolu vers le répertoire cible
    file_dir_path = Path(config["ROOT_DIR"], "static/medias/" + dir_file)
    files_out = []

    # Parcourt le répertoire et récupère les fichiers (ignore les fichiers cachés)
    for root, dirs, files in os.walk(file_dir_path):
        for i in files:
            if i[0] == ".":
                continue  # Ignore les fichiers cachés
            files_out.append(i)

    # Trie la liste des fichiers par ordre alphabétique
    files_out.sort()

    return files_out


@bp.route("add_file/<string:dir_file>", methods=["POST"])
@json_resp
def api_add_images(dir_file):
    """
    Fonction utilisée lors d'une requête POST sur l'endpoint "add_file/<string:dir_file>".
    Elle permet d'ajouter un fichier (image ou document) dans le répertoire spécifié côté serveur.
    Cette fonction est typiquement appelée lors de l'envoi d'un fichier depuis un formulaire client.
    """

    # Vérifie que le répertoire demandé est autorisé ("img" ou "doc")
    if not dir_file in ["img", "doc"]:
        return

    # Récupère le fichier envoyé dans la requête (champ "file" du formulaire)
    file = request.files.get("file")

    # Si aucun fichier n'est envoyé, retourne le contenu JSON de la requête (utile pour debug ou cas particulier)
    if not file:
        return request.get_json()

    out = {}
    # Parcourt les champs du formulaire et les ajoute au dictionnaire de sortie
    for key in request.form:
        out[key] = request.form.get(key)
        # Convertit les chaînes "null", "false", "true" en valeurs Python correspondantes
        if out[key] == "null":
            out[key] = None
        if out[key] == "false":
            out[key] = False
        if out[key] == "true":
            out[key] = True

    # Nettoie le nom du fichier en remplaçant certains caractères spéciaux par des underscores
    filename = file.filename
    for c in "/!;, ()}{}":
        filename = filename.replace(c, "_")

    # Sauvegarde le fichier dans le répertoire cible sur le serveur
    file.save(os.path.join(config["ROOT_DIR"], "static/medias/" + dir_file, filename))
    # Ajoute le nom du fichier sauvegardé dans le dictionnaire de sortie
    out["src"] = filename

    # Retourne le dictionnaire contenant les informations du formulaire et le nom du fichier
    return out
