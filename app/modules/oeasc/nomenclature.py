from flask import session, current_app
from pypnnomenclature.repository import get_nomenclature_list
from app.ref_geo.repository import get_type_code
from app.ref_geo.models import VAreas as VA, TAreas

config = current_app.config
DB = config['DB']


def nomenclature_oeasc():
    '''
        fonction pour récupérer toutes les nomenclatures qui concernent l'oeasc
        à l'aide de la commande get_nomenclature_list du module pypnnomenclature
    '''

    # on regarde si la nomenclature existe dans la variable globale g
    if not getattr(session, '_nomenclature', None):

        print("get_nomenclature from db")
        # TODO auto tout de l'oeasc from db ?
        list_data = [

            'OEASC_PEUPLEMENT_ESSENCE',
            'OEASC_PEUPLEMENT_MATURITE',
            'OEASC_PEUPLEMENT_PROTECTION_TYPE',
            'OEASC_PEUPLEMENT_PATURAGE_TYPE',
            'OEASC_PEUPLEMENT_PATURAGE_STATUT',
            'OEASC_PEUPLEMENT_ESPECE',
            'OEASC_PEUPLEMENT_ORIGINE',
            'OEASC_PEUPLEMENT_TYPE',
            'OEASC_PEUPLEMENT_ACCES',
            'OEASC_PEUPLEMENT_PATURAGE_FREQUENCE',
            'OEASC_PEUPLEMENT_PATURAGE_SAISON',
            'OEASC_DEGAT_TYPE',
            'OEASC_DEGAT_GRAVITE',
            'OEASC_DEGAT_ETENDUE',
            'OEASC_DEGAT_ANTERIORITE',
            'OEASC_PEUPLEMENT_ESSENCE',
            'OEASC_DEGAT_GRAVITE',
            'OEASC_DEGAT_ETENDUE',
            'OEASC_DEGAT_ANTERIORITE',
            'OEASC_FORET_TYPE',
            'OEASC_PROPRIETAIRE_DECLARANT',
            'OEASC_PROPRIETAIRE_TYPE',
            'OEASC_DECLARANT_FONCTION',

        ]

        data = {}

        for type_code in list_data:
            data[type_code] = get_nomenclature_list(code_type=type_code)

            if not data[type_code]:
                continue

            # on ne garde que les colonnes qui nous intéresse
            cols = ['id_nomenclature', 'mnemonique', 'cd_nomenclature', 'label_fr']
            values = []

            for d in data[type_code]["values"]:
                d_new = {}
                for key in cols:
                    d_new[key] = d.get(key, None)
                values.append(d_new)
            data[type_code]["values"] = values

        session._nomenclature = data

        dict_sort_nomenclature = {
            'OEASC_DEGAT_TYPE': [
                'ABR',
                'FRO',
                'ÉCO',
                'SANG',
                'LIEV',
                'ABS',
                'P/C',
            ]
        }

        for key, value in dict_sort_nomenclature.items():
            session._nomenclature[key]["values"].sort(key=lambda e: value.index(e['cd_nomenclature']))

    return session._nomenclature


def get_nomenclature_from_id(id_nomenclature, key=""):
    '''
        retourne un element de nomenclature a partir de son id
        si key == "", retourne l'element entier, sinon juste la clé choisie
    '''
    if not id_nomenclature:
        return None

    for _, nomenclature_type in nomenclature_oeasc().items():
        for elem in nomenclature_type["values"]:
            if str(elem["id_nomenclature"]) == str(id_nomenclature):
                if key != "":
                    return elem[key]
                else:
                    return elem

    return None


def get_nomenclature(key_in, value_in, type_code, key_out=""):

    nomemclature_type = nomenclature_oeasc().get(type_code, None)

    if not nomemclature_type:
        return None

    for elem in nomemclature_type["values"]:
        if str(elem[key_in]) == str(value_in):
            if key_out != "":
                return elem[key_out]
            else:
                return elem

    return None


def get_areas_from_ids(id_areas):
    '''
        search areas attributes in db if not yet in session._areas
    '''
    if not getattr(session, '_areas', None):
        session._areas = {}

    id_areas_to_query = []

    for id in id_areas:

        if not session._areas.get(str(id), None):

            id_areas_to_query.append(id)

    if id_areas_to_query:

        print("get areas from db ", len(id_areas_to_query))

        data = DB.session.query(VA).filter(VA.id_area.in_(id_areas_to_query))

        for d in data:

            d_dict = d.as_dict()
            d_dict['type_code'] = get_type_code(d_dict['id_type'])
            session._areas[str(d_dict['id_area'])] = d_dict


def get_area_from_id(id_area):
    '''
        search areas attributes in db if not yet in session._areas
    '''

    if not getattr(session, '_areas', None):
        session._areas = {}

    if not session._areas.get(str(id_area), None):

        print("get single area from db : " + str(id_area))

        data = DB.session.query(VA).filter(id_area == VA.id_area).first()

        if not data:

            return None

        out = data.as_dict(columns=['id_area', 'id_type', 'area_name', 'area_code', 'label'])

        out['type_code'] = get_type_code(out['id_type'])

        session._areas[str(id_area)] = out

    return session._areas[str(id_area)]


def pre_get_dict_nomenclature_areas(declarations):
    '''
        pre process pour recuperer les id_areas contenues dans un tableau de déclaration
        et faire une seule requete en bdd
    '''
    v_id_areas = []

    for declaration in declarations:

        for area in declaration.get('areas_localisation', []):
            v_id_areas.append(area)

        for area in declaration.get('areas_foret', []):
            v_id_areas.append(area)

        foret = declaration.get('foret', None)

        if not foret:
            continue

        for area in foret.get('areas_foret', []):
            v_id_areas.append(area)

    get_areas_from_ids(v_id_areas)


def get_dict_nomenclature_areas(dict_in):
    '''
        récupère les nomenclatures et les aires dans un dictionnaire pour les element d'un dictionnaire
        qui commencent par 'id_nomenclature' ou 'nomenclatures'
        la fonction est appliquée récursivement aux dictionnaire et aux listes
    '''
    if not isinstance(dict_in, dict):

        return dict_in

    for key in dict_in:
        if key.startswith("id_nomenclature_"):
            dict_in[key] = get_nomenclature_from_id(dict_in.get(key, None))
            continue

        if key.startswith("areas") and dict_in[key]:
            dict_res = []
            for elem in dict_in[key]:
                if isinstance(elem, int):
                    dict_res.append(get_area_from_id(elem))
                elif elem.get('id_area'):
                    dict_res.append(get_area_from_id(elem['id_area']))

            if dict_res:
                dict_in[key] = dict_res
            # dict_in[key] = [get_area_from_id(elem['id_area']) for elem in dict_in[key]]
            continue

        if key.startswith("nomenclatures_") and dict_in[key]:
            dict_res = []
            for elem in dict_in[key]:
                if isinstance(elem, int):
                    dict_res.append(get_nomenclature_from_id(elem))
                elif elem.get('id_nomenclature'):
                    dict_res.append(get_nomenclature_from_id(elem['id_nomenclature']))
            if dict_res:
                dict_in[key] = dict_res
            continue

        if isinstance(dict_in[key], dict):
            dict_in[key] = get_dict_nomenclature_areas(dict_in[key])
            continue

        if isinstance(dict_in[key], list):
            dict_in[key] = [get_dict_nomenclature_areas(elem) for elem in dict_in[key]]
            continue

    return dict_in
