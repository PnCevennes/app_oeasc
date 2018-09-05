# -*- coding: utf-8 -*


from pypnnomenclature.models import TNomenclatures

from flask import (
    Blueprint, render_template, request
)

from .repository import (
    nomenclature_oeasc,
    declaration_dict_sample,
    declaration_dict_random_sample,
    create_or_modify,
    dfp_as_dict,
    get_dfp,
)

from .utils import (
    get_listes_essences,
    get_liste_communes,
    check_foret,
    check_proprietaire
)

from .models import (
    TDeclaration,
    TForet, TProprietaire
)

from app.utils.env import DB

from app.utils.utilssqlalchemy import json_resp

from pypnusershub.db.models import User

from app.utils.utilssqlalchemy import as_dict

from app.ref_geo.models import TAreas, LAreas

bp = Blueprint('oeasc_api', __name__)


@bp.route('get_nomenclature_oeasc', methods=['GET'])
@json_resp
def get_nomenclature_oeasc():

    return nomenclature_oeasc()


@bp.route('get_nomenclature_mnemonique/<int:id_nomenclature>', methods=['GET'])
@json_resp
def get_nomenclature(id_nomenclature):

    data = DB.session.query(TNomenclatures.mnemonique).filter(TNomenclatures.id_nomenclature == id_nomenclature).first()[0]

    return data


@bp.route('declaration/<int:id_declaration>', methods=['GET'])
@json_resp
def declaration(id_declaration):

    declaration = DB.session.query(TDeclaration).filter(TDeclaration.id_declaration == id_declaration).first()

    if not declaration:

        return "La déclaration d'identifiant : " + str(id_declaration) + " n'existe pas."

    return declaration.as_dict(True)


@bp.route('get_form_declaration', methods=['POST'])
@json_resp
def get_form_declaration():

    data = request.get_json()

    nomenclature = nomenclature_oeasc()

    declaration_dict = data['declaration']
    id_form = data['id_form']

    # recherche de la  foret le cas echeant (apres un choix de foret documentee)
    check_foret(declaration_dict)
    check_proprietaire(declaration_dict, nomenclature)

    listes_essences = get_listes_essences(declaration_dict)
    declaration_dict["foret"]["communes"] = get_liste_communes(declaration_dict)

    return render_template('modules/oeasc/form/form_declaration.html', declaration=declaration_dict, nomenclature=nomenclature, listes_essences=listes_essences, id_form=id_form)


@bp.route('delete_declaration/<int:id_declaration>', methods=['POST'])
@json_resp
def delete_declaration(id_declaration):

    DB.session.query(
        TDeclaration).filter(
        TDeclaration.id_declaration == id_declaration).delete()

    DB.session.commit()

    return "ok"


@bp.route('test_random', methods=['GET'])
@json_resp
def test_random():

    declaration_dict = declaration_dict_random_sample()

    return declaration_dict


@bp.route('random_populate', defaults={'nb': 1}, methods=['GET'])
@bp.route('random_populate/<int:nb>', methods=['GET'])
@json_resp
def random_populate(nb):

    for i in range(nb):

        declaration_dict = declaration_dict_random_sample()

        if not declaration_dict:

            continue

        # create_date = declaration_dict['meta_create_date']

        check_foret(declaration_dict)
        f_create_or_update_declaration(declaration_dict)

        print("i", i, declaration_dict["foret"]["s_nom_foret"], "public", declaration_dict["foret"]["b_statut_public"], "documenté", declaration_dict["foret"]["b_document"])

    return "ok"


@bp.route('test', methods=['GET'])
@json_resp
def test():

    declaration_dict = declaration_dict_sample()

    id_declaration = 4

    declaration, foret, proprietaire = get_dfp(id_declaration)

    if(declaration):

        declaration_dict = dfp_as_dict(declaration, foret, proprietaire)

    check_foret(declaration_dict)

    return f_create_or_update_declaration(declaration_dict)


def f_create_or_update_declaration(declaration_dict):

    # return declaration_dict["foret"]["areas_foret"]

    declaration = proprietaire = foret = None

    id_declaration = declaration_dict.get("id_declaration", None)

    id_foret = declaration_dict["foret"].get("id_foret", None)
    id_proprietaire = declaration_dict["foret"]["proprietaire"].get("id_proprietaire", None)

    # return [id_foret, id_proprietaire, id_declaration, declaration_dict]

    proprietaire = create_or_modify(TProprietaire, 'id_proprietaire', id_proprietaire, declaration_dict["foret"]["proprietaire"])

    declaration_dict['foret']['id_proprietaire'] = proprietaire.id_proprietaire

    foret = create_or_modify(TForet, 'id_foret', id_foret, declaration_dict["foret"])

    declaration_dict['id_foret'] = foret.id_foret

    if declaration_dict.get("meta_create_date", None):

        declaration = create_or_modify(TDeclaration, 'id_declaration', id_declaration, declaration_dict)
        id_declaration = declaration.id_declaration
        print(declaration_dict['meta_create_date'])

    declaration = create_or_modify(TDeclaration, 'id_declaration', id_declaration, declaration_dict)


    d = dfp_as_dict(declaration, foret, proprietaire)

    return [d]


@bp.route('create_or_update_declaration', methods=['POST'])
@json_resp
def create_or_update_declaration():

    data = request.get_json()

    declaration_dict = data["declaration"]

    return f_create_or_update_declaration(declaration_dict)


@bp.route('get_db/<type>/<key>/<val>', methods=['GET'])
@json_resp
def get_db(type, key, val):

    switch_model = {

        "user": User,
        "t_areas": TAreas,
    }

    table = switch_model.get(type, None)

    if table:

        data = DB.session.query(table).filter(getattr(table, key) == val).first()

        if data:

            return as_dict(data)

    return "None"


@bp.route('declaration_areas/<int:id_declaration>/<string:type>', methods=['GET'])
@json_resp
def declaration_areas(id_declaration, type):

    declaration = DB.session.query(TDeclaration).filter(TDeclaration.id_declaration == id_declaration).first()

    id_foret = declaration.id_foret

    foret = DB.session.query(TForet).filter(TForet.id_foret == id_foret).first()

    areas = []

    if type == "foret":

        areas = foret.areas_foret

    else:

        areas = declaration.areas_localisation

    v = [a.id_area for a in areas]

    out = []

    for id_area in v:

        data = DB.session.query(LAreas).filter(LAreas.id_area == id_area).first()
        out.append(data.get_geofeature())

    return out
