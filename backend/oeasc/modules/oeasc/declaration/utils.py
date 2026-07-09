from oeasc.modules.oeasc.nomenclature import (
    nomenclature_oeasc,
    get_nomenclature_from_id,
    get_dict_nomenclature_areas,
    get_nomenclature,
)
from oeasc.ref_geo_oeasc.models import VMAreasSimples
from flask import current_app
from sqlalchemy import func
from .models import TForet
from .schema import TForetSchema
from pypnusershub.db.models import User
from pypnusershub.schemas import UserSchema
from sqlalchemy import select

config = current_app.config
DB = config["DB"]


def get_areas_from_type_code(areas, type_code):
    """
    Retourne la liste des aires dont le type_code correspond à celui passé en paramètre.

    Args:
        areas (list): Liste de dictionnaires représentant des aires géographiques.
        type_code (str): Code du type d'aire recherché (ex : "OEASC_CADASTRE", "OEASC_ONF_UG", etc.).

    Returns:
        list: Liste des aires (dictionnaires) dont le type_code correspond.

    Utilisation :
        Cette fonction est utilisée dans plusieurs autres fonctions utilitaires du module,
        notamment dans check_massif pour filtrer les aires selon leur type et déterminer
        si le massif doit être renseigné automatiquement dans une déclaration.
    """
    out = []
    if not areas:
        # Si la liste des aires est vide ou None, on retourne une liste vide
        return out
    for area in areas:
        # On vérifie pour chaque aire si son type_code correspond à celui recherché
        if area["type_code"] == type_code:
            out.append(area)
    return out


# def check_massif(declaration_dict):
#     """
#     Cette fonction renseigne automatiquement le massif dans declaration_dict['areas_localisation']
#     si celui-ci n'est pas déjà renseigné.

#     Args:
#         declaration_dict (dict): Dictionnaire contenant les informations de la déclaration,
#         notamment la clé 'areas_localisation' qui liste les aires géographiques associées.

#     Returns:
#         int ou None: Retourne l'id du massif ajouté si trouvé, sinon None.

#     Utilisation :
#         Cette fonction est utilisée lors de la création ou de la modification d'une déclaration
#         pour s'assurer que le massif est bien renseigné lorsque certaines aires (cadastre, UG, PRF)
#         sont présentes mais que le massif ne l'est pas encore.
#     """

#     # On récupère les aires de type CADASTRE, ONF_UG et ONF_PRF
#     areas = get_areas_from_type_code(
#         declaration_dict["areas_localisation"], "OEASC_CADASTRE"
#     )
#     areas += get_areas_from_type_code(
#         declaration_dict["areas_localisation"], "OEASC_ONF_UG"
#     )
#     areas += get_areas_from_type_code(
#         declaration_dict["areas_localisation"], "OEASC_ONF_PRF"
#     )

#     if not areas:
#         # Si aucune aire de ces types n'est présente, on ne fait rien
#         return

#     # On vérifie si un secteur (massif) est déjà renseigné
#     areas_massif = get_areas_from_type_code(
#         declaration_dict["areas_localisation"], "OEASC_SECTEUR"
#     )

#     if areas_massif:
#         # Si le massif est déjà renseigné, on ne fait rien
#         return

#     # On récupère les id_area des aires précédemment filtrées
#     id_areas = [area["id_area"] for area in areas]

#     # On cherche dans la base une aire de type MASSIF correspondant à ces id_area
#     stmt_area = (
#         select(TAreas)
#         .where(TAreas.id_area.in_(id_areas))
#         .where(TAreas.type_code == "OEASC_MASSIF")
#         .limit(1)
#     )
#     area = DB.session.execute(stmt_area).scalars().first()

#     if not area:
#         # Si aucun massif n'est trouvé, on ne fait rien
#         return

#     # On prépare le dictionnaire pour enrichir les informations de nomenclature
#     dict_massif = {"areas_localisation": [{"id_area": area.id_area}]}
#     get_dict_nomenclature_areas(dict_massif)
#     # On ajoute le massif dans la déclaration
#     declaration_dict["areas_localisation"].append(dict_massif["areas_localisation"][0])

#     return area.id_area


# def get_listes_essences(declaration):
#     """
#     Retourne un dictionnaire contenant des listes d'essences pour la création du formulaire.

#     - selected : liste des essences sélectionnées dans principale, secondaires et complémentaires
#     - feuillus : liste des id_nomenclature pour les feuillus à laquelle on enlève les sélectionnées
#     - resineux : idem pour les résineux
#     - degats.id_nomenclature_degat_type : pour un type de dégât, les essences sélectionnées en global (selected)
#       moins les essences concernant ce type de dégât

#     Utilisation :
#         Cette fonction est utilisée lors de la préparation des données pour les formulaires de déclaration,
#         afin de proposer dynamiquement les essences disponibles et celles déjà sélectionnées par l'utilisateur.
#     """

#     nomenclature = nomenclature_oeasc()  # Récupère la nomenclature complète OEASC

#     listes_essences = {}

#     # Initialisation des listes
#     listes_essences["feuillus"] = []
#     listes_essences["resineux"] = []
#     listes_essences["selected"] = []
#     listes_essences["selected_degat"] = []

#     # Ajout de l'essence principale sélectionnée
#     d = declaration.get("id_nomenclature_peuplement_essence_principale", None)
#     if d:
#         listes_essences["selected"].append(d["id_nomenclature"])
#         listes_essences["selected_degat"].append(d["id_nomenclature"])

#     # Ajout des essences secondaires sélectionnées
#     for d in declaration["nomenclatures_peuplement_essence_secondaire"]:
#         listes_essences["selected"].append(d["id_nomenclature"])
#         listes_essences["selected_degat"].append(d["id_nomenclature"])

#     # Ajout des essences complémentaires sélectionnées
#     for d in declaration["nomenclatures_peuplement_essence_complementaire"]:
#         listes_essences["selected"].append(d["id_nomenclature"])

#     # Séparation des essences en feuillus et résineux selon la nomenclature
#     b_feuillus = True
#     for elem in nomenclature["OEASC_PEUPLEMENT_ESSENCE"]["values"]:
#         id = elem["id_nomenclature"]
#         if id not in listes_essences["selected"]:
#             if b_feuillus:
#                 listes_essences["feuillus"].append(id)
#             else:
#                 listes_essences["resineux"].append(id)
#         # On bascule à résineux après le code "AF" (Autres Feuillus)
#         b_feuillus = b_feuillus and (elem["cd_nomenclature"] != "AF")

#     # Préparation des listes d'essences pour chaque type de dégât
#     listes_essences["degats"] = {}
#     for degat in declaration["degats"]:
#         id_nomenclature_degat_type = degat["id_nomenclature_degat_type"]["id_nomenclature"]
#         # On commence avec toutes les essences sélectionnées pour ce type de dégât
#         listes_essences["degats"][id_nomenclature_degat_type] = [
#             e for e in listes_essences["selected_degat"]
#         ]
#         # On retire les essences déjà renseignées pour ce dégât
#         for degat_essence in degat.get("degat_essences", []):
#             if (
#                 degat_essence != {}
#                 and degat_essence["id_nomenclature_degat_essence"]
#                 and degat_essence["id_nomenclature_degat_essence"]["id_nomenclature"]
#                 in listes_essences["degats"][id_nomenclature_degat_type]
#             ):
#                 listes_essences["degats"][id_nomenclature_degat_type].remove(
#                     degat_essence["id_nomenclature_degat_essence"]["id_nomenclature"]
#                 )

#     # On enrichit chaque liste avec les informations complètes de nomenclature
#     for key in listes_essences:
#         if key == "degats":
#             for key_ in listes_essences["degats"]:
#                 v = []
#                 for e in listes_essences["degats"][key_]:
#                     elem = get_nomenclature_from_id(e)
#                     v.append(elem)
#                 listes_essences["degats"][key_] = v
#         else:
#             v = []
#             for e in listes_essences[key]:
#                 elem = get_nomenclature_from_id(e)
#                 v.append(elem)
#             listes_essences[key] = v

#     return listes_essences


# def get_foret_from_name(nom_foret):
#     """
#     Recherche une forêt dans la base de données à partir de son nom.

#     Cette fonction effectue une requête sur la table TForet pour trouver une forêt dont le nom correspond
#     (sans tenir compte de la casse) à celui passé en paramètre. Si aucune forêt n'est trouvée, la fonction
#     retourne None. Sinon, elle retourne un dictionnaire représentant la forêt, sérialisé via le schéma TForetSchema.

#     Args:
#         nom_foret (str): Le nom de la forêt à rechercher.

#     Returns:
#         dict | None: Un dictionnaire contenant les informations de la forêt si elle existe, sinon None.

#     Utilisation:
#         Cette fonction est généralement utilisée lors de la déclaration ou de la consultation d'une forêt
#         dans le système, par exemple pour vérifier l'existence d'une forêt avant d'effectuer une opération
#         ou pour récupérer ses informations détaillées.
#     """

#     stmt_foret = (
#         select(TForet)
#         .where(func.lower(TForet.nom_foret) == func.lower(nom_foret))
#         .limit(1)
#     )
#     data = DB.session.execute(stmt_foret).scalars().first()

#     if not data:
#         return None

#     foret_dict = TForetSchema().dump(data)
#     return foret_dict
