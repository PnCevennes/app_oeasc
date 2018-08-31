# -*- coding: utf-8 -*

from pypnnomenclature.models import TNomenclatures

from flask import (
    Blueprint, render_template, request
)

from .repository import (
    nomenclature_oeasc,
    declaration_dict_sample
)

from .utils import (
    get_listes_essences,
    check_foret
)

from .models import (
    TDeclaration,
    TForet, TProprietaire
)

from app.utils.env import DB

from app.utils.utilssqlalchemy import json_resp

from pypnusershub.db.models import User

from app.utils.utilssqlalchemy import as_dict

from app.ref_geo.models import TAreas

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
def form_declaration(id_declaration):

    declaration = DB.session.query(TDeclaration).filter(TDeclaration.id_declaration == id_declaration).first()

    return declaration.as_dict(True)


@bp.route('test_sample', methods=['POST', 'GET'])
@json_resp
def test_sample():

    declaration = TDeclaration()
    d = declaration_dict_sample()

    declaration.from_dict(d, True)

    d2 = declaration.as_dict(True)

    return d2


@bp.route('get_form_declaration', methods=['POST'])
@json_resp
def get_form_declaration():

    data = request.get_json()

    nomenclature = nomenclature_oeasc()

    declaration = data['declaration']
    id_form = data['id_form']

    # recherche de la  foret le cas echeant (apres un choix de foret documentee)

    check_foret(declaration)

    listes_essences = get_listes_essences(declaration)

    return render_template('modules/oeasc/form/form_declaration.html', declaration=declaration, nomenclature=nomenclature, listes_essences=listes_essences, id_form=id_form)



@bp.route('test_populate', methods=['GET'])
@json_resp
def test_populate():

    # d = declaration_dict_sample()
    # # return d;
    # return TDeclaration().from_dict(d, True).as_dict(True)

    for i in range(10):

        declaration = TDeclaration()
        declaration.from_dict(declaration_dict_sample(), True)

        DB.session.add(declaration)
        DB.session.commit()

    declaration = DB.session.query(
        TDeclaration).filter(
        TDeclaration.id_declaration == 1).first()

    return declaration.as_dict(True)

    return "ok"


@bp.route('delete_declaration/<int:id_declaration>', methods=['POST'])
@json_resp
def delete_declaration(id_declaration):

    DB.session.query(
        TDeclaration).filter(
        TDeclaration.id_declaration == id_declaration).delete()

    DB.session.commit()

    return "ok"


@bp.route('test', methods=['GET'])
@json_resp
def test():

    id_declaration = 3

    declaration = DB.session.query(
        TDeclaration).filter(
        TDeclaration.id_declaration == id_declaration).first()

    if(declaration):

        declaration_dict = declaration.as_dict(True)
        # declaration_dict["foret"]["id_foret"] = 82
        declaration_dict["foret"]["proprietaire"]["s_telephone"] = "06wesh"

    else:

        declaration_dict = declaration_dict_sample()

    return f_create_or_update_declaration(declaration_dict)


def f_create_or_update_declaration(declaration_dict):

    d_inter = TDeclaration().from_dict(declaration_dict, True)

    declaration_dict = d_inter.as_dict(True)

    declaration = TDeclaration()
    id_declaration = declaration_dict["id_declaration"]

    check_foret(declaration_dict)

    id_foret = declaration_dict["foret"]["id_foret"]
    id_proprietaire = declaration_dict["foret"]["proprietaire"]["id_proprietaire"]

    declaration = DB.session.query(
        TDeclaration).filter(
        TDeclaration.id_declaration == id_declaration).first()

    foret = DB.session.query(
        TForet).filter(
        TForet.id_foret == id_foret).first()

    proprietaire = DB.session.query(
        TProprietaire).filter(
        TProprietaire.id_proprietaire == id_proprietaire).first()

    if declaration is None:

        declaration = TDeclaration()
        DB.session.add(declaration)
        DB.session.commit()

        if foret:

            declaration.foret = foret
            DB.session.commit()

    declaration.from_dict(declaration_dict, True)

    DB.session.commit()

    return [declaration.as_dict(), declaration.foret.as_dict(), declaration.foret.proprietaire.as_dict()]


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
