
from .repository import nomenclature_oeasc

from app.utils.env import DB
from sqlalchemy import text
from app.ref_geo.models import TAreas
from app.ref_geo.repository import get_id_type
from .models import TForet


def get_listes_essences(declaration):
    '''
        retourne un dictionnaire conenant des liste d'essences pour la creation du formulaire
            selected : liste des essence selectionnnee dans principale, secondaires et complementaire
            feuillus : liste des id_nomenclature pour les feuillus a laquelle on enleve les selectionnee
            resineux ...
            degats.id_nomenclature_degat_type: pour un type de degat :
                les essence selectionnées en global (selected) moins les essences concernant ce type de degat
    '''
    nomenclature = nomenclature_oeasc()

    listes_essences = {}

    listes_essences["feuillus"] = []
    listes_essences["resineux"] = []
    listes_essences["selected"] = []

    id = declaration.get("id_nomenclature_peuplement_essence_principale", None)
    if id:
        listes_essences["selected"].append(id)

    for d in declaration["nomenclatures_peuplement_essence_secondaire"]:
        listes_essences["selected"].append(d["id_nomenclature"])

    for d in declaration["nomenclatures_peuplement_essence_complementaire"]:
        listes_essences["selected"].append(d["id_nomenclature"])

    b_feuillus = True

    for elem in nomenclature["OEASC_PEUPLEMENT_ESSENCE"]["values"]:

        id = elem['id_nomenclature']

        if id not in listes_essences['selected']:

            if b_feuillus:

                listes_essences["feuillus"].append(id)

            else:

                listes_essences["resineux"].append(id)

        b_feuillus = b_feuillus and (elem['mnemonique'] != "PE_AF")  # PeuplementEssence_AutresFeuillus

    listes_essences["degats"] = {}

    for degat in declaration["degats"]:

        id_nomenclature_degat_type = degat["id_nomenclature_degat_type"]

        listes_essences["degats"][id_nomenclature_degat_type] = [e for e in listes_essences["selected"]]

        for degat_essence in degat.get('degat_essences', []):
            if degat_essence != {}:
                listes_essences["degats"][id_nomenclature_degat_type].remove(degat_essence["id_nomenclature_degat_essence"])

    return listes_essences


def copy_list(liste):

    return [elem for elem in liste]


def get_nomenclature_from_id(id_nomenclature, nomenclature, key="label_fr"):
    '''
        retourne un element de nomenclature a partir de son id
        si key == "", retourne l'element entier, sinon juste la clé choisie
    '''
    for _, nomenclature_type in nomenclature.items():

        for elem in nomenclature_type["values"]:

            if str(elem["id_nomenclature"]) == str(id_nomenclature):

                if key != "":

                    return elem[key]

                else:

                    return elem

    return ""


def get_organisme_name_from_id(id_organisme):

    sql_text = text("SELECT b.nom_organisme \
  FROM utilisateurs.bib_organismes as b \
  WHERE b.id_organisme = {};".format(id_organisme))

    result = DB.engine.execute(sql_text).first()

    return result[0]


def get_description_droit(id_droit):

    switcher = {
        1: "Declarant",
        2: "Declarant",
        3: "Declarant",
        4: "Directeur",
        5: "Directeur",
        6: "Admin"
    }

    return switcher.get(id_droit, 'id_droit {} invalide'.format(id_droit))


def check_foret(declaration):
    '''
        recherche une foret quand une aire est renseignées
    '''

    foret = declaration.get("foret", None)

    if not foret:

        return -1

    id_foret = foret.get("id_foret", None)
    areas_foret = foret.get("areas_foret", None)

    if((not id_foret) and areas_foret):

        # foret = get_id_foret_from_areas(declaration["foret"]["areas_foret"]):

        v_id_type = [get_id_type(type) for type in ["OEASC_ONF_FRT"]]

        for area in areas_foret:

            id_area = area['id_area']
            data = DB.session.query(TAreas).filter(id_area == TAreas.id_area).first()

            if data:

                if data.id_type in v_id_type:

                    forets = DB.session.query(TForet).all()

                    for f in [f.as_dict(True) for f in forets]:

                        for area_foret in f['areas_foret']:

                            if id_area == area_foret['id_area']:

                                declaration['foret'] = f

                                return f
                                return True

    return -2


def utils_dict():
    """
        dictionnaire qui reference les function ci dessus pour les utiliser dans jinja cf server.py

    """
    d = {}

    d["copy_list"] = copy_list
    d["get_description_droit"] = get_description_droit
    d["get_organisme_name_from_id"] = get_organisme_name_from_id
    d["get_nomenclature_from_id"] = get_nomenclature_from_id

    return d
