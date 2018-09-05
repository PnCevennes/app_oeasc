

from app.utils.env import DB
from sqlalchemy import text
from app.ref_geo.models import TAreas
from app.ref_geo.repository import get_id_type
from .models import (
    TForet,
    TProprietaire
)
from .repository import nomenclature_oeasc
from .repository import get_nomenclature_from_id


def get_liste_communes(declaration):

    areas = declaration["foret"]["areas_foret"]

    communes = []

    for area in areas:

        id_area = area["id_area"]

        sql_text = text("SELECT b.area_name \
         FROM ref_geo.l_areas as b, \
         (SELECT l.id_area as id_area, c.id_foret, l.area_name,  ref_geo.intersect_rel_area(c.id_area,'OEASC_COMMUNE',0.05) as id_com, geom\
             FROM oeasc.cor_areas_forets as c, ref_geo.l_areas as l\
             WHERE l.id_area = " + str(id_area) + " AND l.id_area = c.id_area) a\
         WHERE b.id_area = a.id_com\
         ORDER BY a.area_name, b.area_name;")

        data = DB.engine.execute(sql_text)

        [communes.append(d[0]) for d in data]

    return communes


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

            if degat_essence != {} and degat_essence["id_nomenclature_degat_essence"] and degat_essence["id_nomenclature_degat_essence"] in listes_essences["degats"][id_nomenclature_degat_type]:

                print(degat_essence["id_nomenclature_degat_essence"])
                print(listes_essences["degats"][id_nomenclature_degat_type])
                listes_essences["degats"][id_nomenclature_degat_type].remove(degat_essence["id_nomenclature_degat_essence"])

    return listes_essences


def copy_list(liste):

    return [elem for elem in liste]


def get_organisme_name_from_id(id_organisme):

    sql_text = text("SELECT b.nom_organisme \
        FROM utilisateurs.bib_organismes as b \
        WHERE b.id_organisme = {};".format(id_organisme))

    result = DB.engine.execute(sql_text).first()

    return result


def get_organisme_name_from_declarant_id(id_declarant):

    sql_text = text("SELECT b.nom_organisme \
        FROM utilisateurs.bib_organismes as b, utilisateurs.t_roles as r \
        WHERE b.id_organisme = r.id_organisme AND r.id_role = {};".format(id_declarant))

    result = DB.engine.execute(sql_text).first()[0]

    return result


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


def check_proprietaire(declaration_dict, nomenclature):
    '''
        Dans le cas ou le propretaire est le declarant
    '''

    id_nomenclature_proprietaire_declarant = declaration_dict['id_nomenclature_proprietaire_declarant']

    mnemonique = get_nomenclature_from_id(id_nomenclature_proprietaire_declarant, nomenclature, "mnemonique")

    # si le declarant n'est pas le proprietaire
    if mnemonique != 'P_D_O_NP':

        return -1

    # si le proprietaire est déjà renseigné
    if declaration_dict['foret']['id_proprietaire']:

        return -1

    # sinon  on recherche le proprietaire correspondant a l'id declarant
    id_declarant_proprietaire = declaration_dict['foret']['proprietaire']['id_declarant']

    if id_declarant_proprietaire:

        proprietaire = DB.session.query(TProprietaire).filter(id_declarant_proprietaire == TProprietaire.id_declarant).first()

        if proprietaire:

            declaration_dict['foret']['proprietaire'] = proprietaire.as_dict(True)

            return 1

    return -1


def check_foret(declaration_dict):
    '''
        recherche une foret quand une aire est renseignées
    '''

    foret_dict = declaration_dict.get("foret", None)

    if not foret_dict:

        return -1

    id_foret = foret_dict.get("id_foret", None)
    areas_foret = foret_dict.get("areas_foret", None)

    if((not id_foret) and areas_foret):

        # foret = get_id_foret_from_areas(declaration_dict["foret"]["areas_foret"]):

        v_id_type = [get_id_type(type) for type in ["OEASC_ONF_FRT"]]

        for area in areas_foret:

            id_area = area['id_area']
            data = DB.session.query(TAreas).filter(id_area == TAreas.id_area).first()

            if data:

                if data.id_type in v_id_type:

                    forets = DB.session.query(TForet).all()

                    for f in forets:

                        f_dict = f.as_dict(True)

                        for area_foret in f_dict['areas_foret']:

                            if id_area == area_foret['id_area']:

                                id_proprietaire = f_dict.get('id_proprietaire', None)

                                if id_proprietaire:

                                    proprietaire = DB.session.query(TProprietaire).filter(
                                        id_proprietaire == TProprietaire.id_proprietaire).first()

                                    f_dict["proprietaire"] = proprietaire.as_dict(True)

                                declaration_dict['foret'] = f_dict

                                return 1

    return -1


def get_gravite(declaration_dict, nomenclature):

    # id_nomenclature_peuplement_essence_principale = declaration_dict["id_nomenclature_peuplement_essence_principale"]

    id_nomenclature_degat_gravite_global = 0

    for degat in declaration_dict['degats']:

        for degat_essence in degat.get('degat_essences', []):

            # if degat_essence.get('id_nomenclature_degat_essence') == id_nomenclature_peuplement_essence_principale:

            id_nomenclature_degat_gravite = degat_essence.get('id_nomenclature_degat_gravite')

            if id_nomenclature_degat_gravite > id_nomenclature_degat_gravite_global:

                id_nomenclature_degat_gravite_global = id_nomenclature_degat_gravite

    if id_nomenclature_degat_gravite_global == 0:

        return ""

    return get_nomenclature_from_id(id_nomenclature_degat_gravite_global, nomenclature)


def utils_dict():
    """
        dictionnaire qui reference les function ci dessus pour les utiliser dans jinja cf server.py

    """
    d = {}

    d["copy_list"] = copy_list
    d["get_description_droit"] = get_description_droit
    d["get_organisme_name_from_id"] = get_organisme_name_from_id
    d["get_organisme_name_from_declarant_id"] = get_organisme_name_from_declarant_id
    d["get_nomenclature_from_id"] = get_nomenclature_from_id
    d["get_gravite"] = get_gravite

    return d
