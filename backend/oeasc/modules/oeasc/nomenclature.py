from flask import current_app
from pypnnomenclature.repository import get_nomenclature_list
from oeasc.ref_geo.repository import get_type_code
from oeasc.ref_geo.models import VAreas as VA
from oeasc.ref_geo.schema import VAreasSchema
from sqlalchemy import select

# from sqlalchemy.orm import Session

config = current_app.config
DB = config["DB"]

nomenclature_oeasc_types = [
    "OEASC_PEUPLEMENT_ESSENCE",
    "OEASC_PEUPLEMENT_MATURITE",
    "OEASC_PEUPLEMENT_PROTECTION_TYPE",
    "OEASC_PEUPLEMENT_PATURAGE_TYPE",
    "OEASC_PEUPLEMENT_PATURAGE_STATUT",
    "OEASC_PEUPLEMENT_ESPECE",
    "OEASC_PEUPLEMENT_ORIGINE",
    "OEASC_PEUPLEMENT_ORIGINE2",
    "OEASC_PEUPLEMENT_TYPE",
    "OEASC_PEUPLEMENT_ACCES",
    "OEASC_PEUPLEMENT_PATURAGE_FREQUENCE",
    "OEASC_PEUPLEMENT_PATURAGE_SAISON",
    "OEASC_PEUPLEMENT_ESSENCE",
    "OEASC_DEGAT_TYPE",
    "OEASC_DEGAT_GRAVITE",
    "OEASC_DEGAT_ETENDUE",
    "OEASC_DEGAT_ANTERIORITE",
    "OEASC_FORET_TYPE",
    "OEASC_PROPRIETAIRE_DECLARANT",
    "OEASC_PROPRIETAIRE_TYPE",
    "OEASC_DECLARANT_FONCTION",
    "OEASC_MOD_CHASSE",
    "SEXE",
    "STADE_VIE",
]


def nomenclature_oeasc():
    """
    Fonction pour récupérer toutes les nomenclatures qui concernent l'OEASC
    à l'aide de la commande get_nomenclature_list du module pypnnomenclature.

    Cette fonction est utilisée pour charger en mémoire (dans la config Flask)
    toutes les nomenclatures nécessaires à l'application OEASC, afin d'éviter
    de refaire des requêtes à chaque accès. Elle est appelée par les fonctions
    qui ont besoin d'accéder aux valeurs de nomenclature, comme
    get_nomenclature_from_id ou get_nomenclature.
    """

    # On vérifie si les nomenclatures sont déjà présentes dans la config Flask
    # (pour éviter de refaire la requête à chaque appel)
    if not config.get("_nomenclature"):
        # Si elles ne sont pas présentes, on les récupère depuis la base
        list_data = (
            nomenclature_oeasc_types  # Liste des types de nomenclature à charger
        )

        data = {}

        # Pour chaque type de nomenclature, on récupère la liste correspondante
        for type_code in list_data:
            data[type_code] = get_nomenclature_list(code_type=type_code)

            if not data[type_code]:
                continue  # Si aucune donnée n'est trouvée, on passe au suivant

            # On ne garde que les colonnes qui nous intéressent pour l'application
            cols = ["id_nomenclature", "mnemonique", "cd_nomenclature", "label_fr"]
            values = []

            # On filtre chaque élément pour ne garder que les colonnes utiles
            for d in data[type_code]["values"]:
                d_new = {}
                for key in cols:
                    d_new[key] = d.get(key, None)
                values.append(d_new)
            data[type_code][
                "values"
            ] = values  # On remplace la liste par la version filtrée

        # On stocke le résultat dans la config Flask pour le réutiliser plus tard
        config["_nomenclature"] = data

        # Certains types de nomenclature doivent être triés selon un ordre spécifique
        dict_sort_nomenclature = {
            "OEASC_DEGAT_TYPE": [
                "ABR",
                "FRO",
                "ÉCO",
                "SANG",
                "LIEV",
                "ABS",
                "P/C",
            ]
        }

        # On applique le tri personnalisé pour les types concernés
        for key, value in dict_sort_nomenclature.items():
            config["_nomenclature"][key]["values"].sort(
                key=lambda e: value.index(e["cd_nomenclature"])
            )

    # On retourne le dictionnaire des nomenclatures, soit depuis la mémoire, soit fraichement chargé
    return config["_nomenclature"]


def get_nomenclature_from_id(id_nomenclature, key=""):
    """
    Retourne un élément de nomenclature à partir de son identifiant.

    Cette fonction est utilisée lorsqu'on dispose uniquement de l'id_nomenclature
    et qu'on souhaite obtenir toutes les informations associées à cette nomenclature,
    ou seulement une clé précise (par exemple le label ou le code).

    Elle parcourt toutes les nomenclatures chargées en mémoire (via nomenclature_oeasc)
    et retourne l'élément correspondant à l'identifiant fourni.

    Args:
        id_nomenclature (int/str): Identifiant de la nomenclature recherchée.
        key (str): Clé spécifique à retourner (optionnel). Si vide, retourne l'objet complet.

    Returns:
        dict/str/None: L'élément de nomenclature complet ou la valeur de la clé demandée,
        ou None si non trouvé.
    """
    if not id_nomenclature:
        return None

    # On parcourt toutes les nomenclatures chargées
    for _, nomenclature_type in nomenclature_oeasc().items():
        # On parcourt chaque valeur de la nomenclature
        for elem in nomenclature_type["values"]:
            # Si l'id correspond, on retourne l'élément ou la clé demandée
            if str(elem["id_nomenclature"]) == str(id_nomenclature):
                if key != "":
                    return elem[key]
                else:
                    return elem

    # Si aucune nomenclature ne correspond à l'id, on retourne None
    return None


def get_nomenclature(key_in, value_in, type_code, key_out=""):
    """
    Recherche et retourne un élément de nomenclature à partir d'une valeur clé.

    Cette fonction permet d'obtenir une entrée de nomenclature (par exemple un code, un label, etc.)
    en cherchant dans le type de nomenclature spécifié (type_code) la valeur correspondant à key_in == value_in.
    Elle est utile lorsqu'on connaît une valeur (ex : code ou mnemonique) et qu'on souhaite récupérer
    l'objet complet ou une clé précise (ex : label_fr).

    Args:
        key_in (str): La clé sur laquelle effectuer la recherche (ex : "cd_nomenclature", "mnemonique").
        value_in (str/int): La valeur recherchée pour la clé key_in.
        type_code (str): Le type de nomenclature dans lequel chercher (doit être présent dans nomenclature_oeasc_types).
        key_out (str, optionnel): Si renseigné, retourne uniquement la valeur de cette clé dans l'élément trouvé.

    Returns:
        dict/str/None: L'élément de nomenclature complet, ou la valeur de key_out si précisé,
        ou None si aucun élément ne correspond.

    Cas d'utilisation :
        - Pour retrouver le label d'un code de nomenclature (ex : get_nomenclature("cd_nomenclature", "ABR", "OEASC_DEGAT_TYPE", "label_fr"))
        - Pour obtenir l'objet complet à partir d'une mnemonique ou d'un code
        - Utilisé dans les fonctions de mapping ou d'affichage des valeurs de nomenclature
    """
    nomemclature_type = nomenclature_oeasc().get(type_code, None)

    if not nomemclature_type:
        # Si le type de nomenclature n'existe pas, on retourne None
        return None

    # On parcourt toutes les valeurs du type de nomenclature
    for elem in nomemclature_type["values"]:
        # Si la valeur de la clé recherchée correspond à value_in
        if str(elem[key_in]) == str(value_in):
            if key_out != "":
                # Si une clé de sortie est précisée, on retourne uniquement cette valeur
                return elem[key_out]
            else:
                # Sinon, on retourne l'objet complet
                return elem

    # Si aucun élément ne correspond, on retourne None
    return None


def get_areas_from_ids(id_areas):
    """
    Recherche les attributs des aires (areas) en base de données pour une liste d'identifiants,
    uniquement si ces aires ne sont pas déjà présentes dans la session Flask (_areas).

    Cette fonction permet d'optimiser les accès à la base en évitant de refaire des requêtes
    pour des aires déjà chargées en mémoire. Elle est utile lorsqu'on doit traiter plusieurs
    aires en une seule fois (ex : lors du chargement d'une liste de déclarations).

    Args:
        id_areas (list): Liste des identifiants d'aires à récupérer.

    Utilisation typique :
        - Appelée en amont d'un traitement qui nécessite d'accéder aux attributs de plusieurs aires,
          pour précharger toutes les données nécessaires en une seule requête SQL.
        - Utilisée dans la fonction (commentée) pre_get_dict_nomenclature_areas pour optimiser
          le chargement des aires associées à des déclarations.
    """
    # On initialise le cache des aires dans la config Flask si nécessaire
    if not config.get("_areas"):
        config["_areas"] = {}

    id_areas_to_query = []  # Liste des identifiants à interroger en base

    # On parcourt la liste des identifiants fournis
    for id in id_areas:
        # Si l'aire n'est pas déjà présente dans le cache, on l'ajoute à la liste à interroger
        if not config["_areas"].get(str(id), None):
            id_areas_to_query.append(id)

    # Si des aires doivent être récupérées en base
    if id_areas_to_query:

        # On construit la requête SQL pour récupérer toutes les aires d'un coup
        stmt = select(VA).where(VA.id_area.in_(id_areas_to_query))
        result_db = DB.session.execute(
            stmt
        ).all()  # Exécution de la requête, récupération des résultats

        # On convertit les résultats en liste de dictionnaires via le schéma Marshmallow
        all_area = VAreasSchema(many=True).dump(result_db)

        # Pour chaque aire récupérée, on ajoute le type_code et on la stocke dans le cache
        for area in all_area:
            area["type_code"] = get_type_code(area["id_type"])
            config["_areas"][str(area["id_area"])] = area


def get_area_from_id(id_area):
    """
    Recherche les attributs d'une aire (area) en base de données à partir de son identifiant,
    uniquement si cette aire n'est pas déjà présente dans la session Flask (_areas).

    Cette fonction est utilisée pour accéder rapidement aux informations d'une aire
    sans refaire de requête si elle a déjà été chargée en mémoire. Elle est appelée
    par les fonctions qui doivent enrichir un dictionnaire avec les données d'une aire,
    comme get_dict_nomenclature_areas.

    Args:
        id_area (int/str): Identifiant de l'aire à récupérer.

    Returns:
        dict/None: Dictionnaire des attributs de l'aire, ou None si non trouvée.
    """
    # On initialise le cache des aires dans la config Flask si nécessaire
    if not config.get("_areas"):
        config["_areas"] = {}

    # Si l'aire n'est pas déjà présente dans le cache, on la récupère en base
    if not config["_areas"].get(str(id_area), None):

        # On construit la requête SQL pour récupérer l'aire
        stmt = select(VA).where(VA.id_area == id_area)
        data = DB.session.execute(stmt).scalars().first()

        if not data:
            return None

        # On convertit le résultat en dictionnaire via le schéma Marshmallow
        area_dict = VAreasSchema().dump(data)

        # On ajoute le type_code à l'aire
        area_dict["type_code"] = get_type_code(area_dict["id_type"])
        config["_areas"][str(id_area)] = area_dict

    # On retourne l'aire depuis le cache
    return config["_areas"][str(id_area)]


def get_dict_nomenclature_areas(dict_in):
    """
    Parcourt récursivement un dictionnaire (ou une liste de dictionnaires) pour remplacer
    les identifiants de nomenclature et d'aires par leurs objets complets.

    Cette fonction est utilisée pour enrichir un dictionnaire contenant des clés
    commençant par 'id_nomenclature_', 'nomenclatures_' ou 'areas' en remplaçant
    les identifiants par les objets correspondants (nomenclature ou aire).
    Elle applique ce traitement de façon récursive sur les sous-dictionnaires et listes.

    Cas d'utilisation :
        - Pour préparer les données avant affichage ou export, en fournissant
          les informations complètes au lieu des seuls identifiants.
        - Utilisée dans les routes ou les fonctions qui doivent retourner des
          objets enrichis à partir de données brutes issues de la base.

    Args:
        dict_in (dict): Dictionnaire à traiter.

    Returns:
        dict: Dictionnaire enrichi avec les objets nomenclature et aire.
    """
    if not isinstance(dict_in, dict):
        # Si l'entrée n'est pas un dictionnaire, on la retourne telle quelle
        return dict_in

    for key in dict_in:
        # Si la clé correspond à un identifiant de nomenclature
        if key.startswith("id_nomenclature_"):
            dict_in[key] = get_nomenclature_from_id(dict_in.get(key, None))
            continue

        # Si la clé correspond à une liste d'aires
        if key.startswith("areas") and dict_in[key]:
            dict_res = []
            for elem in dict_in[key]:
                if isinstance(elem, int):
                    dict_res.append(get_area_from_id(elem))
                elif isinstance(elem, dict) and elem.get("id_area"):
                    dict_res.append(get_area_from_id(elem["id_area"]))
            if dict_res:
                dict_in[key] = dict_res
            continue

        # Si la clé correspond à une liste de nomenclatures
        if key.startswith("nomenclatures_") and dict_in[key]:
            dict_res = []
            for elem in dict_in[key]:
                if isinstance(elem, int):
                    dict_res.append(get_nomenclature_from_id(elem))
                elif isinstance(elem, dict) and elem.get("id_nomenclature"):
                    dict_res.append(get_nomenclature_from_id(elem["id_nomenclature"]))
            if dict_res:
                dict_in[key] = dict_res
            continue

        # Si la valeur est un sous-dictionnaire, on applique la fonction récursivement
        if isinstance(dict_in[key], dict):
            dict_in[key] = get_dict_nomenclature_areas(dict_in[key])
            continue

        # Si la valeur est une liste, on applique la fonction à chaque élément
        if isinstance(dict_in[key], list):
            dict_in[key] = [get_dict_nomenclature_areas(elem) for elem in dict_in[key]]
            continue

    return dict_in
