"""
 Routes pour les pages declaration
"""
from flask import Blueprint, render_template, request, session

from app.modules.oeasc.nomenclature import nomenclature_oeasc
from app.modules.oeasc.user.utils import check_auth_redirect_login


from .repository import (
    dfpu_as_dict_from_id_declaration,
    get_declarations,
    get_declaration,
    get_declaration_table,
)

from .utils import get_listes_essences

bp = Blueprint("declaration", __name__)


@bp.route("/signalement_degats_forestiers")
def signalement_degats_forestiers():
    """
    accueil pour les signalement de degat forestiers
    """
    return render_template("modules/oeasc/pages/declaration/systeme_alerte.html")


@bp.route("informations_declaration")
@check_auth_redirect_login(1)
def informations_declaration():
    """
    page d'informations, en prélude au formulaire
    """

    return render_template(
        "modules/oeasc/pages/declaration/informations_declaration.html"
    )


@bp.route("/modifier_ou_creer_declaration/", defaults={"id_declaration": -1})
@bp.route("/modifier_ou_creer_declaration/<int:id_declaration>")
@check_auth_redirect_login(1)
def modifier_declaration(id_declaration):
    """
    page de declaration ou modification de degats forestiers

    :param id_declaration: identifiant en base de l'object declaration
    :type  id_declaration: integer ou None
    """

    if id_declaration != -1:
        declaration_dict = dfpu_as_dict_from_id_declaration(id_declaration)
    else:
        declaration_dict = dfpu_as_dict_from_id_declaration(id_declaration)

    declaration_table = get_declaration_table(declaration_dict)

    nomenclature = nomenclature_oeasc()

    listes_essences = []
    if declaration_dict:
        listes_essences = get_listes_essences(declaration_dict)

    id_form = request.args.get("id_form", "form_foret_statut")

    return render_template(
        "modules/oeasc/pages/declaration/modifier_ou_creer_declaration.html",
        declaration=declaration_dict,
        declaration_table=declaration_table,
        nomenclature=nomenclature,
        listes_essences=listes_essences,
        id_form=id_form,
        id_declaration=id_declaration,
    )


@bp.route("/declaration/<int:id_declaration>")
@check_auth_redirect_login(1)
def declaration(id_declaration):
    """
    page affichant une declaration

    TODO
    """

    declaration_dict = get_declaration(id_declaration)

    return render_template(
        "modules/oeasc/pages/declaration/declaration.html",
        declaration_table=declaration_dict,
        declaration=declaration_dict,
        id_declaration=id_declaration,
        nomenclature=nomenclature_oeasc(),
        btn_action=1,
    )


@bp.route("/declarations")
@check_auth_redirect_login(1)
def route_declarations():
    """
    page affichant la liste de declaration d'un utilisateur et de sa strucutre
    (sauf le cas ou structure = 'Particulier')
    les roles animateurs et administrateur peuvent tout voir
    """

    id_declarant = None

    if session.get("current_user", None):
        id_declarant = session["current_user"]["id_role"]

    nomenclature = nomenclature_oeasc()

    declarations = get_declarations(False, id_declarant)

    return render_template(
        "modules/oeasc/pages/declaration/declarations.html",
        declarations=declarations,
        nomenclature=nomenclature,
    )


@bp.route("/degats_grand_gibier")
def degats_gibier():
    """
    page du suvi de l'équilibre ASC

    TODO
    """

    return render_template("modules/oeasc/pages/declaration/degats_gibier.html")
